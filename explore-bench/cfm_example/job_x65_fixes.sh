#!/bin/bash
# X6.5: corrected teachers against their originals, identical maps and seeds, objectives
# untouched. Quantifies what the implementation fixes alone are worth.
#
#     sbatch job_x65_fixes.sh                  # all six arms as one array
#     sbatch --array=1,3 job_x65_fixes.sh      # just mtsp_fix and milp_cpp_fix
#     sbatch job_x65_fixes.sh milp_cpp_fix     # one named arm, no array
#
# A 6-task array, 60 runs each (6 maps x seeds 41-50, 2 robots, 2000 steps) -- the same
# grid as X5 and X6, so every row pairs 1:1 by (map, seed) with every arm already
# collected. The tasks are independent, so SLURM runs them in parallel exactly as six
# separate submissions would, with one job id to watch and cancel.
#
#     task 0  mtsp              task 1  mtsp_fix
#     task 2  milp_cpp          task 3  milp_cpp_fix
#     task 4  greedy_ratio      task 5  greedy_ratio_fix
#
# An explicit method argument overrides the array index, so a single arm can be re-run
# without editing anything.
#
# WHAT THE FIXES ARE. `fixes=True` turns on exactly two corrections and changes no
# objective, no candidate cap, no replan cadence and no goal tolerance:
#
#   X6.1  a frontier cluster's representative is chosen from that cluster's own valid,
#         reachable members, instead of being produced by clipping a medoid coordinate
#         into the safe rim -- which can in principle yield a cell that is not a frontier
#         and not even free.
#   X6.2  the greedy mTSP fallback tries every robot, shortest route first, and stops only
#         when no robot can reach any remaining candidate. The original took the
#         shortest-route robot alone and gave up if that one robot was blocked, discarding
#         candidates another robot could have served.
#
# WHY THE ORIGINALS ARE RE-RUN rather than paired against results_x6_*.csv. Adding the
# instrumentation touched __call__ and greedy() in the shared code path. On corner seed 41
# all four arms are bit-identical -- 513/513 and 549/549, same overlap, same solve counts,
# same replan breakdown -- but one seed is not proof over 60, and an uninstrumented
# baseline is the only way to show the measurement did not perturb what it measures.
# Pairing the new `mtsp` rows against results_x6_mtsp.csv is then a free check that it did
# not.
#
# EXPECT NO EFFECT. Both fixes are latent on everything measured so far: the clip never
# produced an invalid representative in 1490 examined, and the greedy fallback only runs
# when HiGHS fails, which it did on 0 of 6310 solves. The honest prior is that this
# changes nothing, and a null here is the useful result -- it rules the implementation out
# as an explanation and leaves the receding-horizon replanning, which X6.4 shows fires on
# a timer 76-85% of the time while the robots essentially never arrive at a goal.
#
# No GPU, no training.
#
#SBATCH --job-name=CFM-X65
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --array=0-5
#SBATCH --time=10:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --output=CFM-X65-%A_%a.out
#SBATCH --error=CFM-X65-%A_%a.err
# %A_%a rather than the method name: SBATCH directives are read before the script runs, so
# they cannot see the array index resolve to a method. The method is echoed as the first
# line of every log and is in the run log's filename.

set -euo pipefail

ARMS=(mtsp mtsp_fix milp_cpp milp_cpp_fix greedy_ratio greedy_ratio_fix)
# an explicit argument wins, so one arm can be re-run without an array
METHOD="${1:-}"
if [ -z "$METHOD" ]; then
  IDX="${SLURM_ARRAY_TASK_ID:-}"
  if [ -z "$IDX" ]; then
    echo "no method given and not an array task."
    echo "usage: sbatch $0            # all six arms"
    echo "       sbatch $0 <method>   # one arm: ${ARMS[*]}"
    exit 2
  fi
  if [ "$IDX" -ge "${#ARMS[@]}" ]; then
    echo "array index $IDX is out of range: only ${#ARMS[@]} arms exist (0-$((${#ARMS[@]} - 1)))"
    exit 2
  fi
  METHOD="${ARMS[$IDX]}"
fi
echo "=== X6.5 arm: $METHOD  (job ${SLURM_JOB_ID:-local}, array task ${SLURM_ARRAY_TASK_ID:-none}) ==="

case "$METHOD" in
  mtsp|mtsp_fix|milp_cpp|milp_cpp_fix|greedy_ratio|greedy_ratio_fix) ;;
  *) echo "usage: sbatch $0 <mtsp|mtsp_fix|milp_cpp|milp_cpp_fix|greedy_ratio|greedy_ratio_fix>"
     exit 2 ;;
esac

# conda.sh rather than bin/activate: a sourced script inherits the caller's positional
# parameters, and bin/activate reads $1 as the environment name -- which is what killed
# the first X6 batch with "EnvironmentNameNotFound: cost".
source ~/miniconda3/etc/profile.d/conda.sh
conda activate mujoco-env
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd ~/explore-bench-cfm/explore-bench/cfm_example

OUT="results_x65_${METHOD}.csv"
JOB_ID="${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-local-$$}}${SLURM_ARRAY_TASK_ID:+_$SLURM_ARRAY_TASK_ID}"
RUN_LOG="run_x65_${METHOD}_${JOB_ID}.log"
exec > >(tee -a "$RUN_LOG") 2>&1
source ./notify.sh

report_init "X6.5 implementation fixes: $METHOD" \
"60 runs on the X5/X6 grid -- 6 maps x seeds 41-50, 2 robots, max 2000 steps.
Pairs 1:1 against its twin arm and against every result already collected.
The fixes are X6.1 (representative chosen from valid reachable cluster members instead of
a clipped coordinate) and X6.2 (greedy fallback tries every robot before giving up). No
objective, cap, cadence or tolerance is changed.
Both are latent on everything measured so far, so a null is the expected and useful result.
Expect 2-4h. No GPU, no training."

stage "preflight"
python -c "import scipy; print('scipy', scipy.__version__)"
python - "$METHOD" <<'PY'
import sys
m = sys.argv[1]
from cfm_teachers import TEACHERS, SOLVE_STATS
assert m in TEACHERS, f'{m} missing from TEACHERS (re-scp cfm_teachers.py): {sorted(TEACHERS)}'
for need in ('fallbacks', 'resolves', 'max_seconds', 'cand_total'):
    assert need in SOLVE_STATS, f'cfm_teachers.py predates X6.3 instrumentation ({need} missing)'
# the fix arms must actually have the fixes on, and the originals must not
want = m.endswith('_fix')
got = '_Fixed' in [c.__name__ for c in TEACHERS[m].__mro__]
assert got == want, f'{m}: fixes mixin present={got} but expected {want}'
assert 'X6.1' in open('cfm_teachers.py').read(), 'cfm_teachers.py has no X6.1 fix'
assert 'X6.2' in open('cfm_teachers.py').read(), 'cfm_teachers.py has no X6.2 fix'
print(f'preflight OK: {m}, fixes={want}, X6.3 instrumentation present')
PY

stage "evaluate $METHOD (60 runs)"
rm -f "$OUT"
for MP in loop corridor corner room loop_with_corridor room_with_corner; do
  for S in 41 42 43 44 45 46 47 48 49 50; do
    echo "--- $METHOD $MP seed $S"
    python -u run_eval.py --method "$METHOD" --map "$MP" --seed "$S" \
           --max-steps 2000 --csv "$OUT"
  done
  notify "**X6.5 $METHOD** \`$JOB_ID\`: $MP done ($(($(wc -l < "$OUT") - 1))/60 runs)"
done

stage "report"
# X6.3 wants fallback frequency and solve behaviour aggregated, not just per run
SOLVER="$(grep -h '^solver:' "$RUN_LOG" | python -c "
import re, sys
s = f = p = sub = 0; sec = 0.0; mx = 0.0; cand = []
for l in sys.stdin:
    m = re.search(r'(\d+) solves, (\d+) not proven optimal, (\d+) infeasible, worst gap '
                  r'([\d.e+-]+), ([\d.]+)s total / ([\d.]+)s max, (\d+)/(\d+) fell back', l)
    if m:
        s += int(m.group(1)); sub += int(m.group(2)); sec += float(m.group(5))
        mx = max(mx, float(m.group(6))); f += int(m.group(7)); p += int(m.group(8))
    c = re.search(r'([\d.]+) candidates per plan', l)
    if c: cand.append(float(c.group(1)))
if s:
    print(f'{s} solves over 60 runs, {sub} not proven optimal, {f}/{p} fell back to greedy')
    print(f'{sec:.0f}s total in HiGHS, {mx:.2f}s worst single solve')
    print(f'{sum(cand)/len(cand):.1f} candidates per plan (mean of per-run means)')
else:
    print('no MILP solves (greedy_ratio uses none)')
")"
REPLANS="$(grep -h '^replans:' "$RUN_LOG" | python -c "
import re, sys, collections
c = collections.Counter(); runs = 0
for l in sys.stdin:
    runs += 1
    for k, v in re.findall(r'(\w+) (\d+) \(', l): c[k] += int(v)
t = sum(c.values()) or 1
print(f'{t} replans over {runs} runs: ' + '  '.join(f'{k} {v} ({100*v/t:.0f}%)'
      for k, v in c.most_common()))
")"
echo "$SOLVER"; echo "$REPLANS"

notify "$(python discord_report.py "X6.5 $METHOD FINAL (implementation fixes)" "$OUT")
\`\`\`
$SOLVER
$REPLANS
\`\`\`
Pair the arms once all six are in:
  python merge_results.py results_x65_*.csv > results_x65.csv
  python analyse.py results_x65.csv
  python analyse_by_map.py results_x65.csv --contrast mtsp mtsp_fix --contrast milp_cpp milp_cpp_fix
And check the instrumentation did not perturb the baseline -- both files carry the same
method label, so merging pools them into one group instead of contrasting them; compare
the rows directly:
  diff <(cut -d, -f1-4,10-16 results_x65_mtsp.csv | sort) \
       <(cut -d, -f1-4,10-16 results_x6_mtsp.csv  | sort) && echo IDENTICAL"
