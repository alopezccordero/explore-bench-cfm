#!/bin/bash
# E-B (+ E3): two inference-time fixes for the students, neither needing a retrain.
#
# Both act inside cfm_common.cfm_goal_fn, so the existing cfm_cpp.pt / cfm_mtsp.pt are
# used exactly as they are:
#
#   --nsample N   draw N goals from the flow instead of 1 and keep whichever lands
#                 nearest a real frontier. The flow is stochastic (noise at x0, then
#                 Euler steps), and mean_snap_cells is the strongest predictor of
#                 steps_98 in every table so far, so this trades sampler variance for
#                 accuracy. A local probe on `corridor` moved snap 12.6 -> 7.99.
#
#   --exclude R   keep a robot off frontier cells within R cells of a goal a teammate
#                 already claimed. The teachers forbid two robots sharing a viewpoint
#                 with a hard MILP constraint; the student cannot learn that from
#                 per-robot marginals, and env.goals already held the information that
#                 choose_goal never looked at. Students sit at 0.43-0.47 overlap against
#                 teachers at 0.10-0.13.
#
# ARM 1 isolates --nsample. ARM 2 adds --exclude on top, so arm2 - arm1 is E3's effect.
# ARM 3 checks whether 16 samples is the right number or whether it saturates earlier.
# Every row pairs 1:1 with results_e1.csv, which is this grid at nsample=1, exclude=0.
#
# This also answers a question E-A depends on: if 16 samples recover most of the gap the
# student's error is variance, and geodesic interpolation is a refinement; if they do not,
# the error is bias and E-A is the main event.
#
# No GPU: run_eval.py loads the checkpoint with map_location='cpu' and never moves it, so
# the flow integration is CPU work and tiny next to the simulator step.
#
#SBATCH --job-name=CFM-EB-inference
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --output=CFM-EB-%j.out
#SBATCH --error=CFM-EB-%j.err

set -euo pipefail

source ~/miniconda3/bin/activate
conda activate mujoco-env

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

cd ~/explore-bench-cfm/explore-bench/cfm_example

JOB_ID="${SLURM_JOB_ID:-local-$$}"
RUN_LOG="run_eb_${JOB_ID}.log"
exec > >(tee -a "$RUN_LOG") 2>&1
# shellcheck source=notify.sh
source ./notify.sh

report_init "E-B inference-time fixes" \
"Two free fixes on the existing checkpoints: multi-sample goal selection (--nsample 16)
and teammate exclusion (--exclude 35). 96 runs in 3 arms, expect ~5h.
Arm1 = nsample only, Arm2 = + exclusion, Arm3 = does N saturate.
Decides whether the student's error is variance (then E-A is a refinement) or bias."

stage "preflight"
python --version
python -c "import scipy, torch; print('scipy', scipy.__version__, 'torch', torch.__version__)"
# fail now, not in five hours, if the checkpoints or the new flags are missing
python - <<'PY'
import inspect, torch
from cfm_common import VelocityField, cfm_goal_fn
sig = inspect.signature(cfm_goal_fn).parameters
assert 'nsample' in sig and 'exclude' in sig, 'cfm_common.py is stale: re-scp it'
for c in ('cfm_cpp.pt', 'cfm_mtsp.pt'):
    VelocityField().load_state_dict(torch.load(c, map_location='cpu'))
print('preflight OK: checkpoints load, cfm_goal_fn has nsample/exclude')
PY

MAPS="loop corridor corner room loop_with_corridor room_with_corner"
SEEDS="41 42 43"
CKPTS="cfm_cpp.pt cfm_mtsp.pt"

rm -f results_eb.csv results_eb_exclude.csv results_eb_sweep.csv

# --- ARM 1: multi-sample only (36 runs) -------------------------------------------------
stage "arm 1: --nsample 16"
notify "**E-B** \`$JOB_ID\` arm 1/3: --nsample 16, both checkpoints, 6 maps x 3 seeds."
for CK in $CKPTS; do for MP in $MAPS; do for S in $SEEDS; do
  echo "--- arm1 $CK $MP seed $S"
  python -u run_eval.py --method cfm --ckpt "$CK" --map "$MP" --seed "$S" \
         --nsample 16 --max-steps 2000 --csv results_eb.csv
done; done; done
notify "$(python discord_report.py "E-B arm 1 - nsample 16 (compare snap against E1: cpp 19.0, mtsp 20.8)" results_eb.csv)"

# --- ARM 2: multi-sample + teammate exclusion (36 runs) --------------------------------
# 35 cells is the sensor range, so the robots' claimed regions stop overlapping
stage "arm 2: --nsample 16 --exclude 35"
notify "**E-B** \`$JOB_ID\` arm 2/3: adding --exclude 35. Arm2 minus arm1 is E3's effect on overlap."
for CK in $CKPTS; do for MP in $MAPS; do for S in $SEEDS; do
  echo "--- arm2 $CK $MP seed $S"
  python -u run_eval.py --method cfm --ckpt "$CK" --map "$MP" --seed "$S" \
         --nsample 16 --exclude 35 --max-steps 2000 --csv results_eb_exclude.csv
done; done; done
notify "$(python discord_report.py "E-B arm 2 - nsample 16 + exclude 35 (overlap vs arm 1)" results_eb_exclude.csv)"

# --- ARM 3: does N saturate? (24 runs, two maps bracketing the difficulty range) --------
stage "arm 3: nsample sweep"
notify "**E-B** \`$JOB_ID\` arm 3/3: nsample in {1,4,64} on corridor (easiest) and room_with_corner (hardest)."
for N in 1 4 64; do for MP in corridor room_with_corner; do for S in $SEEDS; do
  echo "--- arm3 nsample=$N $MP seed $S"
  python -u run_eval.py --method cfm --ckpt cfm_cpp.pt --map "$MP" --seed "$S" \
         --nsample "$N" --max-steps 2000 --csv results_eb_sweep.csv
done; done; done

stage "report"
notify "$(python discord_report.py "E-B FINAL" results_eb.csv results_eb_exclude.csv results_eb_sweep.csv)
Baseline to compare (E1, nsample=1, exclude=0):
cfm_cpp s98 654 snap 19.0 overlap 0.473 | cfm_mtsp s98 610 snap 20.8 overlap 0.432.
Arm 3 rows are all cfm_cpp; the nsample used is not in the csv, so read them in order
1,1,1,4,4,4,64,64,64 per map."
