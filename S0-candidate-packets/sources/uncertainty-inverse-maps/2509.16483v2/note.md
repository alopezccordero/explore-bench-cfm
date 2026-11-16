# Canonical entrypoint
All relative evidence filenames in the copied extraction note below refer to ../mapping-competitors/, NOT this canonical directory. Parent independently inspected key method/failure anchors; original full text preserved.

# Source note 02 — sparse generative completion competitor

Exact title: Octree Diffusion for Semantic Scene Generation and Completion.
Authors: Xujia Zhang; Brendan Crowe; Christoffer Heckman.
ID/version read: arXiv:2509.16483v2 (initial 2025-09-20; revision 2026-03-31). Abstract-page metadata: accepted ICRA 2026; Proceedings of the 2026 IEEE International Conference on Robotics and Automation. No DOI verified. Paper license: arXiv perpetual non-exclusive distribution.
URLs: https://arxiv.org/abs/2509.16483v2 ; https://arxiv.org/html/2509.16483v2 .
Saved full texts: 2509.16483v2.txt, 2509.16483v2.full.html, 2509.16483v2.pdf.

## Method, scope, evidence
Two-stage generation: coarse octree split/structure diffusion, then dual-octree-graph latent semantic diffusion with patch VAE. Partial lidar occupancy and optional semantics guide inference via postconditioned blending/inpainting; same architectural framework also generates/outpaints without retraining for each mask. §§III-C/D, text lines 182–193. Claims of one framework across indoor/outdoor do NOT imply one jointly trained universal model; §V explicitly proposes future work to unify indoor/outdoor training with guidance and compatible vocabularies.
Representation and postconditioned completion overlap strongly with an 'efficient probabilistic complete map from partial occupancy' proposal. It is diffusion, not flow matching.

## Evaluation datasets, splits, metrics
§IV, lines 240–247: SemanticKITTI official training set/validation set; 20 categories including empty, 0.2 m voxels, 256×256×32 grid. Replica indoor data, 92 categories, fixed random 90/10 scene split because no official split; 0.05 m voxels, 128×128×32. Indoor split membership/seed not independently verified. CU-Multi outdoor campus lidar tests zero-shot generalization qualitatively (§IV-C, lines 348–351); not a held-out calibrated uncertainty benchmark.
Metrics: FID, KID, MMD, plus selected class IoUs/mIoU when supplied oracle coarse occupancy. Feature metrics use a trained BEV VAE outdoors and 3D VAE indoors (§IV-A, lines 311–318), not directly comparable to SceneSense image-feature FID numbers.
Table II SemanticKITTI: two-stage generation FID 0.2107; semantic-only generation with ground-truth structure 0.0289; semantic completion 0.0353; SemCity baseline 0.0940. Do NOT compare oracle-stage generation, partial completion, and unconditional baselines as identical tasks. Table IV semantic generation given GT coarse occupancy mIoU 16.9; Table V Replica oracle-coarse mIoU 32.22. Those are not end-to-end partial-scan completion mIoUs. Text explicitly explains mask dilation and imperfect alignment. Tables II/III have differing scale conventions.
§V lines 352–363: structure stage bottleneck, mask dilation, current evaluation OFFLINE; robotic navigation integration is future work. No on-robot navigation success or exploration performance demonstrated.

## Uncertainty audit
Multiple plausible semantic maps and distributional generation quality demonstrated. No held-out occupancy probability reliability, Brier score, NLL, ECE, credible-set coverage or collision-risk calibration reported. Joint coherent map samples could support a downstream uncertainty evaluator, but no such validated decision pipeline shown. Distributional FID/KID/MMD are not conditional posterior calibration. Observations preserved at latent/coarse scale can still misalign high-resolution geometry, explicitly acknowledged in §V.

## Code/license/reproduction status
Paper's GitHub URL redirects to https://github.com/XUJIAZHANG2002/Octree-Scene-Diffusion (API snapshot lookup-4.txt). Public repo with substantive package/configs/scripts, root listing github-0.json, README octree-readme.raw. GitHub reports license null and /license endpoint returns 404 (octree-license.raw): no explicit repo license established; do not assume upstream OctFusion licensing propagates to new code. Paper license is not code permission.
README explicitly states indoor weights are a RETRAIN, not originals used in paper; weights not in repo; per-stage checkpoint/config/latent-scaling contracts and outdoor paper-matching structure checkpoint are described. This is more informative than simply 'code available', but exact downloadable checkpoint availability not independently tested. Dataset licenses remain separate; canonical SemanticKITTI/Replica/CU-Multi terms were not audited here.

## Near-duplicate / novelty risk
Same lab and overlapping authors with SceneSense, but materially different octree/semantic representation; treat as related competitor rather than a new independent uncertainty result. Builds on OctFusion; compare scene completion, not object-generation capability. High overlap for claims of training-free mask conditioning, indoor/outdoor completion, sparse 3D generative maps. A defensible new lane must add calibrated conditional uncertainty and validated planner utility, not only a sparse representation or generation/diversity metric.
