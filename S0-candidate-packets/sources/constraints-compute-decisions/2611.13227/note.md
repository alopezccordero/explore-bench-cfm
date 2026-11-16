# Latent Barrier Steering: Hierarchical Safety for Generative Planning

Authors: Renhao Zhang; Mingzhe Li; Bruno Castro da Silva
First-posted year: 2026; inspected version: 2611.13227v1.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2611.13227v1
Persistent ID: arXiv:2611.13227; https://arxiv.org/abs/2611.13227v1
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/latest-2611.13227-fulltext.txt
Database resolution: Persistent arXiv ID and read version verified in full-text header; no successful scholarly-graph resolution recorded for this additional non-seed source.

## Full-text-backed reading note and boundaries

Parent inspected Sec. 5, Sec. 6 Limitations and Conclusion, Appendix I runtime table and Appendix B softmin geometry. Uses frozen multimodal FM planner across methods and new test-time constraints; latent steering followed by path-space CBF. Already addresses choosing a new behavior mode when local repairs lose goal-reaching. Appendix I has separate Stage-I/II times; 2D I Full LBS 0.35 s + 0.10 s. Sec. 6: Franka guarantee covers planned end-effector path, NOT tracking error or full-body collisions; local regularity and nonvanishing pulled-back gradients encouraged, not certified. Zeroth-order latent steering adds overhead. This disqualifies generic 'latent/homotopy steering beats local repair' as fresh question. Does not establish wall-deadline scheduling with independent grid-segment verification. No release/license/checkpoint verified.

No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
