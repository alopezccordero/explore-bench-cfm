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
# mtsp / milp_cpp only
p.add_argument('--max-nodes', type=int, default=10,
               help='frontier clusters kept as MILP nodes (by true information gain)')
p.add_argument('--replan', type=int, default=10,
               help='re-solve the MILP every N steps as well; 0 = only when a goal is used up')
p.add_argument('--goal-tol', type=float, default=12.0,
               help='cells a goal may recede with its frontier before the MILP is re-solved')
p.add_argument('--cpp-balance', type=float, default=1.0,
               help='weight of the makespan term in milp_cpp (0 = pure min-sum travel)')
args = p.parse_args() #arguments used


def snap_to_frontier(fmask, m, pos, goal):
    """Teacher goal -> nearest frontier cell this robot can walk to, and how far that was."""
    valid = fmask & np.isfinite(geodesic_dist(m, pos)) #drop frontiers behind unknown space
    if not valid.any():
        return None, None
    cells = np.argwhere(valid)
    d2 = ((cells - np.asarray(goal, float)) ** 2).sum(1)
    j = int(d2.argmin())
    return cells[j], float(np.sqrt(d2[j]))


conds, starts, goals, snaps = [], [], [], [] #dataset arrays
dropped = 0 #states where the teacher never reached a frontier
for name in args.maps: #we start by iterating the maps
    for ep in range(args.episodes): #episodes is per maps
        random.seed(args.seed * 1000 + ep)  # GridEnv picks start cells with `random`
        # plain GridEnv: step_for_X() calls get_goal_for_X() itself, so no goal_fn
        env = make_env(name, args.robots) #we create the exploration environment.
        if args.method in TEACHERS:
            # the privileged teachers are just another get_goal, so step_for_cost drives
            # and senses exactly as it does for the benchmark's own methods
            kw = dict(max_nodes=args.max_nodes, replan=args.replan, goal_tol=args.goal_tol)
            if args.method == 'milp_cpp':
                kw['balance'] = args.cpp_balance
            get_goal = make_teacher(args.method, env, **kw)
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
                        g, snap = snap_to_frontier(fmask, m, pos, teacher_goals[i])
                        #goal cells
                        if g is None or tuple(g) == pos:
                            continue #nothing reachable left, or the teacher stayed put
                        if snap > args.max_snap:
                            dropped += 1 #stalled short of a frontier: no goal to learn from
                            continue
                        conds.append(build_condition(m, pos, mates).astype(np.float16)) #condition
                        #5 x 64 x 64 data
                        starts.append(pos) #pos of robot during step
                        goals.append(g) #goal of the step
                        snaps.append(snap) #how far the goal moved to land on a frontier
            with quiet():
                step_env() #take step for mmpf or cost, whichever teacher we are recording
            if coverage(env) >= 0.98: #if civerage is > than 0.98, break all the loop
                break
        print(f'{name:20s} episode {ep}: {step + 1:4d} steps, coverage {coverage(env):.1%}, '
              f'{len(conds)} examples so far, {time.time() - t0:.0f}s') #print the episode, step, coverage,
        #length of conditions (how many examples are there) and the time.

if not conds:
    raise SystemExit('no examples collected')

np.savez_compressed(args.out, cond=np.stack(conds), start=to_norm(starts),
                    goal=to_norm(np.stack(goals)[:, None, :])) # (N, 1, 2)
#saves examples into data.npz. each step  % 10 == 0. is recorded with
#with its conditions (5 X 64 X 64), the starting position of the robot and the goal.
###conditions are
##free space, obstacles, unkown space, current robot pos, teammates (meaning that position is stored twice.)
print(f'saved {len(conds)} {args.method} examples to {args.out} (mean snap to frontier '
      f'{np.mean(snaps):.2f} cells, dropped {dropped} stalled states)')
