# Control-Ready Uncertainty for Trajectory Diffusion

Verified metadata: Control-Ready Uncertainty for Trajectory Diffusion
Authors (arXiv citation format): Xue, Zhiwei; Kam, Jia Yue; Qiu, Jinhang; Cheng, Yifeng; Gursoy, Ege; Wang, Jiaming; Bonnet, Vincent; Soh, Harold
Persistent identifier/version read: arXiv:2610.12431v1
Version history visible on fetched page: Thu, 8 Oct 2026 17:57:01 UTC (3,124 KB)
Retrieved: 2026-11-16 CST (actual UTC timestamps in scout search_log.jsonl).
Metadata: https://arxiv.org/abs/2610.12431v1
Full text: https://arxiv.org/html/2610.12431v1
Saved full HTML: ../inverse/2610.12431v1-full.raw
Readable extracted text: ../inverse/2610.12431v1.paragraphs.txt and ../inverse/2610.12431v1.txt

## Full-text-supported observations and limits

Inspected §§3.1–3.4, 4.1–4.4 (paragraphs 18–165). SCOPE distills score curvature into structured banded+low-rank precision around mode-conditioned diffusion trajectories. Held-out per-horizon scale calibration via NLL; joint trajectory tubes and per-time covariances support MPPI collision costs and exploration. Diag/banded/low-rank/no-calibration ablations, ORCA Y-corridor, Maze2D and Franka Panda. Reports calibration improves dense-crowd SR; therefore broad 'diffusion uncertainty helps decisions' already tested. Local Laplace interpretation depends on near-mode anchor; calibration of approximate local Gaussian tubes is not full multimodal posterior correctness.
This is FUTURE TRAJECTORY uncertainty, not a static environmental map posterior. Has correlation/control ablations but not the same-cell-marginal-preserving shuffle proposed in draft B. Code/checkpoints/license not verified in this pass. S2 successful exact-title record (saved s2-2610.12431.raw). Adjacent competitor, not a seed needed for map-specific minimum.

Status: source note from actual full-text sections, not an abstract-only lead. No empirical reproduction performed. Claim of no metric means not found in inspected protocol, not a proof about all later versions. Paper distribution license does not automatically license software/data.
