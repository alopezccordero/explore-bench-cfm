# Flow Matching Posterior Sampling: A Training-free Conditional Generation for Flow Matching

Verified metadata: Flow Matching Posterior Sampling: A Training-free Conditional Generation for Flow Matching
Authors (arXiv citation format): Song, Kaiyu; Lai, Hanjiang; Pan, Yan; Yue, Kun; yin, Jian
Persistent identifier/version read: arXiv:2411.07625v3
Version history visible on fetched page: Tue, 12 Nov 2024 08:14:39 UTC (6,467 KB); Mon, 14 Jul 2025 03:46:26 UTC (2,554 KB); Sat, 9 Aug 2025 08:22:53 UTC (2,067 KB)
Retrieved: 2026-11-16 CST (actual UTC timestamps in scout search_log.jsonl).
Metadata: https://arxiv.org/abs/2411.07625v3
Full text: https://arxiv.org/html/2411.07625v3
Saved full HTML: ../inverse/2411.07625v3-full.raw
Readable extracted text: ../inverse/2411.07625v3.paragraphs.txt and ../inverse/2411.07625v3.txt

## Full-text-supported observations and limits

Inspected §§1–4, §5.1–5.4, §6 (paragraphs 5–100, 208–258). FMPS introduces velocity correction with a surrogate score and gradient-aware/gradient-free variants to use pretrained unconditional flow priors for conditional generation. Images: box inpainting, super-resolution, deblurring, segmentation/sketch/identity guidance, text/style. §5 metrics are SSIM, LPIPS, FID, condition distance, KID, CLIP and Gram style; no reported posterior coverage or event calibration in inspected experiment protocol. 100 sampling steps and one RTX4090 stated. Better image generation metrics do not validate a map posterior. §6 notes seed-dependent failures and color deviations. A method named posterior sampling is not thereby an empirically calibrated posterior sampler.
No official code URL identified in inspected HTML links; code status unverified, not nonexistent. Not selected as seed because it is closer to restoration guidance than a matched simulator posterior. Strong methodological competitor for training-free conditioning, not a fair drop-in benchmark of noise-conditioned amortization.

Status: source note from actual full-text sections, not an abstract-only lead. No empirical reproduction performed. Claim of no metric means not found in inspected protocol, not a proof about all later versions. Paper distribution license does not automatically license software/data.
