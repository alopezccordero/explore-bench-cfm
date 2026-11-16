# Canonical entrypoint
All relative evidence filenames in the copied extraction note below refer to ../mapping-competitors/, NOT this canonical directory. Parent independently inspected key method/failure anchors; original full text preserved.

# Source note 04 — flow-matching occupancy novelty blocker

Exact title: FMOcc: TPV-Driven Flow Matching for 3D Occupancy Prediction with Selective State Space Model.
Authors: Jiangxia Chen; Tongyuan Huang; Ke Song.
ID/version read: arXiv:2507.02250v1, 2025-07-03 (abstract metadata). HTML body additionally prints 'August 24, 2026' without changing version header: retain versioned URL and do not silently treat that body date as a new submission. No accepted venue or DOI verified. Paper license: arXiv perpetual non-exclusive distribution.
URLs: https://arxiv.org/abs/2507.02250v1 ; https://arxiv.org/html/2507.02250v1 .
Saved full text: 2507.02250v1.txt; original HTML fmocc-full.raw; PDF fmocc-pdf.pdf; abstract fmocc-abs.raw.

## What the method actually does
Camera-based autonomous-driving semantic occupancy from two temporal frames and surround-view images. Image encoder and LSS lift image features to voxel features. Flow Matching SSM module maps incomplete/masked input features toward semantic-label embeddings, operating through tri-perspective-view features and selective state-space layers. Velocity MSE and Euler integration described in §3.3. Mask training handles sensor/feature corruption.
Critical distinction: §3.1 discusses general Gaussian-to-data rectified flow, but actual §3.3 defines V0 as masked INPUT IMAGE FEATURES and V1 as encoded semantic LABELS. This is feature refinement with flow matching, NOT an experimentally validated stochastic posterior sampler of alternative complete robotic maps. Do not assume Gaussian randomness in preliminaries means the implemented inference yields meaningful posterior diversity.

## Evidence anchors
- §3.1.1 lines 96–102: rectified-flow preliminaries and velocity regression.
- §3.3 lines 123–145: source masked features, target label embeddings, TPV refinement, Euler update, velocity MSE.
- §3.5 lines 159–164: feature/camera masking schedule.
- §4.1 lines 543–547: datasets, labels, mIoU/RayIoU, training.
- §4.2 lines 550–553: visible-mask protocol difference and baseline comparisons.
- §4.3 lines 558–567: flow-vs-diffusion speed/accuracy, masking robustness, distant prediction.
- §5 lines 575–577: occupancy forecasting is FUTURE work; current work predicts present occupancy.

## Datasets/evaluator and results
Occ3D-nuScenes and OpenOcc; 700 training scenes/150 validation scenes, 20 s clips, annotations 2 Hz; 0.4 m voxels, +/-40 m x/y, -1 to 5.4 m vertical; 17/16 categories respectively (§4.1). These are driving perception benchmarks rather than incremental mapping/exploration. Inputs six cameras; model camera-only even though raw collection vehicle has lidar/radar.
Reported two-frame ResNet50 headline: Occ3D-nuScenes RayIoU 43.1%, mIoU 39.8%; OpenOcc RayIoU 42.6%; inference memory 5.4 GB and 330 ms stated in abstract. Main training: 24 epochs, four A40 GPUs, batch 8, 704×256 inputs. No new experiments run here. Compare equal backbone/input resolution/temporal frames/visibility-mask policy. Paper separates with/without visible-mask baselines but prose says masks omitted in training and later reports mask variants: retain exact row/protocol rather than pool all numbers. Claims of general state of the art are author claims, not verified as of November 2026.

## Calibration and decision audit
No posterior calibration, sample-frequency validation, proper probabilistic scores, credible-set coverage, collision calibration, on-robot planner evaluation, or navigation utility study identified. Robustness to masked features and better mIoU do not establish uncertainty calibration. No conditional diversity evaluator is supplied. Flow-matching training alone does not establish identifiable conditional posterior when its source is deterministic image features.

## Code and licenses
No official code URL identified in paper/abstract. GitHub repository-name search q=FMOcc returned unrelated substring matches (saved fmocc-search.raw), no verified official implementation. Code/checkpoints/license UNVERIFIED, not proven nonexistent. Dataset licensing not directly audited; nuScenes-derived access/terms are separate. Paper distribution license does not license benchmark data or code.

## Novelty risk / recommendation
Defeats a broad 'first flow matching for 3D occupancy prediction' claim. Weaker nearest task match than SceneSense for robotic mapping, but mandatory architecture-level prior art. A calibrated conditional flow over incomplete/noisy occupancy maps could still differ by inference target, stochastic conditioning, evidence likelihood, online map provenance, and evaluation. Must explicitly contrast feature refinement against a joint map posterior; do not characterize FMOcc as already solving posterior calibration, nor dismiss it simply because it is automotive.
