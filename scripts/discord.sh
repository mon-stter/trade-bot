#!/usr/bin/env bash
# Discord notification wrapper. Falls back to memory/notifications.log (committed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
FALLBACK="$ROOT/memory/notifications.log"
if [[ -f "$ENV_FILE" ]]; then set -a; source "$ENV_FILE"; set +a; fi

if [[ $# -gt 0 ]]; then msg="$*"; else msg="$(cat)"; fi
if [[ -z "${msg// /}" ]]; then echo 'usage: bash scripts/discord.sh "<message>"' >&2; exit 1; fi
stamp="$(date '+%Y-%m-%d %H:%M %Z')"

if [[ -z "${DISCORD_WEBHOOK_URL:-}" ]]; then
  printf '\n[%s] (fallback — DISCORD_WEBHOOK_URL unset)\n%s\n' "$stamp" "$msg" >> "$FALLBACK"
  echo "[discord fallback] appended to memory/notifications.log"
  exit 0
fi

payload="$(python3 -c 'import json,sys; print(json.dumps({"content": sys.argv[1]}))' "$msg")"
curl --fail-with-body -sS -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" -d "$payload"
echo
