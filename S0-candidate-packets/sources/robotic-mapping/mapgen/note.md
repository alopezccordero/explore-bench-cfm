# Map Prediction and Generative Entropy for Multi-Agent Exploration

Authors (verbatim arXiv metadata): Spinos, Alexander; Woosley, Bradley; Rokisky, Justin; Korpela, Christopher; Rogers III, John G.; Bittner, Brian A.
Identifier/version inspected: arXiv:2501.13189v1
URL: https://arxiv.org/abs/2501.13189v1
Full text URL fetched: https://arxiv.org/pdf/2501.13189 (version established from PDF watermark or arXiv metadata query).
Retrieval date: 2026-11-16 CST.
Local full text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/mapgen/paper.pdf
Extracted text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/mapgen/fulltext.txt
Metadata: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/mapgen/metadata.json
Sections/pages inspected: pp. 1–6, especially III-B/C, V, VI-A. Selective reading is not a claim of auditing every appendix.

## Full-text-backed claims
- Sec. III / pp. 3–4 converts 200x200 occupancy maps to image inpainting. Stable Diffusion, RePaint and LaMa are compared. Observation-shaped masks materially affect Stable Diffusion performance; changing masks is not automatically a pure scene shift.
- p. 4 describes procedural town maps with a main street and rectangular/L/C-shaped buildings, 2000 training maps and 2000 test maps. This narrow grammar does not establish general indoor topology performance.
- Sec. V / p. 5 explicitly treats each predicted map as a noisy observation updating per-cell posterior confidence, with saturation. The entropy is temporal generative variation, not a demonstrated calibrated conditional posterior.
- Sec. VI / pp. 5–6 uses three robots, 10 trials per setting and map prediction every 2.5s. Generative entropy improves predicted-map accuracy convergence but is worse for physical cells uncovered than even constant task reward. This is valuable published evidence of objective-dependent reversal.
- p. 6 notes roughly 90% map accuracy before observation because most space is empty. Cell accuracy is therefore a poor sole primary metric for narrow critical connectivity.

## Limitations and relationship to proposed question
Supports both candidates: uncertainty aggregation can reverse coverage rankings, and temporal predictions can be fused as evidence. Do NOT say the paper proved overconfidence: it did not measure calibration under frozen observations. The resampling-vs-evidence RQ tests that possible failure explicitly, distinguishing Monte Carlo estimator precision from information about the world. No public runnable release of its exact simulator was verified in this scout.

## Resolution status
Official arXiv abstract/PDF and identifier-list API resolved this title/version. Raw API query is sources/robotic-mapping/search-responses/arxiv-id-resolution.txt. For prospective packet seeds, Semantic Scholar identifier lookup was attempted and returned HTTP 429; see search_log.jsonl and s2-ID.txt responses. OpenAlex resolution is independently logged, but is not a substitute for a successful S1 Semantic Scholar traversal. No local experiments or paper result replications were performed.
