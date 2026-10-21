#!/bin/bash
# X5-geodesic: train on data_x4.npz with GEODESIC interpolation at K=64, then evaluate.
#
# This arm interpolates along the stored 64-waypoint geodesic route and targets its
# tangent. Its twin, job_x5_linear.sh, interpolates along the straight line
# x_t = (1-t)x0 + t x1 -- the original objective. Both read the same dataset, apply the
# same arc filter and evaluate on the same maps, seeds and exclusion settings, so the two
# result files pair 1:1 by (map, seed, exclude) and the conditional path is the only
# difference between them.
#
# WHY RE-RUN THIS. The earlier geodesic tests were not tests. train_cfm.py interpolates
# linearly between stored waypoints, and at K=8 those chords left free space on 27.4% of
# examples against 36.3% for a plain straight line -- so E-A (-60 steps, 3 seeds) and X1
# (+9 steps, p=0.29, 20 seeds) were comparing two nearly identical objectives. Verified on
# data_x4.npz:
#
#     K      spacing  invalid    <40 / 40-80 / 80-160 / 160+
#      8       9.4c    27.4%    6.1% / 18.3% / 66.8% / 97.5%
#     64       1.0c     5.7%    0.0% /  0.0% /  0.0% / 69.5%
#     line        -    36.3%
#
# --max-arc 160 drops the 8.2% of examples whose route exceeds 160 cells, where even 63
# segments still clip corners. Those are goals 160+ simulator steps away, and the teacher
# re-solves every 10 steps, so they record commitments it never executed. Both arms drop
# the same examples -- 41,683 of 45,291 kept -- which keeps the comparison paired while
# making the geodesic path valid on essentially all of the training data. First run where
# there is a real treatment to detect.
#
# Evaluated at exclude 0 and 35: coordination is the one established effect (p=0.0001 in
# X1), and whether geodesic still helps once robots stop picking redundant goals is a
# different question from whether it helps without that.
#
# No array job. Training uses the GPU for ~30 min; the ~3h of evaluation is CPU-only and
# leaves it idle, which is the cost of keeping this to a single self-contained script.
#
#SBATCH --job-name=CFM-X5-geodesic
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=09:00:00
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=32G
#SBATCH --output=CFM-X5-geodesic-%j.out
#SBATCH --error=CFM-X5-geodesic-%j.err

set -euo pipefail

source ~/miniconda3/bin/activate
conda activate mujoco-env
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd ~/explore-bench-cfm/explore-bench/cfm_example

CKPT=cfm_x5_geodesic.pt
OUT=results_x5_geodesic.csv
JOB_ID="${SLURM_JOB_ID:-local-$$}"
RUN_LOG="run_x5_geodesic_${JOB_ID}.log"
exec > >(tee -a "$RUN_LOG") 2>&1
source ./notify.sh

report_init "X5 geodesic interpolation (K=64)" \
"Training on data_x4.npz with --max-arc 160 (41683 of 45291 examples kept), then
evaluating at exclude 0 and 35 over 6 maps x 10 seeds = 120 runs.
Pairs against job_x5_linear.sh on the same data, seeds and settings.
Expect ~30 min training on GPU plus ~3h evaluation."

stage "preflight"
python -c "import scipy, torch; print('scipy', scipy.__version__, 'torch', torch.__version__, 'cuda', torch.cuda.is_available())"
nvidia-smi || true
python - <<'PY'
import numpy as np
src = open('train_cfm.py').read()
assert '--max-arc' in src, 'train_cfm.py has no --max-arc (re-scp it)'
assert 'geodesic interpolation' in src, 'train_cfm.py has no geodesic path (re-scp it)'
d = np.load('data_x4.npz', allow_pickle=True)
assert 'path' in d.files, 'data_x4.npz has no path array'
assert d['path'].shape[1] == 64, f"expected K=64, found K={d['path'].shape[1]}"
assert 'raw_path' in d.files, 'data_x4.npz has no raw routes'
print(f"preflight OK: {len(d['cond'])} examples, K={d['path'].shape[1]}, "
      f"{len(d['raw_path'])} raw cells")
PY

stage "train (geodesic, K=64, arc <= 160)"
python -u train_cfm.py --data data_x4.npz --max-arc 160 --out "$CKPT"
notify "**X5 geodesic** \`$JOB_ID\`: training done, \`$CKPT\` written. Starting 120 evaluations."

stage "evaluate (120 runs)"
rm -f "$OUT"
for EX in 0 35; do
  for MP in loop corridor corner room loop_with_corridor room_with_corner; do
    for S in 41 42 43 44 45 46 47 48 49 50; do
      echo "--- geodesic ex=$EX $MP seed $S"
      python -u run_eval.py --method cfm --ckpt "$CKPT" --map "$MP" --seed "$S" \
             --exclude "$EX" --max-steps 2000 --csv "$OUT"
    done
  done
  notify "$(python discord_report.py "X5 geodesic - exclude $EX done" "$OUT")"
done

stage "report"
notify "$(python discord_report.py "X5 geodesic FINAL (K=64, arc<=160)" "$OUT")
Pair against the other arm once both are done:
  python merge_results.py results_x5_linear.csv results_x5_geodesic.csv > results_x5.csv
  python analyse.py results_x5.csv
For reference, the earlier invalid-treatment runs: geodesic 628 vs linear 688 at 3 seeds,
then +9 steps p=0.29 at 20 seeds."
