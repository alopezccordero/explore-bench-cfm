# Independent round-005 full-text audit — Observation-Aligned Mask Priors

Retrieved 2026-11-16 ~04:11 CST from https://arxiv.org/html/2605.16818v2 (HTTP200). Exact title: **Observation-Aligned Mask Priors for Learning Physical Fields from Authentic Occlusions**. Authors: **Chiyuan Ma; Zihan Zhou; Tianshu Yu**. Identifier arXiv:2605.16818; immutable inspected v2, 29 September 2026. Saved `full.html`, `full.txt`, `blocks.txt`. Official title/authors/version header independently inspected (`full.txt` lines204–225). New S2 batch HTTP429; identifier resolution incomplete, not nonexistent.

## Actual sections inspected
Introduction, §2, §§3.1–3.3 (through limitations of unconditional intersection), §§4.4–4.5 and conclusion. `blocks.txt` lines210–289,370–419 plus full.txt lines260–314:
- Introduction explicitly challenges independent pixel dropout/block heuristics versus authentic occlusion structure, introduces BFN-generated mask priors and observation-aligned intersections.
- §2 specifies a conditional-expectation reconstruction objective and query-positive-exposure premise. Do not confuse positive query exposure with proof of calibrated joint posterior sampling.
- §§3.1–3.3 describe learned mask distributions and intersection, with theorem assumptions and practical sparsity/overlap limitations. This audit did not validate every theorem/proof.
- §4.4 uses spatial query frequency as a **heuristic reliability indicator**, not a generic posterior calibration certificate.
- §4.5 explicitly compares Pixel/Block-wise/other selection and reports controlled partition/backbone comparisons (appendix not independently inspected this round).
- Conclusion reports oceanographic reconstruction MSE/PSNR improvements. These are authors' reported results, not our reproduction. Paper text CC-BY does not establish code/weight/data rights.

## Decision / limits
Generic 'authentic masks rather than random masks' is already occupied, including controlled mask comparisons. C can only be a bounded grid/FM joint-posterior replication or external-validity audit with advisor acceptance. This paper uses BFN for masks and diffusion reconstruction, not the precise learned CFM sampler proposed in C; that distinction does not establish novelty. It concerns authentic satellite observations, which must NOT become project requirements: Alejandro's setting is 2D grid algorithms, no physical sensor constraints. Proposed reveal rules must be stated as simulator interventions and matched to the actual simulator if its API becomes available. No empirical effect, executable evaluator or simulator compatibility was established here.
