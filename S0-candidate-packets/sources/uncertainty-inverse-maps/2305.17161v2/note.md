# Flow Matching for Scalable Simulation-Based Inference

Verified metadata: Flow Matching for Scalable Simulation-Based Inference
Authors (arXiv citation format): Dax, Maximilian; Wildberger, Jonas; Buchholz, Simon; Green, Stephen R.; Macke, Jakob H.; Schölkopf, Bernhard
Persistent identifier/version read: arXiv:2305.17161v2
Version history visible on fetched page: Fri, 26 May 2023 18:00:01 UTC (3,856 KB); Fri, 27 Oct 2023 12:37:54 UTC (4,701 KB)
Retrieved: 2026-11-16 CST (actual UTC timestamps in scout search_log.jsonl).
Metadata: https://arxiv.org/abs/2305.17161v2
Full text: https://arxiv.org/html/2305.17161v2
Saved full HTML: ../inverse/2305.17161v2-full.raw
Readable extracted text: ../inverse/2305.17161v2.paragraphs.txt and ../inverse/2305.17161v2.txt

## Full-text-supported observations and limits

Inspected full text §§2–5, §3.1 probability mass coverage, Appendix benchmark/calibration results, and implementation links (paragraphs 29, 66–111, 125, 418). FMPE regresses a conditional velocity on joint simulator parameter-observation draws; posterior inference is amortized and stochastic through the initial reference draw. Ten SBI tasks and gravitational-wave inference establish feasibility of posterior CFM, not map calibration. §3.1 explicitly says mass coverage does NOT imply conservative posteriors and some regions may still be undersampled. Regularity assumptions for mass-coverage theorem are not guaranteed for neural parameterizations. P–P plots and distributional comparisons are useful precedents, not a guarantee under new masks/noise or robotic domain shift.
Code: https://github.com/dingo-gw/flow-matching-posterior-estimation verified via GitHub API 200; MIT in returned metadata; README retrieved. No installation or benchmark execution. Not an occupancy evaluator. This is an essential method seed for both drafts. Scholarly resolution: S2 429; exact-title OpenAlex match W7133217679 (conference DOI 10.52202/075280-0737 returned, not independently publisher-verified) and duplicate W7222387233; use arXiv ID to avoid silently merging records.

Status: source note from actual full-text sections, not an abstract-only lead. No empirical reproduction performed. Claim of no metric means not found in inspected protocol, not a proof about all later versions. Paper distribution license does not automatically license software/data.

## Final identifier resolution checkpoint
{
  "database": "OpenAlex",
  "id": "https://openalex.org/W7133217679",
  "title": "Flow Matching for Scalable Simulation-Based Inference",
  "doi_returned": "https://doi.org/10.52202/075280-0737",
  "raw": "/home/sircordero/research/s0-overnight-2026-11-16/sources/uncertainty-inverse-maps/inverse/openalex-fmpe.raw",
  "match": "exact title after case normalization; primary arXiv metadata independently retrieved",
  "S2": "429 for this seed; not a nonexistent-paper result"
}
This database metadata match is not execution of the reference repository citation graph resolver, which was not run.
