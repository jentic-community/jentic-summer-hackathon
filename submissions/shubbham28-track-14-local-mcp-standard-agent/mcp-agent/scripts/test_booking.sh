#!/usr/bin/env bash
# Debug booking_search endpoint of the Browser MCP server
# Usage (env overrides):
#   ENDPOINT=http://localhost:8003/tool/browser_op CITY="Dublin" N=3 TIMEOUT=120 ./test_booking.sh
#   DATE_FROM=2025-09-10 DATE_TO=2025-09-12 ./test_booking.sh

set -euo pipefail

# Config (override via env)
ENDPOINT="${ENDPOINT:-http://localhost:8003/tool/browser_op}"
CITY="${CITY:-Dublin}"
N="${N:-3}"
DATE_FROM="${DATE_FROM:-}"   # e.g. 2025-09-10
DATE_TO="${DATE_TO:-}"       # e.g. 2025-09-12
TIMEOUT="${TIMEOUT:-120}"    # seconds
OUT_DIR="${OUT_DIR:-./debug_booking}"
mkdir -p "$OUT_DIR"

echo "Endpoint: $ENDPOINT"
echo "City: $CITY  N: $N  Dates: ${DATE_FROM:-unset} -> ${DATE_TO:-unset}"

format_metrics='http_code:%{http_code} time_namelookup:%{time_namelookup} time_connect:%{time_connect} time_appconnect:%{time_appconnect} time_starttransfer:%{time_starttransfer} time_total:%{time_total}\n'

echo
echo "1) Smoke test: open_title on booking.com"
OPEN_TITLE_PAYLOAD='{"action":"open_title","args":{"url":"https://www.booking.com"}}'
curl -sS -o "$OUT_DIR/open_title.json" -w "$format_metrics" \
  --connect-timeout 10 --max-time 30 \
  -H 'Content-Type: application/json' \
  -X POST "$ENDPOINT" \
  -d "$OPEN_TITLE_PAYLOAD" || true

echo "open_title response saved to $OUT_DIR/open_title.json"

echo
echo "2) booking_search"
if [[ -n "$DATE_FROM" && -n "$DATE_TO" ]]; then
  DATA=$(cat <<EOF
{"action":"booking_search","args":{"city":"$CITY","n":$N,"date_from":"$DATE_FROM","date_to":"$DATE_TO"}}
EOF
)
else
  DATA=$(cat <<EOF
{"action":"booking_search","args":{"city":"$CITY","n":$N}}
EOF
)
fi

curl -sS -o "$OUT_DIR/booking_search.json" -w "$format_metrics" \
  --connect-timeout 15 --max-time "$TIMEOUT" \
  -H 'Content-Type: application/json' \
  -X POST "$ENDPOINT" \
  -d "$DATA" || true

echo "booking_search response saved to $OUT_DIR/booking_search.json"

if command -v jq >/dev/null 2>&1; then
  echo
  echo "Response (without logs):"
  jq 'del(.logs)' "$OUT_DIR/booking_search.json" || true
  echo
  echo "Artifacts (if any):"
  CSV_PATH=$(jq -r '.result.csv_path // empty' "$OUT_DIR/booking_search.json" || true)
  SHOT_PATH=$(jq -r '.result.screenshot_path // empty' "$OUT_DIR/booking_search.json" || true)
  [[ -n "$CSV_PATH" ]] && echo "CSV: $CSV_PATH"
  [[ -n "$SHOT_PATH" ]] && echo "Screenshot: $SHOT_PATH"
else
  echo
  echo "Raw response:"
  cat "$OUT_DIR/booking_search.json"
fi

echo
echo "Done. Inspect server logs if timeouts persist (Playwright navigation may be slow or blocked)."
