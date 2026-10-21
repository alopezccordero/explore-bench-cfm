#!/bin/bash
# X5-linear: train on data_x4.npz with STRAIGHT-LINE interpolation, then evaluate.
#
# This is the control arm. It interpolates along x_t = (1-t)x0 + t x1 and targets x1 - x0,
# the original conditional flow matching objective, ignoring the stored route entirely.
# Its twin, job_x5_geodesic.sh, follows the 64-waypoint geodesic route instead. Both read
# the same dataset, apply the same arc filter and evaluate on the same maps, seeds and
# exclusion settings, so the two result files pair 1:1 by (map, seed, exclude) and the
# conditional path is the only difference between them.
#
# The control matters because data_x4.npz is a fresh collection. Comparing a geodesic model
# trained on it against cfm_cpp.pt or cfm_ea_linear.pt would confound the objective with
# the data -- the mistake that made the X1 geodesic cells uninterpretable. Training both
# arms from one dataset isolates the interpolation.
#
# --max-arc 160 is applied here too, dropping the same 3,608 examples (41,683 of 45,291
# kept). It is not needed for this arm -- a straight line is a straight line at any length
# -- but the arms must see identical data for the pairing to mean anything.
#
# Evaluated at exclude 0 and 35: coordination is the one established effect (p=0.0001 in
# X1), and whether the interpolation matters once robots stop picking redundant goals is a
# different question from whether it matters without that.
#
# No array job. Training uses the GPU for ~30 min; the ~3h of evaluation is CPU-only and
# leaves it idle, which is the cost of keeping this to a single self-contained script.
#
#SBATCH --job-name=CFM-X5-linear
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=09:00:00
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=32G
#SBATCH --output=CFM-X5-linear-%j.out
#SBATCH --error=CFM-X5-linear-%j.err

set -euo pipefail

source ~/miniconda3/bin/activate
conda activate mujoco-env
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd ~/explore-bench-cfm/explore-bench/cfm_example

CKPT=cfm_x5_linear.pt
OUT=results_x5_linear.csv
JOB_ID="${SLURM_JOB_ID:-local-$$}"
RUN_LOG="run_x5_linear_${JOB_ID}.log"
exec > >(tee -a "$RUN_LOG") 2>&1
source ./notify.sh

report_init "X5 linear interpolation (control)" \
"Control arm for the geodesic test. Training on data_x4.npz with --max-arc 160 (41683 of
45291 examples kept, same as the geodesic arm), then evaluating at exclude 0 and 35 over
6 maps x 10 seeds = 120 runs.
Pairs against job_x5_geodesic.sh on the same data, seeds and settings.
Expect ~30 min training on GPU plus ~3h evaluation."

stage "preflight"
python -c "import scipy, torch; print('scipy', scipy.__version__, 'torch', torch.__version__, 'cuda', torch.cuda.is_available())"
nvidia-smi || true
python - <<'PY'
import numpy as np
src = open('train_cfm.py').read()
assert '--max-arc' in src, 'train_cfm.py has no --max-arc (re-scp it)'
assert '--linear' in src, 'train_cfm.py has no --linear (re-scp it)'
d = np.load('data_x4.npz', allow_pickle=True)
assert 'path' in d.files, 'data_x4.npz has no path array'
assert d['path'].shape[1] == 64, f"expected K=64, found K={d['path'].shape[1]}"
print(f"preflight OK: {len(d['cond'])} examples, K={d['path'].shape[1]}")
PY

stage "train (linear control, arc <= 160)"
python -u train_cfm.py --data data_x4.npz --max-arc 160 --linear --out "$CKPT"
notify "**X5 linear** \`$JOB_ID\`: training done, \`$CKPT\` written. Starting 120 evaluations."

stage "evaluate (120 runs)"
rm -f "$OUT"
for EX in 0 35; do
  for MP in loop corridor corner room loop_with_corridor room_with_corner; do
    for S in 41 42 43 44 45 46 47 48 49 50; do
      echo "--- linear ex=$EX $MP seed $S"
      python -u run_eval.py --method cfm --ckpt "$CKPT" --map "$MP" --seed "$S" \
             --exclude "$EX" --max-steps 2000 --csv "$OUT"
    done
  done
  notify "$(python discord_report.py "X5 linear - exclude $EX done" "$OUT")"
done

stage "report"
notify "$(python discord_report.py "X5 linear FINAL (control, arc<=160)" "$OUT")
Pair against the other arm once both are done:
  python merge_results.py results_x5_linear.csv results_x5_geodesic.csv > results_x5.csv
  python analyse.py results_x5.csv"
