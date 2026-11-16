# Ergodic Trajectory Design by Learned Pushforward Maps: Provable Coverage via Conditional Flow Matching

Authors (verbatim arXiv metadata): Aghazadeh, Ehsan; Malekzadeh, Masoud; Ghasemi, Ahmad; Pishro-Nik, Hossein
Identifier/version inspected: arXiv:2605.13063v1
URL: https://arxiv.org/abs/2605.13063v1
Full text URL fetched: https://arxiv.org/pdf/2605.13063 (version established from PDF watermark or arXiv metadata query).
Retrieval date: 2026-11-16 CST.
Local full text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/pushforward/paper.pdf
Extracted text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/pushforward/fulltext.txt
Metadata: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/pushforward/metadata.json
Sections/pages inspected: pp. 1–8; Sec. 2.2 Remark 1, Sec. 3 assumptions and error floor, Sec. 4. Selective reading is not a claim of auditing every appendix.

## Full-text-backed claims
- Sec. 2 / pp. 2–4 constructs annular latent ergodic trajectories then learns an OT-CFM spatial pushforward for a fixed prescribed target. Reuse is across trajectories/agents for a given density and constraints, not free adaptation to a new posterior.
- p. 3 distinguishes a measurable pushforward existence statement from a smooth learned ODE diffeomorphism, and explicitly introduces topology residuals when support cannot be exactly matched.
- pp. 5–6 error bounds require stated Lipschitz/smoothness assumptions and include approximation/topology floors. Architectural bounds can be much looser than empirical diagnostics. No general Bayesian posterior-calibration theorem follows.
- pp. 7–8 compares target-coverage/energy/no-fly metrics on Milano data, with warnings that zero violation can accompany degenerate coverage. Reported performance is not independently replicated.
- Only main theory/setup/experiments inspected; 55-page appendix not exhaustively audited. No code/data license independently cleared.

## Limitations and relationship to proposed question
Near competitor for fixed-density amortization and topology-support limits, not a direct answer to active unknown-map sensing. Avoid asserting a new theorem merely from connectedness of supports; finite-precision thresholded occupancy and discontinuous observation operators change the question. Interesting higher-risk family, but not an undergraduate-safe primary compared to finite-map mechanisms.

## Resolution status
Official arXiv abstract/PDF and identifier-list API resolved this title/version. Raw API query is sources/robotic-mapping/search-responses/arxiv-id-resolution.txt. For prospective packet seeds, Semantic Scholar identifier lookup was attempted and returned HTTP 429; see search_log.jsonl and s2-ID.txt responses. OpenAlex resolution is independently logged, but is not a substitute for a successful S1 Semantic Scholar traversal. No local experiments or paper result replications were performed.
