#!/bin/bash
# X1: coordination x sampling x interpolation, at power that can actually settle it.
#
# WHY. Every ambiguous result so far has been ambiguous for the same reason: 6 maps x 3
# seeds cannot resolve the effects we care about. Paired sign tests on the October runs
# gave exclusion p=0.031, geodesic p=0.238, and nothing survives a Holm correction across
# the family. From the observed paired spread (mean -99, sd 174 steps for exclusion), 3
# seeds gives 68% power if the true effect is as large as measured and only 23% if it is
# half that; 20 seeds gives 100% and 88%. So this is the same questions, properly powered.
#
# PRIMARY COMPARISON, DECLARED BEFORE RUNNING:
#   exclude 35 vs exclude 0, at nsample 1, on cfm_ea_geodesic.pt,
#   paired by (map, seed), metric steps_98 with non-completions charged max_steps.
# Everything else is secondary and reported with effect sizes and intervals.
#
# DESIGN NOTE. The geodesic comparison uses cfm_ea_linear.pt vs cfm_ea_geodesic.pt, which
# were trained on the SAME dataset. Comparing cfm_cpp.pt against the geodesic model would
# confound the objective with the data they were trained on; cfm_cpp.pt is carried only as
# a practical reference point, not as the geodesic comparator.
#
# One array task per seed, each writing its own csv. run_eval.py appends, so 20 tasks
# sharing one file would interleave rows; merge afterwards with merge_results.py.
#
#SBATCH --job-name=CFM-X1-grid
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=08:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --array=0-19
#SBATCH --output=CFM-X1-%A_%a.out
#SBATCH --error=CFM-X1-%A_%a.err

set -euo pipefail

source ~/miniconda3/bin/activate
conda activate mujoco-env
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd ~/explore-bench-cfm/explore-bench/cfm_example

SEED=$((41 + SLURM_ARRAY_TASK_ID))
JOB_ID="${SLURM_ARRAY_JOB_ID:-local}_${SLURM_ARRAY_TASK_ID:-0}"
RUN_LOG="run_x1_${JOB_ID}.log"
OUT="results_x1_seed${SEED}.csv"
exec > >(tee -a "$RUN_LOG") 2>&1
source ./notify.sh

# only the first task narrates, or twenty tasks spam the channel
if [ "${SLURM_ARRAY_TASK_ID:-0}" = "0" ]; then
  report_init "X1 powered grid" \
"3 checkpoints x nsample{1,4} x exclude{0,35} x 6 maps x 20 seeds = 1440 runs.
Primary: exclude 35 vs 0 at nsample 1 on cfm_ea_geodesic.pt, paired by (map,seed).
One array task per seed; ~3h per task, all 20 in parallel."
else
  trap - EXIT     # non-zero tasks stay quiet
fi

stage "preflight seed $SEED"
python - <<'PY'
import inspect, torch
from cfm_common import VelocityField, cfm_goal_fn
assert 'steps' in inspect.signature(cfm_goal_fn).parameters, 'cfm_common.py is stale'
import csv, subprocess
for c in ('cfm_cpp.pt', 'cfm_ea_linear.pt', 'cfm_ea_geodesic.pt'):
    VelocityField().load_state_dict(torch.load(c, map_location='cpu'))
print('preflight OK')
PY

rm -f "$OUT"
MAPS="loop corridor corner room loop_with_corridor room_with_corner"

stage "evaluate seed $SEED"
for CK in cfm_ea_geodesic.pt cfm_ea_linear.pt cfm_cpp.pt; do
  for NS in 1 4; do
    for EX in 0 35; do
      for MP in $MAPS; do
        echo "--- $CK ns=$NS ex=$EX $MP seed $SEED"
        python -u run_eval.py --method cfm --ckpt "$CK" --map "$MP" --seed "$SEED" \
               --nsample "$NS" --exclude "$EX" --max-steps 2000 --csv "$OUT"
      done
    done
  done
done

echo "seed $SEED done: $(($(wc -l < "$OUT") - 1)) rows in $OUT"
if [ "${SLURM_ARRAY_TASK_ID:-0}" = "0" ]; then
  notify "**X1** task 0 (seed $SEED) finished: $(($(wc -l < "$OUT") - 1)) rows.
When every task is done:  python merge_results.py results_x1_seed*.csv > results_x1.csv
then:  python analyse.py results_x1.csv"
fi
