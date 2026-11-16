# Synthesis evidence check 001: fusion is a heuristic, and clamping is essential counterevidence

Retrieval date: 2026-11-16 CST. Full-text inspection, not replication. No research experiments run.

## OctoMap
Exact title: **OctoMap: an efficient probabilistic 3D mapping framework based on octrees**.
Authors: Armin Hornung; Kai M. Wurm; Maren Bennewitz; Cyrill Stachniss; Wolfram Burgard. Year 2013. DOI **10.1007/s10514-012-9321-0**. Metadata verified by Crossref exact-title query, saved `crossref-octomap.raw` (first result); official project https://octomap.github.io/ links author-hosted full text https://www.arminhornung.de/Research/pub/hornung13auro.pdf . Saved `octomap.pdf` and `octomap-fulltext.txt` (17 pages). Read pp. 4–6, Sec. 3.2, and pp. 8–9 sensor-integration details selectively. PDF extraction issued a missing-fontTools warning; prose used here is legible, equations should be checked against PDF before implementation.

Supported claims:
- Sec. 3.2 p. 5 Eqs. 1–3 specify occupancy update, uniform-prior log-odds accumulation and symmetric hit/miss counting interpretation.
- pp. 5–6 explicitly explain that unbounded accumulation can require as many contrary observations as previous supporting observations to flip a cell; Eq. 4 CLAMPS log odds to bound confidence and permit faster adaptation.
- Sec. 3.4 p. 6 notes that for some navigation tasks a maximum-likelihood map is sufficient. Thus calibrated posterior probability is not the sole legitimate use of occupancy scores.
- The published occupancy update is a sensor-fusion operator. This paper does NOT empirically study learned map-sample fusion and does NOT establish a newly discovered error in SceneSense.

Important counterevidence: do not attack an unclamped caricature of a deployed OctoMap implementation. The candidate must include clamped accumulation, symmetric/asymmetric sensor weights and deployment-intended thresholded utility. Clamping bounds confidence but is not by itself a proof that learned sample frequency becomes correct map posterior probability. Whether published SceneSense configurations inherit which OctoMap clamp values is NOT verified by this reading; code/config audit remains open. No assertion of unbounded deployed drift is justified.

## SceneSense journal extension, independent direct reinspection
Exact title: **Robust Robotic Exploration and Mapping Using Generative Occupancy Map Synthesis**.
Authors: Lorin Achey; Alec Reed; Brendan Crowe; Bradley Hayes; Christoffer Heckman. arXiv **2506.20049v2**, DOI **10.1007/s10514-025-10229-0** (publisher DOI from scout's verified metadata, not newly resolved here). Full text re-fetched https://arxiv.org/html/2506.20049v2; saved `scenesense.raw` and `scenesense.txt`; original page-marked PDF extraction also inspected at `../robotic-mapping/scenesense/fulltext.txt`, pp. 8–10 / Secs. 5.4, 6, 7 (lines 660–830).

Supported claims:
- Fig. 4: various maps from equivalent input are fused via Eq. 7.
- Sec. 6 explicitly criticizes replacement because it can cause oscillatory trajectory shifts; persistent merging is a deliberate engineering tradeoff, not carelessness.
- Eq. 7 combines previous occupancy with a generated or sensed update; generated occupied-cell confidence can be lower than sensor confidence; observed and predicted regions are distinguished.
- Sec. 7 evaluates IoU/FID/KID, not a conditional posterior calibration score.

Candidate implication: compare fusion with a **sample-mean replacement AND a provenance-separated temporally smoothed replacement**. Otherwise any utility gain from persistence is confounded with repeated-evidence accounting. Frozen-evidence posterior invariance is an analytic sanity check, not a sufficient research contribution. The scientifically useful question is the regime-dependent calibration / stability / correction tradeoff after new actual sensor evidence, under controlled map ambiguity and predictor error. Do not equate diffusion results with CFM results; apply operators to the same CFM samples only in a later approved study.

## Retrieval / seed traversal status
The guessed project PDF URL https://octomap.github.io/octomap.pdf returned 404; recovered via project page, not treated as absence. Semantic Scholar lookup of arXiv:2506.20049 returned HTTP 429; saved `s2-scenesense.raw`. Crossref successfully resolves the OctoMap DOI/title/authors. Full S1 citation traversal has not been performed; rate limiting is not a nonexistent paper. Requests and outcomes appended to global `search_log.jsonl`.

**Later same-round resolution addendum:** the POST batch endpoint `https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,authors,year,externalIds` successfully resolved all seven distinct initial packet seeds, including SceneSense paperId `82d100a979fc0c2bd548d36f58f0439651fe9721` and OctoMap paperId `92f66d26dc52d4b9bde8684520a3dddfb3bd8d36`. Raw response saved `s2-seeds-batch.raw`. OpenAlex exact-title matches also succeeded for all seven. This supersedes unresolved individual lookup status for those initial seeds, but is not a completed S1 graph traversal.
