# BridgeFlow: Fast and Robust SE(2)-Equivariant Motion Planning with Flow Matching

Authors: Xinzhe Zhou; Xuyang Wang; Xiaoming Duan; Jianping He
First-posted year: 2026; inspected version: 2607.14725v1.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2607.14725v1
Persistent ID: arXiv:2607.14725; https://arxiv.org/abs/2607.14725v1
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/planning-agent/2607.14725-fulltext.txt
Database resolution: OpenAlex resolved https://openalex.org/W7169628581; Semantic Scholar HTTP 429 (rate limit, not absence). OpenAlex metadata title checked; authors normalized to full text. Database publication year may differ from first-posted year.

## Full-text-backed reading note and boundaries

BridgeFlow — particularly close 2-D occupancy-map and few-step baseline

Exact title: BridgeFlow: Fast and Robust SE(2)-Equivariant Motion Planning with Flow Matching
Authors: Xinzhe Zhou; Xuyang Wang; Xiaoming Duan; Jianping He.
Read version: arXiv:2607.14725v1, 16 Jul 2026.
Identifiers: https://arxiv.org/abs/2607.14725v1 ; https://doi.org/10.48550/arXiv.2607.14725
Actual full text: https://arxiv.org/html/2607.14725v1
Saved: `2607.14725-fulltext.raw/.txt`; metadata `project-5.raw/.txt`.

Verified mechanisms and evidence:
- Sec. III-B–E: Brownian-bridge informative prior, context-aware mini-batch optimal transport, occupancy-conditioned classifier-free guidance, and lightweight task-centric canonicalization rather than expensive equivariant networks.
- Intro contribution, local line 68: explicitly conditions training on occupancy maps to reduce reliance on inference-time optimization. Thus 'condition an FM planner on 2-D occupancy' is not novel.
- Sec. IV-A3, local line 209: K=40 trajectories per context. Success Rate is at least one collision-free goal-reaching candidate; Valid Rate is fraction of valid candidates; collision intensity is colliding WAYPOINT ratio. Report both SR and VR—best-of-40 SR can conceal substantial individual failure. Waypoint collision intensity is not automatically continuous segment verification.
- Sec. IV-B1, Table I, local line 539: 5 steps gives 80.95% VR; 2 steps gives 100% SR but only 70.25% VR and 0.0071 s inference. The latter is a particularly useful counterexample to conflating context success with universally safe samples.
- Sec. V, local line 678: future work includes adaptive noise variance/guidance weights and real-system validation. Its evaluations should not be described as physical-robot safety guarantees.

Code availability:
- No project/repository link was found in full-text hrefs or checked arXiv metadata. GitHub repository search for BridgeFlow returned unrelated results among the inspected top results, not an identified author implementation (`github-search-2.raw`). This is not proof no code exists; it is a bounded availability failure.

Disqualifies: generic few-step occupancy-conditioned FM speedups, generic informative priors, and reporting only 'some candidate succeeded'.



No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
