"""Replay one run with per-step logging and draw what went wrong.

    python diagnose.py --method cost --map corner --seed 44
    python diagnose.py --method cfm --ckpt cfm_x5_linear.pt --exclude 35 --map corner --seed 46

`results_x6.csv` says a run was slow. It does not say why. This re-runs one configuration,
records every robot's position and committed goal at every step, and writes a figure plus
the four quantities that separate the failure modes already visible in the results:

* idle fraction     -- steps where a robot did not move. `cost` on corner seed 44 moved
                       1302 of a possible 4000 robot-steps and still timed out, which is a
                       different failure from running the full 4000 and not finishing.
* goal churn        -- how often the committed goal changes, and how often it changes
                       before being reached. High churn with low progress is oscillation:
                       the planner re-aims every replan and the robot never arrives.
* overlap trace     -- redundant coverage over time. `cost` reaches overlap 0.999, meaning
                       both robots independently covered nearly the whole map.
* tail              -- steps spent between 90% and 98%. The students and greedy_ratio
                       spend 150-175 steps there against mtsp's 89, so the endgame, not
                       the bulk of exploration, is where they lose.

The figure is the ground truth under the team's final known map, with each robot's path
drawn over it and its goal commitments marked, beside the coverage and overlap curves.
"""
import argparse
import os

import numpy as np

os.environ.setdefault('MPLBACKEND', 'Agg')   # before cfm_common picks a backend


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--method', required=True)
    p.add_argument('--map', default='corner')
    p.add_argument('--seed', type=int, default=41)
    p.add_argument('--robots', type=int, default=2)
    p.add_argument('--max-steps', type=int, default=2000)
    p.add_argument('--ckpt', default='cfm_x5_linear.pt')
    p.add_argument('--exclude', type=float, default=0.0)
    p.add_argument('--nsample', type=int, default=1)
    p.add_argument('--steps', type=int, default=20)
    p.add_argument('--out', default='')
    a = p.parse_args()

    import random

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import torch

    from cfm_common import (UNKNOWN, VelocityField, cfm_goal_fn, coverage, make_env,
                            map_path, quiet)
    from cfm_teachers import TEACHERS, make_teacher
    from PIL import Image

    random.seed(a.seed)
    planner = None
    if a.method in ('cost', 'mmpf'):
        env = make_env(a.map, a.robots)
    elif a.method in TEACHERS:
        env = make_env(a.map, a.robots)
        planner = make_teacher(a.method, env)
    elif a.method == 'cfm':
        model = VelocityField()
        model.load_state_dict(torch.load(a.ckpt, map_location='cpu'))
        model.eval()
        env = make_env(a.map, a.robots,
                       cfm_goal_fn(model, torch.Generator().manual_seed(a.seed),
                                   exclude=a.exclude, nsample=a.nsample, steps=a.steps))
    else:
        raise SystemExit(f'unknown method {a.method}')

    if planner is not None:
        step_fn = lambda: env.step_for_cost(get_goal=planner)        # noqa: E731
    else:
        step_fn = env.step_for_mmpf if a.method == 'mmpf' else env.step_for_cost

    pos_log = [[] for _ in range(a.robots)]
    goal_log = [[] for _ in range(a.robots)]
    cov_curve, ovl_curve = [], []
    s90 = s98 = None
    for step in range(1, a.max_steps + 1):
        with quiet():
            step_fn()
        for i in range(a.robots):
            pos_log[i].append(tuple(int(x) for x in env.agent_pos[i]))
            # the teachers hold their commitments themselves; GoalEnv exposes the
            # flow's. `cost` and `mmpf` choose internally and expose nothing, so churn is
            # simply not observable for them -- reported as such rather than as zero.
            g = planner.goals if planner is not None else getattr(env, 'goals', None)
            goal_log[i].append(tuple(int(x) for x in g[i]) if g is not None
                               and len(g) > i else None)
        cov = coverage(env)
        cov_curve.append(cov)
        known_all = np.sum(env.complete_map != UNKNOWN)
        ovl_curve.append(sum(np.sum(b != UNKNOWN) for b in env.built_map) / known_all - 1)
        if s90 is None and cov >= 0.90:
            s90 = step
        if cov >= 0.98:
            s98 = step
            break

    n = len(cov_curve)
    tag = (f'{a.method}' if a.method != 'cfm'
           else f"{os.path.basename(a.ckpt).replace('.pt', '')} ex{a.exclude:g}")
    print(f'\n=== {tag} on {a.map} seed {a.seed} ===')
    print(f'steps run {n}   steps_90 {s90}   steps_98 {s98}   '
          f'final coverage {cov_curve[-1]:.3f}   final overlap {ovl_curve[-1]:.3f}')
    if s90 and s98:
        print(f'tail (90% -> 98%)        {s98 - s90} steps  '
              f'({100 * (s98 - s90) / s98:.0f}% of the run)')
    elif s90:
        print(f'reached 90% at {s90} and never reached 98%: '
              f'{n - s90} steps spent in the tail without finishing')

    print(f'\n{"robot":7}{"moved":>8}{"idle":>8}{"idle%":>7}{"goal sets":>11}'
          f'{"changed early":>15}{"mean goal dist":>16}')
    for i in range(a.robots):
        pl, gl = pos_log[i], goal_log[i]
        moved = sum(1 for k in range(1, n) if pl[k] != pl[k - 1])
        idle = (n - 1) - moved
        changes = sum(1 for k in range(1, n) if gl[k] != gl[k - 1] and gl[k] is not None)
        # a goal abandoned before the robot stood on it: churn rather than completion
        early = 0
        for k in range(1, n):
            if gl[k] != gl[k - 1] and gl[k - 1] is not None and pl[k - 1] != gl[k - 1]:
                early += 1
        dists = [float(np.hypot(g[0] - q[0], g[1] - q[1]))
                 for g, q in zip(gl, pl) if g is not None]
        if not dists:
            print(f'{i:<7}{moved:>8}{idle:>8}{100 * idle / max(n - 1, 1):>6.0f}%'
                  f'{"n/a":>11}{"n/a":>15}{"n/a":>16}')
            continue
        print(f'{i:<7}{moved:>8}{idle:>8}{100 * idle / max(n - 1, 1):>6.0f}%'
              f'{changes:>11}{early:>15}{np.mean(dists) if dists else 0:>16.1f}')

    print('\nread it as: high idle% with low coverage = robots stopped having anywhere to '
          'go;\n  "changed early" near "goal sets" = the goal is re-aimed before it is '
          'reached (oscillation);\n  final overlap near 1.0 = both robots independently '
          'covered the whole map.')

    # ---------------------------------------------------------------- figure
    gt = np.array(Image.open(map_path(a.map)))
    fig, ax = plt.subplots(1, 2, figsize=(15, 6.5),
                           gridspec_kw={'width_ratios': [1.25, 1]})
    known = env.complete_map != UNKNOWN
    shade = np.where(gt == 0, 0.25, 1.0)              # walls dark
    shade = np.where(~known, shade * 0.45, shade)     # unexplored dimmed
    ax[0].imshow(shade, cmap='gray', vmin=0, vmax=1, interpolation='nearest')
    colours = ['#d7263d', '#1b6ca8', '#2a9d4a', '#c77dff']
    for i in range(a.robots):
        pl = np.array(pos_log[i], float)
        ax[0].plot(pl[:, 1], pl[:, 0], lw=1.1, color=colours[i % 4], alpha=0.85,
                   label=f'robot {i} path')
        ax[0].scatter(pl[0, 1], pl[0, 0], s=90, marker='o', facecolor='none',
                      edgecolor=colours[i % 4], lw=2, zorder=5)
        gs = [g for g in goal_log[i] if g is not None]
        if gs:
            uniq = np.array(sorted(set(gs)), float)
            ax[0].scatter(uniq[:, 1], uniq[:, 0], s=14, marker='x',
                          color=colours[i % 4], alpha=0.6, zorder=4,
                          label=f'robot {i} goals ({len(uniq)} distinct)')
    ax[0].set_title(f'{tag} — {a.map} seed {a.seed}\n'
                    f'{n} steps, coverage {cov_curve[-1]:.1%}, '
                    f'overlap {ovl_curve[-1]:.2f}'
                    + ('' if s98 else '  — NEVER REACHED 98%'), fontsize=11)
    ax[0].legend(loc='upper right', fontsize=8, framealpha=0.9)
    ax[0].set_xticks([]); ax[0].set_yticks([])

    ax[1].plot(cov_curve, color='#1b6ca8', lw=1.6, label='team coverage')
    ax[1].plot(ovl_curve, color='#d7263d', lw=1.4, label='overlap (redundancy)')
    ax[1].axhline(0.98, ls=':', c='k', lw=1)
    ax[1].axhline(0.90, ls=':', c='gray', lw=1)
    if s90:
        ax[1].axvline(s90, ls='--', c='gray', lw=1)
        ax[1].text(s90, 0.02, f' 90% @ {s90}', fontsize=8, color='gray')
    if s98:
        ax[1].axvline(s98, ls='--', c='k', lw=1)
        ax[1].text(s98, 0.10, f' 98% @ {s98}', fontsize=8)
    ax[1].set_xlabel('step'); ax[1].set_ylim(0, 1.05)
    ax[1].set_title('coverage and redundancy over time', fontsize=11)
    ax[1].legend(loc='lower right', fontsize=9)
    ax[1].grid(alpha=0.25)

    out = a.out or f'diag_{tag.replace(" ", "_")}_{a.map}_{a.seed}.png'
    fig.tight_layout()
    fig.savefig(out, dpi=115)
    plt.close(fig)
    print(f'\nwrote {out}')


if __name__ == '__main__':
    main()
