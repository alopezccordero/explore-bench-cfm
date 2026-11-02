#!/bin/bash
# CPU smoke test: numerical unit tests and 1 paired trial of each policy.
# Submit: sbatch job_noise_smoke.sh
#SBATCH --job-name=CFM-noise-smoke
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --output=noise_smoke_%j.out
#SBATCH --error=noise_smoke_%j.err

set -euo pipefail
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate mujoco-env
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$HOME/explore-bench-cfm/explore-bench/cfm_example"
[[ -f cfm_x5_linear.pt ]] || { echo 'Missing cfm_x5_linear.pt' >&2; exit 2; }
[[ -f ../Explore-Bench/grid_simulator/cfm_policy.py ]] || {
  echo 'Missing custom Explore-Bench/grid_simulator/cfm_policy.py' >&2
  exit 2
}
python -m unittest discover -s tests -v
OUT="noise_smoke_${SLURM_JOB_ID}.csv"
[[ ! -e "$OUT" ]] || { echo "Output $OUT exists" >&2; exit 2; }
for VARIANT in independent static online; do
  echo "Smoke test: $VARIANT on room seed 41"
  python -u run_noise_experiment.py \
    --variant "$VARIANT" --map room --seed 41 \
    --ckpt cfm_x5_linear.pt --robots 2 \
    --max-steps 2000 --replan 10 --flow-steps 20 \
    --bank-size 1024 --exclude 0 --step-seconds 1.0 \
    --csv "$OUT"
done
python analyze_noise_experiments.py "$OUT" --bootstrap 1000
printf 'Smoke test succeeded: %s\n' "$OUT"
