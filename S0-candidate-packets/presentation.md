# Presentation draft — update with final checkpoint before 05:30 CST

Alejandro — I corrected the scope: **your project is 2D grid environments and algorithms, not 3D or physical-sensor hardware.** Any visibility, partial-observation or query restriction below is a deliberately chosen simulator rule, not an assumed hardware limit. I have not verified the actual simulator API from the supplied workflow repository, so these are instrument proposals, not claims that a benchmark already runs in your environment.

The strongest outcome of the research was pruning weak questions. Existing work already studies correlated map decisions, authentic observation masks, persistent occupancy fusion, and FM samples-versus-integration tradeoffs. I would **not** sell any of those generic ideas as a new gap.

## Five more precise questions

**1. Joint-map dependence: when does retaining correlations become harmful?**
Holding marginal door probabilities and the decision algorithm fixed, when do finite or misspecified joint map hypotheses improve or worsen navigation compared with shuffled hypotheses with the same marginals?
- Instrument: small known grid-world population, one declared reveal, common truth and fixed continuation.
- Primary: capped navigation cost, including failures.
- Useful negative: simpler beliefs are sufficient—or safer when joint structure is wrong.
- Caveat: correlations helping is already established, including a2D-grid study and an optimal-policy theorem in SCOS (2509.19559v2). Prediction-consistency/robustness is also established in learning-augmented CTP (2209.11100v1). The contribution would have to be the precise finite-sample/wrong-dependence replication boundary, not those generic findings. Match marginals before the query, not by secretly reintroducing joint-inference information afterward.

**2. Temporal memory: should stability live in the map or the planner?**
Can replaceable speculative occupancy plus route-switch hysteresis match a strong clamped/reset accumulator, especially when later reveals contradict earlier completions?
- Instrument: representation × planner-memory factorial, equal tuning and completion budgets; both sides get safeguards.
- Primary: capped navigation cost, not just calibration.
- Useful negative: accumulated speculative maps remain better under a fair stability treatment.
- Caveat: this minimum is mapping/algorithm research, not an FM result; planner-memory prior-art coverage remains incomplete.

**3. Direct FM: does the training reveal policy matter for whole-map uncertainty?**
Does training a small conditional FM on the stipulated simulator reveal process rather than random masks improve joint posterior approximation on the same test records?
- Instrument: **actually trained** matched models plus an exact finite-grid posterior reference; no oracle substituted for the model.
- Primary: a joint-distribution discrepancy contrast; pixel error is only secondary.
- Useful negative: random masking transfers adequately or regularizes better at the fixed budget.
- Caveat: mask alignment is already recommended in CFMI and studied elsewhere. This is a bounded grid-specific replication, with no held-out-world claim in the minimum. Training feasibility is untested.

**4. Query objectives: when is connectivity the wrong question?**
When does choosing reveals to learn whether *any route exists* underperform choosing them to learn route cost?
- Instrument: equal-cost queries; compare connectivity information, cell variance, whole-world information and same-prior cost lookahead.
- Useful negative: a simpler proxy suffices in a defined regime.
- Caveat: a known fallback making connectivity information zero is algebra, not a discovery. Reject this option if it cannot go beyond that example.

**5. Higher-risk planning audit: learned geometry or checker-supplied success?**
Do route-closing map edits change raw FM proposals more usefully than matched irrelevant edits, and does collision-verifier selection conceal the difference?
- Instrument: paired map edits, common latent draws, independently varied proposal/verifier maps; always score against the true edited map.
- Useful negative: checked success is not attributable to useful proposal conditioning.
- Caveat: geometry-intervention auditing already exists, and an accessible licensed occupancy-conditioned model is **not yet verified**. Park this unless an eligible model or separately approved tiny-model construction is feasible.

## My recommendation
**Start the advisor discussion with #1 if controlled 2D algorithm replication is acceptable.** Its strength is a clean matched-marginal intervention and a meaningful wrong-dependence failure boundary, not novelty. **#2 is the smaller-construction fallback**, not automatically the stronger question. **If flow matching must be central, discuss #3 first instead**; it keeps FM essential and has explicit feasibility stops. #5 is the parked model-dependent option.

One important evaluator catch: a draft joint-distribution score was mathematically identifying but almost insensitive to a severe correlation mistake at its proposed practical tolerance. I documented the analytic counterexample, revised the new packet's kernel and effect direction before selection, and withdrew any accepted-equivalence claim until the margin is justified. That is an instrument correction—not an experimental result.

**Status:** five distinct conditional question drafts, not five proven finalists. Each has all five S0 artifacts and full-text-linked seeds; no evaluator, pilot or training was run, no novelty was established, and no state was passed. Project dates/hours/compute remain assumptions. You choose the question; **Dr. Enriquez decides Gate A**.

Full decision memo: `/home/sircordero/research/s0-overnight-2026-11-16/REPORT.md`.
Packets: `candidates/{joint-map-dependence,temporal-memory-location,grid-observation-policy-transfer,connectivity-directed-sensing,map-conditioning-verifier-audit}/task/`.
Evidence, rejected versions, exact construction plans and checks: `sources/`, `recovery_reviews/`, `iterations/`, `VALIDATION.md` and `PROGRESS.md` in the same workspace. The reference repository remains read-only and unchanged by this work.
