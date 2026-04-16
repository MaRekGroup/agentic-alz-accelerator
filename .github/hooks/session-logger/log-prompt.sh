#!/usr/bin/env bash
# Session Logger: Log each prompt interaction
set -euo pipefail

if [[ "${SKIP_SESSION_LOG:-}" == "true" ]]; then
  exit 0
fi

INPUT=$(cat)

mkdir -p logs/copilot/sessions

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

PROMPT_LEN=0
if command -v jq &>/dev/null; then
  PROMPT_TEXT=$(printf '%s' "$INPUT" | jq -r '.userPrompt // empty' 2>/dev/null || echo "")
  PROMPT_LEN=${#PROMPT_TEXT}
fi

if command -v jq &>/dev/null; then
  jq -Rn \
    --arg timestamp "$TIMESTAMP" \
    --argjson len "$PROMPT_LEN" \
    '{"timestamp":$timestamp,"event":"user_prompt","prompt_length":$len}' \
    >> logs/copilot/sessions/session.log
else
  echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"user_prompt\",\"prompt_length\":$PROMPT_LEN}" \
    >> logs/copilot/sessions/session.log
fi

exit 0
