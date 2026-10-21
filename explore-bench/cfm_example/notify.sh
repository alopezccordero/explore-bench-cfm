#!/bin/bash
# Discord reporting shared by job_ea.sh / job_eb.sh / job_ec.sh.
#
# Sourced, not executed. Provides:
#   notify "<text>"      post a message (markdown works; silently skipped with no webhook)
#   stage "<name>"       mark what the job is doing, so a failure can say where it died
#   report_init "<name>" install the exit trap and announce the start
#
# The payload is built with python rather than inline JSON, because results tables contain
# quotes, newlines and backticks that break hand-escaped curl bodies.

WEBHOOK_FILE="${WEBHOOK_FILE:-$HOME/.discord_webhook}"
STAGE="startup"
JOB_ID="${SLURM_JOB_ID:-local-$$}"
JOB_NAME="${JOB_NAME:-unnamed}"
RUN_LOG="${RUN_LOG:-run_${JOB_ID}.log}"

notify() {
    if [ ! -f "$WEBHOOK_FILE" ]; then
        echo "[notify] no $WEBHOOK_FILE, printing instead:"; echo "$1"; return 0
    fi
    WEBHOOK_FILE="$WEBHOOK_FILE" python - "$1" <<'PY' || echo "[notify] post failed (ignored)"
import json, os, sys, urllib.request
hook = open(os.environ['WEBHOOK_FILE']).read().strip()
body = sys.argv[1]
# Discord caps a message at 2000 characters; keep the tail, which holds the newest lines
if len(body) > 1900:
    body = body[:200] + "\n...[trimmed]...\n" + body[-1650:]
req = urllib.request.Request(hook, data=json.dumps({'content': body}).encode('utf-8'),
                             headers={'Content-Type': 'application/json'})
urllib.request.urlopen(req, timeout=30).read()
PY
}

stage() { STAGE="$1"; echo "=== stage: $1"; }

_on_exit() {
    rc=$?
    if [ "$rc" -eq 0 ]; then
        notify "**$JOB_NAME** - job \`$JOB_ID\` finished normally on \`$(hostname)\`
elapsed $(( (SECONDS) / 60 )) min, all stages completed."
    else
        notify "**$JOB_NAME** - job \`$JOB_ID\` FAILED, exit $rc
died in stage: **$STAGE**  (host \`$(hostname)\`, after $(( (SECONDS) / 60 )) min)
last lines of the log:
\`\`\`
$(tail -n 18 "$RUN_LOG" 2>/dev/null || echo 'no log captured')
\`\`\`"
    fi
}

report_init() {
    JOB_NAME="$1"
    trap _on_exit EXIT
    notify "**$JOB_NAME** - job \`$JOB_ID\` started on \`$(hostname)\`
$2"
}
