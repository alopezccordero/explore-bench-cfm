# MapEx: Indoor Structure Exploration with Probabilistic Information Gain from Global Map Predictions

Authors (verbatim arXiv metadata): Ho, Cherie; Kim, Seungchan; Moon, Brady; Parandekar, Aditya; Harutyunyan, Narek; Wang, Chen; Sycara, Katia; Best, Graeme; Scherer, Sebastian
Identifier/version inspected: arXiv:2409.15590v3
URL: https://arxiv.org/abs/2409.15590v3
Full text URL fetched: https://arxiv.org/pdf/2409.15590 (version established from PDF watermark or arXiv metadata query).
Retrieval date: 2026-11-16 CST.
Local full text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/mapex-original/paper.pdf
Extracted text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/mapex-original/fulltext.txt
Metadata: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/mapex-original/metadata.json
Sections/pages inspected: pp. 1–6, especially Sec. III, IV-A–D, V-A–F and Eq. 4. Selective reading is not a claim of auditing every appendix.

## Full-text-backed claims
- Sec. III / p. 2 assumes known robot poses and noise-free 360-degree LiDAR.
- Sec. IV / pp. 3–4 uses LaMa global map predictions, a three-network ensemble trained on subsets, pixel variance, a mean-map accumulated-occupancy raycast threshold (0.8), and sums variance in estimated visible unknown space. Frontier reward divides by distance. This is a practical proxy, not exact mutual information.
- Sec. V / pp. 4–5 describes KTH blueprints, 149 maps after deduplication, building-group train/test separation, 10 held-out floorplans with four starts, 1000 timesteps, 20m LiDAR and 2500 samples. These are paper protocol claims, not locally executed runs.
- pp. 5–6 Topological Understanding (TU) already tests downstream A* goal-reaching success, with failure for collision or no goal reach, across 100 random goals per map.
- p. 6 reports observed-map visibility is competitive; the paper itself motivates strong sensor-only baselines rather than only nearest-frontier comparisons.

## Limitations and relationship to proposed question
This is the strongest competitor for topology-aware exploration and establishes that neither multiple maps, visibility-weighted uncertainty nor measuring planning utility is an unoccupied gap. The candidate asks about expected information in connectivity queries and a controlled bottleneck-by-nuisance interaction, not “add topology.” Same sampler and same visibility/sensor model are required. Code/README retrieved from https://github.com/castacks/MapEx; root LICENSE is Clear BSD; source data and weights have separate unresolved licensing. README advertises explore.py and coverage/IoU evaluation; a turnkey TU/calibration evaluator was not established.

## Resolution status
Official arXiv abstract/PDF and identifier-list API resolved this title/version. Raw API query is sources/robotic-mapping/search-responses/arxiv-id-resolution.txt. For prospective packet seeds, Semantic Scholar identifier lookup was attempted and returned HTTP 429; see search_log.jsonl and s2-ID.txt responses. OpenAlex resolution is independently logged, but is not a substitute for a successful S1 Semantic Scholar traversal. No local experiments or paper result replications were performed.
