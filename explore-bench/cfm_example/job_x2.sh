#!/bin/bash
# X2: how many Euler steps does the flow need?
#
# sample_goals() hardcodes 20 forward-Euler steps and nothing exposed it. Measured offline
# on 3000 training examples, endpoint error against the teacher goal:
#
#     steps     linear   geodesic
#        20       3.45       8.69
#        50       3.44       7.64
#       100       3.44       7.35
#       200       3.44       7.24
#
# Linear is exact at any step count -- its conditional path is a straight line. The
# geodesic model learns a curved field and loses ~17% of its endpoint accuracy to
# under-integration. So E-A compared a correctly integrated model against an
# under-integrated one.
#
# BUT do not expect this to translate: geodesic's endpoint error is twice linear's and it
# still won on exploration (628 vs 688 steps). Endpoint accuracy has now failed to predict
# exploration quality three separate times -- multi-sampling cut snap 12.6 -> 5.8 while
# steps rose, and snap barely moved in E-A while steps fell 9%. This measures whether the
# free knob helps behaviour, and it is equally informative if it does not.
#
#SBATCH --job-name=CFM-X2-euler
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --array=0-4
#SBATCH --output=CFM-X2-%A_%a.out
#SBATCH --error=CFM-X2-%A_%a.err

set -euo pipefail

source ~/miniconda3/bin/activate
conda activate mujoco-env
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd ~/explore-bench-cfm/explore-bench/cfm_example

SEED=$((41 + SLURM_ARRAY_TASK_ID))
JOB_ID="${SLURM_ARRAY_JOB_ID:-local}_${SLURM_ARRAY_TASK_ID:-0}"
RUN_LOG="run_x2_${JOB_ID}.log"
OUT="results_x2_seed${SEED}.csv"
exec > >(tee -a "$RUN_LOG") 2>&1
source ./notify.sh

if [ "${SLURM_ARRAY_TASK_ID:-0}" = "0" ]; then
  report_init "X2 Euler steps" \
"Does integrating the flow more finely help the geodesic model in the simulator?
2 checkpoints x steps{20,50,100} x 6 maps x 5 seeds = 180 runs, one task per seed.
Offline the geodesic endpoint error improves 8.69 -> 7.35 cells from 20 to 100 steps;
whether that shows up in exploration is the open question."
else
  trap - EXIT
fi

stage "preflight seed $SEED"
python -c "
import inspect
from cfm_common import cfm_goal_fn
assert 'steps' in inspect.signature(cfm_goal_fn).parameters, 'cfm_common.py is stale'
import csv
h = next(csv.reader(open('results_ec.csv')))
print('preflight OK')"

rm -f "$OUT"
MAPS="loop corridor corner room loop_with_corridor room_with_corner"

stage "evaluate seed $SEED"
for CK in cfm_ea_geodesic.pt cfm_ea_linear.pt; do
  for ST in 20 50 100; do
    for MP in $MAPS; do
      echo "--- $CK steps=$ST $MP seed $SEED"
      python -u run_eval.py --method cfm --ckpt "$CK" --map "$MP" --seed "$SEED" \
             --steps "$ST" --max-steps 2000 --csv "$OUT"
    done
  done
done

echo "seed $SEED done: $(($(wc -l < "$OUT") - 1)) rows"
if [ "${SLURM_ARRAY_TASK_ID:-0}" = "0" ]; then
  notify "**X2** task 0 (seed $SEED) done. Merge with:
python merge_results.py results_x2_seed*.csv > results_x2.csv"
fi
