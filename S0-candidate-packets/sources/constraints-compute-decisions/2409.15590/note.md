# MapEx: Indoor Structure Exploration with Probabilistic Information Gain from Global Map Predictions

Authors: Cherie Ho; Seungchan Kim; Brady Moon; Aditya Parandekar; Narek Harutyunyan; Chen Wang; Katia Sycara; Graeme Best; Sebastian Scherer
First-posted year: 2024; inspected version: 2409.15590v3.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2409.15590v3
Persistent ID: arXiv:2409.15590; https://arxiv.org/abs/2409.15590v3
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/maps-agent/mapex.html.txt
Database resolution: OpenAlex resolved https://openalex.org/W4413925576; Semantic Scholar HTTP 429 (rate limit, not absence). OpenAlex metadata title checked; authors normalized to full text. Database publication year may differ from first-posted year.

## Full-text-backed reading note and boundaries

MapEx: Indoor Structure Exploration with Probabilistic Information Gain from Global Map Predictions
- Full text: https://arxiv.org/html/2409.15590v3 (retrieved through unversioned HTML; embedded header identifies v3).
- Local originals: mapex.html; extracted full text: mapex.html.txt.
- Peer-reviewed version confirmed in repository README: ICRA 2025, DOI 10.1109/ICRA55743.2025.11128862.
- Nearest competitor for the proposed decision question. This is an ENSEMBLE of LaMa inpainting predictors, NOT a diffusion map posterior.
- Evidence: lines 288–290 state use of LaMa; lines 233–259 describe multiple predictions, mean/variance and global topological understanding. Lines 734–736 define TU: use the predicted map to plan an A* path; failure is collision with ground truth or failure to reach goal; evaluate 100 random goal locations per map.
- Exact quote (734): “Topological Understanding (TU), to directly evaluate how much the outcome of a robot’s exploration aids downstream path planning tasks.”
- Exact quote (780): “Interestingly, Observed Map, which reasons on observed map, shows competitive performance.” This is an especially important negative baseline: prediction is not necessarily the key benefit, and the visibility model may dominate uncertainty.
- Lines 754–765 compare uncertainty-only UPEN and coverage-only IG-Hector; lines 780–783 ablate No Visibility, No Variance, Deterministic, Observed Map. Do not interpret its simultaneous gains in IoU and TU as a demonstrated ranking reversal: the paper establishes a task metric and baselines, not the stronger joint-posterior mechanism proposed here.
- Runnable public artifact: https://github.com/castacks/MapEx. Retrieved mapex_repo.json, mapex_tree.json, mapex_README.md, mapex_LICENSE, mapex_gitmodules.txt. README lines 94–120 provides `cd scripts/; python3 explore.py` and built-in nearest/upen/hectoraug/visvarprob baselines plus ablations. It is documented runnable, NOT execution-tested by this scout.
- Data: tree verifies actual `kth_test_maps/.../occ_map.npy`, `valid_space.npy`, visualization files. README supplies pretrained three-model LaMa ensemble via Google Drive and KTH evaluation setup. Linked weights were not downloaded or independently access-tested. Requires LaMa environment, range_libc compiled extension, pyastar2d, numba; not a zero-dependency benchmark.
- License: repository LICENSE is BSD-3-Clause-Clear; retain notices, no implied patent rights. This does NOT establish that upstream KTH floor plans, LaMa submodule, and external weights all have the same license. Dataset-specific redistribution rights remain unverified; do not silently relicense the maps under the top-level code license.



No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
