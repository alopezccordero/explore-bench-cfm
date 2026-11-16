# All Roads Lead to Rome: Flow-driven Multi-Anchor Exploration for Open-Environment Active 3D Mapping

Authors (verbatim arXiv metadata): Li, Yang; Wu, Aming; Zhang, Zihao; Han, Ziju; Zhang, Sijia; Han, Yahong
Identifier/version inspected: arXiv:2609.36889v2
URL: https://arxiv.org/abs/2609.36889v2
Full text URL fetched: https://arxiv.org/pdf/2609.36889 (version established from PDF watermark or arXiv metadata query).
Retrieval date: 2026-11-16 CST.
Local full text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/rome/paper.pdf
Extracted text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/rome/fulltext.txt
Metadata: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/rome/metadata.json
Sections/pages inspected: pp. 1–10 (Secs. 1–5), pp. 12–14 checklist. Selective reading is not a claim of auditing every appendix.

## Full-text-backed claims
- Sec. 3.2 / pp. 3–5 defines a 4D goal anchor (x,y,sin theta,cos theta), Gaussian-to-oracle-anchor CFM with linear interpolation and velocity regression, then samples K anchors. This is anchor generation, NOT a calibrated posterior over complete maps.
- Secs. 3.3–3.4 / pp. 5–7 add A* planning, path clustering including topological distance, and learned hierarchical scoring. Thus a gain over deterministic regression is not by itself an isolated test of CFM or of posterior uncertainty.
- Sec. 4 / pp. 7–9 reports AiMDoom and MP3D, matched initial poses, five trajectories per scene, difficulty and cross-dataset shifts. Reported gains are authors’ claims, not replicated here.
- p. 10 limitations explicitly identify coarse anchors versus full-map reasoning, errors in predicted obstacle maps and downstream mode construction.
- pp. 12–14 checklist says full proofs are omitted, extended hyperparameters absent, and code will be released upon acceptance. A GitHub identifier search returned no repository; this is not proof no code exists.

## Limitations and relationship to proposed question
Strongest direct competitor to generic CFM exploration generalization. Reject that generic RQ. Distinguish proposed topology-query study by holding one map sampler/frontier set fixed and changing only the decision functional, with exact posterior controls and graph ambiguity manipulation. No evidence here establishes a calibrated Bayesian map distribution or an isolated causal benefit of multimodality under equal proposal/reranking compute. The PDF labels NeurIPS 2026; conference acceptance was not independently verified and must not be inferred from its header.

## Resolution status
Official arXiv abstract/PDF and identifier-list API resolved this title/version. Raw API query is sources/robotic-mapping/search-responses/arxiv-id-resolution.txt. For prospective packet seeds, Semantic Scholar identifier lookup was attempted and returned HTTP 429; see search_log.jsonl and s2-ID.txt responses. OpenAlex resolution is independently logged, but is not a substitute for a successful S1 Semantic Scholar traversal. No local experiments or paper result replications were performed.
