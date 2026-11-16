# Uncertainty-driven Planner for Exploration and Navigation

Authors: Georgakis, Georgios; Bucher, Bernadette; Arapin, Anton; Schmeckpeper, Karl; Matni, Nikolai; Daniilidis, Kostas
Identifier: arXiv:2202.11907v1
Retrieved: 2026-11-16 CST
URL: https://arxiv.org/abs/2202.11907v1
Full text: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/upen/paper.pdf
Extracted: /home/sircordero/research/s0-overnight-2026-11-16/sources/robotic-mapping/upen/fulltext.txt
Inspected: pp. 1–4, especially Sec. III-A–C; pp. 5–6 navigation protocol/discussion

## Supported observations and limits
Sec. III-A predicts local occupancy outside the sensor FOV using an ensemble of UNets and registers local predictions into a global map via Bayesian updates. Sec. III-B uses ensemble variance for exploration. Sec. III-C explicitly constructs a different objective for goal navigation: per-path occupancy obstruction proxy, uncertainty and distance in an upper-confidence formulation. This is already task-dependent uncertainty-based planning, not merely raw cell entropy. p. 6 shows that success and path-length efficiency can diverge; pose is assumed noise-free in the navigation evaluation.

This materially weakens any claim that choosing a decision-relevant uncertainty measure is new. Candidate A must be a controlled joint-connectivity risk and posterior-mode-fidelity study, not “task-aware uncertainty.” The max-cell obstruction proxy is not the same construct as graph connectivity probability across joint complete maps. Candidate B can also include the registered prediction map as another source of dependence, but no evidence here establishes that its map probabilities are miscalibrated. No code/data deployment claims are made from this paper. Scope of full-text inspection is methods and evaluation design, not every cited reference.

Official abstract/PDF resolved. Not a packet seed; separate S2 resolution not attempted for this additional competitor. Version from extracted PDF watermark.
