# Flow Matching Ergodic Coverage

Authors (verbatim arXiv metadata): Sun, Max Muchen; Pinosky, Allison; Murphey, Todd
Identifier/version inspected: arXiv:2504.17872v1
URL: https://arxiv.org/abs/2504.17872v1
Full text URL fetched: https://arxiv.org/pdf/2504.17872 (version established from PDF watermark or arXiv metadata query).
Retrieval date: 2026-11-16 CST.
Local full text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/ergodic/paper.pdf
Extracted text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/ergodic/fulltext.txt
Metadata: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/ergodic/metadata.json
Sections/pages inspected: pp. 4–6 derivation, p. 12–13 limitations/hardware; project/code README. Selective reading is not a claim of auditing every appendix.

## Full-text-backed claims
- Sec. III / pp. 4–6 distinguishes physical system time from outer flow time. The empirical trajectory distribution is matched to a reference probability flow under dynamics through a linear-quadratic subproblem; Algorithm 1 repeatedly simulates trajectory and updates control sequence.
- p. 6 Fig. 2 notes kernel bandwidth can cause mode collapse or under-exploration. Choice of flow geometry affects reachable modes, not just image quality.
- pp. 12–13 limitations: long-horizon trajectory optimization is not a guaranteed closed-loop MPC version for Stein/Sinkhorn flows; score estimation from sparse target samples and disconnected targets cause problems, and iteration/step sizes require tuning.
- Project links https://github.com/MurpheyLab/flow-ergodic-coverage (GPL-3.0), with JAX/lqrax/ott notebooks for point-mass, differential-drive and aircraft coverage. Repository and README verified but not installed/run.

## Limitations and relationship to proposed question
A qualitatively distinct family: distributional trajectory coverage, not posterior map completion or a learned anchor policy. Useful possible higher-risk RQ: when does faster density matching fail to reduce hidden-map uncertainty under changing occlusion geometry? Not promoted to full packet because deciding target information density creates a second inference problem and published dynamic replanning work needs deeper resolution. Mapping a prescribed density is not itself discovering an unknown environment. DOI 10.15607/RSS.2025.XXI.051 resolved in OpenAlex.

## Resolution status
Official arXiv abstract/PDF and identifier-list API resolved this title/version. Raw API query is sources/robotic-mapping/search-responses/arxiv-id-resolution.txt. For prospective packet seeds, Semantic Scholar identifier lookup was attempted and returned HTTP 429; see search_log.jsonl and s2-ID.txt responses. OpenAlex resolution is independently logged, but is not a substitute for a successful S1 Semantic Scholar traversal. No local experiments or paper result replications were performed.
