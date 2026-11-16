# Canonical entrypoint
All relative evidence filenames in the copied extraction note below refer to ../mapping-competitors/, NOT this canonical directory. Parent independently inspected key method/failure anchors; original full text preserved.

# Source note 03 — downstream embodied navigation competitor

Exact title: Plug-and-Play Label Map Diffusion for Universal Goal-Oriented Navigation.
Authors: Zhixuan Shen; Yijie Zeng; Shengxiang Luo; Tianrui Li; Haonan Luo.
ID/version read: arXiv:2605.05960v1, 2026-05-07. Abstract metadata calls this an extended version of accepted ICML 2026 paper (21 pages, 10 figures); official code README also identifies ICML 2026. No DOI verified. Paper license: arXiv perpetual non-exclusive distribution.
URLs: https://arxiv.org/abs/2605.05960v1 ; https://arxiv.org/html/2605.05960v1 .
Saved: 2605.05960v1.txt, 2605.05960v1.full.html, 2605.05960v1.pdf, plmd-readme.raw, plmd-meta.raw, plmd-root.raw.

## Method and overlap
Predicts unknown portions of 2D BEV obstacle and semantic label maps with a two-network DDPM/SDE restoration framework. Obstacle network is pretrained/frozen and supplies SPADE-like structural guidance to semantic denoising. Not a flow-matching map posterior. Uses HDBSCAN clusters of generated goal pixels to propose navigation goals; selects a composite density/size/distance score. Existing navigation strategy falls back if no cluster. Observed map evidence stays sensor-anchored; generated labels are high-level hypotheses (§3.3, lines 152–158).
Thus an 'occupancy/map completion helps a planner' claim is substantially occupied, even for plug-in rather than policy-learning approaches.

## Data and evaluation
§§3.2/4.1: simulated Habitat exploration collects partial/full map pairs; FBE 500 steps, snapshots every 25 steps, 2,000 episodes. 256×256 training maps; source semantic projection maps 480×480, 40 channels; RedNet labels; 100 denoising steps. Indoor HM3D_v0.1, HM3D_v0.2, MP3D. ObjectNav on all three; Instance-ImageNav on HM3D_v0.2; multi-robot ObjectNav on HM3D_v0.2/MP3D. Multiple downstream baseline policies. Metrics SR, SPL, PSNR, NOT calibration. Table 1 IIN row: IEVE 0.702 SR/0.252 SPL; PLMD RL variant 0.776/0.283. Appendix N confirms A40 no-PLMD 0.702/0.252 vs T=100 0.776/0.283, with extra inference cost. These are navigation improvement results, not occupancy posterior validation.
Appendix F, line 1039: separate MP3D training 471,900 pairs (377,520 train/94,380 validation). Notes scene similarity between HM3D_v0.1/v0.2 and omits training v0.2 for that reason. Need explicit scene-level split audit before calling the paired-map holdout independent; adjacent masks of the same episode are near-duplicates. Main text states pretraining data separate from evaluation environments; this audit did not independently verify scene lists.
Appendix P (line 1292) explicitly says training/testing limited to SIMULATOR. Jetson AGX Orin runtime ablations are not proof of a deployed robot navigation experiment. Does not claim outdoor generality.

## Uncertainty versus diversity
No posterior reliability/coverage or calibrated risk evaluation found. Density of a generated goal-pixel cluster is NOT estimated probability that the object truly lies there. SR/SPL measure decisions, and PSNR measures pixel fidelity; none imply calibrated conditional map uncertainty. The hypothesis-preserving interface is nevertheless a useful baseline for downstream handling of hallucinated maps and avoids blindly treating generated observations as sensor evidence. Paper warns prediction errors could cause unsafe actions (Appendix P).

## Code/license status
Verified official https://github.com/FrankZxShen/PLMD, public nonempty repository, root snapshot plmd-root.raw. README provides map collection, obstacle/semantic training, ON/IIN/MRON evaluation entry points. README line 76 says pretrained weights 'will be provided with the official release'; do not assert downloadable ready-to-run checkpoints verified. GitHub license null; no top-level LICENSE in retrieved root listing: code usage rights not established. Upstream dependencies/datasets separately licensed.
Appendix Q asserts HM3D/MP3D licenses not stated and merely cites papers. This is an author assertion, NOT a defensible license audit; dataset access/terms need checking directly before reuse. Do not repeat 'unlicensed' or 'public-domain' as fact.

## Novelty / near-duplicate risk
Not the same publication family as SceneSense. Closest for BEV label completion as an auxiliary navigation module, including multi-robot settings. Strong overlap with label/occupancy generative completion, preserving observed regions, and downstream planner utility. Flow replacing DDPM and achieving equivalent SR alone would be a narrow speed/architecture change, not evidence of a calibrated map posterior. For this research lane compare both sample-based uncertainty and identical downstream goal/planner interfaces at matched latency/sample budget.
