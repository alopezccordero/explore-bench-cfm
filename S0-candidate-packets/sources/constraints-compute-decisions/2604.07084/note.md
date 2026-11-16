# Flow Motion Policy: Manipulator Motion Planning with Flow Matching Models

Authors: Davood Soleymanzadeh; Xiao Liang; Minghui Zheng
First-posted year: 2026; inspected version: 2604.07084v2.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2604.07084v2
Persistent ID: arXiv:2604.07084; https://arxiv.org/abs/2604.07084v2
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/planning-agent/2604.07084-fulltext.txt
Database resolution: OpenAlex resolved https://openalex.org/W7152398954; Semantic Scholar HTTP 429 (rate limit, not absence). OpenAlex metadata title checked; authors normalized to full text. Database publication year may differ from first-posted year.

## Full-text-backed reading note and boundaries

Flow Motion Policy — strongest direct steps-versus-samples competitor

Exact title: Flow Motion Policy: Manipulator Motion Planning with Flow Matching Models
Authors: Davood Soleymanzadeh; Xiao Liang; Minghui Zheng.
Read version: arXiv:2604.07084v2, 15 Aug 2026.
Identifiers: https://arxiv.org/abs/2604.07084v2 ; https://doi.org/10.48550/arXiv.2604.07084 (arXiv-issued DOI, not a claimed journal DOI).
Actual full text: https://arxiv.org/html/2604.07084v2
Saved: `2604.07084-fulltext.raw`, `2604.07084-fulltext.txt`; metadata `verify-5.raw/.txt`.

Verified mechanisms and evidence:
- Sec. III-C, Eqs. (7)–(8), Algorithm 3; local lines 155–186: samples N complete candidate paths, evaluates collision cost using minimum signed distance and a safety-distance threshold, and selects the first collision-free path. Real deployment uses robot SDF over environment representation; simulation uses cuRobo batched collision checking. The abstract's phrase 'without ... collision checker during motion planning' must NOT be read as 'no collision verification': the best-of-N variant explicitly checks candidates.
- Sec. IV, Table I caption, local line 543: principal comparisons use 20 flow steps, and distinguish FMP-1 from FMP-100.
- Sec. IV-C, Figs. 6, 8–13, local lines 877–890: NFE sweeps, sample-count ablations, and Euler-step sweeps are already present. Figs. 11 and 13 cover steps in [5,90], both without and with best-of-N sampling.
- Exact substantive conclusion, local line 890: 'Increasing the number of solver steps, with or without best-of-N sampling, provides little improvement in success rate but increases planning time.' Local line 889 states increasing samples improves success but increases generation/evaluation time. Thus 'more candidates beats more integration' is already an explicit reported observation, not an untouched hypothesis.
- Sec. III-C's collision cost is expressed as a sum over trajectory configurations. This is not, by itself, proof of continuous swept-volume safety between configurations. Do not claim the code has been audited for continuous collision handling; code is not released on the checked project page.

Code/evaluator availability:
- Verified project: https://davoodsz.github.io/FlowMotionPolicy.github.io/ (`project-2.raw/.txt`, HTTP 200).
- Its code and dataset links explicitly say 'Coming Soon'; no implementation URL is provided there. Do not make this a promised immediately reproducible baseline.

Disqualifies: novelty claims for best-of-N FM planning with post-generation collision selection; routine step-count/sample-count success-time sweeps. Does not establish a joint fixed-deadline verifier-fidelity scheduler in occupancy maps.



No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
