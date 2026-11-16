# EGT: Execution-Grounded Traversability through Learned Closed-Loop Trajectory Distributions

Authors: Chinmay Mundane; Amith Manoharan; Arun Kumar Singh
First-posted year: 2026; inspected version: 2611.09270v1.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2611.09270v1
Persistent ID: arXiv:2611.09270; https://arxiv.org/abs/2611.09270v1
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/latest-2611.09270-fulltext.txt
Database resolution: Persistent arXiv ID and read version verified in full-text header; no successful scholarly-graph resolution recorded for this additional non-seed source.

## Full-text-backed reading note and boundaries

Parent inspected Sec. III-A sample average, III-B training/sampling, III-C fallback, IV-A setup, IV-C/D/Table I/II and V limitations. Learns distributions of CLOSED-LOOP trajectories conditioned on reference, terrain and vehicle/controller context; this is not simply generative map quality. 10 Euler steps, 30 predicted executions per candidate, 100 candidates; stop-and-plan average 1s on reported mounted RTX 3090 laptop. Grouped calibration evaluated on 650 once-executed reference paths; at predicted p=1, 481/485 actual executions succeed. A point prediction of 1 from finite samples is not certainty. Unsafe acceptance in Table I divides by 52 actually unsuccessful executions, NOT by accepted trajectories: denominator matters. Planning lowers required confidence if no candidate passes, bounded by abort threshold, then returns no-go. V: fixed vehicle/controller, nondeformable terrain, no post-endpoint stability guarantee; nonlinear least-squares kinematic prior major overhead. Strong competitor for any 'use FM event probability and abstain' idea. Code/license not independently verified; Gazebo/JAX/data collection too heavy as mandatory undergraduate baseline.

No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
