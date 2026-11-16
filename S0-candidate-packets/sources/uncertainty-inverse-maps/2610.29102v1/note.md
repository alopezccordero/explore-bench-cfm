# Diffusion Posterior Sampling with Uncertain Forward Models

Verified metadata: Diffusion Posterior Sampling with Uncertain Forward Models
Authors (arXiv citation format): Shangguan, Wentao; Goyal, Vivek K
Persistent identifier/version read: arXiv:2610.29102v1
Version history visible on fetched page: Wed, 21 Oct 2026 02:47:28 UTC (33,378 KB)
Retrieved: 2026-11-16 CST (actual UTC timestamps in scout search_log.jsonl).
Metadata: https://arxiv.org/abs/2610.29102v1
Full text: https://arxiv.org/html/2610.29102v1
Saved full HTML: ../inverse/2610.29102v1-full.raw
Readable extracted text: ../inverse/2610.29102v1.paragraphs.txt and ../inverse/2610.29102v1.txt

## Full-text-supported observations and limits

Inspected §§1–4 and §5 limitations (paragraphs 5–16, 41–63, 127–148, 196–249, 285–298). Diffusion samplers with fixed forward-parameter estimates omit nuisance uncertainty. UAL approximately integrates it into candidate-dependent structured measurement covariance; exact under affine Gaussian nuisance dependence, approximate with nonlinear forward models. Six inverse tasks; uses paired fixed sampler/prior/schedule, CRPS, energy and local variogram scores, plus quadrature likelihood/score comparisons. Claims about imaging improvements remain paper reports, not scout experiments. Average posterior-divergence bound covers likelihood approximation, not sampler error; nuisance independence and fixed Gaussian model are assumptions.
This is sensor/forward uncertainty, not generally calibrating a map posterior. Strong reason to keep known sensor noise versus misspecified sensor model separate. No official reusable code or dataset permissions independently audited; not a seed. A scalar noise sweep alone would miss structured likelihood error.

Status: source note from actual full-text sections, not an abstract-only lead. No empirical reproduction performed. Claim of no metric means not found in inspected protocol, not a proof about all later versions. Paper distribution license does not automatically license software/data.
