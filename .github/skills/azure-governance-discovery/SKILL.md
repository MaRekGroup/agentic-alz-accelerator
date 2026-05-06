---
name: azure-governance-discovery
description: "Deterministic Azure Policy discovery for Enterprise Landing Zones. Lists effective policy assignments at management group and subscription scopes (including inherited), classifies effects, filters Defender auto-assignments, and emits the governance-constraints JSON envelope. USE FOR: Step 3.5 governance discovery, refreshing 04-governance-constraints.json. DO NOT USE FOR: artifact writing (parent Governance agent handles that), architecture mapping, challenger orchestration."
compatibility: Requires Python 3.10+, Azure CLI on PATH, read access to target scope.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: governance
---

# Azure Governance Discovery Skill

Deterministic policy discovery for Enterprise Landing Zone governance assessment.
Replaces LLM-driven policy enumeration with a script that does batched ARM REST
traversal and emits the schema-compliant `04-governance-constraints.json` envelope.

The parent Governance agent (`governance.md`) invokes it via `run_in_terminal`,
reads the one-line JSON status from stdout, and proceeds to artifact writing
without pulling raw Azure REST responses into LLM context.

## When to Use

- Step 3.5 governance discovery for a customer
- Refreshing the governance snapshot after policy changes
- Regenerating inputs for Step 4 (IaC Plan) and Step 5 (IaC Code)
- Verifying policy inheritance from management group hierarchy

## When NOT to Use

- Writing `04-governance-constraints.md` — parent Governance agent handles that
- Cross-referencing architecture resources — parent-side LLM work
- Challenger review orchestration — parent-side LLM work
- Post-deployment compliance monitoring — use Monitoring agent (Sentinel)

## Usage

```bash
# Subscription-scoped discovery
python .github/skills/azure-governance-discovery/scripts/discover.py \
    --scope /subscriptions/{sub-id} \
    --customer marekgroup \
    --out agent-output/marekgroup/04-governance-constraints.json

# Management-group-scoped discovery (Enterprise Landing Zone estate)
python .github/skills/azure-governance-discovery/scripts/discover.py \
    --scope /providers/Microsoft.Management/managementGroups/{mg-prefix} \
    --customer marekgroup \
    --out agent-output/marekgroup/04-governance-constraints.json
```

## Flags

| Flag | Required | Description |
|------|----------|-------------|
| `--scope` | Yes | ARM scope (subscription or management group) |
| `--customer` | Yes | Customer name for output path resolution |
| `--out` | Yes | Output path for JSON envelope |
| `--include-defender` | No | Include Defender auto-assigned policies (excluded by default) |
| `--effects` | No | Comma-separated effects to include (default: `Deny,DeployIfNotExists,Modify,Audit`) |

## Output Schema

The script emits a `governance-constraints-v1` envelope:

```json
{
  "$schema": "governance-constraints/v1",
  "generated": "2026-05-06T12:00:00Z",
  "scope": "/providers/Microsoft.Management/managementGroups/mrg",
  "customer": "marekgroup",
  "summary": {
    "total_assignments": 47,
    "deny_count": 3,
    "deploy_if_not_exists_count": 12,
    "modify_count": 5,
    "audit_count": 27,
    "exempt_count": 2,
    "defender_filtered": 8
  },
  "blockers": [
    {
      "assignment_id": "/providers/.../policyAssignments/deny-public-ip",
      "display_name": "Deny Public IP Addresses",
      "effect": "Deny",
      "scope": "/providers/Microsoft.Management/managementGroups/mrg-landingzones",
      "resource_types": ["Microsoft.Network/publicIPAddresses"],
      "iac_impact": "Cannot deploy public IPs in landing zone subscriptions"
    }
  ],
  "auto_remediation": [...],
  "audit_only": [...],
  "exemptions": [...],
  "security_baseline_alignment": {
    "tls_enforcement": true,
    "https_only": true,
    "no_public_blob": true,
    "managed_identity": false,
    "entra_only_sql": true,
    "no_public_network": true
  }
}
```

## Effect Classification

| Effect | Category | Impact on IaC |
|--------|----------|---------------|
| `Deny` | **Blocker** | IaC MUST NOT create denied resources — deployment will fail |
| `DeployIfNotExists` | Auto-remediate | Platform will auto-fix — IaC can rely on it |
| `Modify` | Auto-remediate | Platform will modify properties — IaC should still set them |
| `Audit` | Advisory | No deployment impact — report to Challenger for review |
| `Disabled` | Inactive | Ignore — policy is not enforced |

## Defender Auto-Assignment Filtering

Microsoft Defender for Cloud auto-assigns many `DeployIfNotExists` policies.
By default, these are **filtered out** of the output because:

1. They are platform-managed (not customer-controlled)
2. They create noise in the governance constraints document
3. They don't represent customer policy decisions

Filter criteria: `assignedBy` field contains "Security Center" or "Microsoft Defender for Cloud".

Use `--include-defender` to include them if needed for audit purposes.

## Integration with Governance Agent

The Governance agent (Warden) uses this skill as follows:

```text
1. Agent reads customer scope from alz-recall (estate → MG prefix)
2. Agent invokes: python .github/skills/azure-governance-discovery/scripts/discover.py ...
3. Script outputs one-line JSON status to stdout: {"status": "ok", "blockers": 3, "total": 47}
4. Agent reads the full JSON envelope from --out path
5. Agent generates 04-governance-constraints.md from the JSON data
6. Agent records findings via alz-recall: alz-recall finding {customer} --severity high ...
```

## Integration with Other Agents

| Agent | How It Uses Discovery Output |
|-------|------------------------------|
| **Strategist** (Step 4) | Reads `blockers[]` to avoid denied resource types in plan |
| **Forge** (Step 5) | Reads `security_baseline_alignment` to know which properties are policy-enforced |
| **Challenger** (Gates) | Reviews blocker count and unresolved audit findings |
| **Sentinel** (Step 8) | Compares live state against governance constraints for drift |

## Existing Tools

This skill augments (does not replace) our existing `src/tools/policy_checker.py`
which provides SDK-based compliance state queries. The discovery script adds:

- Direct ARM REST traversal (no SDK dependency for CI)
- Management group inheritance resolution
- Effect classification and Defender filtering
- Schema-compliant JSON envelope output

## Guardrails

**DO:** Run with `--scope` at the management group level for full estate discovery ·
Filter Defender auto-assignments by default · Classify effects into categories ·
Output one-line JSON status for agent consumption.

**DON'T:** Pull raw policy JSON into LLM context · Include disabled policies ·
Run at subscription scope when MG-scope is available · Skip the Defender filter
without explicit `--include-defender` flag.
