# Separating Intrinsic Ambiguity from Estimation Uncertainty in Deep Generative Models for Linear Inverse Problems

Verified metadata: Separating Intrinsic Ambiguity from Estimation Uncertainty in Deep Generative Models for Linear Inverse Problems
Authors (arXiv citation format): Guo, Yuxin; Deng, Dongrui; Grover, Pulkit
Persistent identifier/version read: arXiv:2605.15050v1
Version history visible on fetched page: Thu, 14 May 2026 16:45:19 UTC (6,225 KB)
Retrieved: 2026-11-16 CST (actual UTC timestamps in scout search_log.jsonl).
Metadata: https://arxiv.org/abs/2605.15050v1
Full text: https://arxiv.org/html/2605.15050v1
Saved full HTML: ../inverse/2605.15050v1-full.raw
Readable extracted text: ../inverse/2605.15050v1.paragraphs.txt and ../inverse/2605.15050v1.txt

## Full-text-supported observations and limits

Inspected §§1–5 and calibration diagnostics (paragraphs 14–22, 41–108, 116; §4.2). Separates intrinsic non-identifiability from noise-propagated variability using linear range/null decomposition. Cascade null generator conditioned on ORACLE identifiable component is used for calibration diagnosis, while end-to-end predictions condition on inferred component; these must not be compared as deployable information-equivalent pipelines. Gaussian analytic test, qualitative accelerated fastMRI and EEG source inverse problem. SBC over scalar summaries is explicitly necessary, not sufficient, for correct posterior. Similar reconstruction correlations can coexist with different null-space SBC failures.
No directly verified code repository. MRI data access/terms not audited. Not a robotic occupancy mask theorem: visibility is nonlinear and depends on obstacles. Supports separating sources of statistical uncertainty; does NOT justify calling model disagreement epistemic uncertainty or calling all generated variance calibrated ambiguity.

Status: source note from actual full-text sections, not an abstract-only lead. No empirical reproduction performed. Claim of no metric means not found in inspected protocol, not a proof about all later versions. Paper distribution license does not automatically license software/data.
