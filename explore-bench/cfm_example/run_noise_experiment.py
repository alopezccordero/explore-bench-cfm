"""E1 frozen-initial versus E2 online-updated noise partition feasibility study.

Run from explore-bench/cfm_example with the SAME checkpoint, maps, seeds,
number of robots, replanning period and inference steps across conditions.

This is intentionally a controlled *sampling intervention* on the existing
per-agent CFM, NOT a trained joint CFM / full MoSDOT method. The existing CFM
was trained from independent robot samples around each robot's position. No
alignment of arbitrary noise sectors with joint modes has been established.
Use mode-goal distance and noncompletion rates as feasibility diagnostics.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import time

import numpy as np
import torch
from scipy.spatial import cKDTree

from cfm_common import (GoalEnv, NOISE, UNKNOWN, VelocityField, build_condition,
                        cell, coverage, frontier_mask, from_norm, geodesic_dist,
                        map_path, quiet, to_norm)
from structured_noise import build_noise_bank


class NoisePlanner:
    def __init__(self, model, *, variant, seed, flow_steps, bank_size,
                 max_clusters, max_modes, exclusion):
        self.model = model
        self.variant = variant
        self.flow_steps = flow_steps
        self.bank_size = bank_size
        self.max_clusters = max_clusters
        self.max_modes = max_modes
        self.exclusion = exclusion
        self.rng = np.random.default_rng(seed + 1_000_003)
        self.bank_rng = np.random.default_rng(seed + 2_000_029)
        self.initial_bank = None
        self.initialized = False
        self.replans = 0
        self.bank_builds = 0
        self.no_bank = 0
        self.mode_samples = 0
        self.sample_draws = 0
        self.mode_goal_distances = []
        self.snap_dists = []
        self.planning_seconds = 0.0
        self.bank_seconds = 0.0
        self.mode_counts = []
        self.initial_frontier_modes = 0
        self.cell_mass_errors = []

    def _build_bank(self, env, fmask):
        m = env.complete_map
        positions = np.asarray([cell(p) for p in env.agent_pos], dtype=np.int32)
        start = time.perf_counter()
        bank = build_noise_bank(m, positions, fmask, geodesic_dist, to_norm,
                                self.bank_rng, max_clusters=self.max_clusters,
                                max_modes=self.max_modes, bank_size=self.bank_size)
        self.bank_seconds += time.perf_counter() - start
        self.bank_builds += 1
        if bank is not None:
            self.mode_counts.append(len(bank.probabilities))
            self.cell_mass_errors.append(float(np.abs(bank.observed_mass - bank.capacities).max()))
        return bank

    def initialize(self, env):
        """E1's one-and-only partition uses the map immediately after reset."""
        if self.initialized:
            return
        self.initialized = True
        if self.variant == 'static':
            self.initial_bank = self._build_bank(env, frontier_mask(env.complete_map))
            self.initial_frontier_modes = (len(self.initial_bank.probabilities)
                                           if self.initial_bank is not None else 0)

    def _flow(self, env, z):
        positions = np.asarray([cell(p) for p in env.agent_pos], float)
        conds = []
        for i, pos in enumerate(positions):
            mates = [cell(x) for j,x in enumerate(env.agent_pos) if j != i]
            conds.append(build_condition(env.complete_map, cell(pos), mates))
        cond = torch.as_tensor(np.stack(conds), dtype=torch.float32)
        start = np.asarray(to_norm(positions), np.float32)
        x = torch.as_tensor(start + float(NOISE) * z, dtype=torch.float32)
        n = len(positions)
        with torch.inference_mode():
            for i in range(self.flow_steps):
                tau = torch.full((n,1), i/self.flow_steps, dtype=torch.float32)
                x = x + self.model(x, tau, cond) / self.flow_steps
        return np.asarray(from_norm(x.cpu().numpy()), float).reshape(n, 2)

    def _snap(self, env, proposed, fmask):
        # Match the original evaluation's nearest-reachable-frontier projection.
        m = env.complete_map
        targets=[]
        for i,p in enumerate(env.agent_pos):
            d = geodesic_dist(m, cell(p))
            valid = fmask & np.isfinite(d)
            if not valid.any():
                targets.append(cell(p))
                continue
            pts = np.argwhere(valid)
            if self.exclusion > 0 and targets:
                allowed = np.ones(len(pts), bool)
                for q in targets:
                    allowed &= np.sum((pts-np.array(q))**2, axis=1) > self.exclusion**2
                if allowed.any():
                    pts = pts[allowed]
            snapdist, j = cKDTree(pts).query(proposed[i])
            self.snap_dists.append(float(snapdist))
            targets.append(tuple(int(c) for c in pts[int(j)]))
        return targets

    def plan(self, env, fmask):
        start = time.perf_counter()
        self.replans += 1
        if self.variant == 'static':
            bank = self.initial_bank
        elif self.variant == 'online':
            bank = self._build_bank(env, fmask)
        else:
            bank = None
        if bank is None:
            self.no_bank += 1
            z = self.rng.standard_normal((len(env.agent_pos),2)).astype(np.float32)
            mode_index = None
        else:
            z, mode_index, draws = bank.sample(self.rng)
            self.mode_samples += 1
            self.sample_draws += draws
        proposed = self._flow(env, z)
        assigned = self._snap(env, proposed, fmask)
        if mode_index is not None:
            # This is *only* a proxy for whether noise structure controls the CFM.
            # The mode's goals may become stale in E1 as map exploration continues.
            ref = bank.goals[mode_index]
            self.mode_goal_distances.append(float(np.mean(np.linalg.norm(
                np.asarray(assigned, float) - ref, axis=1))))
        self.planning_seconds += time.perf_counter()-start
        return assigned


class ScheduledJointGoalEnv(GoalEnv):
    def __init__(self, *args, planner, replan, **kwargs):
        super().__init__(*args, goal_fn=None, **kwargs)
        self.joint_planner = planner
        self.replan_period = replan
        self.policy_calls = 0
        self.goals = None

    def get_goal_for_cost(self):
        self.policy_calls += 1
        fmask = frontier_mask(self.complete_map)
        if self.goals is None:
            should_plan = True
        else:
            should_plan = (self.replan_period > 0 and
                           (self.policy_calls-1) % self.replan_period == 0)
            for i, g in enumerate(self.goals):
                if g is None or not fmask[g] or g == cell(self.agent_pos[i]):
                    should_plan = True
                    break
        if should_plan:
            self.goals = self.joint_planner.plan(self, fmask)
        return np.asarray(self.goals, dtype=int)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant', choices=['independent','static','online'], required=True)
    p.add_argument('--map', default='room')
    p.add_argument('--robots', type=int, default=2)
    p.add_argument('--seed', type=int, default=41)
    p.add_argument('--ckpt', default='cfm_x5_linear.pt')
    p.add_argument('--max-steps', type=int, default=2000)
    p.add_argument('--replan', type=int, default=10)
    p.add_argument('--flow-steps', type=int, default=20)
    p.add_argument('--bank-size', type=int, default=1024)
    p.add_argument('--max-clusters', type=int, default=6)
    p.add_argument('--max-modes', type=int, default=12)
    p.add_argument('--exclude', type=float, default=0.0,
                   help='Keep identical in E1 and E2; default zero isolates noise.')
    p.add_argument('--step-seconds', type=float, default=1.0,
                   help='Provisional simulation seconds per step; verify with evaluator.')
    p.add_argument('--csv', default='results_noise_experiments.csv')
    p.add_argument('--trace-json', default=None,
                   help='Optional output path for detailed one-run metadata.')
    args = p.parse_args()
    if args.robots < 1 or args.flow_steps < 1 or args.replan < 1:
        p.error('robots, flow-steps, and replan must be positive')
    if args.step_seconds <= 0:
        p.error('step-seconds must be positive')

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    model = VelocityField()
    model.load_state_dict(torch.load(args.ckpt, map_location='cpu', weights_only=True))
    model.eval()
    planner = NoisePlanner(model, variant=args.variant, seed=args.seed,
                           flow_steps=args.flow_steps, bank_size=args.bank_size,
                           max_clusters=args.max_clusters,
                           max_modes=args.max_modes, exclusion=args.exclude)
    env = ScheduledJointGoalEnv(.1, 3.5, args.robots, 1000,
                                map_path(args.map), visualization=True,
                                planner=planner, replan=args.replan)
    with quiet():
        env.reset_for_traditional()
    planner.initialize(env)
    start = time.perf_counter()
    reached = coverage(env) >= .95
    steps = 0
    if not reached:
        for steps in range(1,args.max_steps+1):
            with quiet():
                env.step_for_cost()
            if coverage(env) >= .95:
                reached = True
                break
    end = time.perf_counter()

    paths = [len(x) for x in env.path_log]
    known = int(np.sum(env.complete_map != UNKNOWN))
    each = [int(np.sum(x != UNKNOWN)) for x in env.built_map]
    row = {
      'variant': args.variant, 'map': args.map, 'robots': args.robots,
      'seed': args.seed, 'ckpt': os.path.basename(args.ckpt),
      'time_to_95_percent_coverage': round(steps * args.step_seconds, 3),
      'unit': 'simulated_seconds_provisional',
      'reached_95': int(reached), 'capped': int(not reached),
      'steps_to_95_or_cap': steps, 'coverage': round(float(coverage(env)), 5),
      'overlap': round(float(sum(each)/max(known,1)-1), 4),
      'team_path': sum(paths),
      'replans': planner.replans, 'bank_builds':planner.bank_builds,
      'bank_fallbacks':planner.no_bank, 'initial_modes': planner.initial_frontier_modes,
      'mean_modes': round(float(np.mean(planner.mode_counts)),3) if planner.mode_counts else 0,
      'mean_mode_to_goal_cells': round(float(np.mean(planner.mode_goal_distances)),3)
                                  if planner.mode_goal_distances else '',
      'mean_snap_cells': round(float(np.mean(planner.snap_dists)),3)
                         if planner.snap_dists else '',
      'max_mass_error': round(max(planner.cell_mass_errors),4)
                        if planner.cell_mass_errors else '',
      'noise_draws': planner.sample_draws,
      'bank_seconds': round(planner.bank_seconds,4),
      'planning_seconds': round(planner.planning_seconds,4),
      'evaluation_wall_seconds': round(end-start,4),
      'replan_period':args.replan, 'flow_steps':args.flow_steps,
      'bank_size':args.bank_size, 'exclusion_cells':args.exclude,
      'step_seconds':args.step_seconds,
    }
    print(json.dumps(row, indent=2))
    if args.trace_json:
        with open(args.trace_json, 'w') as f:
            json.dump({'result':row,'mode_counts':planner.mode_counts,
                       'cell_mass_errors':planner.cell_mass_errors,
                       'mode_goal_distances':planner.mode_goal_distances}, f, indent=2)
    new = not os.path.isfile(args.csv)
    if not new:
        with open(args.csv, newline='') as f:
            original = next(csv.reader(f), [])
        if original != list(row):
            raise SystemExit('Refusing to append: CSV columns differ from current experiment')
    with open(args.csv, 'a', newline='') as f:
        w=csv.DictWriter(f, fieldnames=row.keys())
        if new:
            w.writeheader()
        w.writerow(row)


if __name__ == '__main__':
    main()
