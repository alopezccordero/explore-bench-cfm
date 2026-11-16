# S0 requirements and audit boundaries
## Mandatory user scope correction — integrated round005
Alejandro's work is a **2D grid simulator/environment and algorithms**, not 3D or physically constrained sensing. Observation visibility, local reveals, partial observability and query budgets below are only explicitly stipulated simulator interventions, not inherited hardware assumptions. Actual simulator API/observability remains unverified: the supplied reference repository is the workflow repository; bounded search located no simulator implementation. Do not infer either full or partial observability as an existing property. No 3D reconstruction, hardware, camera/LiDAR, calibration or physical sensing budget requirement. Existing simulator integration requires an actual API check after permission, not an invented compatibility claim. Scope correction supersedes old sensor-centric descriptions; earlier critiques remain archived.

Source: read-only `rsm-flow-mapping-ug/machine/machine.yaml`, S0 (FRAME), and `handbook/S00.md`, inspected 2026-11-16 CST.

Each surviving candidate requires:

| Requirement | Candidate artifact | Verification |
|---|---|---|
| Answerable subject/comparison RQ, useful negative result | task/task_spec.md | Human/AI adversarial critique; Gate A remains advisor-owned |
| One primary metric, unit and maximize/minimize direction | task/metric.json | JSON/schema and operational-definition review |
| Specific scope, resource/data/time constraints and approvals | task/constraints.json | Feasibility audit; unknowns explicitly assumed |
| Existing evaluator or dated construction plan within project window | task/evaluator_spec.md | Actual access/protocol checks; execution vs plan distinguished |
| 2–4 relevant seeds, every seed carrying real persistent ID | task/seed_papers.json | JSON count, metadata and scholarly lookup; full-text source notes |

Auto guards do not establish scientific quality. Student attestation and advisor approval are not automated or fabricated. This work prepares alternatives; it does not select for Alejandro, request Gate A, or transition states.

All work is isolated under this research directory. Reference repository remains unchanged, with no commits, pushes, PRs, or tags. No HPC jobs/training/experiments. Date of final presentation: November 16, 2026, 05:30 CST (America/Chicago).

AI contributions must be disclosed as source extraction, drafting and criticism. Unresolved literature/API/data/project-window issues stay visible. Citation notes must derive from accessed full text, not model memory. Dates for proposed evaluator construction are plans and depend on student/advisor adoption.
