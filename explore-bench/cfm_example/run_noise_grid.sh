#!/usr/bin/env bash
# Paired research grid. Run only after single-run smoke tests and evaluator verification.
# Writes experiment CSV; does not modify training data or checkpoint files.
set -euo pipefail
OUT="${1:-results_noise_experiments.csv}"
if [[ -e "$OUT" ]]; then
  echo "Refusing to append/overwrite existing $OUT. Choose a new results filename." >&2
  exit 2
fi
for map in loop corridor corner room loop_with_corridor room_with_corner; do
  for seed in {41..50}; do
    for variant in independent static online; do
      echo "--- $map seed=$seed variant=$variant"
      python run_noise_experiment.py \
        --variant "$variant" --map "$map" --seed "$seed" \
        --ckpt cfm_x5_linear.pt --robots 2 --max-steps 2000 \
        --replan 10 --flow-steps 20 --bank-size 1024 \
        --exclude 0 --step-seconds 1.0 --csv "$OUT"
    done
  done
done
python analyze_noise_experiments.py "$OUT"
