# Flow Matching for Atmospheric Retrieval of Exoplanets: Where Reliability meets Adaptive Noise Levels

Verified metadata: Flow Matching for Atmospheric Retrieval of Exoplanets: Where Reliability meets Adaptive Noise Levels
Authors (arXiv citation format): Gebhard, Timothy D.; Wildberger, Jonas; Dax, Maximilian; Kofler, Annalena; Angerhausen, Daniel; Quanz, Sascha P.; Schölkopf, Bernhard
Persistent identifier/version read: arXiv:2410.21477v1
Version history visible on fetched page: Mon, 28 Oct 2024 19:28:07 UTC (5,722 KB)
Retrieved: 2026-11-16 CST (actual UTC timestamps in scout search_log.jsonl).
Metadata: https://arxiv.org/abs/2410.21477v1
Full text: https://arxiv.org/html/2410.21477v1
Saved full HTML: ../inverse/2410.21477v1-full.raw
Readable extracted text: ../inverse/2410.21477v1.paragraphs.txt and ../inverse/2410.21477v1.txt

## Full-text-supported observations and limits

Inspected §§2.3, 3, 4, 6; noise-level conditioning, importance sampling, calibration/reliability discussion (paragraphs 202–217, 288–346 and full-text lines around 2981–3343). Model conditions on observation AND assumed noise scale and can vary scale without retraining. Importance weights require a tractable likelihood and mass-covering proposal; their effective sample efficiency is a per-observation reliability diagnostic, unlike aggregate coverage alone. Dataset is simulated exoplanet spectra, not robotic maps. Training uses 33,554,432 spectra plus 1,048,576 validation spectra: do not copy resource envelope to undergraduate minimum. Noise-aware FM is already established; a question merely asking whether conditioning on noise helps is not new. Scope extension must be structured visibility masks and explicit noisy-map boundary conditions.
Code: https://github.com/timothygebhard/fm4ar verified API 200, BSD-3-Clause metadata; README retrieved. Dataset and simulator dependencies separately licensed, not audited. S2 429; arXiv metadata DOI 10.1051/0004-6361/202451861 verified as provided metadata, not independent publisher fetch.

Status: source note from actual full-text sections, not an abstract-only lead. No empirical reproduction performed. Claim of no metric means not found in inspected protocol, not a proof about all later versions. Paper distribution license does not automatically license software/data.
