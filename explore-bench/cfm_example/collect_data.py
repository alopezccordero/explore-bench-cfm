"""Step 1: roll out the teacher on the training maps and save training examples.

Each example is (condition image, robot position, k goal samples from the teacher).
Several goals per state let the model see that the target is a *distribution*.
"""
import argparse
import random
import time

import numpy as np

from cfm_common import (TRAIN_MAPS, build_condition, coverage, frontier_mask, make_env, quiet,
                        robot_and_mates, teacher_goal_fn, teacher_sample, to_norm)

p = argparse.ArgumentParser()
p.add_argument('--maps', nargs='+', default=TRAIN_MAPS)
p.add_argument('--robots', type=int, default=2)
p.add_argument('--episodes', type=int, default=2, help='episodes per map (different starts)')
p.add_argument('--max-steps', type=int, default=600)
p.add_argument('--every', type=int, default=10, help='record a state every N steps')
p.add_argument('--k', type=int, default=16, help='goal samples per state')
p.add_argument('--seed', type=int, default=0)
p.add_argument('--out', default='data.npz')
args = p.parse_args()

rng = np.random.default_rng(args.seed)
conds, starts, goals = [], [], []
for name in args.maps:
    for ep in range(args.episodes):
        random.seed(args.seed * 1000 + ep)  # GridEnv picks start cells with `random`
        env = make_env(name, args.robots, teacher_goal_fn(rng))
        t0 = time.time()
        for step in range(args.max_steps):
            if step % args.every == 0:
                m = env.complete_map
                fmask = frontier_mask(m)
                for i in range(args.robots):
                    pos, mates = robot_and_mates(env, i)
                    g = teacher_sample(m, fmask, pos, mates, args.k, rng)
                    if g is not None:
                        conds.append(build_condition(m, pos, mates).astype(np.float16))
                        starts.append(pos)
                        goals.append(g)
            with quiet():
                env.step_for_cost()
            if coverage(env) >= 0.98:
                break
        print(f'{name:20s} episode {ep}: {step + 1:4d} steps, coverage {coverage(env):.1%}, '
              f'{len(conds)} examples so far, {time.time() - t0:.0f}s')

np.savez_compressed(args.out, cond=np.stack(conds), start=to_norm(starts), goal=to_norm(np.stack(goals)))
print(f'saved {len(conds)} examples to {args.out}')
