# LiFlow: Flow Matching for 3D LiDAR Scene Completion

Authors: Andrea Matteazzi; Dietmar Tutsch
First-posted year: 2026; inspected version: 2602.02232v1.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2602.02232v1
Persistent ID: arXiv:2602.02232; https://arxiv.org/abs/2602.02232v1
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/maps-agent/liflow.html.txt
Database resolution: OpenAlex resolved https://openalex.org/W7127371585; Semantic Scholar HTTP 429 (rate limit, not absence). OpenAlex metadata title checked; authors normalized to full text. Database publication year may differ from first-posted year.

## Full-text-backed reading note and boundaries

LiFlow: Flow Matching for 3D LiDAR Scene Completion
- Full text: https://arxiv.org/html/2602.02232v1.
- Local: liflow.html; liflow.html.txt.
- Crucial positive verification: this really IS FLOW MATCHING for completion of environmental 3D LiDAR scenes. It is not generic photographic generation, object-only completion, or the unrelated spectral “diffusion maps” method.
- Lines 184–189 identify nearest-neighbor FM plus Chamfer matching; Section 4.4 lines 607–676 gives conditioned inference from a single LiDAR scan via Euler integration and classifier-free guidance. Lines 740–754 evaluate CD, JSD, voxel IoU. Lines 1331–1332 discuss improved geometric coverage but weaker very-fine voxel IoU.
- Limits: NO downstream navigation experiment or calibrated doorway/reachability posterior is established by these sections. It supports feasibility of map/scene FM, not a claim that FM samples are calibrated world hypotheses for safe planning. Single-scan upsampling/completion and robot occupancy belief are related but different inference tasks.
- Compute: lines 717–719 specify 18,000 input points, 180,000 target points and NVIDIA A100 80 GB for training/inference. Therefore inappropriate as mandatory undergrad baseline on limited compute.
- Public code: https://github.com/matteandre/LiFlow. MIT license verified by liflow_LICENSE and liflow_repo.json. liflow_README.md documents Python 3.9.21, torch 2.1.1, CUDA 11.8, compiled MinkowskiEngine and PyTorch3D; ground-truth construction via `utils/map_from_scans.py`; `python train.py`; inference/evaluation through `utils/flow_completion_pipeline.py` / `utils/eval_path.py` and flow/refiner checkpoint arguments. External pretrained Google Drive link exists but not downloaded/access-tested.
- Data: SemanticKITTI and Apollo external data links. semantickitti_dataset.html.txt lines 207–212 verifies Creative Commons Attribution-NonCommercial-ShareAlike, explicitly noncommercial and attribution required. Code MIT does not override dataset restrictions. Apollo terms not verified. Refiner comes from LiDiff and requires its own license check.



No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
