# A — When is connectivity information an adequate sensing proxy?
**Round005 scope correction:** Interpret sensing as a deliberately stipulated 2D simulator reveal/query action, not physical sensor constraints. Existing simulator observability/API is not yet verified; no hardware, 3D or calibration requirements. The minimum must earn value beyond the already-known fallback-route degeneracy and existing task-aware query literature.

**Round 003 revision, 2026-11-16. Conditional S0 candidate packet / proxy-sufficiency replication audit, not a selected or approved project.** Earlier broad 'task-aware sensing' pitch is rejected. No evaluator built, training or experiment performed.

## Three plain-language curiosity sentences
A robot may already know that some route exists without knowing which route is cheap.
An uncertain doorway can change the best route without changing whether the goal is reachable.
I want to know when asking about connectivity is enough, and when the robot must ask about route cost instead.

## Precise subject/comparison question
For finite partially observed 2D room-and-doorway map populations, when does choosing one equal-cost feasible probe by information about the binary start–goal reachability event produce lower or higher mean capped navigation cost than visibility-weighted cell variance, whole-world information, and same-prior one-step expected navigation-cost selection, as reachability uncertainty and route-cost ambiguity vary separately?

## Why interesting independent of novelty
Family: active robotic mapping / acquisition objective, not D's representation intervention. All acquisition methods see the same stipulated joint belief or same sampled worlds. Primary comparison remains connectivity-information versus visibility-weighted variance; whole-world information and decision-value comparators test the explanation and prevent a weak-baseline success claim. No claim of new MI planning: MacDonald & Smith (IJRR 2019; online 2018), §§5.1/5.3/7.2 already combine physical sensing/travel cost with world information, compare optimum and vary reachability; Choudhury et al. 1711.07329v1 already target path decision regions rather than complete world reconstruction. MapEx already has visibility×variance and topology-sensitive evaluation.

A useful outcome would delimit whether a compact binary connectivity proxy is adequate relative to a cost-aware selector, not simply demonstrate that topology matters. Minimum is **not FM-specific**: CFM vector-field-regression ODE samples would be a separable later approximation check only if the exact-belief audit is interesting. Advisor must confirm this alignment.

## Competing explanations and informative outcomes
- Information about cheap alternative routes matters after reachability is settled; binary connectivity discards it.
- Any observed advantage comes from visibility, geometry, tie breaking, or probe travel rather than information target.
- World-identity information wastes effort on nuisance worlds; cost-aware selection may avoid both proxies' failures.
- Finite-particle noise, not the target definition, explains score rankings; compare exact versus shared-MC variants separately.
Positive: connectivity proxy approaches decision-value selection at lower scoring cost in a prespecified reachability-dominated regime. Null: no practically important difference within a justified frozen tolerance on the declared population; non-significance alone is not equivalence. Reversal: proxy misses shortcut-value uncertainty or spends effort determining an unactionable unreachable state. A known-fallback all-reachable case makes binary connectivity MI exactly zero **by definition**; this is an analytic degeneracy control, not a new empirical discovery or sufficient contribution.

## Unit, population and intervention
Independent unit: generated map-template instance; start/goal contexts, worlds, sensing draws and solver seeds are nested. Do not count doors/pixels/rollouts as independent replicates. Conditional finite library/prior and legal doorway geometry are declared. Split tuning/test by template family, not masks of the same map. Vary (i) probability that any start–goal route exists and (ii) relative cost/validity ambiguity among alternative routes. Do not claim those factors can be independently changed without checking induced marginals and geometry; require hand-audited crossed template cells where feasible and report infeasible cells, never silently impute.

## Fairness, scope and exclusions
Minimum: exactly one probe from a nonempty equal-cost action set, followed by one shared fixed route execution/backtracking policy. Physical probe travel is through already-observed free corridors; no incidental new sensing en route, an explicit simplified sensor model. Freeze initial start/goal reachability event before scoring; do not alter its meaning across methods. No-probe is a separate cost-benefit diagnostic; it is not a free opt-out given only to the proposed method. If no feasible action, all methods share the same no-probe fallback.

Stipulated prior/library available to all methods is not forbidden truth access. Realized world is hidden from every method and revealed only to evaluation. Exact same-prior cost lookahead is a valid information-matched comparator when charged its scoring budget; an unconstrained version is labeled a diagnostic reference, not a free baseline. Match sample/action sets and decision deadline, freeze tie breaks, record timeouts. Conditional scoring choices/hyperparameters get the same validation budget; no test tuning. Equal-cost minimum must not masquerade as arbitrary travel-cost robustness; unequal-cost extension requires a separately frozen common cost-selection rule.

Excluded: 3D, real buildings, dynamic obstacles, pose errors, claims of deployable safety, new generative architecture, and a full multi-step optimal POMDP. Small enumerated one-step study first; hours/calendar/CPU capacity remain assumed in constraints.json. If only tautological degeneracy cases or oracle superiority remain, **reject A** rather than fill an experiment schedule.

## Governance
Alejandro selects the question; Dr. Enriquez alone decides Gate A. Unknown resources and project window need confirmation. No implementation before Gate C. This packet is not S0 passage.
