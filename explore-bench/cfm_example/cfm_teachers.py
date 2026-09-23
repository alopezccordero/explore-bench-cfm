"""Privileged ("cheating") teachers for collect_data.py.

Both teachers plan on the *ground truth* map. Travel costs come from A* over the real free
space (`Astar.AStar`, the benchmark's own planner, run on `env.gt_map`), and a frontier is
valued by `territory()` -- a Voronoi partition of the whole unexplored map over the
candidate frontiers, so a frontier is worth every cell it gates, however far behind it
lies. Neither number is computable from what the robots have actually seen.

The learner never gets any of that. `collect_data.py` stores `build_condition(...)` of
the *partial* team map, so the flow model is trained to reproduce a decision it could not
have derived from its own input. That gap is the point: the teacher is an upper bound the
student imitates, in the spirit of privileged / learning-by-cheating imitation learning.

Two methods, both exact MILPs solved with HiGHS through `scipy.optimize.milp`:

`mtsp`      Multi-depot *open* mTSP / VRP over the frontier clusters, solved for minimum
            latency: every cluster is visited exactly once, routes start at the robots and
            never return, and `sum_j territory_j * arrival_j` is minimised. Subtours are
            cut with a single-commodity flow. Each robot drives to the first cluster on its
            own route; the rest is discarded and re-solved when a goal is consumed, so it
            behaves as a receding-horizon VRP.

`milp_cpp`  Coverage path planning as a minimum-cost viewpoint *set cover*. Every
            remaining unknown cell must be behind a frontier somebody has taken; among the
            covers, minimise total A* travel plus a makespan term over travel *and*
            sweeping, so the robots get comparable amounts of work rather than comparable
            drives. Each robot heads for the best area-per-distance frontier in its share.

Both score arrival *time*, not distance. Every plan visits every frontier eventually, so
total distance is nearly constant and says little about when the map gets uncovered --
which is exactly what steps-to-90%/98% measure.

The action space of both is the one the student samples on -- frontier cells of the
partial map (`cfm_policy.frontier_mask`) -- so the recorded goal already lies on a
frontier and `collect_data.py`'s snap distance stays near zero.
"""
import math

import numpy as np
from scipy import ndimage, sparse
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.spatial import cKDTree

from cfm_common import FREE, SENSOR_CELLS, UNKNOWN, WALL, frontier_mask

from Astar import AStar  # noqa: E402  (cfm_common puts grid_simulator on sys.path)

# Seconds per MILP solve and the gap HiGHS may stop at. The latency model below is a
# big-M formulation, whose LP relaxation is loose enough that proving optimality can take
# far longer than finding the optimum -- and a 2%-better route is worth nothing here,
# because the plan is thrown away and re-solved a few steps later anyway.
TIME_LIMIT = 3.0
MIP_GAP = 0.02
MIN_NODES = 4       # never prune below this many candidates, however lopsided the map


# ---------------------------------------------------------------- shared privileged view

class Privileged:
    """What both teachers know that the student does not.

    `candidates()` reads the robots' partial map, because a goal has to be a cell the
    student could also have proposed. Everything attached to those cells -- distance,
    information gain, reachability -- is read off the ground truth.
    """

    def __init__(self, env, max_nodes=10, min_cluster=3, replan=10, goal_tol=12.0,
                 min_share=0.02, latency=1.0):
        self.env = env
        self.max_nodes = max_nodes
        self.min_cluster = min_cluster
        self.min_share = min_share  # drop frontiers gating less than this share of what is left
        # How much of mtsp's objective is arrival time rather than distance travelled.
        # 1.0 is pure minimum latency, 0.0 pure minimum distance. Measured on `corner`:
        # latency buys a much tidier split (overlap 0.134 -> 0.073) but reaches 98% later
        # (479 -> 575 steps), because front-loading the big regions strands small pockets
        # that then need long backtracks. Blend to taste.
        self.latency = latency
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

        Only what a robot catches *on arrival* -- see territory() for the region a
        frontier gates, which is what the planners actually score against.
        """
        v = self._view.get(cell)
        if v is None:
            _, scale, _, _ = self.env.optimized_build_map(
                self.env.discrete_to_continuous(cell), 0, self.env.gt_map,
                self.env.resolution, self.env.sensor_range)
            v = np.flatnonzero((scale.ravel() != UNKNOWN) & self.countable).astype(np.int64)
            self._view[cell] = v
        return v

    def territory(self, nodes):
        """Voronoi partition of the unexplored map over the candidate frontiers.

        One multi-source wavefront across the *real* free space, seeded at every candidate
        at once, so each still-unknown cell ends up owned by the frontier a robot would
        have to pass through to reach it. A frontier is then worth the whole region behind
        it, not the slice its sensor happens to catch on arrival.

        That distinction is the whole point of letting the teacher cheat. Scoring by
        visibility alone throws the map knowledge away: measured on `corner`, only ~36% of
        the remaining unknown area is visible from any current frontier, so a
        visibility-scored planner is blind to the other ~64% and behaves myopically.

        Returns (owner, counts): `owner` is a flat map cell -> node index (-1 = nobody),
        `counts[i]` is how many unknown free cells node i gates.
        """
        w = self.env.gt_map.shape[1]
        passable = (self.astar_map == FREE).ravel().copy()
        owner = np.full(passable.shape, -1, np.int32)
        ring = np.array([c[0] * w + c[1] for c in nodes], np.int64)
        owner[ring] = np.arange(len(nodes), dtype=np.int32)
        passable[ring] = False
        while ring.size:
            # 4-neighbours of the whole frontier at once; the map's border ring is never
            # passable, so these indices stay inside the array
            nb = np.concatenate([ring + w, ring - w, ring + 1, ring - 1])
            src = np.tile(owner[ring], 4)
            keep = passable[nb]
            nb, src = nb[keep], src[keep]
            if nb.size == 0:
                break
            nb, first = np.unique(nb, return_index=True)  # ties go to the lowest index
            owner[nb] = src[first]
            passable[nb] = False
            ring = nb
        unknown = (self.env.complete_map.ravel() == UNKNOWN) & (self.astar_map.ravel() == FREE)
        lab = owner[unknown]
        return owner, np.bincount(lab[lab >= 0], minlength=len(nodes))

    # ------------------------------------------------------------ candidate goals

    def candidates(self):
        """Frontier clusters of the *partial* map as (cells, territory, owner map).

        Clusters are pre-filtered by cell count (cheap), then ranked by how much of the
        unexplored map each one gates, and the `max_nodes` biggest survive. The partition
        is recomputed over the survivors so the weights the planners see add up to the
        whole remaining map. Clusters gating nothing are dead frontiers and are dropped.
        """
        m = self.env.complete_map
        lab, n = ndimage.label(frontier_mask(m), structure=np.ones((3, 3)))
        if n == 0:
            return [], np.zeros(0, int), None

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

        _, gated = self.territory(cells)
        keep = list(np.argsort(-gated)[:self.max_nodes])
        # Nearly every frontier gates *something*, so unlike the old zero-gain test this
        # ranking almost never prunes on its own, and mtsp pays for it quadratically: it
        # needs an A* between every pair of nodes. Drop the slivers instead. The threshold
        # is a share of what is left, so as the map fills the survivors' territories
        # shrink too and the last few pockets stop looking negligible.
        floor = self.min_share * float(gated.sum())
        big = [i for i in keep if gated[i] >= floor]
        keep = big if len(big) >= MIN_NODES else keep[:MIN_NODES]
        cells = [cells[i] for i in keep]
        owner, gated = self.territory(cells)  # repartition over the survivors only
        return cells, gated, owner

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
            nodes, gated, owner = self.candidates()
            self.goals = list(pos) if not nodes else self.plan(pos, nodes, gated, owner)
            self._solved_step = env.num_step
            self.solves += 1
        return np.array(self.goals)

    def plan(self, pos, nodes, gated, owner):
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
               options={'time_limit': TIME_LIMIT, 'presolve': True, 'mip_rel_gap': MIP_GAP})
    return None if res.x is None else np.asarray(res.x)


# ---------------------------------------------------------------- mTSP / VRP teacher

class MtspTeacher(Privileged):
    """Multi-depot open mTSP over the frontier clusters, solved for minimum *latency*.

    Arc variables x_ij over {robots} u {clusters}: no arc enters a robot and none leaves a
    cluster twice, so a solution is a set of vehicle paths. Subtours are removed by a
    single-commodity flow -- each cluster absorbs one unit and all units are pushed out of
    the robots. The goal handed to the simulator is the head of each robot's route.

    The objective is `sum_j territory_j * arrival_j`, not total distance. Every route
    visits every cluster either way, so total distance is nearly a constant and optimising
    it says almost nothing about *when* the map gets uncovered -- which is exactly what
    steps-to-90%/98% measure. Weighting each cluster's arrival time by the area it gates
    makes the solver front-load the big unexplored regions: the traveling-repairman
    objective rather than the traveling-salesman one. Arrival times come from big-M
    ordering constraints on the arcs that were already in the model.
    """

    def plan(self, pos, nodes, gated, owner):
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

        # columns: x_k in {0,1} for k < na, the flow f_k in [0, m] on the same arc, then
        # one arrival time a_j per cluster
        # No arrival can exceed the longest possible open route, which uses at most m arcs:
        # bounding by the m largest costs rather than m * the largest keeps the big-M
        # constraints far tighter, and a loose M is what makes this model slow to prove
        finite = sorted(w for w in weight if np.isfinite(w))
        big_m = float(sum(finite[-m:])) + 1.0 if finite else 1.0
        arrive = {j: 2 * na + (j - r) for j in range(r, r + m)}
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

        # arrival times: taking arc i->j puts a_j at least one hop after a_i (a depot's
        # own arrival is 0, so it drops out); slack when the arc is unused
        for k, (a, b) in enumerate(arcs):
            row = {arrive[b]: 1, k: -big_m}
            if a >= r:
                row[arrive[a]] = -1
            rows.append((row, weight[k] - big_m, np.inf))

        # weights normalised so the objective does not depend on map size; the distance
        # term is a tie-break between plans that uncover the map equally fast
        total = float(gated.sum())
        w_j = (gated / total) if total > 0 else np.ones(m) / m
        lat = self.latency
        # both terms are scaled to O(1) so `latency` blends them on comparable footing;
        # the epsilon keeps distance as a tie-break even at latency = 1
        eps = 1e-3 / max(big_m, 1.0)
        c = [((1.0 - lat) / max(big_m, 1.0) + eps) * v for v in weight]             + [0.0] * na + [lat * v for v in w_j]
        x = solve(c, rows, [1] * na + [0] * (na + m),
                  [0] * (2 * na + m), [1] * na + [m] * na + [big_m] * m)
        if x is None:                                               # no feasible split
            return self.greedy(pos, nodes, cost, inter, gated)

        goals, taken = [], set()
        for i in range(r):
            j = next((arcs[k][1] - r for k in out_of[i] if x[k] > 0.5), None)
            if j is None or nodes[j] == pos[i]:
                j = self.fallback(i, cost, taken)
            goals.append(pos[i] if j is None else nodes[j])
            taken.add(j)
        return goals

    def greedy(self, pos, nodes, cost, inter, gated):
        """Best territory per cell travelled, always extending the shortest route.

        The latency objective in miniature, for when HiGHS returns nothing.
        """
        r, m = len(pos), len(nodes)
        end, length, started = list(range(r)), [0.0] * r, [False] * r
        first, left = [None] * r, set(range(m))
        while left:
            i = min(range(r), key=lambda i: length[i])
            rest = sorted(left)
            d = [inter[end[i], j] if started[i] else cost[i, j] for j in rest]
            if not np.isfinite(min(d)):
                break
            value = [(gated[j] + 1.0) / (dj + 1.0) if np.isfinite(dj) else -1.0
                     for j, dj in zip(rest, d)]
            pick = int(np.argmax(value))
            j, step = rest[pick], d[pick]
            length[i] += step
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
        """Flat indices of unknown ground-truth-free cells, thinned to max_elements."""
        u = np.flatnonzero((self.env.complete_map.ravel() == UNKNOWN)
                           & (self.astar_map.ravel() == FREE))
        if len(u) > self.max_elements:
            u = u[np.linspace(0, len(u) - 1, self.max_elements).astype(int)]
        return u

    def plan(self, pos, nodes, gated, owner):
        r, m = len(pos), len(nodes)
        cost = self.cost_matrix(pos, nodes)
        usable = [j for j in range(m) if np.isfinite(cost[:, j]).any()]
        if not usable:
            return list(pos)

        # cover sets come from the territory partition, not from what a viewpoint can see
        # on arrival: every remaining unknown cell belongs to the frontier that gates it,
        # so the cover ranges over the whole unexplored map instead of the ~36% in sensor
        # range of some frontier, which is what made this myopic
        elems = self.elements()
        own = owner[elems]
        seen = np.array([own == j for j in usable])
        seen = seen[:, seen.any(0)]          # cells behind no reachable frontier are dropped

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
        # a robot's share is the driving plus the sweeping: clearing a region of A cells
        # with a sensor of this radius takes roughly A / (2 * SENSOR_CELLS) more steps, so
        # balancing travel alone would hand one robot a corridor and the other a wing
        work = {j: float(gated[j]) / (2.0 * SENSOR_CELLS) for j in usable}
        for i in range(r):                   # T >= this robot's assigned travel + sweeping
            row = {t: 1}
            row.update({col[j, i]: -(cost[i, j] + work[j]) for j in usable
                        if np.isfinite(cost[i, j])})
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
            # within its own share, go for the most area per cell driven, so the big
            # regions fall early rather than whichever frontier happens to be nearest
            j = (max(mine, key=lambda j: (gated[j] + 1.0) / (cost[i, j] + 1.0)) if mine
                 else self.fallback(i, cost, taken))
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
