"""Post one Discord message. Used by notify.sh; usable on its own.

    python notify_send.py "<text>" [webhook_file]

Discord sits behind Cloudflare, which answers **403** to urllib's default
`Python-urllib/3.x` User-Agent. That is why the first version of notify.sh failed while
the plain `curl` in the original job.sh worked. Setting a real User-Agent fixes it, so
this does the POST itself rather than shelling out, and keeps the JSON building and the
sending in one place where the escaping cannot drift.

Exits 0 on success, 1 with the reason on stderr otherwise, so the caller can fall back.
"""
import json
import os
import sys
import urllib.error
import urllib.request

UA = os.environ.get('NOTIFY_UA', 'Mozilla/5.0 (compatible; cfm-explore-bench-notifier/1.0)')
LIMIT = 1900          # Discord rejects a message over 2000 characters


def send(text, webhook_file):
    try:
        with open(os.path.expanduser(webhook_file)) as f:
            hook = f.read().strip()
    except OSError as e:
        print(f'webhook file unreadable: {e}', file=sys.stderr)
        return 1
    if not hook.startswith('http'):
        print('webhook file does not contain a URL', file=sys.stderr)
        return 1

    if len(text) > LIMIT:            # keep the tail: the newest lines matter most
        text = text[:200] + '\n...[trimmed]...\n' + text[-(LIMIT - 250):]
    req = urllib.request.Request(
        hook, data=json.dumps({'content': text}).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': UA})
    try:
        urllib.request.urlopen(req, timeout=30).read()
        return 0
    except urllib.error.HTTPError as e:
        detail = e.read()[:300].decode('utf-8', 'replace')
        hint = ''
        if e.code == 403:
            hint = ('  (403 is usually Cloudflare rejecting the User-Agent -- set '
                    'NOTIFY_UA, or check the webhook was not deleted)')
        elif e.code == 404:
            hint = '  (404 means the webhook URL is wrong or was deleted)'
        elif e.code == 429:
            hint = '  (429 is rate limiting; space the messages out)'
        print(f'http {e.code}: {detail}{hint}', file=sys.stderr)
        return 1
    except Exception as e:
        print(f'{type(e).__name__}: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: notify_send.py "<text>" [webhook_file]')
    hook_file = sys.argv[2] if len(sys.argv) > 2 else os.environ.get(
        'WEBHOOK_FILE', os.path.expanduser('~/.discord_webhook'))
    sys.exit(send(sys.argv[1], hook_file))
