# D — Does joint map uncertainty change decisions? — provisional S0 candidate packet
**Round005 scope correction:** This is a 2D grid-algorithm study, not a 3D/sensor project. Every partial-observation/probe rule is an explicit simulator treatment, not a physical restriction. Existing simulator API/observability is not yet verified; do not claim compatibility. No hardware sensing budgets, real sensors or 3D checkpoints required. Conditional replication only; LAMP and correlated-traversal nearest answers remain decisive objections.
Status: first synthesis draft, not selected, not approved; no evaluator built or experiments performed.

## Three plain-language curiosity sentences
Two uncertain doors may each be open half the time but never open together.
A map made from independent cell guesses can lose that relationship.
I want to know whether keeping the relationship actually changes a useful robot decision.

## Precise question
Under a fixed true distribution of hidden-door worlds, when do finite joint map hypotheses lower or raise one-probe capped navigation cost relative to doorwise-shuffled hypotheses with exactly the same empirical marginals, as sample count, joint-mode misspecification and probe cost vary? This is a controlled robustness/replication question: the general value of door correlations and paid information is already established, not a proposed discovery.

## Subject, comparison and scientific value
Family: Map representation → decision utility.
The SAME coherent joint samples versus independent column permutations of whole-door states, preserving each door’s empirical marginal exactly; include no-shuffle independent-prior negative controls, thresholded mean maps, conservative observed-only, and cost-aware exact one-step reference.

Causal intervention on cross-door dependence in map beliefs, distinct from A’s acquisition-objective intervention. Keep the decision rule fixed across coherent/shuffled representations; only secondary factorial analysis changes acquisition rule. The value is an interpretable operating boundary and an informative negative answer, not a claim of unprecedented architecture or an unoccupied literature gap.

## Competing explanations
The apparent effect is geometry invalidity, finite-sample noise, changed marginals, extra sensing or a stronger decision policy. Joint dependence may be irrelevant if the route is forced or probe cost exceeds information value.

## Outcomes that teach something
Positive: coherent samples help only with actionable correlated ambiguity. Null: shuffled maps make the same decisions or visibility baselines suffice, giving a useful boundary of joint posterior modeling. Reversal: misspecified/undercovers-rare-event joint samples cause more harm than a conservative representation.

## Unit, population and conditions
Independent unit is a generated map-family instance, with starts, goals, observations, sample streams and solver repetitions nested inside it. Do not count pixels, doors or repeated trajectories as independent experimental replicates. Minimum population is explicitly specified finite 2D synthetic room/corridor layouts with hidden whole-door variables (E uses fully given maps and fixed point/disc robot). Only generalize to this distribution; real buildings, sensor pose uncertainty, dynamic obstacles and 3D are excluded. Factor levels and held-out family split must be preregistered after a feasibility pilot, not chosen from final outcomes.

## Fairness and scope
Small finite valid door-world library, exact known joint posterior, one sensing action, fixed receding-horizon downstream policy. No per-pixel shuffling: shuffle whole-door variables so every map remains valid.
Same observation histories, priors, candidate probes/contexts and inference budget unless the named intervention intentionally varies them. Ground-truth worlds are visible ONLY to the evaluator/oracle, never to a deployable method. Exact posterior/oracle references are privileged diagnostics, labeled as such rather than fair learned-policy baselines. Separate known-distribution mechanism results from any later learned-sampler approximation/shift results. CFM is vector-field-regression ODE sampling, not geometric optical flow or the spectral diffusion-maps algorithm.

## Strongest objection and unresolved prerequisites
**Broad mechanism already answered; lead status downgraded after full-text near-answer check at 02:57 CST.** LAMP (2012.02271v1, pp.1–2) explicitly motivates two correlated doors, learns higher-order edge relations, and already reports early disadvantages of a learned correlation model (pp.11–12). Lamarre & Kelly (2505.13674v2, §5.2.3) already compare correlation-aware traversal with fixed initial marginal beliefs, including a same-policy boundary under high risk aversion. Therefore “do correlations matter?” and “can learning them hurt?” are inadequate as standalone contributions. Local full-text notes: `sources/synthesis-0252/{lamp,risk-correlated}/note.md`.

The residual project is a controlled **finite-particle / matched-marginal dependence-misspecification audit**, not a new mechanism. Whether that replication boundary is substantial enough is explicitly Alejandro/advisor's decision. Two doors alone are an evaluator hand-check, not the research result; require held-out geometry families and an ex ante defined robustness boundary. CFM remains optional in the minimum and cannot be smuggled in as a claimed contribution.

Column permutations preserve empirical marginals but do not guarantee exact finite-sample independence. All evaluation uses the SAME true world population P; only method belief Q changes. Use known joint distributions P and alternative Q with identical population door marginals; reject any proposed Q that silently changes marginal quality. Whole-door geometry validity is required even when Q assigns mass to modes absent under P. Do not condition/split separately under each method's assumed world population.

## Round006 — nearest-answer and treatment-order correction
**SCOS (Zhou & Ceyhan,2509.19559v2, §4.4.1 and §8)** already supplies 2D-grid correlation-aware navigation, a correlation/independence downstream example and an optimal-policy coarsening-dominance theorem. Its A3 coarsens the updated full joint posterior at each stage; that is not identical to updating a product prior independently. **Bampis et al. (2209.11100v1, §1.1)** already study prediction-consistency/robustness in CTP; a generic 'right predictions help, wrong ones hurt' pitch is inadequate. Full-text notes: `sources/synthesis-0440/{scos,predictions}/note.md`.

The residual D remains conditional, not strengthened into a novelty claim. **Match empirical marginals at the representation intervention point, before the prospective reveal.** Each representation then conditions its OWN assumed distribution on subsequent legitimate observations. Do not silently feed exact-joint posterior marginals back into the shuffled arm after every reveal: this would resupply joint-inference information. Different post-reveal marginals are an intended mediator, not a failure of the initial matching. A stagewise product-of-exact-posterior baseline may be reported as a separately labeled stronger diagnostic. Known-P optimal information dominance is not a new experimental result; finite-N/wrong-Q/fixed decision-functional regimes are the only possible empirical target. Reversal there does not refute SCOS's theorem.

## Governance
Unknown student hours, hardware and calendar are assumptions. Alejandro chooses the question; Dr. Enriquez alone decides Gate A. This is an S0 candidate packet, NOT a passed state. No implementation before Gate C.
