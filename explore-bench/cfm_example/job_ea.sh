#!/bin/bash
# E-A: obstacle-aware (geodesic) interpolation for the flow-matching objective.
# Collection, training and evaluation in one job.
#
# WHY. train_cfm.py interpolated along the straight line x_t = (1-t) x0 + t x1. That
# assumes a convex space, and this one is full of walls: measured on data_cpp.npz, the
# segment crosses a wall cell in 63% of examples and 23% of the average path is wall or
# not-known-free. So most of the velocity field was fitted at states the robot can never
# occupy, and then integrated from them at inference -- which is what the large
# mean_snap_cells in results.csv (12-30 cells) is measuring, and snap is the strongest
# predictor of steps_98 in every table so far.
#
# WHAT. collect_data.py --waypoints now stores the geodesic route from robot to goal,
# traced down the geodesic_dist field it already computes for the frontier snap (so it is
# nearly free). train_cfm.py interpolates along that route and targets its tangent.
# Verified locally: 0% of waypoint chords leave free space at cell resolution, against
# 63% for the straight line.
#
# STAGES
#   1. collect   data_ea.npz with routes, milp_cpp teacher, same settings as data_cpp.npz
#   2. train     two models on the SAME data -- --linear (control) and geodesic (treatment)
#   3. evaluate  both on 6 test maps x 3 seeds
#
# The control arm matters: data_ea.npz is freshly collected, so comparing the geodesic
# model against the old cfm_cpp.pt would confound the objective change with the data
# change. Stage 2 trains both from one dataset, which isolates the interpolation.
#
#SBATCH --job-name=CFM-EA-geodesic
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=16:00:00
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --output=CFM-EA-%j.out
#SBATCH --error=CFM-EA-%j.err

set -euo pipefail

source ~/miniconda3/bin/activate
conda activate mujoco-env

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

cd ~/explore-bench-cfm/explore-bench/cfm_example

JOB_ID="${SLURM_JOB_ID:-local-$$}"
RUN_LOG="run_ea_${JOB_ID}.log"
exec > >(tee -a "$RUN_LOG") 2>&1          # so a failure can quote the real error
# shellcheck source=notify.sh
source ./notify.sh

report_init "E-A geodesic interpolation" \
"Testing whether interpolating along the geodesic route instead of the straight line
fixes the student's snap distance. 63% of the old training segments crossed a wall.
Stages: collect routes -> train linear vs geodesic on the same data -> evaluate both.
Expect ~7h: ~2h collect, minutes to train on GPU, ~4h for 36 evaluations."

stage "preflight"
python --version
python -c "import scipy, torch; print('scipy', scipy.__version__, 'torch', torch.__version__, 'cuda', torch.cuda.is_available())"
nvidia-smi || true
# check the flags this job depends on actually exist, so it fails in seconds not hours
python - <<'PY'
import re
src = open('collect_data.py').read()
assert '--waypoints' in src, 'collect_data.py is stale: no --waypoints (re-scp it)'
assert 'def geodesic_path' in src, 'collect_data.py is stale: no geodesic_path'
src = open('train_cfm.py').read()
assert '--linear' in src and 'geodesic interpolation' in src, 'train_cfm.py is stale'
from scipy.optimize import milp  # the teacher needs HiGHS
print('preflight OK: --waypoints, geodesic_path, --linear, HiGHS all present')
PY

MAPS="loop corridor corner room loop_with_corridor room_with_corner"
SEEDS="41 42 43"

# ---------------------------------------------------------------- 1. collect with routes
stage "collect (milp_cpp teacher, --every 1 --episodes 10 --waypoints 8)"
notify "**E-A** \`$JOB_ID\` stage 1/3: collecting \`data_ea.npz\` with geodesic routes.
Teacher milp_cpp (reverted 5d5083c build), 5 training maps x 10 episodes, every step."
python -u collect_data.py --method milp_cpp --every 1 --episodes 10 \
       --waypoints 8 --out data_ea.npz
python - <<'PY'
import numpy as np
d = np.load('data_ea.npz')
assert 'path' in d.files, 'no route array was stored'
print('data_ea.npz:', {k: tuple(d[k].shape) for k in d.files})
PY
notify "**E-A** \`$JOB_ID\` stage 1/3 done: $(python -c "
import numpy as np; d=np.load('data_ea.npz')
print(f\"{len(d['cond'])} examples, {d['path'].shape[1]} waypoints per route\")")"

# ---------------------------------------------------------------- 2. train both objectives
stage "train (control: --linear)"
notify "**E-A** \`$JOB_ID\` stage 2/3: training. Control arm first (straight line)."
python -u train_cfm.py --data data_ea.npz --linear --out cfm_ea_linear.pt

stage "train (treatment: geodesic)"
python -u train_cfm.py --data data_ea.npz --out cfm_ea_geodesic.pt
notify "**E-A** \`$JOB_ID\` stage 2/3 done: \`cfm_ea_linear.pt\` and \`cfm_ea_geodesic.pt\` trained on the same data."

# ---------------------------------------------------------------- 3. evaluate both
stage "evaluate (36 runs)"
notify "**E-A** \`$JOB_ID\` stage 3/3: evaluating both models on 6 maps x 3 seeds."
rm -f results_ea.csv
for CK in cfm_ea_linear.pt cfm_ea_geodesic.pt; do
  for MP in $MAPS; do
    for S in $SEEDS; do
      echo "--- $CK $MP seed $S"
      python -u run_eval.py --method cfm --ckpt "$CK" --map "$MP" --seed "$S" \
             --max-steps 2000 --csv results_ea.csv
    done
  done
  notify "$(python discord_report.py "E-A partial - $CK done" results_ea.csv)"
done

stage "report"
notify "$(python discord_report.py "E-A FINAL - geodesic vs linear interpolation, same data" results_ea.csv)
Read the \`snap\` column: that is what this experiment was aimed at.
Compare against results_e1.csv (old data, straight line): cfm_cpp snap 19.0 / s98 654."
