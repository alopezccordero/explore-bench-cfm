"""Audit the privileged teachers: are they actually optimal oracles?

    python audit_teacher.py --method milp_cpp --map room --seed 41 --max-steps 300

Three questions, because "MILP" on its own guarantees none of them.

1. SOLVER GAP. `cfm_teachers.solve()` returns `res.x` and looks at nothing else, so a
   solve that hit TIME_LIMIT and returned an incumbent is indistinguishable from a proven
   optimum. This wraps `solve` and records HiGHS's status, mip_gap and node count for
   every call. A non-zero gap means the teacher's own objective was not minimised.

2. CANDIDATE-SET LOSS. The MILP is optimal over the candidate set, and `candidates()`
   hands it at most `max_nodes` cells: one medoid per frontier cluster, clusters ranked by
   *cell count* and truncated to 3*max_nodes before any information gain is measured. So
   the search space is chosen by a size heuristic. This measures what that discards --
   total reachable gain vs gain offered vs gain kept -- and whether the medoid is even a
   frontier cell after the rim clip.

3. ROUTE-COST APPROXIMATION. `MilpCppTeacher` charges `dist(robot_now, v)` for every
   viewpoint v it assigns to a robot, so a robot assigned k viewpoints is billed k
   independent trips out of its current position instead of one route through them. This
   compares that charge against the true optimal open tour (exact Held-Karp) over the same
   assigned set, and -- what actually matters -- whether the first stop of the real optimal
   tour is the viewpoint the teacher drives to.

Nothing here changes the teachers. It measures them.
"""
import argparse
import itertools
import time

import numpy as np
from scipy import ndimage

import cfm_teachers
from cfm_common import FREE, UNKNOWN, frontier_mask, make_env, quiet  # noqa: F401

SOLVES = []        # one record per MILP solve
LAST_X = [None]    # solution vector of the most recent solve, for the assignment audit
CAND = []          # one record per candidates() call
ROUTE = []         # one record per (solve, robot) assignment
STALE = []         # one record per (step, robot): is the committed goal still worth it?


def patch_solve():
    """Record what HiGHS reported, which cfm_teachers.solve() currently drops."""
    from scipy import sparse
    from scipy.optimize import Bounds, LinearConstraint, milp

    def solve(c, rows, integrality, lo, hi):
        data, ri, ci, lb, ub = [], [], [], [], []
        for i, (coefs, low, up) in enumerate(rows):
            for col, val in coefs.items():
                data.append(float(val)); ri.append(i); ci.append(col)
            lb.append(low); ub.append(up)
        a = sparse.coo_matrix((data, (ri, ci)), shape=(len(rows), len(c))).tocsr()
        t0 = time.time()
        res = milp(c=np.asarray(c, float),
                   constraints=LinearConstraint(a, lb, ub),
                   integrality=np.asarray(integrality),
                   bounds=Bounds(np.asarray(lo, float), np.asarray(hi, float)),
                   options={'time_limit': cfm_teachers.TIME_LIMIT, 'presolve': True})
        SOLVES.append(dict(
            status=int(res.status), secs=time.time() - t0,
            gap=float(res.mip_gap) if res.mip_gap is not None else float('nan'),
            nodes=int(res.mip_node_count or 0), nvar=len(c), ncon=len(rows),
            obj=float(res.fun) if res.fun is not None else float('nan'),
            dual=float(res.mip_dual_bound) if res.mip_dual_bound is not None else float('nan'),
            feasible=res.x is not None))
        LAST_X[0] = None if res.x is None else np.asarray(res.x)
        return LAST_X[0]

    cfm_teachers.solve = solve


def patch_candidates(T):
    """Measure the gain the size pre-filter and max_nodes truncation throw away."""
    orig = T.candidates

    def candidates(self):
        m = self.env.complete_map
        lab, n = ndimage.label(frontier_mask(m), structure=np.ones((3, 3)))
        rec = dict(clusters=n, kept=0, gain_kept=0, gain_offered=0, gain_all=0,
                   off_frontier=0, unreachable=0, dropped_better=0,
                   clusters_measured=0, clusters_unmeasured=0)
        if n:
            fm = frontier_mask(m)
            unknown = (m == UNKNOWN).ravel()
            flat = lab.ravel()
            counts = np.bincount(flat, minlength=n + 1)
            order = np.argsort(flat, kind='stable')[counts[0]:]
            groups = np.split(order, np.cumsum(counts[1:])[:-1])
            big = [g for g in groups if len(g) >= self.min_cluster] or groups
            big.sort(key=len, reverse=True)
            h, w = m.shape

            def rep_of(g):
                pts = np.stack(np.unravel_index(g, m.shape), 1)
                r = pts[np.abs(pts - pts.mean(0)).sum(1).argmin()]
                return (int(np.clip(r[0], 2, h - 3)), int(np.clip(r[1], 2, w - 3)))

            # every cluster's gain, including the ones the size filter never looks at
            AUDIT_CAP = 80            # one sensor simulation per cluster; bound the cost
            rec['clusters_measured'] = min(len(big), AUDIT_CAP)
            rec['clusters_unmeasured'] = max(0, len(big) - AUDIT_CAP)
            all_gain = []
            for g in big[:AUDIT_CAP]:
                c = rep_of(g)
                all_gain.append(int(unknown[self.visible(c)].sum()))
            offered = all_gain[:3 * self.max_nodes]
            rec['gain_all'] = int(sum(all_gain))
            rec['gain_offered'] = int(sum(offered))
            # a cluster the size filter dropped that beats the weakest one it offered
            if len(all_gain) > 3 * self.max_nodes and offered:
                rec['dropped_better'] = int(sum(1 for x in all_gain[3 * self.max_nodes:]
                                                if x > min(offered)))
            # rim clip can push the representative off the frontier, or into a wall
            for g in big[:3 * self.max_nodes]:
                c = rep_of(g)
                if not fm[c]:
                    rec['off_frontier'] += 1
                if self.component[c] == 0:
                    rec['unreachable'] += 1

        cells, gains = orig(self)
        rec['kept'] = len(cells)
        rec['gain_kept'] = int(np.sum(gains)) if len(gains) else 0
        rec['step'] = self.env.num_step
        CAND.append(rec)
        return cells, gains

    T.candidates = candidates


def held_karp_open(start, pts, dist):
    """Exact shortest open tour from `start` visiting every point in `pts`."""
    k = len(pts)
    if k == 0:
        return 0.0, []
    if k == 1:
        return dist(start, pts[0]), [0]
    if k > 11:                       # exact beyond this is not worth the audit's wall time
        return float('nan'), []
    d0 = [dist(start, p) for p in pts]
    dd = [[dist(a, b) for b in pts] for a in pts]
    best = {(1 << i, i): (d0[i], [i]) for i in range(k)}
    for size in range(2, k + 1):
        nxt = {}
        for mask in (m for m in range(1 << k) if bin(m).count('1') == size):
            for last in range(k):
                if not mask >> last & 1:
                    continue
                prev = mask ^ (1 << last)
                cand = []
                for j in range(k):
                    if prev >> j & 1 and (prev, j) in best:
                        c, path = best[(prev, j)]
                        cand.append((c + dd[j][last], path + [last]))
                if cand:
                    nxt[(mask, last)] = min(cand)
        best.update(nxt)
    full = (1 << k) - 1
    opts = [best[(full, i)] for i in range(k) if (full, i) in best]
    return min(opts) if opts else (float('nan'), [])


def patch_goal_tracking(T):
    """X6.4: per step and robot, how much the committed goal is still worth.

    `visible()` is cached per cell, so after the first visit this costs one array index per
    robot per step. A goal whose remaining gain has fallen to zero is a robot walking to a
    frontier that something else already revealed -- the plan is stale but nothing has
    noticed, because `__call__` only re-solves on arrival, on the snap exceeding goal_tol,
    or on the replan timer, and none of those test whether the goal still pays.
    """
    orig = T.__call__

    def call(self):
        goals = orig(self)
        m = self.env.complete_map
        unknown = (m == UNKNOWN).ravel()
        for i, g in enumerate(goals):
            c = (int(g[0]), int(g[1]))
            try:
                gain = int(unknown[self.visible(c)].sum())
            except Exception:
                gain = -1
            p = self.env.agent_pos[i]
            STALE.append(dict(step=self.env.num_step, robot=i, gain=gain,
                              dist=float(np.hypot(c[0] - p[0], c[1] - p[1]))))
        return goals

    T.__call__ = call


def patch_cpp_plan(T):
    """Compare the assignment charge against a true optimal route, per robot per solve."""
    orig = T.plan

    def plan(self, pos, nodes, gains):
        before = len(SOLVES)
        goals = orig(self, pos, nodes, gains)
        if len(SOLVES) == before:        # greedy fallback, no MILP to audit
            return goals
        # recover each robot's assigned set from the goals the solver produced is not
        # possible after the fact, so re-derive it the way plan() does
        r, m = len(pos), len(nodes)
        cost = self.cost_matrix(pos, nodes)
        usable = [j for j in range(m) if np.isfinite(cost[:, j]).any()]
        if not usable:
            return goals
        # the solver's own assignment, read out of x with plan()'s column mapping -- not
        # "every reachable viewpoint", which is a different and much larger set
        x = LAST_X[0]
        if x is None:
            return goals
        col = {(j, i): len(usable) * i + k
               for k, j in enumerate(usable) for i in range(r)}
        for i in range(r):
            share = [j for j in usable
                     if x[col[j, i]] > 0.5 and nodes[j] != pos[i]]
            if len(share) < 2:
                continue
            share = share[:11]
            charge = float(sum(cost[i, j] for j in share))
            tour, path = held_karp_open(pos[i], [nodes[j] for j in share], self.dist)
            drive = min(share, key=lambda j: cost[i, j])
            ROUTE.append(dict(k=len(share), charge=charge, tour=tour,
                              first_matches=bool(path and share[path[0]] == drive),
                              step=self.env.num_step))
        return goals

    T.plan = plan


def pct(x):
    return f'{100 * x:.1f}%'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--method', default='milp_cpp', choices=list(cfm_teachers.TEACHERS))
    p.add_argument('--map', default='room')
    p.add_argument('--seed', type=int, default=41)
    p.add_argument('--robots', type=int, default=2)
    p.add_argument('--max-steps', type=int, default=300)
    p.add_argument('--no-route', action='store_true',
                   help='skip the Held-Karp comparison (it is the slow part)')
    a = p.parse_args()

    import random
    random.seed(a.seed)
    patch_solve()
    cls = cfm_teachers.TEACHERS[a.method]
    patch_candidates(cls)
    patch_goal_tracking(cls)
    if a.method == 'milp_cpp' and not a.no_route:
        patch_cpp_plan(cls)

    env = make_env(a.map, a.robots)
    teacher = cfm_teachers.make_teacher(a.method, env)
    t0 = time.time()
    cov = 0.0
    for step in range(1, a.max_steps + 1):
        with quiet():
            env.step_for_cost(get_goal=teacher)
        cov = np.sum(env.complete_map != UNKNOWN) / env.total_cell_size
        if cov >= 0.98:
            break

    print(f'\n=== {a.method} on {a.map} seed {a.seed}: {step} steps, '
          f'coverage {cov:.1%}, {time.time() - t0:.0f}s wall, '
          f'{teacher.solves} replans ===')

    # ---- 1. solver gap
    print(f'\n1. SOLVER OPTIMALITY  ({len(SOLVES)} MILP solves)')
    if SOLVES:
        st = np.array([s['status'] for s in SOLVES])
        gap = np.array([s['gap'] for s in SOLVES])
        secs = np.array([s['secs'] for s in SOLVES])
        g = gap[np.isfinite(gap)]
        print(f'   status 0 (proven optimal)   {int((st == 0).sum())}/{len(st)}  '
              f'{pct((st == 0).mean())}')
        for s in sorted(set(st.tolist()) - {0}):
            print(f'   status {s} (NOT proven)       {int((st == s).sum())}/{len(st)}')
        print(f'   infeasible / no solution    {sum(1 for s in SOLVES if not s["feasible"])}')
        if len(g):
            print(f'   mip_gap   mean {g.mean():.4f}  median {np.median(g):.4f}  '
                  f'max {g.max():.4f}  >1e-6 on {int((g > 1e-6).sum())}/{len(g)}')
        print(f'   solve time mean {secs.mean():.2f}s  max {secs.max():.2f}s  '
              f'at TIME_LIMIT({cfm_teachers.TIME_LIMIT}s) '
              f'{int((secs >= cfm_teachers.TIME_LIMIT * 0.98).sum())}/{len(secs)}')
        print(f'   size       vars mean {np.mean([s["nvar"] for s in SOLVES]):.0f} '
              f'max {max(s["nvar"] for s in SOLVES)}   '
              f'cons mean {np.mean([s["ncon"] for s in SOLVES]):.0f} '
              f'max {max(s["ncon"] for s in SOLVES)}')
        print(f'   total time in HiGHS         {secs.sum():.0f}s of {time.time() - t0:.0f}s wall')

    # ---- 2. candidate set
    print(f'\n2. CANDIDATE SET  ({len(CAND)} replans)')
    if CAND:
        ga, go, gk = (np.array([c[k] for c in CAND], float)
                      for k in ('gain_all', 'gain_offered', 'gain_kept'))
        ok = ga > 0
        print(f'   frontier clusters found     mean {np.mean([c["clusters"] for c in CAND]):.1f}  '
              f'max {max(c["clusters"] for c in CAND)}')
        print(f'   candidates given to solver  mean {np.mean([c["kept"] for c in CAND]):.1f}  '
              f'(max_nodes cap)')
        if ok.any():
            print(f'   gain surviving size filter  {pct(np.mean(go[ok] / ga[ok]))} of all '
                  f'cluster gain')
            print(f'   gain in the final cand set  {pct(np.mean(gk[ok] / ga[ok]))} of all '
                  f'cluster gain')
        print(f'   replans where the size filter dropped a cluster better than one it '
              f'offered: {sum(1 for c in CAND if c["dropped_better"])}/{len(CAND)}')
        print(f'   representative cell NOT on the frontier after the rim clip: '
              f'{sum(c["off_frontier"] for c in CAND)} of '
              f'{sum(min(c["clusters"], 3 * 10) for c in CAND)} examined')
        print(f'   representative cell in a wall / unreachable component: '
              f'{sum(c["unreachable"] for c in CAND)}')

    # ---- 4. goal staleness (printed before route cost, it is the shorter story)
    print(f'\n4. GOAL STALENESS  ({len(STALE)} step-robot commitments)')
    if STALE:
        gain = np.array([s['gain'] for s in STALE], float)
        dist = np.array([s['dist'] for s in STALE], float)
        ok = gain >= 0
        print(f'   gain still available at the committed goal: '
              f'mean {gain[ok].mean():.0f}  median {np.median(gain[ok]):.0f}')
        for thr in (0, 10, 50):
            bad = ok & (gain <= thr)
            far = bad & (dist > 3)
            print(f'   gain <= {thr:<3} on {pct(bad.mean()):>7} of commitments; '
                  f'of those, {pct((far.sum() / max(bad.sum(), 1))):>7} are still more '
                  f'than 3 cells away')
        dead = ok & (gain == 0) & (dist > 3)
        print(f'   WALKING TO A DEAD GOAL (zero gain, >3 cells out): {pct(dead.mean())} '
              f'of all step-robot commitments')
        print('   ^ X6.4: nothing in __call__ tests whether a held goal still pays, so '
              'this is\n     time spent travelling to information that is already '
              'collected.')
    # ---- 3. route cost
    print(f'\n3. ROUTE-COST APPROXIMATION  ({len(ROUTE)} robot-assignments)')
    if ROUTE:
        ch = np.array([r['charge'] for r in ROUTE])
        tu = np.array([r['tour'] for r in ROUTE])
        f = np.isfinite(tu) & (tu > 0)
        print(f'   viewpoints the solver assigned mean '
              f'{np.mean([r["k"] for r in ROUTE]):.1f}  max {max(r["k"] for r in ROUTE)}')
        if f.any():
            print(f'   charged (sum of depot trips)   mean {ch[f].mean():.0f} cells')
            print(f'   true optimal open tour         mean {tu[f].mean():.0f} cells')
            print(f'   OVERCHARGE ratio               mean {np.mean(ch[f] / tu[f]):.2f}x  '
                  f'median {np.median(ch[f] / tu[f]):.2f}x  max {np.max(ch[f] / tu[f]):.2f}x')
        fm = [r['first_matches'] for r in ROUTE if np.isfinite(r['tour'])]
        if fm:
            print(f'   teacher drives to the optimal tour\'s FIRST stop: '
                  f'{sum(fm)}/{len(fm)}  {pct(np.mean(fm))}')
            print('   ^ this is the one that changes the recorded action. A low number '
                  'means the\n     demonstrations are not the optimal route\'s moves.')
    elif not SOLVES:
        print('   no MILP solves to audit')
    else:
        print('   skipped, or no robot was assigned 2+ viewpoints '
              '(then there is no route to approximate)')


if __name__ == '__main__':
    main()
