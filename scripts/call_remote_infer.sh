#!/usr/bin/env bash
# Helper: call remote ML inference API with sample payload
# Usage: ./scripts/call_remote_infer.sh http://host:8080/infer

set -euo pipefail

URL=${1:-}
if [[ -z "$URL" ]]; then
  echo "Usage: $0 <ML_API_URL>"
  exit 2
fi

cat <<'JSON' | curl -sS -X POST "$URL" -H 'Content-Type: application/json' -d @-
{
  "messages": [
    {"sender": "user", "text": "hello", "timestamp": "2026-04-30T00:00:00Z"},
    {"sender": "user", "text": "you're so mature for your age", "timestamp": "2026-04-30T00:01:00Z"}
  ]
}
JSON

echo
