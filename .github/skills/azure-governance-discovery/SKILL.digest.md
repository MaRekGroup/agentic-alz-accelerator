<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Governance Discovery Skill (Digest)

Deterministic Azure Policy discovery via batched ARM REST traversal for Enterprise Landing Zones.

## Usage

```bash
python .github/skills/azure-governance-discovery/scripts/discover.py \
    --scope /subscriptions/{sub-id} \
    --customer marekgroup \
    --out agent-output/marekgroup/04-governance-constraints.json
```

## Flags

| Flag | Required | Description |
|------|----------|-------------|
| `--scope` | Yes | ARM scope (subscription or management group) |
| `--customer` | Yes | Customer name for output path |
| `--out` | Yes | Output path for JSON envelope |
| `--include-defender` | No | Include Defender auto-assigned policies (excluded by default) |
| `--effects` | No | Comma-separated effects to include (default: Deny,DeployIfNotExists,Modify,Audit) |

## Effect Classification

| Effect | Category | IaC Impact |
|--------|----------|------------|
| `Deny` | **Blocker** | MUST NOT create denied resources |
| `DeployIfNotExists` | Auto-remediate | Platform auto-fixes; IaC can rely on it |
| `Modify` | Auto-remediate | Platform modifies properties; IaC should still set them |
| `Audit` | Advisory | No deployment impact |
| `Disabled` | Inactive | Ignore |

## Output Schema

`governance-constraints-v1` envelope containing: summary (counts by effect), blockers[] (Deny policies with resource types and IaC impact), auto_remediation[], audit_only[], exemptions[], security_baseline_alignment (6-rule boolean map).

> _See SKILL.md for full JSON schema example._

## Defender Filtering

Defender auto-assignments filtered by default (assignedBy contains "Security Center" or "Microsoft Defender"). Use `--include-defender` for audit purposes.

## Integration

| Agent | Usage |
|-------|-------|
| Strategist (Step 4) | Reads blockers[] to avoid denied resource types |
| Forge (Step 5) | Reads security_baseline_alignment for policy-enforced properties |
| Challenger (Gates) | Reviews blocker count and unresolved audit findings |
| Sentinel (Step 8) | Compares live state against governance constraints |

## Guardrails

**DO:** Run at MG-scope when available · Filter Defender by default · Output one-line JSON status.

**DON'T:** Pull raw policy JSON into LLM context · Include disabled policies · Skip Defender filter without `--include-defender`.
