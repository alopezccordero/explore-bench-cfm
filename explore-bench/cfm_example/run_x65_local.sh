#!/bin/bash
# Finish the X6.5 mtsp arms locally, after the kimq node stalled task 1 twice.
#
#     bash run_x65_local.sh            # work through x65_todo.txt, 4 at a time
#
# Each run writes its own CSV in a scratch directory and they are merged at the end.
# Appending from several processes to one file is what interleaved rows in the September
# sweep; per-run files cost nothing and cannot race.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUTDIR="${TMPDIR:-/tmp}/x65local"
mkdir -p "$OUTDIR"
PAR="${PAR:-4}"

run_one() {
  read -r ARM MP S <<< "$1"
  local f="$OUTDIR/${ARM}__${MP}__${S}.csv"
  [ -s "$f" ] && { echo "skip  $ARM $MP $S (already done)"; return 0; }
  if python -u "$HERE/run_eval.py" --method "$ARM" --map "$MP" --seed "$S" \
       --max-steps 2000 --csv "$f" > "$OUTDIR/${ARM}__${MP}__${S}.log" 2>&1; then
    echo "ok    $ARM $MP $S  $(grep -o "'steps_98': [0-9]*" "$OUTDIR/${ARM}__${MP}__${S}.log" | head -1)"
  else
    echo "FAIL  $ARM $MP $S (see $OUTDIR/${ARM}__${MP}__${S}.log)"
    rm -f "$f"
  fi
}
export -f run_one
export OUTDIR HERE

echo "starting $(wc -l < "$HERE/x65_todo.txt") runs, $PAR at a time"
# shellcheck disable=SC2016
xargs -P "$PAR" -I{} bash -c 'run_one "$@"' _ {} < "$HERE/x65_todo.txt"

echo "--- merging"
for ARM in mtsp mtsp_fix; do
  OUT="$HERE/results_x65_${ARM}_local.csv"
  FIRST=1
  : > "$OUT"
  # the rows already collected on the cluster come first, then the local ones
  if [ -s "$HERE/results_x65_${ARM}.csv" ]; then
    cat "$HERE/results_x65_${ARM}.csv" >> "$OUT"; FIRST=0
  fi
  for f in "$OUTDIR/${ARM}__"*.csv; do
    [ -s "$f" ] || continue
    if [ "$FIRST" = 1 ]; then cat "$f" >> "$OUT"; FIRST=0; else tail -n +2 "$f" >> "$OUT"; fi
  done
  echo "  $OUT: $(($(wc -l < "$OUT") - 1))/60 rows"
done
