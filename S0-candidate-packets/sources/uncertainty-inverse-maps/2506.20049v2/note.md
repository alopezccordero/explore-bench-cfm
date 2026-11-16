# Canonical entrypoint
All relative evidence filenames in the copied extraction note below refer to ../mapping-competitors/, NOT this canonical directory. Parent independently inspected key method/failure anchors; original full text preserved.

# Source note 01 — nearest real-robot mapping competitor

Exact title (verified against abstract page and full text): Robust Robotic Exploration and Mapping Using Generative Occupancy Map Synthesis.
Authors: Lorin Achey; Alec Reed; Brendan Crowe; Bradley Hayes; Christoffer Heckman.
ID/version read: arXiv:2506.20049v2, submitted 2025-06-24, revised 2025-12-29. DOI 10.1007/s10514-025-10229-0; arXiv journal reference: Auton Robot 50, 8 (2026). Paper license: arXiv perpetual non-exclusive distribution license, NOT a software license.
Primary URLs: https://arxiv.org/abs/2506.20049v2 and https://arxiv.org/html/2506.20049v2 .
Saved full text: 2506.20049v2.txt; original full HTML: 2506.20049v2.full.html; PDF: 2506.20049v2.pdf. All relative paths in this note are in its directory.

## What it actually does
Sections 4–6: unconditional U-Net/DDPM trained on complete local occupancy, conditioned at inference by repeatedly inpainting known occupied AND known-free voxels. Runs 30 denoising steps. Integrates multiple generated maps into OctoMap with a piecewise probabilistic/log-odds update, treating predicted occupancy as lower-trust evidence than sensor observations. Predicts either locally around robot or around selected graph frontiers. Uses Spot quadruped, lidar/IMU/LIO-SAM, GBPlanner, and an off-board GPU. This already covers much of a generic 'sample ambiguous unseen occupancy and fuse for robot planning' proposal.

## Full-text evidence anchors
- §4.3.2, text lines 224–226: observed occupied/free space is retained by occupancy inpainting.
- §4.3.3, lines 250–251: same context produces multiple different reasonable predictions.
- §6, lines 268–275: probabilistic map merging and configurable prediction/sensor probabilities, with lower trust for predictions.
- §7, lines 278–284: 11,296 unique training poses; IoU, FID, KID; no posterior calibration metric reported.
- §7.1, lines 347–354: frontier prediction has more unknown voxels and more diverse predictions; uses pairwise IoU distributions to characterize diversity.
- §8.2.2, lines 484–489: frontier-centric completion FAILS to finish exploration because generated occupancies erase the observed free/unknown frontier boundary. This is crucial negative evidence, not a universally successful drop-in mapping system.
- §9, lines 493–498: indoor restriction, off-board GPU, confident erroneous predictions and incomplete exploration.

## Evaluation and actual results
Custom indoor lidar occupancy collection, about 1 hour, 11,296 complete local occupancy maps/poses. §7 says multiple indoor environments/buildings and held-out evaluation areas, whereas §9 calls training data 'collected from a single building': unresolved internal description inconsistency. No named downloadable benchmark for these real-world sequences was verified.
Two held-out indoor map-quality environments. RC/FC prediction radius 3.3 m; FC target maximum range 7 m. Probabilistic merging typically 3–5 predictions per pose. Table 1 FC FID: baseline 116.9/150.6; one-shot completion 104.2/133.4; probabilistic merging 30.1/34.5. These are distributional feature distances, not probability calibration.
Narrow-corner traversal plus full exploration in two environments. Table 2 labels 8 runs/configuration but surrounding text describes 10 traversals: do not hide this inconsistency. Full exploration: five starts in environment 1, four in environment 2. Environment 2 local SceneSense mean time 81.68 s vs GBPlanner 106.46 s; frontier method N.A. for completion. Table 3 contains suspicious aggregates (mean exceeding stated max), so do not build quantitative claims from it without original-data clarification. Inference ablation: 0.4437 s end-to-end unconditional vs 1.66 s conditional; practical prediction plus merging adds latency (§8.1.3).

## Calibration versus diversity
Demonstrates sample variability, distributional similarity, heuristic lower trust for predictions, and practical fusion. Does NOT demonstrate that voxel frequencies equal true conditional event probabilities, nominal credible-set coverage, calibration on noisy masks, or calibrated collision risk. Probabilistic update nomenclature is not itself a calibration result. Repeated samples conditioned on substantially the same observations should not be assumed independent sensor evidence; potential overconfidence from repeated fusion is an inference/risk to test, not an experimentally established failure here. Merging can suppress rare but safety-important coherent hypotheses.

## Code/data/license status (retrieved live, not inferred from abstract)
Full paper still says code '[URL-added-post-publication]'. Historical related abstract advertises github.com/arpg/sceneSense_ws, but GitHub API for that repository returned 404. Search found official arpg/SceneSense and arpg/SceneSenseServer, both GitHub-reported Apache-2.0; SceneSense LICENSE endpoint retrieved successfully (scenesense-license.raw). Original SceneSense README identifies IROS 2024, supplies setup/example prediction, but data download field is literally '<link>'. Thus public family code exists, but exact journal-paper reproduction/data/weights were NOT verified. Saved README: scenesense-readme.raw; server README: scenesense-server-readme.raw; repository search snapshot github-1.json.

## Near-duplicate and novelty risk
One lineage, not three independent baselines: SceneSense: Diffusion Models for 3D Occupancy Synthesis from Partial Observation (arXiv:2403.11985v1); Online Diffusion-Based 3D Occupancy Prediction at the Frontier with Probabilistic Map Reconciliation (2409.10681v1); current 2506.20049v2. Exact earlier titles verified from saved broad-retry.raw Atom metadata, not memory. Current arXiv comment explicitly flags text overlap with 2409.10681. Count this as a single evolving competitor family. Generic occupancy diffusion, observation-preserving completion, multiple hypotheses, and probabilistic map fusion are already claimed. Strongest differentiator would be properly evaluated conditional calibration plus a planner that preserves observed/predicted provenance and reasons about joint-map risk—not simply replacing diffusion with flow matching.

## Final identifier resolution checkpoint
{
  "database": "OpenAlex",
  "id": "https://openalex.org/W4414988296",
  "title": "Robust robotic exploration and mapping using generative occupancy map synthesis",
  "doi_returned": "https://doi.org/10.1007/s10514-025-10229-0",
  "raw": "/home/sircordero/research/s0-overnight-2026-11-16/sources/uncertainty-inverse-maps/inverse/openalex-scenesense.raw",
  "match": "exact title after case normalization; primary arXiv metadata independently retrieved",
  "S2": "429 for this seed; not a nonexistent-paper result"
}
This database metadata match is not execution of the reference repository citation graph resolver, which was not run.
