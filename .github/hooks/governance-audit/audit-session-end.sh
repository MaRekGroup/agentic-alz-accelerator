#!/usr/bin/env bash
# Governance Audit: Log session end
set -euo pipefail

if [[ "${SKIP_GOVERNANCE_AUDIT:-}" == "true" ]]; then
  exit 0
fi

INPUT=$(cat)

mkdir -p logs/copilot/governance

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if command -v jq &>/dev/null; then
  jq -Rn \
    --arg timestamp "$TIMESTAMP" \
    '{"timestamp":$timestamp,"event":"session_end"}' \
    >> logs/copilot/governance/audit.log
else
  echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"session_end\"}" \
    >> logs/copilot/governance/audit.log
fi

exit 0
