#!/bin/bash
# X3: re-collect with a step budget the teacher can actually finish in.
#
# collect_data.py defaulted to --max-steps 600 while evaluation allows 2000. In
# data_ea.npz that truncated 18 of 50 episodes -- including all ten on room_3, which
# averaged 89.0% coverage (min 80.4%) and hit the cap every single time:
#
#     corridor_asym       98.2% mean   0/10 capped
#     corridor_sym        98.1%        0/10
#     room_2              97.7%        2/10
#     room_3              89.0%       10/10
#     room_with_corridor  94.4%        6/10
#
# Because --every 1 records every step, those unfinished tails are over-represented, and
# nothing in the file distinguished them from clean demonstrations. That is a live
# suspect for why linear-on-new-data (688 steps) came out worse than linear-on-old-data
# (654) despite an identical objective.
#
# This run raises the cap to 1500 and stores per-episode provenance (episode index, map,
# steps used, final coverage, whether it hit the cap) plus a per-example (episode, step,
# coverage) row, so a later training run can down-weight stagnant stretches rather than
# discarding whole episodes.
#
# No GPU: collection is numpy/scipy/HiGHS/A*. Training is NOT part of this job -- X1 and
# X2 need no retraining, and the next model should be trained on data whose quality has
# been checked first.
#
#SBATCH --job-name=CFM-X3-collect
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=10:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --output=CFM-X3-%j.out
#SBATCH --error=CFM-X3-%j.err

set -euo pipefail

source ~/miniconda3/bin/activate
conda activate mujoco-env
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd ~/explore-bench-cfm/explore-bench/cfm_example

JOB_ID="${SLURM_JOB_ID:-local-$$}"
RUN_LOG="run_x3_${JOB_ID}.log"
exec > >(tee -a "$RUN_LOG") 2>&1
source ./notify.sh

report_init "X3 collection with a 1500-step budget" \
"Re-collecting with --max-steps 1500 and per-episode provenance.
At 600 steps, 18/50 episodes truncated (all ten on room_3, mean coverage 89%).
Teacher milp_cpp, reverted 5d5083c build. Expect ~4-5h, no training in this job."

stage "preflight"
python -c "
src = open('collect_data.py').read()
for need in ('--waypoints', 'def geodesic_path', \"extra['meta']\"):
    assert need in src, f'collect_data.py is stale: missing {need}'
from scipy.optimize import milp
print('preflight OK')"

stage "collect (milp_cpp, --max-steps 1500 --every 1 --episodes 10 --waypoints 8)"
python -u collect_data.py --method milp_cpp --every 1 --episodes 10 --waypoints 8 \
       --max-steps 1500 --out data_x3.npz

stage "report"
SUMMARY="$(python - <<'PY'
import numpy as np
d = np.load('data_x3.npz', allow_pickle=True)
ep = d['episodes']; names = list(d['map_names'])
lines = [f"{len(d['cond'])} examples, {len(ep)} episodes"]
for mi, nm in enumerate(names):
    v = ep[ep[:, 1] == mi]
    if len(v):
        lines.append(f"  {nm:20s} cov {v[:,3].mean():5.1%} min {v[:,3].min():5.1%} "
                     f"capped {int(v[:,4].sum())}/{len(v)}  mean steps {v[:,2].mean():.0f}")
lines.append(f"total capped: {int(ep[:,4].sum())}/{len(ep)}  (was 18/50 at 600 steps)")
print('\n'.join(lines))
PY
)"
echo "$SUMMARY"
notify "**X3** \`$JOB_ID\` collection done:
\`\`\`
$SUMMARY
\`\`\`
Compare with the 600-step run: room_3 was 89.0% mean, 10/10 capped.
If room_3 is still capping, the teacher is stuck rather than slow and the planner needs
the diagnosis, not a bigger budget."
