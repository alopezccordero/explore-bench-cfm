# SafeFlow: Safe Robot Motion Planning with Flow Matching via Control Barrier Functions

Authors: Xiaobing Dai; Zewen Yang; Dian Yu; Fangzhou Liu; Hamid Sadeghian; Sami Haddadin; Sandra Hirche
First-posted year: 2025; inspected version: 2504.08661v3.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2504.08661v3
Persistent ID: arXiv:2504.08661; https://arxiv.org/abs/2504.08661v3
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/planning-agent/2504.08661-fulltext.txt
Database resolution: Persistent arXiv ID and read version verified in full-text header; no successful scholarly-graph resolution recorded for this additional non-seed source.

## Full-text-backed reading note and boundaries

SafeFlow — training-free safety, adaptive integration, terminal filtering

Exact title: SafeFlow: Safe Robot Motion Planning with Flow Matching via Control Barrier Functions
Authors: Xiaobing Dai; Zewen Yang; Dian Yu; Fangzhou Liu; Hamid Sadeghian; Sami Haddadin; Sandra Hirche.
Read version: arXiv:2504.08661v3, 12 Nov 2025.
Identifiers: https://arxiv.org/abs/2504.08661v3 ; https://doi.org/10.48550/arXiv.2504.08661
Actual full text: https://arxiv.org/html/2504.08661v3
Saved: `2504.08661-fulltext.raw/.txt`; metadata `verify-3.raw/.txt`.

Verified mechanisms and evidence:
- Sec. III-A/B, especially QP (29): flow-matching barrier functions add a minimum-intervention correction to learned flow; unified/composite safe sets handle differentiable safety constraints. The mathematical setup defines safe states at trajectory indices. Do not silently upgrade this to exact arbitrary occupancy-pixel swept-segment safety.
- Sec. IV-A, Algorithm 1, local lines 460–503: adaptive fourth/fifth-order Runge–Kutta with error-based accepted steps; composite barrier component activated only after t*=0.5; final line applies a terminal CFMBF safety filter. The prose literally calls the torchdiffeq method 'dropi5'; preserve the source wording rather than relying on it as a valid API spelling.
- Sec. IV-B, local lines 504–530: test-time extra obstacles are smooth ellipse constraints. A discrete occupancy-grid geometry interface is not supplied by that equation.
- Sec. IV-B, Table I discussion, local lines 538–545: 1000 navigation trials; reports 100% safety and approximately 60% higher inference time due to safety regularization, with a distribution/trajectory-quality tradeoff. This is an experimental rate, not evidence that every numerical discretization or real robot is safe.

Code/evaluator availability — important negative result:
- Project https://safeflowmatching.github.io/ links https://github.com/SafeFlowMatching/SafeFlow and https://huggingface.co/datasets/SafeFlowMatching/SafeFlowMatching_Dataset.
- GitHub API confirms public repo, but recursive tree at commit f022042f3afd23ab5e3ba946dbbc50f878889a27 contains ONLY `.gitignore`, `LICENSE`, `README.md`. README says 'Coming soon...'. Evidence: `verify-0.raw`, `verify-1.raw`, `verify-2.raw/.txt`.
- Thus the concrete code URL exists but is a placeholder, NOT runnable released code. Dataset link presence verified; dataset content/download was not independently checked.

Disqualifies: 'add CBF/QP guidance to FM without retraining' and 'delay expensive safety until late flow time' as new project ideas. Makes a strict no-new-training project dependent on alternative public baseline code rather than this repository.



No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
