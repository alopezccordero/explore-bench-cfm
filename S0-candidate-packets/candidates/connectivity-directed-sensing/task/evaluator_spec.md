# Evaluator construction plan — A, round 003; NOT executed

## Status, dates and scope gate
No runnable evaluator for this exact RQ is claimed. Assume **2026-11-23–2027-01-17**, 8–10 hours/week, existing CPU <=16 GB only; actual window/resources unconfirmed. All construction after Gate C; redate if approval arrives later. The plan is not student attestation or Gate A.
- **2026-11-23:** advisor checks whether proxy-sufficiency replication and a mapping-first/non-FM minimum are worth pursuing. Reject if only a designed counterexample remains.
- **2026-12-07:** after Gate C, construct tiny finite legal door-map/prior/sensor model; enumerate hand-checkable cases. Freeze crossed regimes and template-family partitions without final effect estimates.
- **2026-12-10:** implement shared route policy, interfaces, explicit cap H, timing/fallback and analytic tests below.
- **2026-12-14:** bounded feasibility pilot on development templates only; select world/cluster/sample counts and absolute practical tolerance without looking at final test contrasts. Tentative five inference seeds is planning, not power evidence.
- **2026-12-18:** freeze analysis, score weights/ties, library generator/version hashes, splits and all-failure rules; independent trivial-case review before any approved final study.

## Input, output and precise information targets
Input: declared finite library of geometrically valid 2D room/whole-door worlds and prior P, initial physical observations h with explicit likelihood, initial (s,g), same reachable probe set A(h), candidate outcomes/likelihoods, fixed continuation policy pi, shared draws, action/scoring budgets and cap H.

All methods may use the same prior or the same K conditional world draws. Actual current world is **evaluation-only**. Exact reference probability is under this stipulated model, not real-building truth.

For world w, C(w)=1 if s and g are connected in w. Freeze s/g at initial query. Connectivity score is I(C;Y_a|h), using exact enumeration in the minimum. World score is I(W;Y_a|h), not the sum of independent door entropies. Visibility×variance control uses documented expected visible-cell occupancy variance and the same sensor geometry; list exact implementation/formula when built and call any deviation 'MapEx-style proxy', not a reproduced MapEx result. Conditional outcome weighting is explicit; observed cells are not scored as unobserved uncertainty.

Cost selector minimizes J(a|h)=E_P[c_probe(a)+L(pi(h,a,Y_a),W)|h]. It integrates possible observations using the same joint belief; it does not receive W. Fixed pi is identical for all methods after their selected probe. Minimum uses a small declared route library and deterministic execution/backtracking/fallback rules, not a world-optimal continuation available only to one acquisition rule. Candidate routes, probes and their paths are generated from public geometry/initial observed map and development priors only, never final test-world solutions. Record the route/probe construction rule as part of the frozen instrument.

Output: chosen action, all method scores, route/execution trace, costs, elapsed scoring time, input hashes, random seeds, failure flags and capped episode cost. Finite probabilities required; log invalid/missing outputs separately.

## Action fairness and physical observation model
Minimum forces exactly one probe for every acquisition method whenever A(h) is nonempty; travel+sensing cost is equal across this candidate set. All share the same already-observed-free travel routes and receive no additional en-route measurements. Nonempty equal-cost sets and synthetic suppression of incidental sensing restrict generality and must be disclosed. Separate no-probe diagnostic establishes whether probing is worth doing; a cost selector restricted to A(h) is the matched comparator, not an unrestricted oracle with privileged opt-out. Empty A(h) triggers common no-probe policy. Deterministic geometry/ID tie break is identical, especially when connectivity scores are all zero. Log fraction of zero-score ties so random choice is not called informed sensing.

Exact-enumeration scoring for all methods first. Then, only if needed, shared-K MC scoring with paired streams to isolate approximation. Charge sample generation and scoring to identical decision deadlines; timeout invokes a frozen feasible default probe/shared fallback and remains in primary. Untimed exact cost selector is labeled diagnostic reference when it exceeds the budget. Report computational overhead separately from primary navigation cost. CFM is optional later and cannot be claimed scientifically essential by relabeling enumeration.

## Primary metric and failures
Primary **mean_capped_navigation_cost**, minimize, grid-distance-equivalent cost/episode. Before final study fix H>0, containing movement, backtracking and sensing cost in common units. If success occurs before H, cost is incurred total. If unsuccessful (including impossible goal, invalid method output, timeout-induced failed fallback, or exhausted action policy), charge **H**, not zero travel. If success would require cost >H, treat as failure at H. All records remain in denominator. H is common, justified using the development geometry envelope and fixed before final outcomes; sensitivity to H is secondary and may not replace the primary.

Average nested contexts/world realizations/seeds within each independent template instance with frozen weights, then weight independent instances equally within a frozen regime mixture. Contrasts paired on contexts; cluster intervals by template instance, not doors/pixels/trajectories. Report regime contrasts, success fraction, zero-score ties, scoring latency and MC variance. Non-significance is not equivalence. If draw weighting represents P, use known declared weights consistently and disclose finite-library scope.

## Data, access, leakage and minimum feasibility
No external dataset necessary: future original finite world generator. Publishing/license choice remains Alejandro's. Train/tune/test split by topology/template family; no held-out truth used for action set, score tuning, route library, H or stopping. Required crossed conditions include reachability uncertainty and alternative-route ambiguity; verify their achieved values from generator specification and report unsupported cells. Hardcoded all-reachable-known-fallback case is only an analytic control; do not make it the central measured result. Unknown cluster count/precision/scale is pilot dependent. Multi-step optimum is explicitly excluded; even MacDonald & Smith §7.2 report difficult exact optimization, so a small one-step instrument is intentional.

## Trivial tests to construct later — none run
1. Sum-to-one/Bayes update and hand-computed one-door observation/outcome probabilities.
2. C constant 0/1 implies connectivity MI=0 for every probe; common tie break, no divide-by-zero.
3. Known long fallback with uncertain short route: C constant 1 despite route-value information. Test scores, not a claimed effect-size finding.
4. Same-world-identity nuisance changes MI(W;Y) without changing shared policy cost; control identifies world-information distraction.
5. Symmetric equal-cost routes/probes, fully observed/all-free map, unreachable goal, empty probe set.
6. Exact versus increasing-K MC score accounting; common stream; invalid probabilities; timeout/default; no survivor-only cost.
7. All unsuccessful episodes score H; successful <=H costs preserved; success beyond H censored as failure.
8. No extra observations during travel; candidate actions/routes identical and no test-world access; hidden-door geometry remains legal.

## Component/source evidence — not turnkey evaluator claims
- MacDonald/Smith author manuscript: https://ece.uwaterloo.ca/~sl2smith/papers/2017IJRR-Active.pdf ; DOI 10.1177/0278364918772024. §§5.1/5.3 physical sensing/world MI/cost selection, §§7.2/7.3 reachability/prior errors. `sources/synthesis-0322/macdonald/note.md`. No executable release/license verified this round.
- Bayesian Active Edge Evaluation: https://arxiv.org/pdf/1711.07329v1 ; `sources/synthesis-0322/bisect/note.md`. DRD/computational edge checking, not this physical probe evaluator. Code/data promise in v1 is not verified availability.
- MapEx real repo https://github.com/castacks/MapEx ; paper 2409.15590v3. Scout inspected scripts/explore.py and BSD-3-Clause-Clear code; weights/KTH rights and turnkey TU evaluator unresolved. `sources/robotic-mapping/mapex-original/note.md` and `sources/constraints-compute-decisions/maps-agent/SOURCE_NOTES.md`.

Main blockers: does any non-tautological proxy-sufficiency regime remain interesting; can independent reachability/route-value factors be matched without answer encoding; can one-step scoring/candidate sets fit the assumed budget; does advisor require FM centrally? Reject rather than assume these answers.
