## Mandatory 2D-grid scope correction (synthesis round005)
Alejandro works on a 2D grid simulator/environment and algorithms, NOT 3D or physically constrained sensing. Every observation range, reveal rule, occlusion, query budget or footprint below is a stipulated simulator treatment, never an asserted hardware restriction. Existing simulator observability/API is not yet verified: the supplied read-only reference repository was inspected and contains the workflow, with no simulator implementation located by bounded content search. Do not claim this custom construction already matches it. First adapt to its actual observable record/action rules after permission, or explicitly approve the small synthetic mechanism study. No LiDAR, cameras, real-sensor calibration, 3D checkpoints or robots are required. Unknown dates/resources remain assumptions. All implementation awaits applicable gates; no formal S0 approval is asserted.

# Conditional B candidate: where should temporal stability live?

Status: S0 candidate draft, not selected or approved. Evidence and rejection of superseded framing: /home/sircordero/research/s0-overnight-2026-11-16/recovery_reviews/B/review.md.

## Three plain-language curiosity sentences
A robot can change its mind too often when imagined obstacles keep changing. Remembering those imagined obstacles may steady its route but make it slow to accept what its sensors later reveal. I want to know whether remembering the route instead can preserve useful stability without making imagined occupancy persist as probability.

## Research question
For small partially observed grid-navigation tasks with equal completion samples, observations, and bounded planning time, does a sensor-only occupancy belief plus replaceable completion layer and explicit route-switch hysteresis achieve lower mean capped navigation cost than validation-tuned clamped accumulation of predicted occupancy with a sensor-overwrite safeguard, across completion-volatility and contradictory-observation regimes?

Primary estimand: paired mean cost of replacement-plus-hysteresis minus cost of the strongest validation-selected safeguarded accumulation system on the same held-out true-world distribution. Negative favors replacement-plus-hysteresis. Metric and failure charges are fixed in metric.json. A full representation-by-planner-memory factorial determines whether the headline difference is actually attributable to the representation rather than unequal access to planner state.

## Why answering matters
The choice is where temporal memory belongs in a perception-to-planning system. SceneSense §6 explicitly motivates persistent fusion by trajectory oscillation; OctoMap §3.2 already addresses excessive persistence with clamping. Neither inspected source establishes that replacing persistence with planner memory wins this fair closed-loop comparison. This is a bounded mechanism/replication question, not claimed new Bayesian theory or an established literature gap.

## Competing explanations and outcomes
- Stability explanation: clamped accumulation suppresses transient completion errors more effectively than route memory; a positive paired difference supports it under these budgets.
- Separation explanation: explicit route memory preserves useful stability while the replaceable speculative layer adapts better after actual contradictory sensing; a negative difference supports it.
- Null: an interval entirely within the practical tolerance suggests no consequential difference in the tested population. A wide interval crossing zero is inconclusive, not equivalence.
- Reversal: accumulation can win at high volatility while replacement wins after contradiction; prespecified strata expose a boundary rather than changing the primary outcome.
Both failures to match stability and failures to improve adaptation are scientifically informative. Repeated-evidence non-independence and frozen-context exact-posterior superiority are sanity tests, not discoveries.

## Population, units, conditions
Independent unit: generated map family; start-goal episodes and random prediction tapes are nested paired observations. Static 16x16 grids drawn from a declared finite mixture of corridor/doorway layouts, with known discrete world priors. All true worlds remain fixed during an episode. Contradiction means a real sensor reveals that prior completion was wrong, not an unannounced moving obstacle. Test mixtures, sensor model, and splits are frozen before evaluation. Exact finite-world posterior sampling supplies completion tapes; these are explicitly not learned CFM results or claims of real-world calibration.

## Fairness and scope
Both systems maintain identical sensor-only likelihood updates, observed masks, robot pose, action set, common replanning frequency, immediate physical-obstacle veto, collision handling, and CPU deadline. Both may use route memory; the factorial crosses replacement versus accumulation with zero versus validation-tuned hysteresis. Accumulation includes clamping, a prediction-weight grid, sensor-overwrite variant, and a no-overwrite diagnostic. Main competitor is the best safeguarded variant chosen on validation, never an unbounded naive accumulator. Independent validation tuning gets equal candidate counts and wall-time budget. Same prior P, true worlds, and prediction random streams are shared; do not evaluate each method under its own assumed world population.

Minimum scope: finite-world simulation mechanism study, no training or robots. Flow matching is not central or required; student/advisor must approve this adjacent mapping interpretation. Exclude real-robot safety claims, SceneSense deployment-defect claims, learned calibration claims, dynamically changing worlds, HPC, and architecture novelty. If a flow-matching-central project is mandatory, this draft should be rejected rather than cosmetically renamed.
