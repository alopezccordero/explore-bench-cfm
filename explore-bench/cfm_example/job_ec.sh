#!/bin/bash
# E-C: the reference line for results_e1.csv.
#
# E1 evaluated the two students on all six test maps x seeds 41-43, but the baselines and
# teachers only exist for `corner` (seeds 41-43) and `room` (seed 0). Without the rest,
# "the student averages 654 steps" cannot be read as good or bad. This fills the grid:
#
#     4 methods (cost, mmpf, mtsp, milp_cpp) x 6 test maps x 3 seeds = 72 runs
#
# The teachers are the reverted 5d5083c build, which reproduces the mtsp 513 / milp_cpp
# 549 rows already in results.csv on corner seed 41 -- verified to the digit. That keeps
# these rows comparable to the ones already recorded instead of being a second,
# incompatible set.
#
# No GPU: every method here is numpy/scipy/HiGHS/A* on the CPU. Nothing is trained and
# nothing is collected.
#
#SBATCH --job-name=CFM-EC-baselines
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=10:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --output=CFM-EC-%j.out
#SBATCH --error=CFM-EC-%j.err

set -euo pipefail

source ~/miniconda3/bin/activate
conda activate mujoco-env

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

cd ~/explore-bench-cfm/explore-bench/cfm_example

JOB_ID="${SLURM_JOB_ID:-local-$$}"
RUN_LOG="run_ec_${JOB_ID}.log"
exec > >(tee -a "$RUN_LOG") 2>&1
# shellcheck source=notify.sh
source ./notify.sh

report_init "E-C baselines + teachers" \
"Filling the reference line E1 is missing: cost, mmpf, mtsp, milp_cpp on all 6 test maps
x seeds 41-43 = 72 runs. Teachers are the reverted 5d5083c build so these rows match the
corner numbers already in results.csv. Expect ~2h."

stage "preflight"
python --version
python -c "import scipy, torch; print('scipy', scipy.__version__, 'torch', torch.__version__)"
# prove a sparse MILP actually solves, not merely that the import resolves: the teachers
# are useless without HiGHS and this fails in seconds rather than two hours in
python - <<'PY'
import numpy as np
from scipy import sparse
from scipy.optimize import Bounds, LinearConstraint, milp
A = sparse.coo_matrix(([1., 1.], ([0, 0], [0, 1])), shape=(1, 2)).tocsr()
r = milp(c=np.array([1., 2.]), constraints=LinearConstraint(A, [1], [np.inf]),
         integrality=np.array([1, 1]), bounds=Bounds(np.zeros(2), np.ones(2)),
         options={'time_limit': 5, 'presolve': True})
assert r.x is not None, r.message
print('HiGHS sparse MILP OK')
PY

# run_eval.py refuses to append to a csv whose header does not match, rather than
# silently misaligning rows, so start clean
rm -f results_ec.csv

MAPS="loop corridor corner room loop_with_corridor room_with_corner"
SEEDS="41 42 43"

# cheap methods first: an environment or map-path mistake then shows in minutes
for METHOD in cost mmpf milp_cpp mtsp; do
  stage "evaluate $METHOD"
  notify "**E-C** \`$JOB_ID\`: starting **$METHOD** (6 maps x 3 seeds)."
  for MP in $MAPS; do
    for S in $SEEDS; do
      echo "--- $METHOD $MP seed $S"
      python -u run_eval.py --method "$METHOD" --map "$MP" --seed "$S" \
             --max-steps 2000 --csv results_ec.csv
    done
  done
  notify "$(python discord_report.py "E-C partial - $METHOD done" results_ec.csv)"
done

stage "report"
notify "$(python discord_report.py "E-C FINAL - baselines and teachers, 6 maps x 3 seeds" results_ec.csv)
For comparison, E1's students over the same grid:
cfm_cpp s98 654 (sd 318), cfm_mtsp s98 610 (sd 202), overlap 0.47 / 0.43."
