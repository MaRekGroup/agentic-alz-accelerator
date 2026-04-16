#!/usr/bin/env bash
# Governance Audit: Log each user prompt for audit trail
set -euo pipefail

if [[ "${SKIP_GOVERNANCE_AUDIT:-}" == "true" ]]; then
  exit 0
fi

INPUT=$(cat)

mkdir -p logs/copilot/governance

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Extract prompt text
PROMPT_TEXT=""
if command -v jq &>/dev/null; then
  PROMPT_TEXT=$(printf '%s' "$INPUT" | jq -r '.userPrompt // empty' 2>/dev/null || echo "")
fi

# Log prompt metadata (not full content, to avoid leaking sensitive info)
PROMPT_LEN=${#PROMPT_TEXT}

if command -v jq &>/dev/null; then
  jq -Rn \
    --arg timestamp "$TIMESTAMP" \
    --argjson len "$PROMPT_LEN" \
    '{"timestamp":$timestamp,"event":"user_prompt","prompt_length":$len}' \
    >> logs/copilot/governance/audit.log
else
  echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"user_prompt\",\"prompt_length\":$PROMPT_LEN}" \
    >> logs/copilot/governance/audit.log
fi

exit 0
