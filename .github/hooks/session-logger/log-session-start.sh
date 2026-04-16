#!/usr/bin/env bash
# Session Logger: Log session start
set -euo pipefail

if [[ "${SKIP_SESSION_LOG:-}" == "true" ]]; then
  exit 0
fi

INPUT=$(cat)

mkdir -p logs/copilot/sessions

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SESSION_ID="${RANDOM}${RANDOM}"
CWD=$(pwd)
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

if command -v jq &>/dev/null; then
  jq -Rn \
    --arg timestamp "$TIMESTAMP" \
    --arg session_id "$SESSION_ID" \
    --arg cwd "$CWD" \
    --arg branch "$BRANCH" \
    '{"timestamp":$timestamp,"event":"session_start","session_id":$session_id,"cwd":$cwd,"branch":$branch}' \
    >> logs/copilot/sessions/session.log
else
  echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"session_start\",\"session_id\":\"$SESSION_ID\",\"cwd\":\"$CWD\",\"branch\":\"$BRANCH\"}" \
    >> logs/copilot/sessions/session.log
fi

echo "📝 Session logging active"
exit 0
