# E1/E2: Frozen vs Online Structured Noise in Explore-Bench

## Scope and status

**Prototype / feasibility study — not yet a trained MoSDOT-style joint CFM.**
This experiment uses an *unchanged, independently trained per-agent CFM*
(`cfm_x5_linear.pt`) with joint noise-region selection at inference time.
There is no proven correspondence between its source-noise sectors and
frontier-assignment modes. The experiment must test that correspondence rather
than assume it. Full Explore-Bench integration has not yet been verified.

### Question

Does repartitioning a joint Gaussian source distribution using the **current
observed** frontier clusters at each replan improve exploration time to 95%
coverage over keeping the **initial** partition frozen?

The predeclared primary contrast is **online vs static**. The independent
Gaussian source is a secondary control. This prototype is a precursor to a
possible joint, mode-aware CFM method, not a complete test of that method.

## Mechanism

At a planning event, compute reachable frontier clusters from the **currently
observed map**, never simulator ground truth. Construct candidate joint
frontier modes (one tentative frontier goal per robot). Prefer distinct clusters
when enough clusters exist, and score combinations by cluster size and
observed-map travel distance. For each candidate joint assignment, create
directional anchors in the normalized joint Gaussian noise space (2N dimensions).

Fit **approximate** Laguerre cell weights using Monte Carlo semi-discrete OT.
Equal Gaussian cell capacities are targeted; the observed mass errors are logged.
Selection is *utility-biased* across modes, which differs from the equal cell
capacities. That deliberate weighting changes the actual Gaussian source
distribution: simply sampling cells by their exact Gaussian masses would
reconstruct the original Gaussian and be a null intervention.

Select a mode, rejection-sample a joint Gaussian vector within its cell, split
it into N two-dimensional epsilon vectors and feed each into the unchanged
per-robot CFM conditioned on the **current** map. Snap each CFM output to a
reachable frontier. Execute those goals via the existing benchmark's A* and
sensor model until a replan or an invalid goal.

This is heuristic source shaping. The anchors are **not** learned behavior-mode
supports, and nothing guarantees the CFM output will match the chosen mode.

## Experiment E1: frozen / initial structure

Build the initial mode bank just after the environment's initial observation.
Freeze all its anchors, probabilities and Laguerre weights for the entire
episode. At every subsequent joint replan, sample **new** noise from this same
initial bank while still conditioning the CFM on the **current** map and robot
positions. If no bank can be made initially, use independent Gaussian fallback
and report it. There is no online partition update.

**H1:** Initial structured noise improves exploration compared with independent
Gaussian sampling even without adaptation.

## Experiment E2: online repartitioning

Keep the same initial network checkpoint, team-level replanning schedule,
sampling algorithm, goal projection, sensor model and training data. At each
joint replan, rebuild frontier assignments, mode anchors and Laguerre cells
using the **newly observed partial map**. Sample noise from the current
partition. If no feasible mode bank exists, use independent Gaussian fallback
and log that event.

**H2:** Online repartitioning improves time to 95% coverage compared with E1
because newly opened, exhausted or obstructed frontiers alter what coordinated
behavior should mean.

## Independent noise control

At each replan, sample independent Gaussian epsilon per robot; use the exact
same trained network, synchronized replanning and frontier projection as E1/E2.

## Fixed protocol (provisional pending evaluator sign-off)

| Factor | Value |
| --- | --- |
| Primary metric | `time_to_95_percent_coverage`, minimize |
| Units | **Provisional simulated seconds**, controlled by `--step-seconds` |
| Maps | loop, corridor, corner, room, loop_with_corridor, room_with_corner |
| Training maps | corridor_asym, corridor_sym, room_2, room_3, room_with_corridor |
| Seeds | 41–50, paired by map and seed |
| Robots | 2 for primary experiment |
| Checkpoint | `cfm_x5_linear.pt` |
| CFM solver | 20 Euler integration steps |
| Joint replanning | Every 10 simulator calls, or if a goal becomes invalid |
| Maximum horizon | 2,000 simulator steps |
| Exclusion | Zero to isolate the noise effect |
| Main comparison | E2 online − E1 static, negative is favorable |
| Secondary comparison | E1 static − independent, negative is favorable |

All 3 conditions use the same map and seed. Do not cherry-pick maps or seeds.
A non-completing trial is scored at the 2,000-step cap and flagged as
`capped=1`. Never interpret a capped time as a directly observed T95.

The existing `run_eval.py` uses steps-to-90% and steps-to-98%. The new runner
records T95 but **assumes a provisional seconds-per-step mapping** until
Explore-Bench's time semantics and coverage denominator are independently
verified against the frozen S0 evaluator.

## Diagnostics and possible failure explanations

Report overlap and redundant travel as *secondary* metrics, mean CFM-to-frontier
snap distance, distance between the chosen mode's prototype goals and the
actually executed goals, number of partitions constructed, Gaussian cell mass
fit errors, bank fallbacks, sampling draws, and both partition-building and
total planning wall time.

In particular, a bank might be **degenerate at episode start** (only one joint
frontier mode). Online repartitioning could be beneficial merely because it
constructs more choices later; make the initial mode-count distribution visible.
Alternatively, noise regions may have *no reliable relationship* to generated
goals because the pretrained per-agent CFM never learned such a coupling.
If so, the next stage is joint mode-consistent training, not post-hoc tuning on
held-out maps.

E2 refits Laguerre partitions repeatedly, so although both methods use the
same 20 network evaluations per planning event, **their total compute is not
equal**. Log this and perform wall-time-budget-matched ablations before a
publication claim of equal-compute superiority.

The initial teacher code uses individual observation/goal examples. A full
method would require synchronous joint (map, team positions, assigned joint
frontier mode, joint goal) teacher data; a joint 2N goal flow and mode-aligned
noise/target coupling; and comparison with explicit frontier assignment,
PCDP-style reranking, ordinary CFM, and classical frontier baselines.

## Execution

From `explore-bench/cfm_example`, with the linked Explore-Bench simulator,
its custom `grid_simulator/cfm_policy.py`, and the checkpoint available:

```bash
python -m unittest discover -s tests -v
python run_noise_experiment.py --variant independent --map room --seed 41 --csv noise_smoke.csv
python run_noise_experiment.py --variant static      --map room --seed 41 --csv noise_smoke.csv
python run_noise_experiment.py --variant online      --map room --seed 41 --csv noise_smoke.csv
python analyze_noise_experiments.py noise_smoke.csv
```

Only after inspecting smoke-test output, run `bash run_noise_grid.sh`
(6 maps × 10 seeds × 3 methods = 180 trial runs).

## S0 and reproducibility boundaries

The source GitHub repository does not contain tracked `task/` or `machine/`
S0 files, and these experiments do not fill or modify those requirements.
The evaluator program, seconds/step conversion, frozen evaluator checksum,
and Gate A advisor approval remain outstanding. Python syntax and four isolated
unit tests were checked prior to branch upload; **full simulator runs were not
executed or asserted successful**. This branch is separate from `main`.
