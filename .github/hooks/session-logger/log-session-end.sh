#!/usr/bin/env bash
# Session Logger: Log session end
set -euo pipefail

if [[ "${SKIP_SESSION_LOG:-}" == "true" ]]; then
  exit 0
fi

INPUT=$(cat)

mkdir -p logs/copilot/sessions

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if command -v jq &>/dev/null; then
  jq -Rn \
    --arg timestamp "$TIMESTAMP" \
    '{"timestamp":$timestamp,"event":"session_end"}' \
    >> logs/copilot/sessions/session.log
else
  echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"session_end\"}" \
    >> logs/copilot/sessions/session.log
fi

exit 0
