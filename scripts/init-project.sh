#!/usr/bin/env bash
# init-project.sh — Bootstrap a new customer engagement
#
# Creates the per-customer directory structure under agent-output/,
# copies sample config files, and seeds the estate state JSON.
#
# Usage:
#   ./scripts/init-project.sh --customer <name> [--prefix <pfx>] [--region <region>]
#
# Examples:
#   ./scripts/init-project.sh --customer contoso --prefix cto --region eastus2
#   ./scripts/init-project.sh --customer acme

set -euo pipefail

# --- Defaults ---
CUSTOMER=""
PREFIX="alz"
REGION="southcentralus"

# --- Parse args ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --customer) CUSTOMER="$2"; shift 2 ;;
    --prefix)   PREFIX="$2"; shift 2 ;;
    --region)   REGION="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 --customer <name> [--prefix <pfx>] [--region <region>]"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$CUSTOMER" ]]; then
  echo "Error: --customer is required"
  echo "Usage: $0 --customer <name> [--prefix <pfx>] [--region <region>]"
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_DIR="$REPO_ROOT/agent-output/$CUSTOMER"

if [[ -d "$OUTPUT_DIR" ]]; then
  echo "Error: agent-output/$CUSTOMER/ already exists"
  exit 1
fi

echo "Initializing customer: $CUSTOMER"
echo "  Prefix: $PREFIX"
echo "  Region: $REGION"
echo "  Output: agent-output/$CUSTOMER/"
echo ""

# --- Create directory structure ---
mkdir -p "$OUTPUT_DIR"/{tdd,diagrams,architecture,adr,assessment,deliverables}

# --- Seed estate state ---
cat > "$OUTPUT_DIR/00-estate-state.json" << EOF
{
  "\$schema": "estate-state/v1",
  "description": "Estate-level state for $CUSTOMER — tracks ALL landing zones.",
  "estate": {
    "customer": "$CUSTOMER",
    "prefix": "$PREFIX",
    "primary_region": "$REGION",
    "iac_tool": "bicep",
    "management_group_prefix": "$PREFIX",
    "created": "$(date -u +%Y-%m-%d)",
    "updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  },
  "platform_landing_zones": {
    "management": { "status": "pending" },
    "connectivity": { "status": "pending" },
    "identity": { "status": "pending" },
    "security": { "status": "pending" }
  },
  "application_landing_zones": {},
  "governance": { "policies_assigned": false, "rbac_configured": false },
  "day2": { "monitoring_active": false, "last_compliance_scan": null }
}
EOF

# --- Copy sample configs ---
if [[ -f "$REPO_ROOT/environments/subscriptions.sample.json" ]]; then
  if [[ ! -f "$REPO_ROOT/environments/subscriptions.json" ]]; then
    cp "$REPO_ROOT/environments/subscriptions.sample.json" "$REPO_ROOT/environments/subscriptions.json"
    echo "Copied environments/subscriptions.sample.json → subscriptions.json"
  else
    echo "environments/subscriptions.json already exists — skipping"
  fi
fi

for sample in "$REPO_ROOT"/infra/bicep/parameters/*.sample.bicepparam; do
  target="${sample%.sample.bicepparam}.bicepparam"
  if [[ ! -f "$target" ]]; then
    cp "$sample" "$target"
    echo "Copied $(basename "$sample") → $(basename "$target")"
  fi
done

for sample in "$REPO_ROOT"/infra/terraform/environments/*/terraform.tfvars.sample; do
  target="${sample%.sample}"
  if [[ ! -f "$target" ]]; then
    cp "$sample" "$target"
    echo "Copied $(basename "$sample") → $(basename "$target")"
  fi
done

echo ""
echo "Done! Next steps:"
echo "  1. Edit environments/subscriptions.json with real subscription IDs"
echo "  2. Edit infra/bicep/parameters/*.bicepparam with real parameter values"
echo "  3. Start the workflow: ask the orchestrator to begin"
echo ""
echo "To track this customer's output in git (for a private fork):"
echo "  Add '!agent-output/$CUSTOMER/' to .gitignore"
