# Map Space Belief Prediction for Manipulation-Enhanced Mapping

Verified metadata: Map Space Belief Prediction for Manipulation-Enhanced Mapping
Authors (arXiv citation format): Marques, Joao Marcos Correia; Dengler, Nils; Zaenker, Tobias; Mucke, Jesper; Wang, Shenlong; Bennewitz, Maren; Hauser, Kris
Persistent identifier/version read: arXiv:2502.20606v3
Version history visible on fetched page: Fri, 28 Feb 2025 00:10:52 UTC (12,216 KB); Tue, 27 May 2025 05:37:31 UTC (19,619 KB); Wed, 18 Jun 2025 07:21:56 UTC (5,668 KB)
Retrieved: 2026-11-16 CST (actual UTC timestamps in scout search_log.jsonl).
Metadata: https://arxiv.org/abs/2502.20606v3
Full text: https://arxiv.org/html/2502.20606v3
Saved full HTML: ../inverse/2502.20606v3-full.raw
Readable extracted text: ../inverse/2502.20606v3.paragraphs.txt and ../inverse/2502.20606v3.txt

## Full-text-supported observations and limits

Inspected §§III–VI and Appendix CNABU accuracy/calibration experiment (paragraphs 114–178, 185–218, 299–334, 388–398). CNABU uses Beta occupancy/Dirichlet semantics evidential representation for learned belief propagation under viewpoint and manipulation actions. POMDP planner chooses observations or pushes for shelf mapping; simulation and real shelf transfer. §belief explicitly FACTORS cells independently, despite learned context-dependent updates capturing spatial priors. Appendix reports mIoU AND mean ECE across sequential observations; this is real calibration evaluation, not just diversity. Thus do NOT claim calibrated mapping itself is absent from prior work. mECE is not validation of joint map probability or path collision risk.
Real-world section reports depth/segmentation domain gap; high-quality segmentation and representative simulation ground truth are limitations. Privileged clairvoyant oracle appendix is a diagnostic bound, not fair deployable baseline.
Official https://github.com/NilsDengler/manipulation_enhanced_map_prediction verified API 200; license null, reuse permission unresolved. Data/checkpoint download and actual evaluator execution unverified. S2 429. Critical nearest uncertainty competitor for draft B, but not flow/diffusion generative maps.

Status: source note from actual full-text sections, not an abstract-only lead. No empirical reproduction performed. Claim of no metric means not found in inspected protocol, not a proof about all later versions. Paper distribution license does not automatically license software/data.

## Final identifier resolution checkpoint
{
  "database": "OpenAlex",
  "id": "https://openalex.org/W4417305590",
  "title": "Map Space Belief Prediction for Manipulation-Enhanced Mapping",
  "doi_returned": "https://doi.org/10.48550/arxiv.2502.20606",
  "raw": "/home/sircordero/research/s0-overnight-2026-11-16/sources/uncertainty-inverse-maps/inverse/openalex-2502.20606v3.raw",
  "match": "exact title after case normalization; primary arXiv metadata independently retrieved",
  "S2": "429 for this seed; not a nonexistent-paper result"
}
This database metadata match is not execution of the reference repository citation graph resolver, which was not run.
