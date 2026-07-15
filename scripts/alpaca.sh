#!/usr/bin/env bash
# Alpaca API wrapper. Uses --fail-with-body so error JSON is visible.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
if [[ -f "$ENV_FILE" ]]; then set -a; source "$ENV_FILE"; set +a; fi

: "${ALPACA_API_KEY:?ALPACA_API_KEY not set in environment}"
: "${ALPACA_SECRET_KEY:?ALPACA_SECRET_KEY not set in environment}"
API="${ALPACA_ENDPOINT:-https://paper-api.alpaca.markets/v2}"
DATA="${ALPACA_DATA_ENDPOINT:-https://data.alpaca.markets/v2}"
H_KEY="APCA-API-KEY-ID: $ALPACA_API_KEY"
H_SEC="APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY"
CURL=(curl --fail-with-body -sS -H "$H_KEY" -H "$H_SEC")

cmd="${1:-}"; shift || true
case "$cmd" in
  account)    "${CURL[@]}" "$API/account" ;;
  positions)  "${CURL[@]}" "$API/positions" ;;
  position)   "${CURL[@]}" "$API/positions/${1:?usage: position SYM}" ;;
  quote)      "${CURL[@]}" "$DATA/stocks/${1:?usage: quote SYM}/quotes/latest" ;;
  orders)     "${CURL[@]}" "$API/orders?status=${1:-open}" ;;
  calendar)   "${CURL[@]}" "$API/calendar?start=${1:?usage: calendar START END}&end=${2:?}" ;;
  order)      "${CURL[@]}" -H "Content-Type: application/json" -X POST \
                -d "${1:?usage: order '<json>'}" "$API/orders" ;;
  cancel)     "${CURL[@]}" -X DELETE "$API/orders/${1:?usage: cancel ORDER_ID}" ;;
  cancel-all) "${CURL[@]}" -X DELETE "$API/orders" ;;
  close)      "${CURL[@]}" -X DELETE "$API/positions/${1:?usage: close SYM}" ;;
  close-all)  "${CURL[@]}" -X DELETE "$API/positions" ;;
  *) echo "Usage: bash scripts/alpaca.sh <account|positions|position|quote|orders|calendar|order|cancel|cancel-all|close|close-all> [args]" >&2; exit 1 ;;
esac
echo
