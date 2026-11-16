# SceneSense: Diffusion Models for 3D Occupancy Synthesis from Partial Observation

Authors: Alec Reed; Brendan Crowe; Doncey Albin; Lorin Achey; Bradley Hayes; Christoffer Heckman
First-posted year: 2024; inspected version: 2403.11985v1.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2403.11985v1
Persistent ID: arXiv:2403.11985; https://arxiv.org/abs/2403.11985v1
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/maps-agent/scenesense.html.txt
Database resolution: Persistent arXiv ID and read version verified in full-text header; no successful scholarly-graph resolution recorded for this additional non-seed source.

## Full-text-backed reading note and boundaries

SceneSense: Diffusion Models for 3D Occupancy Synthesis from Partial Observation
- Full text: https://arxiv.org/html/2403.11985v1.
- Local: scenesense.html; scenesense.html.txt.
- Verified REAL environmental occupancy completion, not generic image synthesis. RGB-D-conditioned diffusion predicts 3D occupancy in unobserved regions while respecting measured occupied/free space.
- Strong metric mismatch evidence in quantitative discussion, line 631: a wall is displaced 0.1–0.2 m; prediction IoU is 0.52 versus 0.61 for running occupancy. Exact quote: “even if the prediction would be useful in planning, since the wall is mislocated the metric reports a much worse IoU than the running occupancy.”
- Scope restriction: this is an author-provided qualitative planning-usefulness example, NOT an actual downstream collision/success ranking experiment. Their FID/KID preference does not prove FID/KID are task-correct or calibrated. Lines 626–636 discuss the metric problem and respect for measured space.
- Public code: https://github.com/arpg/SceneSense, Apache-2.0 verified by scenesense_LICENSE and scenesense_repo.json. scenesense_tree.json confirms example inference and small example data/conditioning weight files. scenesense_README.md specifies Ubuntu 20.04, CUDA 11/12, tests on 3080 and 4070 Ti Super, `python3 example_prediction.py`.
- Important reproducibility constraint: README's full-data download is literally `<link>` (lines 31–35); do NOT report a complete downloadable dataset release. It does contain bundled example data. Retrieved scenesense_example_prediction.py.txt confirms CUDA inference, HF model `alre5639/full_rgbd_unet_512_more_pointnet`, and local conditioning weights `data/SceneSenseExData/171` (lines 91–102). Weight/model-card license not separately verified.
- The paper's old project URL https://arpg.github.io/scenesense/ returns 404, logged. GitHub search recovered the real repository; paper's “will be released” language is stale relative to repository availability.



No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
