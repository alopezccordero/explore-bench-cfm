"""Step 3: run one method on one map and report team metrics.

Methods: cost and mmpf (the benchmark's own two), teacher (the sampling target in
cfm_common), mtsp and milp_cpp (the privileged MILP teachers of cfm_teachers.py, which
plan on the ground truth and so read as an upper bound rather than a baseline), cfm (the
trained flow). The same --seed gives every method the same start positions, so runs are
directly comparable.
"""
import argparse
import csv
import os
import random
import sys
import time

if '--show' in sys.argv:
    os.environ['SHOW_GRID'] = '1'  # must be set before cfm_common picks the plotting backend

import matplotlib.pyplot as plt
import numpy as np
import torch

from cfm_common import (UNKNOWN, VelocityField, cfm_goal_fn, coverage, make_env, quiet,
                        teacher_goal_fn)
from cfm_teachers import TEACHERS, make_teacher

p = argparse.ArgumentParser()
p.add_argument('--method', choices=['cost', 'mmpf', 'teacher', 'cfm'] + list(TEACHERS),
               required=True)
p.add_argument('--map', default='room')
p.add_argument('--robots', type=int, default=2)
p.add_argument('--seed', type=int, default=0)
p.add_argument('--max-steps', type=int, default=2000)
p.add_argument('--ckpt', default='cfm.pt')
p.add_argument('--csv', default='results.csv')
p.add_argument('--show', action='store_true', help='open the simulator window and update it every step')
# mtsp / milp_cpp only, same meaning as in collect_data.py
p.add_argument('--max-nodes', type=int, default=10)
p.add_argument('--replan', type=int, default=10)
p.add_argument('--goal-tol', type=float, default=12.0)
p.add_argument('--latency', type=float, default=1.0)
p.add_argument('--cpp-balance', type=float, default=1.0)
args = p.parse_args()

random.seed(args.seed)  # start positions
planner = None
if args.method in ('cost', 'mmpf'):
    env = make_env(args.map, args.robots)
elif args.method == 'teacher':
    env = make_env(args.map, args.robots, teacher_goal_fn(np.random.default_rng(args.seed)))
elif args.method in TEACHERS:
    env = make_env(args.map, args.robots)
    kw = dict(max_nodes=args.max_nodes, replan=args.replan, goal_tol=args.goal_tol)
    if args.method == 'milp_cpp':
        kw['balance'] = args.cpp_balance
    else:
        kw['latency'] = args.latency
    planner = make_teacher(args.method, env, **kw)
else:
    model = VelocityField()
    model.load_state_dict(torch.load(args.ckpt, map_location='cpu'))
    model.eval()
    env = make_env(args.map, args.robots, cfm_goal_fn(model, torch.Generator().manual_seed(args.seed)))

# step_for_mmpf is a copy of step_for_cost that calls get_goal_for_mmpf() itself:
# it takes no get_goal hook, so the method is chosen by picking the step function.
if planner is not None:
    step_fn = lambda: env.step_for_cost(get_goal=planner)  # noqa: E731
else:
    step_fn = env.step_for_mmpf if args.method == 'mmpf' else env.step_for_cost

t0 = time.time()
steps_90 = steps_98 = None
for step in range(1, args.max_steps + 1):
    with quiet():
        step_fn()
    cov = coverage(env)
    if steps_90 is None and cov >= 0.90:
        steps_90 = step
    if cov >= 0.98:
        steps_98 = step
        break

paths = [len(p) for p in env.path_log]
known_all = np.sum(env.complete_map != UNKNOWN)
known_each = [np.sum(b != UNKNOWN) for b in env.built_map]
snaps = getattr(env, 'snap_dists', [])
row = {
    'method': args.method, 'map': args.map, 'robots': args.robots, 'seed': args.seed,
    # two students trained on two teachers are both method=cfm, so the checkpoint is the
    # only thing telling their rows apart
    'ckpt': os.path.basename(args.ckpt) if args.method == 'cfm' else '',
    'steps_90': steps_90, 'steps_98': steps_98, 'final_coverage': round(float(cov), 4),
    'total_path': sum(paths), 'longest_path': max(paths),
    'overlap': round(float(sum(known_each) / known_all - 1), 3),  # the paper's definition
    'mean_snap_cells': round(float(np.mean(snaps)), 2) if snaps else '',
    'seconds': round(time.time() - t0),
}
print(row)
new = not os.path.exists(args.csv)
if not new:
    with open(args.csv, newline='') as f:
        old = next(csv.reader(f), [])
    if old != list(row):
        raise SystemExit(
            f'{args.csv} has the columns {old}, but this run writes {list(row)}. Appending '
            f'would misalign every row -- move the old file aside or pass a different --csv.')
with open(args.csv, 'a', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(row))
    if new:
        w.writeheader()
    w.writerow(row)

if args.show:
    print('Finished. Close the window to exit.')
    plt.ioff()
    plt.show()
