# Adaptive Time Step Flow Matching for Autonomous Driving Motion Planning

Authors: Ananya Trivedi; Anjian Li; Mohamed Elnoor; Yusuf Umut Ciftci; Avinash Singh; Jovin D’sa; Sangjae Bae; David Isele; Taşkın Padır; Faizan M. Tariq
First-posted year: 2026; inspected version: 2602.10285v2.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2602.10285v2
Persistent ID: arXiv:2602.10285; https://arxiv.org/abs/2602.10285v2
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/planning-agent/2602.10285-fulltext.txt
Database resolution: Persistent arXiv ID and read version verified in full-text header; no successful scholarly-graph resolution recorded for this additional non-seed source.

## Full-text-backed reading note and boundaries

Adaptive Time Step Flow Matching — adaptive compute is already a planner mechanism

Exact title: Adaptive Time Step Flow Matching for Autonomous Driving Motion Planning
Authors: Ananya Trivedi; Anjian Li; Mohamed Elnoor; Yusuf Umut Ciftci; Avinash Singh; Jovin D'sa; Sangjae Bae; David Isele; Taskin Padir; Faizan M. Tariq. (Author typography in HTML includes Taşkın Padır.)
Read version: arXiv:2602.10285v2, 14 Feb 2026.
Identifiers: https://arxiv.org/abs/2602.10285v2 ; https://doi.org/10.48550/arXiv.2602.10285
Actual full text: https://arxiv.org/html/2602.10285v2
Saved: `2602.10285-fulltext.raw/.txt`; metadata `verify-4.raw/.txt`.

Verified mechanisms and evidence:
- Sec. III-C, IV-A/B, local lines 97–116: learns a lightweight scalar variance estimator alongside the flow predictor; higher predicted variance gives smaller integration steps. Uses U-Net bottleneck features through four-layer width-512 MLP. This is a learned uncertainty heuristic, not a verified safety certificate or a collision-based adaptive controller.
- Sec. V-C, local line 384: compares Flow-Euler 5 and 50, Flow-Adaptive, and NoQP; decoders exported to ONNX and TensorRT. Runtime claims therefore cannot be transplanted to unoptimized Python/CPU evaluation.
- Sec. V-D, Table V, local lines 420–426: reports about 45 ms total inference and 4.7 average NFE; adaptive integration gives quality comparable to 50 fixed steps, and fixed 5 steps is worse despite matched average NFE. QP adds about 1–2 ms. This directly anticipates adaptive computation for FM planning.
- Sec. V-C, local line 388: collisions are evaluated OPEN LOOP; explicit obstacle-avoidance constraints in postprocessing are FUTURE WORK. The QP smoothness/dynamic improvement is NOT evidence of hard collision safety. This is an important disqualifier for any proposal that treats a generic dynamics QP as a verified collision filter.

Code availability:
- https://flow-matching-self-driving.github.io/ is verified (`project-3.raw/.txt`). It explicitly says 'Code will be released publicly', with no actual implementation link. Not presently established as runnable.

Disqualifies: learned uncertainty-based adaptive time steps as new. Does not solve the proposed full budget-allocation/independent-verification problem, and has a training burden for its adaptive module.



No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
