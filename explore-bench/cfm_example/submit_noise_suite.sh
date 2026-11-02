#!/bin/bash
# Convenience submitter: smoke -> all three method arrays -> merged analysis.
# Uses SLURM dependencies so a smoke failure does not waste 180 full trials.
# Run from cfm_example: bash submit_noise_suite.sh
set -euo pipefail
cd "$HOME/explore-bench-cfm/explore-bench/cfm_example"

SMOKE=$(sbatch --parsable job_noise_smoke.sh)
INDEPENDENT=$(sbatch --parsable --dependency="afterok:$SMOKE" job_noise_independent.sh)
STATIC=$(sbatch --parsable --dependency="afterok:$SMOKE" job_noise_static.sh)
ONLINE=$(sbatch --parsable --dependency="afterok:$SMOKE" job_noise_online.sh)
ANALYSIS=$(sbatch --parsable --dependency="afterok:$INDEPENDENT:$STATIC:$ONLINE" \
  job_noise_analyze.sh "$INDEPENDENT" "$STATIC" "$ONLINE")

printf 'Smoke:       %s\nIndependent: %s\nStatic:      %s\nOnline:      %s\nAnalysis:    %s\n' \
  "$SMOKE" "$INDEPENDENT" "$STATIC" "$ONLINE" "$ANALYSIS"
printf 'Check: squeue -u "$USER"\n'
printf 'The full grid starts only if the smoke job passes.\n'
