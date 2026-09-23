"""Privileged ("cheating") teachers for collect_data.py.

Both teachers plan on the *ground truth* map: travel costs come from A* over the real
free space (`Astar.AStar`, the benchmark's own planner, run on `env.gt_map`), and the
value of a goal comes from the simulator's own sensor model, which says exactly how much
still-unknown area a robot would reveal by standing there. Neither number is computable
from what the robots have actually seen.

The learner never gets any of that. `collect_data.py` stores `build_condition(...)` of
the *partial* team map, so the flow model is trained to reproduce a decision it could not
have derived from its own input. That gap is the point: the teacher is an upper bound the
student imitates, in the spirit of privileged / learning-by-cheating imitation learning.

Two methods, both exact MILPs solved with HiGHS through `scipy.optimize.milp`:

`mtsp`      Multi-depot *open* mTSP / VRP over the frontier clusters. Every cluster is
            visited exactly once, routes start at the robots and never return, total true
            travel distance is minimised. Subtours are cut with a single-commodity flow.
            Each robot drives to the first cluster on its own route; the rest is discarded
            and re-solved when a goal is consumed, so it behaves as a receding-horizon VRP.

`milp_cpp`  Coverage path planning as a minimum-cost viewpoint *set cover*. Every unknown
            cell that any candidate viewpoint can actually see must be seen by somebody;
            among the covers, minimise total A* travel plus a makespan term that keeps the
            robots' workloads balanced. Each robot drives to the cheapest viewpoint it was
            assigned.

The action space of both is the one the student samples on -- frontier cells of the
partial map (`cfm_policy.frontier_mask`) -- so the recorded goal already lies on a
frontier and `collect_data.py`'s snap distance stays near zero.
"""
import math

import numpy as np
from scipy import ndimage, sparse
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.spatial import cKDTree

from cfm_common import FREE, UNKNOWN, WALL, frontier_mask

from Astar import AStar  # noqa: E402  (cfm_common puts grid_simulator on sys.path)

TIME_LIMIT = 10.0    # seconds per MILP solve; HiGHS returns its incumbent after this


# ---------------------------------------------------------------- shared privileged view

class Privileged:
    """What both teachers know that the student does not.

    `candidates()` reads the robots' partial map, because a goal has to be a cell the
    student could also have proposed. Everything attached to those cells -- distance,
    information gain, reachability -- is read off the ground truth.
    """

    def __init__(self, env, max_nodes=10, min_cluster=3, replan=10, goal_tol=12.0):
        self.env = env
        self.max_nodes = max_nodes
        self.min_cluster = min_cluster
        # Re-solve every N steps as well as on events (0 = events only). 10 measured best
        # for both teachers on `room`: it beats 25 because a plan built on a 25-step-old
        # map sends robots to stale frontiers, and beats 1 on wall clock several times
        # over while finishing sooner, because better plans need fewer steps to run.
        self.replan = replan
        self.goal_tol = goal_tol  # how far a goal may drift with its frontier before re-solving

        # A* treats anything that is not 254 as an obstacle, so blueprint-unknown space
        # cannot be walked through; the border ring keeps its get_neighbor() in range.
        self.astar_map = np.where(env.gt_map == FREE, FREE, WALL).astype(np.uint8)
        self.astar_map[[0, -1], :] = WALL
        self.astar_map[:, [0, -1]] = WALL
        # cells in different components of the real free space are unreachable from each
        # other: checking that first stops A* from expanding the whole map before failing
        self.component, _ = ndimage.label(self.astar_map == FREE, structure=np.ones((3, 3)))
        # cells that count towards the benchmark's coverage metric (gt free or gt wall)
        self.countable = (env.gt_map != UNKNOWN).ravel()

        self._dist = {}          # (cell, cell) -> true A* length
        self._view = {}          # cell -> flat indices the sensor would reveal there
        self.goals = None
        self.solves = 0
        self._solved_step = -10 ** 9

    # ------------------------------------------------------------ privileged quantities

    def dist(self, a, b):
        """True walking distance a -> b: A* on the ground-truth free space."""
        if a == b:
            return 0.0
        key = (a, b) if a <= b else (b, a)
        d = self._dist.get(key)
        if d is None:
            ca, cb = self.component[a], self.component[b]
            if ca == 0 or cb == 0 or ca != cb:
                d = math.inf
            else:
                path = np.asarray(AStar(a, b, self.astar_map, 'euclidean').searching()[0], float)
                d = float(np.hypot(*(path[1:] - path[:-1]).T).sum()) if len(path) > 1 else 0.0
            self._dist[key] = d
        return d

    def visible(self, cell):
        """Flat indices of the countable cells the sensor would reveal from `cell`.

        This is the simulator's own omni-directional scan against the ground truth, so
        occlusion is handled exactly as it will be when the robot arrives. The set does
        not depend on what is known yet, so it is cached for good.
        """
        v = self._view.get(cell)
        if v is None:
            _, scale, _, _ = self.env.optimized_build_map(
                self.env.discrete_to_continuous(cell), 0, self.env.gt_map,
                self.env.resolution, self.env.sensor_range)
            v = np.flatnonzero((scale.ravel() != UNKNOWN) & self.countable).astype(np.int64)
            self._view[cell] = v
        return v

    # ------------------------------------------------------------ candidate goals

    def candidates(self):
        """Frontier clusters of the *partial* map as (cells, gains), best gain first.

        Clusters are pre-filtered by cell count (cheap) before their true gain is measured
        (one sensor simulation each), then the `max_nodes` most informative survive.
        Clusters that would reveal nothing are dead frontiers and are dropped.
        """
        m = self.env.complete_map
        lab, n = ndimage.label(frontier_mask(m), structure=np.ones((3, 3)))
        if n == 0:
            return [], np.zeros(0, int)

        flat = lab.ravel()
        counts = np.bincount(flat, minlength=n + 1)
        order = np.argsort(flat, kind='stable')[counts[0]:]
        groups = np.split(order, np.cumsum(counts[1:])[:-1])
        big = [g for g in groups if len(g) >= self.min_cluster] or groups
        big.sort(key=len, reverse=True)

        h, w = m.shape
        cells = []
        for g in big[:3 * self.max_nodes]:
            pts = np.stack(np.unravel_index(g, m.shape), 1)
            rep = pts[np.abs(pts - pts.mean(0)).sum(1).argmin()]
            # the sensor model writes a 3x3 patch around the viewpoint, so stay off the rim
            cells.append((int(np.clip(rep[0], 2, h - 3)), int(np.clip(rep[1], 2, w - 3))))

        unknown = (m == UNKNOWN).ravel()
        gains = np.array([int(unknown[self.visible(c)].sum()) for c in cells])
        keep = list(np.argsort(-gains)[:self.max_nodes])
        keep = [i for i in keep if gains[i] > 0] or keep
        return [cells[i] for i in keep], gains[keep]

    # ------------------------------------------------------------ sticky goal interface

    def __call__(self):
        """(num_agents, 2) goals, the shape GridEnv.step_for_cost() expects.

        A goal is *followed*, not just held. Walking towards a frontier pushes it back --
        the cell aimed at stops touching unknown space as soon as the robot sees past it,
        typically on the very next step -- so a goal that has only receded is re-snapped
        onto the nearest frontier cell and kept. The MILP runs again when a robot actually
        arrives, when its frontier is gone rather than merely moved (the snap exceeds
        `goal_tol`, e.g. the corridor it was following opened into a room), or every
        `replan` steps so the routing can take new map into account.
        """
        env = self.env
        pos = [(int(p[0]), int(p[1])) for p in env.agent_pos]
        cells = np.argwhere(frontier_mask(env.complete_map))
        stale = self.goals is None or len(cells) == 0
        if not stale:
            tree, kept = cKDTree(cells), []
            for g, p in zip(self.goals, pos):
                d, j = tree.query(tuple(g))
                if tuple(g) == p or d > self.goal_tol:
                    stale = True
                    break
                kept.append((int(cells[j][0]), int(cells[j][1])))
            if not stale:
                self.goals = kept
        if self.replan and env.num_step - self._solved_step >= self.replan:
            stale = True
        if stale:
            nodes, gains = self.candidates()
            self.goals = list(pos) if not nodes else self.plan(pos, nodes, gains)
            self._solved_step = env.num_step
            self.solves += 1
        return np.array(self.goals)

    def plan(self, pos, nodes, gains):
        raise NotImplementedError

    # ------------------------------------------------------------ helpers for subclasses

    def cost_matrix(self, pos, nodes):
        """cost[r][j]: true A* distance from robot r to candidate j (inf = unreachable)."""
        return np.array([[self.dist(p, c) for c in nodes] for p in pos])

    @staticmethod
    def fallback(r, cost, taken):
        """Nearest reachable candidate, for a robot the optimiser left without one."""
        free = [j for j in range(cost.shape[1]) if j not in taken and np.isfinite(cost[r, j])]
        pool = free or [j for j in range(cost.shape[1]) if np.isfinite(cost[r, j])]
        return min(pool, key=lambda j: cost[r, j]) if pool else None


def solve(c, rows, integrality, lo, hi):
    """min c.x subject to `rows`, a list of (coefficients dict, lb, ub). None if no plan.

    HiGHS gets a time limit and its incumbent is accepted, so a hard instance degrades
    into a good feasible plan instead of stalling the data collection.
    """
    data, ri, ci, lb, ub = [], [], [], [], []
    for i, (coefs, low, up) in enumerate(rows):
        for col, val in coefs.items():
            data.append(float(val))
            ri.append(i)
            ci.append(col)
        lb.append(low)
        ub.append(up)
    a = sparse.coo_matrix((data, (ri, ci)), shape=(len(rows), len(c))).tocsr()
    res = milp(c=np.asarray(c, float), constraints=LinearConstraint(a, lb, ub),
               integrality=np.asarray(integrality),
               bounds=Bounds(np.asarray(lo, float), np.asarray(hi, float)),
               options={'time_limit': TIME_LIMIT, 'presolve': True})
    return None if res.x is None else np.asarray(res.x)


# ---------------------------------------------------------------- mTSP / VRP teacher

class MtspTeacher(Privileged):
    """Multi-depot open mTSP: split the frontier clusters into one route per robot.

    Arc variables x_ij over {robots} u {clusters}: no arc enters a robot and none leaves a
    cluster twice, so a solution is a set of vehicle paths. Subtours are removed by a
    single-commodity flow -- each cluster absorbs one unit and all units are pushed out of
    the robots -- which is compact enough that HiGHS solves these in milliseconds. The
    goal handed to the simulator is the head of each robot's route.
    """

    def plan(self, pos, nodes, gains):
        r, m = len(pos), len(nodes)
        cost = self.cost_matrix(pos, nodes)
        inter = np.array([[self.dist(a, b) for b in nodes] for a in nodes])

        # arcs: robot -> cluster and cluster -> cluster; unreachable pairs are left out
        arcs = [(i, r + j) for i in range(r) for j in range(m) if np.isfinite(cost[i, j])]
        arcs += [(r + i, r + j) for i in range(m) for j in range(m)
                 if i != j and np.isfinite(inter[i, j])]
        if not arcs:
            return list(pos)
        weight = [cost[a, b - r] if a < r else inter[a - r, b - r] for a, b in arcs]
        na = len(arcs)

        out_of = {v: [] for v in range(r + m)}
        into = {v: [] for v in range(r + m)}
        for k, (a, b) in enumerate(arcs):
            out_of[a].append(k)
            into[b].append(k)

        # columns: x_k in {0,1} for k < na, then the flow f_k in [0, m] on the same arc
        rows = []
        for j in range(r, r + m):
            rows.append(({k: 1 for k in into[j]}, 1, 1))            # visited exactly once
            rows.append(({k: 1 for k in out_of[j]}, 0, 1))          # left at most once
            flow = {na + k: 1 for k in into[j]}
            for k in out_of[j]:
                flow[na + k] = flow.get(na + k, 0) - 1
            rows.append((flow, 1, 1))                               # absorbs one unit
        usable = [i for i in range(r) if out_of[i]]
        # every robot that can reach a cluster gets one, as long as there are enough to go
        # round -- an idle robot is wasted exploration, which min-sum would not punish
        floor = 1 if len(usable) <= m else 0
        for i in usable:
            rows.append(({k: 1 for k in out_of[i]}, floor, 1))
        if floor == 0:
            rows.append(({k: 1 for i in usable for k in out_of[i]}, m, m))
        rows.append(({na + k: 1 for i in usable for k in out_of[i]}, m, m))  # robots supply m
        for k in range(na):
            rows.append(({na + k: 1, k: -m}, -np.inf, 0))           # flow only on used arcs

        x = solve(list(weight) + [0.0] * na, rows, [1] * na + [0] * na,
                  [0] * (2 * na), [1] * na + [m] * na)
        if x is None:                                               # no feasible split
            return self.greedy(pos, nodes, cost, inter)

        goals, taken = [], set()
        for i in range(r):
            j = next((arcs[k][1] - r for k in out_of[i] if x[k] > 0.5), None)
            if j is None or nodes[j] == pos[i]:
                j = self.fallback(i, cost, taken)
            goals.append(pos[i] if j is None else nodes[j])
            taken.add(j)
        return goals

    def greedy(self, pos, nodes, cost, inter):
        """Nearest-neighbour mTSP, always extending the shortest route. If HiGHS fails."""
        r, m = len(pos), len(nodes)
        end, length, started = list(range(r)), [0.0] * r, [False] * r
        first, left = [None] * r, set(range(m))
        while left:
            i = min(range(r), key=lambda i: length[i])
            rest = sorted(left)
            d = [inter[end[i], j] if started[i] else cost[i, j] for j in rest]
            if not np.isfinite(min(d)):
                break
            j = rest[int(np.argmin(d))]
            length[i] += min(d)
            if first[i] is None:
                first[i] = j
            end[i], started[i] = j, True
            left.discard(j)
        goals, taken = [], set()
        for i in range(r):
            j = first[i] if first[i] is not None else self.fallback(i, cost, taken)
            goals.append(pos[i] if j is None else nodes[j])
            taken.add(j)
        return goals


# ---------------------------------------------------------------- MILP coverage teacher

class MilpCppTeacher(Privileged):
    """Coverage path planning as a min-cost viewpoint set cover with a makespan term.

    Elements are the cells that are still unknown and do count towards coverage, thinned
    to `max_elements` so the constraint matrix stays small. Column (v, r) means "robot r
    visits viewpoint v". Every element that *can* be seen must be seen, each viewpoint
    belongs to at most one robot, and T bounds each robot's assigned travel, so

        min  sum_{v,r} dist(r, v) * y[v, r]  +  balance * T

    buys full coverage of the reachable unknown area at the lowest total A* distance while
    keeping the split between robots even. The robot then drives to the cheapest viewpoint
    in its own share; the rest of the share is re-solved on arrival. Travel is scored per
    viewpoint rather than along a route, which is the usual assignment relaxation of
    multi-robot CPP -- `mtsp` is the one that reasons about route order.
    """

    def __init__(self, *args, max_elements=400, balance=1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_elements = max_elements
        self.balance = balance

    def elements(self):
        """Flat indices of unknown-but-countable cells, thinned to at most max_elements."""
        u = np.flatnonzero((self.env.complete_map.ravel() == UNKNOWN) & self.countable)
        if len(u) > self.max_elements:
            u = u[np.linspace(0, len(u) - 1, self.max_elements).astype(int)]
        return u

    def plan(self, pos, nodes, gains):
        r, m = len(pos), len(nodes)
        cost = self.cost_matrix(pos, nodes)
        usable = [j for j in range(m) if np.isfinite(cost[:, j]).any()]
        if not usable:
            return list(pos)

        elems = self.elements()
        seen = np.array([_member(self.visible(nodes[j]), elems) for j in usable])
        seen = seen[:, seen.any(0)]          # unknown cells no viewpoint reaches are dropped

        col = {(j, i): len(usable) * i + k for k, j in enumerate(usable) for i in range(r)}
        t = len(usable) * r                  # index of the makespan variable
        c = [0.0] * (t + 1)
        for (j, i), k in col.items():
            c[k] = cost[i, j] if np.isfinite(cost[i, j]) else 0.0
        c[t] = self.balance

        rows = []
        for e in range(seen.shape[1]):       # every reachable unknown cell is seen by someone
            rows.append(({col[j, i]: 1 for k, j in enumerate(usable) if seen[k, e]
                          for i in range(r)}, 1, np.inf))
        for j in usable:                     # a viewpoint belongs to one robot, or to none
            rows.append(({col[j, i]: 1 for i in range(r)}, 0, 1))
        for i in range(r):                   # T >= this robot's assigned travel
            row = {t: 1}
            row.update({col[j, i]: -cost[i, j] for j in usable if np.isfinite(cost[i, j])})
            rows.append((row, 0, np.inf))
            if len(usable) >= r:             # nobody sits idle while work is left
                rows.append(({col[j, i]: 1 for j in usable}, 1, np.inf))

        hi = [1.0] * t + [np.inf]
        for (j, i), k in col.items():
            if not np.isfinite(cost[i, j]):
                hi[k] = 0.0                  # robot i cannot get to viewpoint j
        x = solve(c, rows, [1] * t + [0], [0.0] * (t + 1), hi)
        if x is None:
            return self.greedy(pos, nodes, cost, seen, usable)

        goals, taken = [], set()
        for i in range(r):
            mine = [j for j in usable if x[col[j, i]] > 0.5 and nodes[j] != pos[i]]
            j = min(mine, key=lambda j: cost[i, j]) if mine else self.fallback(i, cost, taken)
            goals.append(pos[i] if j is None else nodes[j])
            taken.add(j)
        return goals

    def greedy(self, pos, nodes, cost, seen, usable):
        """Cheapest-per-new-cell set cover, then each robot takes its nearest pick."""
        left = np.ones(seen.shape[1], bool)
        chosen = []
        while left.any() and len(chosen) < len(usable):
            ratio = []
            for k, j in enumerate(usable):
                new = int((seen[k] & left).sum())
                reach = cost[:, j].min()
                ratio.append((reach + 1.0) / new if new and np.isfinite(reach) else np.inf)
            k = int(np.argmin(ratio))
            if not np.isfinite(ratio[k]):
                break
            left &= ~seen[k]
            chosen.append(usable[k])
        goals, taken = [], set()
        for i in range(len(pos)):
            mine = [j for j in chosen if j not in taken and np.isfinite(cost[i, j])
                    and nodes[j] != pos[i]]
            j = min(mine, key=lambda j: cost[i, j]) if mine else self.fallback(i, cost, taken)
            goals.append(pos[i] if j is None else nodes[j])
            taken.add(j)
        return goals


def _member(sorted_idx, query):
    """Boolean "is in", for two arrays of flat indices, the left one sorted."""
    if len(sorted_idx) == 0:
        return np.zeros(len(query), bool)
    p = np.searchsorted(sorted_idx, query).clip(0, len(sorted_idx) - 1)
    return sorted_idx[p] == query


TEACHERS = {'mtsp': MtspTeacher, 'milp_cpp': MilpCppTeacher}


def make_teacher(method, env, **kwargs):
    """`method` is a key of TEACHERS; the result is a callable GridEnv uses as get_goal."""
    return TEACHERS[method](env, **kwargs)
