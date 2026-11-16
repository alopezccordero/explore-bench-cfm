# Flow Matching with Missing Data

Verified metadata: Flow Matching with Missing Data
Authors (arXiv citation format): Khan, Fairoz Nower; Nahim, Nabuat Zaman; Ju, Peizhong
Persistent identifier/version read: arXiv:2607.28698v3
Version history visible on fetched page: Thu, 30 Jul 2026 10:37:01 UTC (150 KB); Mon, 12 Oct 2026 06:33:52 UTC (179 KB); Thu, 15 Oct 2026 01:11:35 UTC (179 KB)
Retrieved: 2026-11-16 CST (actual UTC timestamps in scout search_log.jsonl).
Metadata: https://arxiv.org/abs/2607.28698v3
Full text: https://arxiv.org/html/2607.28698v3
Saved full HTML: ../inverse/2607.28698v3-full.raw
Readable extracted text: ../inverse/2607.28698v3.paragraphs.txt and ../inverse/2607.28698v3.txt

## Full-text-supported observations and limits

Inspected §§1–4, §6 experiment text, §7 and appendix implementation pointers (paragraphs 5–99, 136–229, 376–469; appendix text at 1607 and 1769). The setting is missing TRAINING endpoints, not merely incomplete inference observations. Oracle pattern-conditioned stochastic completion exactly recovers complete-data FM objective under arbitrary missingness; identifying that law is the issue. Under MAR/MCAR ordinary complete-data conditional suffices under stated assumptions; MNAR requires mechanism information/additional assumptions. Naive MAR self-supervision can be selection-biased. Fixed-parameter loss-variance result says one completion per observation is optimal under fixed evaluation budget; do not confuse with optimal SGD training or posterior sample count.
§6 tests deterministic versus stochastic completions and seven UCI datasets at five MCAR rates. Crucial correction: frozen STOCHASTIC imputation can preserve spread; deterministic conditional-mean imputation is the collapse risk. No robotic visibility or downstream path-risk benchmark demonstrated. Real-data comparisons chiefly generation/imputation, not proof of map calibration under MNAR. No official code URL in inspected HTML links. S2 429. Essential premise seed for missingness controls, but draft deliberately has complete synthetic training maps to avoid conflating two problems.

Status: source note from actual full-text sections, not an abstract-only lead. No empirical reproduction performed. Claim of no metric means not found in inspected protocol, not a proof about all later versions. Paper distribution license does not automatically license software/data.

## Final identifier resolution checkpoint
{
  "database": "OpenAlex",
  "id": "https://openalex.org/W7172336041",
  "title": "Flow Matching with Missing Data",
  "doi_returned": "https://doi.org/10.48550/arxiv.2607.28698",
  "raw": "/home/sircordero/research/s0-overnight-2026-11-16/sources/uncertainty-inverse-maps/inverse/openalex-2607.28698v3.raw",
  "match": "exact title after case normalization; primary arXiv metadata independently retrieved",
  "S2": "429 for this seed; not a nonexistent-paper result"
}
This database metadata match is not execution of the reference repository citation graph resolver, which was not run.
