#!/bin/bash
# Discord reporting shared by job_ea.sh / job_eb.sh / job_ec.sh.
#
# Sourced, not executed. Provides:
#   notify "<text>"      post a message (markdown works)
#   stage "<name>"       mark what the job is doing, so a failure can say where it died
#   report_init "<name>" install the exit trap and announce the start
#
# Sending lives in notify_send.py, which sets a real User-Agent: Discord is behind
# Cloudflare and answers 403 to urllib's default Python-urllib/3.x. If that fails, curl
# is tried (its User-Agent is accepted, which is why the plain curl in the original
# job.sh worked). Either way the message is appended to notify_outbox.txt first, so a
# delivery problem never loses the content -- and every outcome is printed, because a
# silent notifier is worse than none.

WEBHOOK_FILE="${WEBHOOK_FILE:-$HOME/.discord_webhook}"
NOTIFY_OUTBOX="${NOTIFY_OUTBOX:-notify_outbox.txt}"
STAGE="startup"
JOB_ID="${SLURM_JOB_ID:-local-$$}"
JOB_NAME="${JOB_NAME:-unnamed}"
RUN_LOG="${RUN_LOG:-run_${JOB_ID}.log}"
NOTIFY_DIR="${NOTIFY_DIR:-$(pwd)}"

notify() {
    local msg="$1" out hook code
    printf '\n===== %s  %s\n%s\n' "$(date '+%F %T')" "$JOB_NAME/$JOB_ID" "$msg" \
        >> "$NOTIFY_OUTBOX" 2>/dev/null || true

    if [ ! -r "$WEBHOOK_FILE" ]; then
        echo "[notify] no readable $WEBHOOK_FILE; content kept in $NOTIFY_OUTBOX"
        return 0
    fi

    if out="$(WEBHOOK_FILE="$WEBHOOK_FILE" python "$NOTIFY_DIR/notify_send.py" "$msg" 2>&1)"; then
        echo "[notify] sent"
        return 0
    fi
    echo "[notify] python send failed: $out"

    # curl fallback, for the case where it is the User-Agent and not the webhook
    if command -v curl >/dev/null 2>&1; then
        hook="$(tr -d '\r\n' < "$WEBHOOK_FILE")"
        code="$(python -c "
import json,sys
b=sys.argv[1]
b=b if len(b)<=1900 else b[:200]+chr(10)+'...[trimmed]...'+chr(10)+b[-1650:]
sys.stdout.write(json.dumps({'content':b}))" "$msg" \
            | curl -sS -o /dev/null -w '%{http_code}' -X POST \
                   -H 'Content-Type: application/json' --data-binary @- "$hook" 2>&1)"
        case "$code" in
            200|204) echo "[notify] sent (curl $code)"; return 0 ;;
            *)       echo "[notify] curl got HTTP $code" ;;
        esac
    fi
    echo "[notify] undelivered; content kept in $NOTIFY_OUTBOX"
}

stage() { STAGE="$1"; echo "=== stage: $1"; }

_on_exit() {
    rc=$?
    if [ "$rc" -eq 0 ]; then
        notify "**$JOB_NAME** - job \`$JOB_ID\` finished normally on \`$(hostname)\`
elapsed $(( SECONDS / 60 )) min, all stages completed."
    else
        notify "**$JOB_NAME** - job \`$JOB_ID\` FAILED, exit $rc
died in stage: **$STAGE**  (host \`$(hostname)\`, after $(( SECONDS / 60 )) min)
last lines of the log:
\`\`\`
$(tail -n 18 "$RUN_LOG" 2>/dev/null || echo 'no log captured')
\`\`\`"
    fi
}

report_init() {
    JOB_NAME="$1"
    trap _on_exit EXIT
    echo "[notify] webhook=$WEBHOOK_FILE outbox=$NOTIFY_OUTBOX dir=$NOTIFY_DIR"
    notify "**$JOB_NAME** - job \`$JOB_ID\` started on \`$(hostname)\`
$2"
}
