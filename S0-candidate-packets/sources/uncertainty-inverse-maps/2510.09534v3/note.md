# Conditional Flow Matching for Bayesian Posterior Inference

Verified metadata: Conditional Flow Matching for Bayesian Posterior Inference
Authors (arXiv citation format): Zhai, Percy S.; Jeong, So Won; Ročková, Veronika
Persistent identifier/version read: arXiv:2510.09534v3
Version history visible on fetched page: Fri, 10 Oct 2025 16:48:28 UTC (1,372 KB); Wed, 15 Oct 2025 14:51:36 UTC (1,372 KB); Wed, 1 Apr 2026 00:14:49 UTC (1,395 KB)
Retrieved: 2026-11-16 CST (actual UTC timestamps in scout search_log.jsonl).
Metadata: https://arxiv.org/abs/2510.09534v3
Full text: https://arxiv.org/html/2510.09534v3
Saved full HTML: ../inverse/2510.09534v3-full.raw
Readable extracted text: ../inverse/2510.09534v3.paragraphs.txt and ../inverse/2510.09534v3.txt

## Full-text-supported observations and limits

Inspected §§1, 3–5, Appendix E.4 coverage experiment and computation paragraph (paragraphs 308–416, 917–924, 975–979). Learns block-triangular joint velocity, yielding conditional transport; extra monotonicity assumptions produce conditional Brenier transport and nested credible sets. Figure 3/Appendix coverage example is Gaussian conjugate, 100 independent observations, checking posterior mass of sets; do not generalize this to exact conditional frequentist coverage in high-dimensional maps. Text notes high observation dimensionality, multimodality and heavy-tail difficulties. Authors report CPU experiments, not GPU dependency; this does not establish speed on maps.
Official code https://github.com/sowonjeong/flow-posterior API 200 (small repository, license null). No license permission established; implementation not run. S2 429. This blocks a broad claim that flow posterior credible sets/calibration have not been studied; map-level and decision-event reliability remain separate empirical targets.

Status: source note from actual full-text sections, not an abstract-only lead. No empirical reproduction performed. Claim of no metric means not found in inspected protocol, not a proof about all later versions. Paper distribution license does not automatically license software/data.
