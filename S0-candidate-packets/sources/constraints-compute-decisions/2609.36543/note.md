# Planning-Oriented 3D Scene Completion via Coupled TUDF–Occupancy Representation Learning from Partial Observations

Authors: Tianyou Yu; Pengfei Zhao; Chao Xu
First-posted year: 2026; inspected version: 2609.36543v1.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2609.36543v1
Persistent ID: arXiv:2609.36543; https://arxiv.org/abs/2609.36543v1
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/maps-agent/planning_oriented.html.txt
Database resolution: OpenAlex resolved https://openalex.org/W7214934168; Semantic Scholar HTTP 429 (rate limit, not absence). OpenAlex metadata title checked; authors normalized to full text. Database publication year may differ from first-posted year.

## Full-text-backed reading note and boundaries

Planning-Oriented 3D Scene Completion via Coupled TUDF–Occupancy Representation Learning from Partial Observations
- Full text: https://arxiv.org/html/2609.36543v1; abstract metadata separately retrieved as planning_oriented_abs.html.
- Local: planning_oriented.html; planning_oriented.html.txt.
- Most direct recent competitor on map→planning mismatch, though deterministic rather than posterior-sampling based. Joint occupancy and truncated unsigned distance fields are coupled for trajectory optimization.
- Lines 621 onward deliberately evaluate geometric environments and dense pillars/narrow passages. Lines 981–1016 compare actual trajectory outcomes evaluated against ground truth.
- Exact quote (986): “this leads to reduced obstacle clearance and more collision failures, despite the relatively high occupancy accuracy.” The preceding explanation attributes it to OCC-only positive distance bias, short trajectories close to obstacles and incomplete reconstruction. This IS a measured planning mechanism, unlike SceneSense's illustrative example.
- Lines 991–996 discuss unsigned-distance invalid initialization and joint model safety/efficiency tradeoff. Lines 1011–1016 show occlusion/boundary failures; lines 1028–1037 explicitly leave uncertainty-aware completion for future work.
- Code/data constraint: line 215 says “The dataset generation pipeline and implementation code will be publicly released upon publication.” No verified released implementation or license in retrieved text; do not treat publication promise as runnable code. The full text does not establish the proposed joint-posterior/probe-value question.



No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
