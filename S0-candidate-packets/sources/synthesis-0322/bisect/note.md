# Full-text evidence — Bayesian Active Edge Evaluation on Expensive Graphs

Retrieved 2026-11-16 ~03:23 CST. Authors: **Sanjiban Choudhury, Siddhartha Srinivasa, Sebastian Scherer** (PDF byline). Identifier **arXiv:1711.07329v1**, submitted 2017-11-20; later IJCAI 2018 record DOI **10.24963/ijcai.2018/679** found in OpenAlex. Claims below are from inspected arXiv v1, not presumed identical conference text.

Full text: `https://arxiv.org/pdf/1711.07329v1`; saved `sources/synthesis-0322/bisect.pdf`, extracted `bisect.txt`. Inspected introduction/§II pp1–2, §IV-D p5, §§V-A–C pp5–7, case study §V-D p7 and discussion opening p8. Official arXiv API verified version/byline/title. S2 batch matched identifier/title/authors, S2 `6c7c37677b0b971562b7fbdefb59c8fa0288d439`; OpenAlex direct matched title and conference DOI. Raw records in parent directory.

## Supported nearest-answer evidence
- Introduction explicitly distinguishes identifying a feasible path from fully identifying a world: decision-region determination (DRD) needs only sufficient information to certify one candidate path. Regions can overlap; this is not binary global connectivity uncertainty.
- §V-B explicitly constructs independent BISECT baseline from **column averages of the same world/test matrix X**. D's broad joint-vs-marginal decision-value idea is directly anticipated, though algorithm also changes.
- §V-C reports stronger advantage in structured TwoWall/MovingWall/Maze/Baffle than less-correlated Forest; data size changes performance; finite-world DIRECT-only failures do not vanish in reported plot. Generic structure/finite-support/null-regime claims therefore cannot support unoccupied-gap rhetoric.
- §IV-D mixes posterior empirical marginals with 0.5 to retain nonzero support for tail worlds and switches to independent BISECT; finite-support fallback is not a new mechanism discovered here.
- §II optimizes expensive **computational edge-check** cost, not robot travel-to-sensing. Introduction explicitly admits ignoring solution quality and using a fixed path library. These differences bound the preemption claim; do not assert it literally executes our physical probe experiment.
- §V-A says paths are built by solving/subsampling k-shortest paths on the dataset and gives a train/test split. Our instrument must build candidate path/probe sets without final test-truth access; do not copy a vague split as a leakage-safe guarantee.
- v1 footnote says code/data link is planned for camera-ready; no current runnable release or license verified from that promise.

## Consequence
Supports demoting broad D and A 'learn only useful uncertainty' pitches. Combined with MacDonald/Smith's physical observation-cost formulation, there is little justification for promoting A merely because D lost its lead. Residual A is a proxy-sufficiency audit; residual D a controlled representation/interface robustness replication, both conditional on advisor interest and FM relevance. No empirical results produced in this commission.
