"""Step 1: roll out a benchmark teacher on the training maps and save training examples.

--method picks the teacher. Two of them are GridEnv's own, and see only what the robots
have seen:

    mmpf      potential field
    cost      nearest frontier cluster

The other two are in cfm_teachers.py and are allowed to cheat -- they plan on the ground
truth with A* distances and the simulator's real sensor model:

    mtsp      multi-depot open mTSP / VRP over the frontier clusters (MILP)
    milp_cpp  coverage path planning as a min-cost viewpoint set cover (MILP)

Cheating is the point. The condition image saved here is always built from the *partial*
team map, so the model is trained to reproduce a choice it could not have computed from
its own input, and at evaluation time it has to reproduce it without the ground truth.

All four expose the same pair -- a get_goal callable that chooses the goals for the
current team map, and a step function that drives one step toward them -- so the goal
recorded here is exactly the one the robot then pursues.

Each example is (condition image, robot position, the goal the teacher chose). Every
teacher is deterministic in the map state, so there is one goal per state rather than a
sample set: goals are stored with a length-1 sample axis, the (N, K, 2) layout
train_cfm.py expects.

Goals are snapped onto frontier_mask (free cells touching unknown), the support
choose_goal() samples on at inference. mmpf's own frontiers are the *unknown* side, a
cell over; cost already returns a free cell beside its cluster centre; mtsp and milp_cpp
choose on frontier_mask itself, so for them the snap is a no-op.

When mmpf's potential-field walk does not converge it returns a cell one step from the
robot instead of a frontier. That is still a usable mmpf action -- it crawls a cell at a
time -- but it is not a goal, and snapping it would invent a target mmpf never chose.
Those states are dropped; --max-snap is the cutoff in cells.
"""
import argparse
import random
import time

import numpy as np

from cfm_common import (TRAIN_MAPS, build_condition, coverage, frontier_mask, geodesic_dist,
                        make_env, quiet, robot_and_mates, to_norm)
from cfm_teachers import TEACHERS, make_teacher

def teacher_kwargs(method, **wanted):
    """Keep only the options the installed teacher actually accepts.

    cfm_teachers.py gets reverted between experiments (the territory/latency variants are
    kept as patches), and each version takes a different set of options. Filtering by the
    real signature means an older teacher ignores flags it never had instead of dying on
    them, and a typo in an option name still shows up as a stale-flag warning.
    """
    import inspect
    from cfm_teachers import TEACHERS
    cls = TEACHERS[method]
    accepted = set()
    for klass in cls.__mro__:
        sig = inspect.signature(klass.__init__).parameters
        accepted |= {n for n, p in sig.items()
                     if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)}
    drop = sorted(k for k in wanted if k not in accepted)
    if drop:
        print(f'note: this {method} build has no {", ".join(drop)} -- ignoring')
    return {k: v for k, v in wanted.items() if k in accepted}


p = argparse.ArgumentParser()
p.add_argument('--method', choices=['mmpf', 'cost'] + list(TEACHERS), default='mmpf',
               help='which teacher to record; mtsp and milp_cpp plan on the ground truth')
p.add_argument('--maps', nargs='+', default=TRAIN_MAPS)
p.add_argument('--robots', type=int, default=2)
p.add_argument('--episodes', type=int, default=2, help='episodes per map (different starts)')
p.add_argument('--max-steps', type=int, default=600)
p.add_argument('--every', type=int, default=10, help='record a state every N steps')
p.add_argument('--max-snap', type=float, default=5.0,
               help='drop a state when the teacher goal is farther than this from a frontier')
p.add_argument('--seed', type=int, default=0)
p.add_argument('--out', default='data.npz')
p.add_argument('--waypoints', type=int, default=8,
               help='points per stored route; 0 stores goals only, as before')
# mtsp / milp_cpp only
p.add_argument('--max-nodes', type=int, default=10,
               help='frontier clusters kept as MILP nodes (by true information gain)')
p.add_argument('--replan', type=int, default=10,
               help='re-solve the MILP every N steps as well; 0 = only when a goal is used up')
p.add_argument('--goal-tol', type=float, default=12.0,
               help='cells a goal may recede with its frontier before the MILP is re-solved')
p.add_argument('--latency', type=float, default=0.5,
               help='mtsp objective: 1 = minimum arrival time, 0 = minimum distance')
p.add_argument('--min-share', type=float, default=0.02,
               help='drop frontier clusters gating less than this share of the unexplored map')
p.add_argument('--makespan', type=float, default=0.5,
               help='mtsp objective: weight on the plan completion time')
p.add_argument('--cpp-balance', type=float, default=1.0,
               help='weight of the makespan term in milp_cpp (0 = pure min-sum travel)')
args = p.parse_args() #arguments used


def snap_to_frontier(fmask, dist, goal):
    """Teacher goal -> nearest frontier cell this robot can walk to, and how far that was.

    Takes the robot's geodesic distance field rather than recomputing it: the caller needs
    the same field to trace the route to the goal, and that BFS is the single most
    expensive thing in collection (~72 ms a call, more than a simulator step).
    """
    valid = fmask & np.isfinite(dist)       #drop frontiers behind unknown space
    if not valid.any():
        return None, None
    cells = np.argwhere(valid)
    d2 = ((cells - np.asarray(goal, float)) ** 2).sum(1)
    j = int(d2.argmin())
    return cells[j], float(np.sqrt(d2[j]))


STEP4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def geodesic_path(dist, goal):
    """Cells from the robot to `goal`, walking the BFS field downhill.

    `dist` is geodesic_dist(m, pos): 4-connected step counts through *known free* space,
    so the route never crosses a wall and never enters unknown space -- the states the
    student can actually occupy and condition on.
    """
    cur = (int(goal[0]), int(goal[1]))
    d = dist[cur]
    if not np.isfinite(d):
        return None
    out = [cur]
    h, w = dist.shape
    while d > 0:
        for dy, dx in STEP4:
            n = (cur[0] + dy, cur[1] + dx)
            if 0 <= n[0] < h and 0 <= n[1] < w and dist[n] == d - 1:
                cur, d = n, d - 1
                out.append(cur)
                break
        else:                               # field is not monotone: should not happen
            return None
    return out[::-1]                        # robot -> goal


def resample(path, k):
    """`k` points spaced evenly along `path` by arc length, endpoints included."""
    p = np.asarray(path, float)
    if len(p) < 2:
        return np.repeat(p.reshape(1, 2), k, axis=0)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*(p[1:] - p[:-1]).T))])
    at = np.linspace(0.0, s[-1], k)
    return np.stack([np.interp(at, s, p[:, 0]), np.interp(at, s, p[:, 1])], axis=1)


conds, starts, goals, snaps = [], [], [], [] #dataset arrays
paths = []  #geodesic route robot -> goal, for E-A's obstacle-aware interpolation
# Per-example provenance. 18 of 50 episodes in data_ea.npz hit the 600-step cap (all ten
# on room_3), so its truncated tails are over-represented and indistinguishable from
# clean demonstrations. Recording this lets a later run down-weight them instead of
# discarding whole episodes.
meta = []        #(episode index, step, coverage at the time)
ep_rows = []     #(episode index, map index, steps used, final coverage, hit the cap?)
episode = -1
dropped = 0 #states where the teacher never reached a frontier
for name in args.maps: #we start by iterating the maps
    for ep in range(args.episodes): #episodes is per maps
        episode += 1
        random.seed(args.seed * 1000 + ep)  # GridEnv picks start cells with `random`
        # plain GridEnv: step_for_X() calls get_goal_for_X() itself, so no goal_fn
        env = make_env(name, args.robots) #we create the exploration environment.
        if args.method in TEACHERS:
            # the privileged teachers are just another get_goal, so step_for_cost drives
            # and senses exactly as it does for the benchmark's own methods
            kw = dict(max_nodes=args.max_nodes, replan=args.replan, goal_tol=args.goal_tol,
                      min_share=args.min_share)
            if args.method == 'milp_cpp':
                kw['balance'] = args.cpp_balance
            else:
                kw['latency'] = args.latency
                kw['makespan'] = args.makespan
            get_goal = make_teacher(args.method, env, **teacher_kwargs(args.method, **kw))
            step_env = lambda: env.step_for_cost(get_goal=get_goal)  # noqa: E731
        else:
            get_goal = env.get_goal_for_mmpf if args.method == 'mmpf' else env.get_goal_for_cost
            step_env = env.step_for_mmpf if args.method == 'mmpf' else env.step_for_cost
        t0 = time.time() #starting time (unix time)
        for step in range(args.max_steps): #for each step
            if step % args.every == 0: ##every 10 step record the state
                m = env.complete_map.copy() #map (copied: step_env rebuilds complete_map)
                fmask = frontier_mask(m) #frontiers of the map
                if fmask.any():
                    with quiet():
                        teacher_goals = get_goal() #the goal the teacher picked, one per robot
                    for i in range(args.robots): #for each robot
                        pos, mates = robot_and_mates(env, i) # record position of robot, and other robots
                        dist = geodesic_dist(m, pos)  #reused for the route below
                        g, snap = snap_to_frontier(fmask, dist, teacher_goals[i])
                        #goal cells
                        if g is None or tuple(g) == pos:
                            continue #nothing reachable left, or the teacher stayed put
                        if snap > args.max_snap:
                            dropped += 1 #stalled short of a frontier: no goal to learn from
                            continue
                        route = geodesic_path(dist, g) if args.waypoints else None
                        if args.waypoints and route is None:
                            dropped += 1  #no route through known space: nothing to learn
                            continue
                        if args.waypoints:
                            paths.append(resample(route, args.waypoints))
                        conds.append(build_condition(m, pos, mates).astype(np.float16)) #condition
                        #5 x 64 x 64 data
                        starts.append(pos) #pos of robot during step
                        goals.append(g) #goal of the step
                        snaps.append(snap) #how far the goal moved to land on a frontier
                        meta.append((episode, step, coverage(env)))
            with quiet():
                step_env() #take step for mmpf or cost, whichever teacher we are recording
            if coverage(env) >= 0.98: #if civerage is > than 0.98, break all the loop
                break
        ep_rows.append((episode, args.maps.index(name), step + 1, coverage(env),
                        int(step + 1 >= args.max_steps)))
        print(f'{name:20s} episode {ep}: {step + 1:4d} steps, coverage {coverage(env):.1%}, '
              f'{len(conds)} examples so far, {time.time() - t0:.0f}s') #print the episode, step, coverage,
        #length of conditions (how many examples are there) and the time.

if not conds:
    raise SystemExit('no examples collected')

extra = {}
if meta:
    extra['meta'] = np.asarray(meta, np.float32)          # (N, 3) episode, step, coverage
    extra['episodes'] = np.asarray(ep_rows, np.float32)   # (E, 5) see above
    extra['map_names'] = np.asarray(args.maps)
if paths:
    # (N, K, 2) normalised route. train_cfm.py picks this up automatically and
    # interpolates along it instead of along the straight line, which on the previous
    # dataset crossed a wall in 63% of examples.
    extra['path'] = to_norm(np.stack(paths))
np.savez_compressed(args.out, cond=np.stack(conds), start=to_norm(starts),
                    goal=to_norm(np.stack(goals)[:, None, :]), **extra) # (N, 1, 2)
#saves examples into data.npz. each step  % 10 == 0. is recorded with
#with its conditions (5 X 64 X 64), the starting position of the robot and the goal.
###conditions are
##free space, obstacles, unkown space, current robot pos, teammates (meaning that position is stored twice.)
print(f'saved {len(conds)} {args.method} examples to {args.out} (mean snap to frontier '
      f'{np.mean(snaps):.2f} cells, dropped {dropped} stalled states)')
