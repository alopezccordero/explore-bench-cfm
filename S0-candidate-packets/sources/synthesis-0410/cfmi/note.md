# Independent round-005 full-text audit — CFMI

Retrieved 2026-11-16 ~04:11 CST via https://arxiv.org/html/2506.09258v1 (HTTP 200). Exact title: **CFMI: Flow Matching for Missing Data Imputation**. Authors: **Vaidotas Simkus; Michael U. Gutmann**. Persistent identifier arXiv:2506.09258; inspected immutable version v1, 10 June 2025. Full HTML: `full.html`; raw extraction `full.txt`; paragraph extraction `blocks.txt`. Official fulltext title/authors/version header inspected. S2 batch lookup retried this round and returned HTTP429; saved parent `s2-batch-error.txt`, actual request in global search_log.jsonl. Failure is not evidence of a nonexistent paper.

## Sections actually inspected
`blocks.txt` lines 87–229: title/metadata, introduction; §§2.1–2.3; §§3.1–3.3. Relevant exact text:
- §2.1, line135 explicitly adopts MAR as probability of missingness depending only on observed values, not missing values.
- §2.2, lines143–147 already formulates shared arbitrary conditional distributions, heuristic target/context splitting, and a training-to-imputation generalization caveat.
- §3.1, lines177–183 describes zero padding, missing-coordinate flow, auxiliary mask input and architecture choice.
- **§3.2 line201: “An effective strategy should closely align with the true missingness mechanism to help the model prioritise learning the most important conditional distributions.”** Lines205/209 define Random and Random-Historical strategies; the latter already mixes random splitting with real missingness-pattern intersections.
- §3.3 lines227–229 explicitly acknowledges generalization gaps in conditioning/target dimensionality and reports robustness in the paper's evaluations.

## Decision / limits
This is stronger nearest-answer evidence against C than merely 'arbitrary-mask FM exists': aligning train masks to intended observations and finite-capacity allocation are ALREADY explicit premises in CFMI. Therefore no claim that our random-versus-local-reveal question discovers mask matching or its relevance. The only defensible residual is a bounded 2D-grid replication: an actually trained CFM, fixed target observation population and joint-distribution scorer against an exact finite prior. Complete-map supervision in the proposed grid study differs from CFMI's incomplete-data emphasis, but does not prove a gap or create novelty by itself. The paper does not establish a result for Alejandro's actual simulator; its API has not been located in the supplied reference repository. First-hit rays are optional stipulated algorithmic reveal rules, not physical sensor constraints.

Our derivation that deterministic noiseless first-hit rays can be ignorable given their revealed record is an investigator inference, not a quoted CFMI theorem. Likewise the kernel/tolerance defect identified in `../analytic-instrument-audit.md` is our analytic critique of a proposed packet, not a result reported here. No code, evaluator, training or experiment was executed.
