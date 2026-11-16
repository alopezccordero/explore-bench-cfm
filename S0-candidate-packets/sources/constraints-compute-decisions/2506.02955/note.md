# UniConFlow: A Unified Constrained Flow-Matching Framework for Certified Motion Planning

Authors: Zewen Yang; Xiaobing Dai; Dian Yu; Zhijun Li; Majid Khadiv; Sandra Hirche; Sami Haddadin
First-posted year: 2025; inspected version: 2506.02955v3.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2506.02955v3
Persistent ID: arXiv:2506.02955; https://arxiv.org/abs/2506.02955v3
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/planning-agent/2506.02955-fulltext.txt
Database resolution: OpenAlex resolved https://openalex.org/W4415135146; Semantic Scholar HTTP 429 (rate limit, not absence). OpenAlex metadata title checked; authors normalized to full text. Database publication year may differ from first-posted year.

## Full-text-backed reading note and boundaries

UniConFlow — exact compute decomposition and finite-step safety caveat

Exact title: UniConFlow: A Unified Constrained Flow-Matching Framework for Certified Motion Planning
Authors: Zewen Yang; Xiaobing Dai; Dian Yu; Zhijun Li; Majid Khadiv; Sandra Hirche; Sami Haddadin.
Read version: arXiv:2506.02955v3, 8 Oct 2026.
Identifiers: https://arxiv.org/abs/2506.02955v3 ; https://doi.org/10.48550/arXiv.2506.02955
Actual full text: https://arxiv.org/html/2506.02955v3
Saved: `2506.02955-fulltext.raw/.txt`; metadata `project-4.raw/.txt`.

Verified mechanisms and evidence:
- Secs. IV–V: prescribed-time zeroing function (PTZF) guides the sampling ODE through QP corrections for equality and inequality constraints. Sec. VI-C3, local lines 1038–1077: PTZF-guided sampling followed by violation-segment extraction, local repair, and global certification. This already targets compute savings by repairing only violating trajectory windows.
- Sec. VI-E, Table II and Appendix C-D/Fig. 18, local lines 1210–1269 and 2835–2839: explicit component compute accounting. Table II is stronger evidence than the prose summary: pendulum ODE/QP/refinement/total = 1.95/0.35/0.20/2.50 ms; raceline = 2.00/0.22/0.38/2.60 ms; pseudo-2-D manipulator = 22.50/3.20/6.00/31.70 ms; 3-D manipulator = 81.50/15.50/8.00/105.00 ms. ODE fraction ranges 71.0–78.0%. QP is 14.0% for pendulum (the prose's '8.5%' low-dimensional wording omits this, so use Table II).
- Sec. VI-E, local lines 1212–1214: solver uses 13 steps for low-dimensional settings, 133 for pseudo-2-D manipulator, 263 for 3-D manipulator. These are reported task settings, not an apples-to-apples scaling law or budget-optimal choices.
- Table III, local lines 1270–1309: Stage-1 pre-refinement certified rates are 88.4% pendulum, 98.1% raceline, 89.2% pseudo-2-D manipulator, 86.1% 3-D manipulator. 'The generator is always certified without refinement' is contradicted by their own ablation.
- Discussion, local line 2909: explicitly states certificates are continuous-time under assumptions; finite-step solvers, precision, and gradients leave residual violations; Stage 1 should be interpreted as a constraint-aware warm start, while terminal refinement closes the numerical gap. It names 'discretization-aware certificates' as future work. This is exceptionally strong evidence against casually transferring continuous-time theory to a few-step implementation.
- Discussion, local line 2911: sim-to-real mismatch from unmodeled friction/actuator dynamics remains, and unstructured physical uncertainty is not explicitly handled.

Code/evaluator availability:
- https://uniconflow.github.io/ verified HTTP 200 (`project-1.raw/.txt`), but the checked page exposes demos/results and no actual code repository link. Not an executable evaluator release established by this audit.

Disqualifies: generic inference-time equality/inequality enforcement, localized repair, or simply reporting ODE-versus-safety overhead as novel. Also means 'ODE always dominates' is already a measured outcome in one relevant framework, but remains hardware/task-specific.



No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
