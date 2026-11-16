# Evaluator/component availability audit

Retrieved 2026-11-16 CST. This is a source note for web/code documentation, not an academic full-text paper. Raw responses are preserved in search-responses/ under the listed tags; exact URLs/status/timestamps are in the scout search_log.jsonl.

## MapEx: verified components, not a turnkey new evaluator
Official project: https://mapex-explorer.github.io/ (HTTP 200; tag mapex-site).
Official code linked by that project: https://github.com/castacks/MapEx.
API metadata/readme/tree: https://api.github.com/repos/castacks/MapEx, /readme, /git/trees/HEAD?recursive=1 (HTTP 200; tags castacks-MapEx-meta/readme/tree).
Saved decoded README: search-responses/castacks-MapEx-README.md.
Root LICENSE: https://raw.githubusercontent.com/castacks/MapEx/main/LICENSE (HTTP 200; tag mapex-license). Clear BSD License with copyright 2025 AirLab. GitHub labels BSD-3-Clause-Clear. Patent grants explicitly excluded in text.

README documents scripts/explore.py, configs with modes nearest/upen/hectoraug/visvarprob, initial map/start arguments, and processed kth_test_maps directories. API tree confirms occ_map.npy and valid_space.npy across those directories. README documents pretrained LaMa checkpoint folder at a Google Drive link, but actual download and checkpoint compatibility were not tested. Its metrics workflow generates global_pred then runs calc_metrics_subdirectory.py for coverage and predicted IoU. Code source for explore.py and calc_metrics_subdirectory.py was retrieved (tags mapex-main-code/mapex-metrics-code) and inspected without running. The metric script includes IoU and coverage routines; this is not evidence of an existing primary reachability Brier/calibration evaluator. Paper-defined Topological Understanding remains an evaluator extension unless its implementation is separately located/verified.

No conclusion that KTH XML data, processed NPY maps, manually corrected floorplans or model weights inherit the code license. Original/processed data rights and exact training split artifacts remain unresolved. A guessed KTH page returned 404; it was a failed lookup, not a verified dataset source. Do not cite that URL as the floorplan dataset.

## SceneSense: public code exists, deployment/data unclear
Paper-advertised arpg/sceneSense_ws API endpoint returned HTTP 404 (tag scene-repo). A separate repository search found https://github.com/arpg/SceneSense (tag scene-search) with Apache-2.0 license metadata. README retrieved through https://api.github.com/repos/arpg/SceneSense/readme (tag scenesense-readme). It specifies Ubuntu 20.04/CUDA, setup.bash and example_prediction.py, but Download data is literally <link>. Thus an original implementation exists; its data and complete newer probabilistic ROS/evaluation stack were not verified usable. This corrects the possible but false inference “404 means no SceneSense code.”

## Flow Matching Ergodic Coverage
Project https://murpheylab.github.io/lqr-flow-matching/ (200; ergodic-site) links https://github.com/MurpheyLab/flow-ergodic-coverage.git. API metadata/readme/tree retrieved (MurpheyLab-flow-ergodic-coverage-*). License metadata GPL-3.0; README explicitly GPL version 3 or later. JAX/lqrax/ott tutorials include Stein/Sinkhorn point-mass coverage, differential drive and 3D aircraft coverage. Code is an available density/trajectory coverage component, not an unknown-map posterior benchmark. Older lqr-flow-matching links remain in README; current repo redirects/naming must be checked again at implementation. No install or notebook run performed.

## NextBestPath / AiMDoom
Repository https://github.com/shiyao-li/NextBestPath identified via GitHub search then metadata/readme/tree (shiyao-li-NextBestPath-*). README documents PyTorch3D/Trimesh simulator, ground-truth point-cloud and coverage evaluation routines, test_nbp_planning.py, train_nbp.py, AiMDoom difficulty-level data and NBP weights via Google Drive, and https://github.com/shiyao-li/AiMDoom toolkit. Only README/tree access verified; no Drive download, simulator execution or data/license acceptance. GitHub metadata license is null: absent recognized license is a blocker to assuming reuse/redistribution rights, not proof of a specific restrictive license. Dataset assets and MP3D terms require separate checks. This component measures 3D surface coverage, not the proposed finite posterior metric.

## Rome release status
The retrieved paper checklist says code will be released upon acceptance; extended hyperparameters not included in that version. Exact identifier GitHub repository search returned no items. This does not prove no code exists elsewhere. Its PDF NeurIPS header is not independently verified acceptance. No runnable Rome evaluator is asserted.

## Honest construction consequence
Use original future-authored procedural finite-support grids and explicit sensor models for minimum S0 evaluator construction, after Gate C. Both packets list dated construction milestones and tests that have NOT run. External MapEx/SceneSense/NextBestPath resources inform baselines and scientific context, not a claim that these precise RQs already have installed runnable evaluators. Student window, compute and permissions remain assumptions.
