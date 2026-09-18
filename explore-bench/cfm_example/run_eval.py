"""Step 3: run one method on one map and report team metrics.

Methods: cost (the benchmark's own), teacher (the target distribution the model
imitates), cfm (the trained flow). The same --seed gives every method the same
start positions, so runs are directly comparable.
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

p = argparse.ArgumentParser()
p.add_argument('--method', choices=['cost', 'teacher', 'cfm'], required=True)
p.add_argument('--map', default='room')
p.add_argument('--robots', type=int, default=2)
p.add_argument('--seed', type=int, default=0)
p.add_argument('--max-steps', type=int, default=2000)
p.add_argument('--ckpt', default='cfm.pt')
p.add_argument('--csv', default='results.csv')
p.add_argument('--show', action='store_true', help='open the simulator window and update it every step')
args = p.parse_args()

random.seed(args.seed)  # start positions
if args.method == 'cost':
    env = make_env(args.map, args.robots)
elif args.method == 'teacher':
    env = make_env(args.map, args.robots, teacher_goal_fn(np.random.default_rng(args.seed)))
else:
    model = VelocityField()
    model.load_state_dict(torch.load(args.ckpt))
    model.eval()
    env = make_env(args.map, args.robots, cfm_goal_fn(model, torch.Generator().manual_seed(args.seed)))

t0 = time.time()
steps_90 = steps_98 = None
for step in range(1, args.max_steps + 1):
    with quiet():
        env.step_for_cost()
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
    'steps_90': steps_90, 'steps_98': steps_98, 'final_coverage': round(float(cov), 4),
    'total_path': sum(paths), 'longest_path': max(paths),
    'overlap': round(float(sum(known_each) / known_all - 1), 3),  # the paper's definition
    'mean_snap_cells': round(float(np.mean(snaps)), 2) if snaps else '',
    'seconds': round(time.time() - t0),
}
print(row)
new = not os.path.exists(args.csv)
with open(args.csv, 'a', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(row))
    if new:
        w.writeheader()
    w.writerow(row)

if args.show:
    print('Finished. Close the window to exit.')
    plt.ioff()
    plt.show()
