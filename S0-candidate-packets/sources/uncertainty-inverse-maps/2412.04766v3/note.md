# DAWN-FM: Data-Aware and Noise-Informed Flow Matching for Solving Inverse Problems

Verified metadata: DAWN-FM: Data-Aware and Noise-Informed Flow Matching for Solving Inverse Problems
Authors (arXiv citation format): Ahamed, Shadab; Haber, Eldad
Persistent identifier/version read: arXiv:2412.04766v3
Version history visible on fetched page: Fri, 6 Dec 2024 04:18:49 UTC (31,455 KB); Wed, 12 Mar 2025 17:30:41 UTC (33,025 KB); Sat, 28 Feb 2026 16:18:14 UTC (22,304 KB)
Retrieved: 2026-11-16 CST (actual UTC timestamps in scout search_log.jsonl).
Metadata: https://arxiv.org/abs/2412.04766v3
Full text: https://arxiv.org/html/2412.04766v3
Saved full HTML: ../inverse/2412.04766v3-full.raw
Readable extracted text: ../inverse/2412.04766v3.paragraphs.txt and ../inverse/2412.04766v3.txt

## Full-text-supported observations and limits

Inspected §§1–3 method, §numerical experiments and implementation (§§6–9 in full text; paragraphs 6, 99, 156–158, 228–242, 335). DAWN-FM explicitly embeds measured data and known noise scale in velocity network; DAW-FM ablates noise embedding. Image deblurring MNIST/STL10/CIFAR10 and tomography MedMNIST. Gaussian noise is injected with magnitude sampled over 0–20% data range; noise-aware method generally more robust at higher noise, with crossover reported around <=5% and exceptions such as CIFAR10 at stated noise. Training uses an A6000 48GB: not assumed available. Multiple generated images enable UQ in author framing, but inspected evaluation emphasizes reconstruction/misfit rather than calibrated voxel/path probabilities. Do not claim adding a noise channel is new.
Official https://github.com/ahxmeds/DAWN-FM verified API 200 and MIT metadata; paper both advertises URL and has older upon-acceptance release text. Repository existence is now verified, runnable evaluator not. S2 429. Essential noise-aware comparator for draft A, not a claim of inventing noise conditioning.

Status: source note from actual full-text sections, not an abstract-only lead. No empirical reproduction performed. Claim of no metric means not found in inspected protocol, not a proof about all later versions. Paper distribution license does not automatically license software/data.

## Final identifier resolution checkpoint
{
  "database": "OpenAlex",
  "id": "https://openalex.org/W4405173541",
  "title": "DAWN-FM: Data-aware and noise-informed flow matching for solving inverse problems",
  "doi_returned": "https://doi.org/10.3934/fods.2026005",
  "raw": "/home/sircordero/research/s0-overnight-2026-11-16/sources/uncertainty-inverse-maps/inverse/openalex-2412.04766v3.raw",
  "match": "exact title after case normalization; primary arXiv metadata independently retrieved",
  "S2": "429 for this seed; not a nonexistent-paper result"
}
This database metadata match is not execution of the reference repository citation graph resolver, which was not run.
