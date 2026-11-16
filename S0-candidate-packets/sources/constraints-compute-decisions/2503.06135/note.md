# FlowMP: Learning Motion Fields for Robot Planning with Conditional Flow Matching

Authors: Khang Nguyen; An T. Le; Tien Pham; Manfred Huber; Jan Peters; Minh Nhat Vu
First-posted year: 2025; inspected version: 2503.06135v1.
Retrieved: 2026-11-16 CST (request timestamps in sibling logs).
Official full text: https://arxiv.org/html/2503.06135v1
Persistent ID: arXiv:2503.06135; https://arxiv.org/abs/2503.06135v1
Actual saved full-text extraction: /home/sircordero/research/s0-overnight-2026-11-16/sources/constraints-compute-decisions/planning-agent/2503.06135-fulltext.txt
Database resolution: OpenAlex resolved https://openalex.org/W6891958636; Semantic Scholar HTTP 429 (rate limit, not absence). OpenAlex metadata title checked; authors normalized to full text. Database publication year may differ from first-posted year.

## Full-text-backed reading note and boundaries

 (additional retrieved full text, useful baseline provenance)
- Full text also retrieved: https://arxiv.org/html/2503.06135v1 ; title FlowMP: Learning Motion Fields for Robot Planning with Conditional Flow Matching; authors Khang Nguyen, An T. Le, Tien Pham, Manfred Huber, Jan Peters, Minh Nhat Vu. Local `2503.06135-fulltext.raw/.txt`.
- Sec. IV setup, local line 293: 25 candidates, lengths 64/128/256, 30 inference steps for both MPD and FlowMP, NVIDIA RTX 4070. Sec. IV-D reports inference time. These are fixed settings, not a three-way equal-budget study.
- Repo: https://github.com/mkhangg/flow_mp ; API tree verified at 81e70afb58073182a854f12c858242e65713eb6e (`evaluator-0.raw`, `evaluator-1.raw`, `evaluator-2.raw`).
- Inference/training notebook: https://github.com/mkhangg/flow_mp/blob/81e70afb58073182a854f12c858242e65713eb6e/scripts/train_flow/train_env.ipynb (path verified in API tree, notebook itself not executed/read in this audit).
- Geometry evaluator inspected: https://github.com/mkhangg/flow_mp/blob/81e70afb58073182a854f12c858242e65713eb6e/flow_mp/env/obstacle.py (`code-3.raw`). `CollisionEnvironment.getTrajDist(pts)` computes intersection LENGTH between Shapely `LineString(pts)` and the buffered obstacle union. This is concrete segment-geometry machinery, not only waypoint occupancy. However intersection length alone does not define boundary-touch collision policy; exact touch semantics need explicit treatment. Constructor default safety_margin=0.00.
- Occupancy generator inspected: https://github.com/mkhangg/flow_mp/blob/81e70afb58073182a854f12c858242e65713eb6e/flow_mp/env/env_functions.py (`code-2.raw`).
- This is a release unlike the SafeFlow placeholder; no claim of turnkey reproduction or pretrained-checkpoint sufficiency has been verified. README typo links requirements.text while instruction names requirements.txt.


Parent rechecked public repo/README and license endpoint: license null / 404; checkpoint usability NOT established. README guarantee language is not accepted as an independent safety proof.

No local evaluator execution or source empirical replication was performed. Local source paths in copied delegated notes are relative to their original planning-agent/maps-agent folders, not this id directory. The complete delegated note remains the provenance for those references.
