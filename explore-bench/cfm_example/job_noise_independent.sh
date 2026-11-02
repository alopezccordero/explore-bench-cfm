#!/bin/bash
# independent noise source: six held-out maps x seeds 41..50 (60 paired trials).
# Submit: sbatch job_noise_independent.sh
#SBATCH --job-name=CFM-noise-independent
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=10:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --array=0-5%2
#SBATCH --output=noise_%x_%A_%a.out
#SBATCH --error=noise_%x_%A_%a.err

set -euo pipefail
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate mujoco-env
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$HOME/explore-bench-cfm/explore-bench/cfm_example"

MAPS=(loop corridor corner room loop_with_corridor room_with_corner)
MAP="${MAPS[SLURM_ARRAY_TASK_ID]}"
VARIANT=independent
OUT="noise_${VARIANT}_${SLURM_ARRAY_JOB_ID}_${MAP}.csv"

# Never overwrite prior runs. Each array task owns a unique file.
if [[ -e "$OUT" ]]; then
  echo "Refusing to overwrite $OUT" >&2
  exit 2
fi
[[ -f cfm_x5_linear.pt ]] || { echo 'Missing cfm_x5_linear.pt' >&2; exit 2; }
[[ -f ../Explore-Bench/grid_simulator/cfm_policy.py ]] || {
  echo 'Missing custom Explore-Bench/grid_simulator/cfm_policy.py' >&2
  exit 2
}
python -c 'import scipy, torch; import structured_noise, run_noise_experiment' 

echo "Starting $VARIANT on $MAP, job $SLURM_ARRAY_JOB_ID task $SLURM_ARRAY_TASK_ID"
echo "Commit: $(git rev-parse HEAD)"

for SEED in {41..50}; do
  echo "=== $VARIANT map=$MAP seed=$SEED $(date -Iseconds) ==="
  python -u run_noise_experiment.py \
    --variant "$VARIANT" --map "$MAP" --seed "$SEED" \
    --ckpt cfm_x5_linear.pt --robots 2 \
    --max-steps 2000 --replan 10 --flow-steps 20 \
    --bank-size 1024 --exclude 0 --step-seconds 1.0 \
    --csv "$OUT"
done

python - "$OUT" "$VARIANT" "$MAP" <<'PY_CHECK'
import csv, sys
filename,variant,mapname=sys.argv[1:]
with open(filename,newline='') as f:
    rows=list(csv.DictReader(f))
assert len(rows)==10, f'Expected 10 paired seeds, got {len(rows)}'
assert {int(r['seed']) for r in rows}==set(range(41,51))
assert all(r['variant']==variant and r['map']==mapname for r in rows)
print(f'Validated {len(rows)} runs: {variant}, {mapname}')
PY_CHECK

echo "Completed $VARIANT $MAP: $OUT"
