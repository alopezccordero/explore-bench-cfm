# Flow Matching for Generative Modeling

Authors (verbatim arXiv metadata): Lipman, Yaron; Chen, Ricky T. Q.; Ben-Hamu, Heli; Nickel, Maximilian; Le, Matt
Identifier/version inspected: arXiv:2210.02747v2
URL: https://arxiv.org/abs/2210.02747v2
Full text URL fetched: https://arxiv.org/pdf/2210.02747 (version established from PDF watermark or arXiv metadata query).
Retrieval date: 2026-11-16 CST.
Local full text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/flowmatching/paper.pdf
Extracted text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/flowmatching/fulltext.txt
Metadata: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/flowmatching/metadata.json
Sections/pages inspected: pp. 1–5 and p. 7; Secs. 2–4 / Theorem 2. Selective reading is not a claim of auditing every appendix.

## Full-text-backed claims
- Sec. 2 / p. 2 defines ODE-generated continuous normalizing flows and pushforward densities.
- Sec. 3.2 / p. 4 Theorem 2 states that conditional and marginal flow-matching objectives have identical gradients under stated positive-density assumptions.
- Sec. 4 describes Gaussian conditional paths; terminal samples approximate a data distribution rather than guaranteeing an exactly discrete map distribution.
- p. 7 compares generative compute/quality; no robot sensor likelihood, map topology or posterior calibration is tested.

## Limitations and relationship to proposed question
Essential method premise for CFM as a conditional joint map/door-configuration sampler. Here conditioning on physical observations is an additional designed variable, not something automatically provided by the word “conditional” in the theorem (which originally conditions per target data example). Dequantization/thresholding and finite sample/ODE budgets require validation. This seed supports the instrument, not a claim that CFM beats diffusion for the proposed RQs.

## Resolution status
Official arXiv abstract/PDF and identifier-list API resolved this title/version. Raw API query is sources/robotic-mapping/search-responses/arxiv-id-resolution.txt. For prospective packet seeds, Semantic Scholar identifier lookup was attempted and returned HTTP 429; see search_log.jsonl and s2-ID.txt responses. OpenAlex resolution is independently logged, but is not a substitute for a successful S1 Semantic Scholar traversal. No local experiments or paper result replications were performed.
