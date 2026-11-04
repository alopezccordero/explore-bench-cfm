#!/bin/bash
# Submit after all 3 experiment arrays succeed, passing their SLURM job IDs:
# sbatch --dependency=afterok:$INDEPENDENT:$STATIC:$ONLINE job_noise_analyze.sh "$INDEPENDENT" "$STATIC" "$ONLINE"
#SBATCH --job-name=CFM-noise-analysis
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --output=noise_analysis_%j.out
#SBATCH --error=noise_analysis_%j.err

set -euo pipefail
if [[ $# -ne 3 ]]; then
  echo "Usage: sbatch job_noise_analyze.sh INDEPENDENT_JOB_ID STATIC_JOB_ID ONLINE_JOB_ID" >&2
  exit 2
fi
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate mujoco-env
cd "$HOME/explore-bench-cfm/explore-bench/cfm_example"

python - "$1" "$2" "$3" <<'PY_MERGE'
import csv
import pathlib
import sys

ids=dict(zip(('independent','static','online'),sys.argv[1:]))
rows=[]
columns=None
maps=('loop','corridor','corner','room','loop_with_corridor','room_with_corner')
for variant,job_id in ids.items():
    if not job_id.isdigit():
        raise SystemExit(f'Not a numeric SLURM job ID: {variant}={job_id}')
    for name in maps:
        file=pathlib.Path(f'noise_{variant}_{job_id}_{name}.csv')
        if not file.is_file():
            raise SystemExit(f'Missing result file: {file}')
        with file.open(newline='') as f:
            reader=csv.DictReader(f)
            if columns is None:
                columns=reader.fieldnames
            elif columns != reader.fieldnames:
                raise SystemExit(f'CSV schema mismatch in {file}')
            items=list(reader)
        if len(items)!=10:
            raise SystemExit(f'{file}: expected 10 rows; got {len(items)}')
        if {int(x['seed']) for x in items} != set(range(41,51)):
            raise SystemExit(f'{file}: seeds do not match 41..50')
        if any(x['variant']!=variant or x['map']!=name for x in items):
            raise SystemExit(f'{file}: unexpected variant or map')
        rows.extend(items)
assert len(rows)==180, f'Expected 180 rows, got {len(rows)}'
output=pathlib.Path(f"noise_merged_{ids['independent']}_{ids['static']}_{ids['online']}.csv")
if output.exists():
    raise SystemExit(f'Refusing to overwrite {output}')
with output.open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
print(f'Wrote {len(rows)} evaluation rows to {output}',flush=True)
PY_MERGE

OUT="noise_merged_${1}_${2}_${3}.csv"
python analyze_noise_experiments.py "$OUT"
