#!/bin/bash
# X4: re-collect at K=64 and keep the complete A* routes, so geodesic interpolation can
# finally be tested with a conditional path that does not cross walls.
#
# WHY. data_x3.npz stores only K=8 waypoints, and train_cfm.py interpolates linearly
# between them. Measured exactly over all 45,291 routes, those chords leave free space on
# 27.8% of examples -- against 31.6% for the plain straight line the geodesic path was
# meant to replace. Worst on room_with_corridor (44.4%) and on long routes (100% above
# 160 cells). So both E-A (-60 steps, 3 seeds) and X1 (+9 steps, p=0.29, 20 seeds) tested
# a treatment that was barely distinguishable from the control. Geodesic interpolation is
# untested, not refuted.
#
# Measured directly on matched room_3 routes, changing only waypoint density:
#
#     route arc     K=8     K=64
#       0- 40      3.7%     0.0%
#      40- 80     12.7%     0.0%
#      80-160     57.0%     0.0%
#        160+    100.0%   100.0%
#     overall     17.5%     5.4%
#
# K=64 fixes everything under 160 cells. The residual is the 6.2% of examples whose route
# exceeds 160 cells, where even 63 segments span 2.5-9 cells and at least one clips a
# corner -- and those are goals ~160+ simulator steps away that the teacher re-solves every
# 10 steps, so they record commitments it never executed. Filter them at training time.
#
# WHAT IS NEW. The full cell-by-cell route is now stored in ragged CSR form:
#     raw_path          (sum of lengths, 2) int16  every route concatenated
#     raw_path_offsets  (N,) int64                 where each route starts
#     raw_path_lengths  (N,) int32                 how many cells each has
# resample() is lossy and irreversible -- the K=8 points in data_x3.npz cannot be refined,
# which is why this needs a fresh collection at all. With the raw cells on disk, K becomes
# a training-time choice and no future K question needs another 4-hour run.
#
# No GPU: collection is numpy/scipy/HiGHS/A*. No training here -- verify the data first.
#
#SBATCH --job-name=CFM-X4-k64
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=11:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=24G
#SBATCH --output=CFM-X4-%j.out
#SBATCH --error=CFM-X4-%j.err

set -euo pipefail

source ~/miniconda3/bin/activate
conda activate mujoco-env
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd ~/explore-bench-cfm/explore-bench/cfm_example

JOB_ID="${SLURM_JOB_ID:-local-$$}"
RUN_LOG="run_x4_${JOB_ID}.log"
exec > >(tee -a "$RUN_LOG") 2>&1
source ./notify.sh

report_init "X4 collection at K=64 with raw routes" \
"Re-collecting so geodesic interpolation can be tested with a valid conditional path.
At K=8 the chords between waypoints left free space on 27.8% of data_x3.npz, vs 31.6%
for a plain straight line -- so there was almost no treatment to detect.
Also storing the complete A* routes (raw_path / offsets / lengths), which makes K a
training-time choice. Expect ~4-5h, no GPU, no training."

stage "preflight"
python --version
python -c "import scipy, torch; print('scipy', scipy.__version__, 'torch', torch.__version__)"
# fail in seconds, not hours, if the tree is stale
python - <<'PY'
src = open('collect_data.py').read()
for need in ("'raw_path'", "raw_path_offsets", "raw_path_lengths",
             'def geodesic_path', '--waypoints', "extra['meta']"):
    assert need in src, f'collect_data.py is stale: missing {need} (re-scp it)'
import os
assert os.path.exists('verify_routes.py'), 'verify_routes.py missing (re-scp it)'
from scipy.optimize import milp
print('preflight OK: raw-route storage, provenance and HiGHS all present')
PY

stage "collect (milp_cpp, --waypoints 64, --max-steps 1500, raw routes kept)"
# No arc cutoff here on purpose: raw_path lets long routes be filtered at training time,
# and dropping them now would be irreversible for no saving worth having.
python -u collect_data.py --method milp_cpp --every 1 --episodes 10 \
       --waypoints 64 --max-steps 1500 --out data_x4.npz

stage "verify raw routes"
# Six checks: CSR integrity, endpoints, 4-connectivity, cells in free space, resample
# fidelity, and chord validity across K. Non-zero exit fails the job, because a dataset
# that silently violates any of these would be trained on and believed.
VERIFY="$(python verify_routes.py data_x4.npz)" && VOK=1 || VOK=0
echo "$VERIFY"

stage "report"
EPISODES="$(python - <<'PY'
import numpy as np
d = np.load('data_x4.npz', allow_pickle=True)
ep, names = d['episodes'], list(d['map_names'])
out = [f"{len(d['cond'])} examples, {len(ep)} episodes, "
       f"{len(d['raw_path'])} raw route cells ({d['raw_path'].nbytes/1e6:.1f} MB)"]
for mi, nm in enumerate(names):
    v = ep[ep[:, 1] == mi]
    if len(v):
        out.append(f"  {nm:20s} cov {v[:,3].mean():5.1%} min {v[:,3].min():5.1%} "
                   f"capped {int(v[:,4].sum())}/{len(v)} steps {v[:,2].mean():.0f}")
out.append(f"total capped: {int(ep[:,4].sum())}/{len(ep)}")
print('\n'.join(out))
PY
)"
echo "$EPISODES"

notify "**X4** \`$JOB_ID\` collection $([ "$VOK" = 1 ] && echo 'and verification complete' || echo 'done but VERIFICATION FAILED')
\`\`\`
$EPISODES
\`\`\`
\`\`\`
$VERIFY
\`\`\`
Read the K=8 row against the K=64 row and the 'line' row: K=8 and the straight line were
nearly the same, which is why geodesic never reproduced. Next: retrain linear vs geodesic
on data_x4.npz with arc filtering, then re-run the X1 grid."

if [ "$VOK" != 1 ]; then
  echo "verification failed -- not treating this dataset as usable"
  exit 1
fi
