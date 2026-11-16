## Mandatory 2D-grid scope correction (synthesis round005)
Alejandro works on a 2D grid simulator/environment and algorithms, NOT 3D or physically constrained sensing. Every observation range, reveal rule, occlusion, query budget or footprint below is a stipulated simulator treatment, never an asserted hardware restriction. Existing simulator observability/API is not yet verified: the supplied read-only reference repository was inspected and contains the workflow, with no simulator implementation located by bounded content search. Do not claim this custom construction already matches it. First adapt to its actual observable record/action rules after permission, or explicitly approve the small synthetic mechanism study. No LiDAR, cameras, real-sensor calibration, 3D checkpoints or robots are required. Unknown dates/resources remain assumptions. All implementation awaits applicable gates; no formal S0 approval is asserted.

# Conditional S0 draft: task-relevant map dependence of FM proposals

## Three curiosity sentences
A planner can look successful because its checker discards bad suggestions. I want to know whether a flow-matching planner changes its suggestions when an obstacle closes a useful route. I also want to know whether it reacts just as much to an obstacle that cannot matter for the trip.

## Question
For a fixed occupancy-conditioned continuous flow-matching trajectory generator on held-out paired 2-D maps with fixed start and goal, is the improvement in raw proposal validity from updating stale map conditioning larger for route-topology-changing edits than for occupancy-matched, certified task-irrelevant edits, and does common verifier selection conceal this selective dependence?

Status: scientifically defensible conditional audit, NOT an executable finalist. No usable licensed occupancy-conditioned checkpoint has been established. It is not the rejected E samples/NFE/deadline proposal.

## Estimand and population
A base map M has two distinct available routes and at least one feasible fallback after the intervention. T closes one designated corridor; I changes the same number of occupied cells in a permanently disconnected region. Keep start, goal, robot footprint, map frame, latent draws, guidance, integration settings and proposal count fixed. Topology here means availability of a declared route channel in the free-space graph; it does not mean an unmeasured Betti number. Certify both edits with exact finite-grid connectivity and swept-segment geometry, not a learned label or a planner timeout.

For edit e in {T,I}, let V(c,e) be the fraction of all raw trajectories generated under condition c that are valid on edited true map M_e. Define g_e=V(M_e,e)-V(M,e). Primary D=mean_base[g_T-g_I], reported in percentage points. Thus compare correct versus stale conditioning on the SAME edited evaluation geometry; a raw before/after validity drop alone confounds increased difficulty. Higher D indicates more task-selective useful map dependence, not overall superiority. Unit is a base-map family/quartet; proposals and latent repeats are nested, not independent samples.

## Why answer it
Selective useful response would support dependence on relevant geometry in this population. Near-zero D with adequate measurement precision would bound its practical benefit, not establish that the model ignores all geometry. A negative D/reversal suggests distractibility or harmful updates. Strong raw dependence with weak selected-path differences means the checker masks proposal changes; weak raw dependence but good checked success cautions against attributing system success to the learned proposal. Broad intervals are inconclusive. A nonresponsive, generally incompetent model is not evidence of an interesting shortcut: establish competence on ordinary held-out base maps before interpreting the audit.

Competing explanations: learned local geometry; start/goal/template memorization; response to any occupancy edit; out-of-distribution edits; verifier-only rejection; discretization artifacts. Check edited occupancy survives model preprocessing. Controls and exact labels separate some, not all, explanations; no claim to identify internal representations or causal reasoning.

## Fair comparison and scope
Primary comparison is within one frozen model, not different architectures. Cross proposal map {base, edited} with verifier map {base, edited}; always score on true edited map. Verifier only selects first feasible candidate, never repairs or optimizes; retain no-selection failures. Include no-verifier raw outputs, identical bank reused across verifier arms, map-blind proposal control and exact grid planner as instrument/ceiling controls. Exact planner is not an equal-compute neural competitor. No test-based tuning. Timing is secondary descriptive, not a primary deadline question.

Minimum: point/disc robot, static fully observed synthetic occupancy maps, two-route tasks with feasible fallback, one small approved model. Exclude partial observation, active sensing, learned map completion, manipulator dynamics, driving, broad generalization claims, safety certification and model scaling. Alejandro chooses; Dr. Enriquez owns Gate A. Construction/training requires later permissions and Gate C.
