#!/bin/bash
# X6-baselines: every baseline and oracle on the X5 evaluation grid, so the student has
# something to be measured against.
#
#     for M in cost mmpf mtsp milp_cpp greedy_ratio; do
#         sbatch -J "CFM-X6-$M" job_x6_baselines.sh "$M"
#     done
#
# Pass -J so the method lands in the log name: SBATCH directives are read before the
# script runs, so they cannot see $1, and all five would otherwise write CFM-X6-base-*.
#
# One method per submission, five submissions, all independent -- so they run in parallel
# and a crash in one costs one method rather than the set. Each does 6 maps x seeds 41-50
# = 60 runs at --robots 2 --max-steps 2000, which is exactly the X5 grid, so every row
# pairs 1:1 by (map, seed) against results_x5_linear.csv and results_x5_geodesic.csv.
#
# WHY greedy_ratio IS IN THIS LIST. It is new (cfm_teachers.GreedyRatioTeacher): each robot
# takes the candidate with the best true information gain per true travel cell, using the
# same privileged view and the same candidate set as the MILPs. The teacher audit found
# that the two MILP teachers are not limited by their solver or their candidates --
# 385/385 solves proven optimal at gap 0, and the candidate set retains 99.4-100% of
# available cluster gain -- but that both minimise objectives which are not the benchmark
# metric. On seed 41 the greedy rule beat both on the two harder maps:
#
#     map                 milp_cpp     mtsp    greedy      (steps_98 / steps_90)
#     room                 383/298  399/319   514/317
#     corner               549/383  513/413   496/356
#     room_with_corner     834/521  825/674   614/351
#
# That is one seed on three maps and it is not a result yet. This job is what turns it
# into one, or kills it, over 60 paired runs.
#
# Nothing here trains anything and nothing needs a GPU. The teachers' MILPs take 0.01-0.19s
# and the time goes entirely into simulator steps.
#
#SBATCH --job-name=CFM-X6-base
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=10:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --output=CFM-X6-%x-%j.out
#SBATCH --error=CFM-X6-%x-%j.err

set -euo pipefail

METHOD="${1:-}"
case "$METHOD" in
  cost|mmpf|mtsp|milp_cpp|greedy_ratio) ;;
  *) echo "usage: sbatch $0 <cost|mmpf|mtsp|milp_cpp|greedy_ratio>"; exit 2 ;;
esac

source ~/miniconda3/etc/profile.d/conda.sh
conda activate mujoco-env
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd ~/explore-bench-cfm/explore-bench/cfm_example

OUT="results_x6_${METHOD}.csv"
JOB_ID="${SLURM_JOB_ID:-local-$$}"
RUN_LOG="run_x6_${METHOD}_${JOB_ID}.log"
exec > >(tee -a "$RUN_LOG") 2>&1
source ./notify.sh

report_init "X6 baseline: $METHOD" \
"60 runs on the X5 grid -- 6 maps x seeds 41-50, 2 robots, max 2000 steps -- so every row
pairs by (map, seed) against the X5 student results.
greedy_ratio is the new information-ratio oracle from the teacher audit; the audit cleared
the MILPs' solver (385/385 proven optimal, gap 0) and their candidate set (99.4-100% of
cluster gain kept), leaving the objective as the thing to test.
Expect 2-4h. No GPU, no training."

stage "preflight"
python -c "import scipy; print('scipy', scipy.__version__)"
# fail in seconds if the tree is stale, not after an hour of runs under the wrong code
python - "$METHOD" <<'PY'
import sys
m = sys.argv[1]
from cfm_teachers import TEACHERS, SOLVE_STATS
if m in ('mtsp', 'milp_cpp', 'greedy_ratio'):
    assert m in TEACHERS, f'{m} missing from cfm_teachers.TEACHERS (re-scp it): {sorted(TEACHERS)}'
assert 'worst_gap' in SOLVE_STATS, 'cfm_teachers.py predates solver gap reporting (re-scp it)'
src = open('analyse.py').read()
assert "--vs" in src, 'analyse.py predates --vs, so baselines will not pair against the student (re-scp it)'
print(f'preflight OK: {m} available, gap reporting present, analyse.py can pair baselines')
PY

stage "evaluate $METHOD (60 runs)"
rm -f "$OUT"
for MP in loop corridor corner room loop_with_corridor room_with_corner; do
  for S in 41 42 43 44 45 46 47 48 49 50; do
    echo "--- $METHOD $MP seed $S"
    python -u run_eval.py --method "$METHOD" --map "$MP" --seed "$S" \
           --max-steps 2000 --csv "$OUT"
  done
  notify "**X6 $METHOD** \`$JOB_ID\`: $MP done ($(($(wc -l < "$OUT") - 1))/60 runs)"
done

stage "report"
notify "$(python discord_report.py "X6 baseline $METHOD FINAL" "$OUT")
Pair against the student once the five baselines are in:
  python merge_results.py results_x6_*.csv results_x5_linear.csv results_x5_geodesic.csv > results_x6.csv
  python analyse.py results_x6.csv --vs 'x5_linear ns1 ex35 st20'
The --vs form is needed because a baseline label has fewer fields than a student label,
and the automatic pairing only relates configurations with the same number of fields."
