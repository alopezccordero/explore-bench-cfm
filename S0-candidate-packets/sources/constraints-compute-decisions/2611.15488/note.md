# FloCOS: Predicting Compact Forward Occupancy Sets of Surrounding Vehicles via Conditional Flow Matching

Authors: Chuansheng Dong; Yinxiao Zhan; Zongdian Li; Peng Hou; Jin Wang; Jiayu Fan
First-posted year: 2026; inspected version: 2611.15488v1.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2611.15488v1
Persistent ID: arXiv:2611.15488; https://arxiv.org/abs/2611.15488v1
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/latest-2611.15488-fulltext.txt
Database resolution: Persistent arXiv ID and read version verified in full-text header; no successful scholarly-graph resolution recorded for this additional non-seed source.

## Full-text-backed reading note and boundaries

Parent inspected full-text Secs. III–V and Conclusion, especially V-A protocol, V-B1/B2 and Tables I–III. This is dynamic forward occupancy of vehicles conditioned on histories/map features, NOT static indoor map completion. Conditional FM generates temporal convex-component coefficients; training coverage and union-area objectives are planner-facing. V-B/Table I: comparable occupancy coverage can accompany different completion; FORCE-OPT 85.2% completion versus 69.7% full-horizon coverage, whereas FloCOS 85.6% completion and 99.3% coverage. Do not equate completion with calibrated coverage. These are reported results, not this scout's replications. V-D/Table III explicitly excludes elementwise operations, preprocessing, set postprocessing and planning from FLOPs. Thus network FLOPs cannot be cited as end-to-end planner latency. V-A: other vehicles replay recorded trajectories without reacting; physical experiments use broadcast ground-truth SV pose. Limited validation does not establish real-traffic safety. No code/data license release independently verified; WOMD terms not checked. Competes directly with generic 'coverage versus planning utility' proposal; useful expansion family but not minimum undergrad evaluator.

No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
