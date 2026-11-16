# D — Does joint map uncertainty change decisions? — provisional rationale

> **Round006, ~04:46 CST: additional near-answer and instrument correction.** SCOS (Zhou & Ceyhan,2509.19559v2) already studies correlation-aware navigation on2D grids and proves optimal-policy coarsening dominance under explicit A3. Its stagewise product-of-exact-posterior is not an independently updated product prior. D now fixes permutation BEFORE the prospective reveal and permits different post-reveal marginals as an intended mediator. Bampis et al.2209.11100v1 already study prediction consistency versus robustness in CTP; generic 'wrong maps hurt' is not a gap. Notes `sources/synthesis-0440/{scos,predictions}/note.md`. Exact-P superiority is a control, not a contribution; conditional finite-N/wrong-Q replication remains the only survivor. SCOS replaces optional generic FM as the fourth seed; all earlier critique retained below. S2 new-seed429 unresolved, OpenAlex direct resolution successful.

> **Round 02, ~03:03 CST: broad framing rejected as a sufficient contribution; provisional lead demoted.** This file retains the initial argument below as historical critique provenance. Current RQ is the finite-particle/matched-marginal dependence-misspecification robustness audit in task/task_spec.md. LAMP's two-door example and higher-order correlation learning (2012.02271v1 pp.1–2), including early disadvantages of an imperfect correlation method (pp.11–12), and correlated CVaR-CTP's value-of-information comparison and same-policy null (2505.13674v2 §5.2.3), defeat the generic pitch. Full-text notes and successful S2/OpenAlex records are in sources/synthesis-0252/. Two nearest seeds replace the generic SceneSense seed; four total seeds. No novelty asserted.

What could still be worth doing is a tightly controlled replication boundary: change only dependence in the method belief, preserve empirical marginals, hold the true evaluation population fixed, separate finite MC error from wrong joint modes, and charge every failed episode. Not acceptable: demonstrate two correlated doors and call it new; compare predicted cost distributions under different assumed truths; add CFM only for naming. Keep/reject depends on whether this boundary is interesting to Alejandro/advisor and feasible in the assumed window. A/B do not win by default. A–D direct-FM relevance remains unresolved.

Causal intervention on cross-door dependence in map beliefs, distinct from A’s acquisition-objective intervention. Keep the decision rule fixed across coherent/shuffled representations; only secondary factorial analysis changes acquisition rule.

## Why care even if duplicated?
The output would be a bounded regime/replication result with controlled explanations, not a novelty-dependent “better model” task. Positive: coherent samples help only with actionable correlated ambiguity. Null: shuffled maps make the same decisions or visibility baselines suffice, giving a useful boundary of joint posterior modeling. Reversal: misspecified/undercovers-rare-event joint samples cause more harm than a conservative representation.

## Strongest competing work / objection
A contrived two-door demonstration proves possibility but not a substantial research question. Need a preregistered regime map and competing explanation controls; learned CFM is not essential to the base mechanism, making alignment with study area an explicit advisor choice.

## Minimum and feasibility
Small finite valid door-world library, exact known joint posterior, one sensing action, fixed receding-horizon downstream policy. No per-pixel shuffling: shuffle whole-door variables so every map remains valid.
Unknown resources/time explicitly assumed in task/constraints.json; no empirical performance or pilot is claimed. Define what “independent” means for finite sample permutations; residual dependence can remain. Guard against empirical marginals versus population marginals mismatch. May merge with A if distinction lacks scope.

## How to explain to Dr. Enriquez
“Holding empirical door occupancy marginals, sensor actions and sample budgets fixed, when does preserving joint dependence among hidden doors lower one-probe navigation cost relative to doorwise-shuffled map hypotheses, as dependence, bottleneck relevance and probe travel cost vary?”
The five task artifacts are a candidate packet, not evidence S0 passed. Alejandro decides whether he wants this question; only advisor Gate A can accept it.

## Current source status
All seeds link to local full-text notes, several created by independent scouts. Seed metadata and nearest answers require continued adversarial checking; source existence is not successful S1 traversal. See seed file status and VALIDATION.md. Current packet is intentionally provisional and preserves blockers.
