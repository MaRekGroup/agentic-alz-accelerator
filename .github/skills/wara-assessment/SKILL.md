---
name: wara-assessment
description: "WAF 5-pillar check catalog, scoring model, severity definitions, and CAF design area mappings. USE FOR: brownfield assessment, compliance scoring, recommendation generation. DO NOT USE FOR: discovery (use brownfield-discovery), report formatting (use assessment-report)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: azure-assessment
---

# WARA Assessment Skill

Domain knowledge for evaluating Azure environments against the Well-Architected
Framework (WAF) 5 pillars and Cloud Adoption Framework (CAF) design areas.

## Implementation Reference

- **Engine:** `src/tools/wara_engine.py` (`WaraEngine`)
- **Check catalog:** `src/config/wara_checks.yaml`
- **Data model:** `Finding`, `PillarScore`, `AssessmentResult`
- **Input:** `DiscoveryResult` from `src/tools/discovery.py`

## WAF 5 Pillars

| Pillar | Prefix | Focus |
|--------|--------|-------|
| Reliability | `REL-` | HA, zones, redundancy, backup, DR |
| Security | `SEC-` | TLS, encryption, network ACLs, identity, secrets |
| Cost Optimization | `COS-` | Budgets, orphaned resources, right-sizing |
| Operational Excellence | `OPE-` | Policies, tagging, logging, automation, MG hierarchy |
| Performance | `PER-` | SKU selection, replication tier, throughput |

## Scoring Model

Each pillar starts at 100 points. Findings deduct points by severity:

| Severity | Deduction | Description |
|----------|-----------|-------------|
| Critical | −20 | Security baseline violation or data loss risk |
| High | −10 | WAF/CAF misalignment with operational impact |
| Medium | −5 | Best practice gap with moderate impact |
| Low | −2 | Minor improvement opportunity |

**Overall score** = equal-weighted average of all 5 pillar scores.

Pillar score floor is 0 (never negative).

## Confidence Levels

| Level | Meaning |
|-------|---------|
| High | Query is deterministic, evidence is conclusive |
| Medium | Query may have false positives, manual review recommended |
| Low | Heuristic check, context-dependent |

## Check Types

### `resource_graph`

Runs a KQL query against Azure Resource Graph. Returns matching resources as evidence.

- `match: any` — finding if query returns results (non-compliant resources found)
- `match: empty` — finding if query returns zero results (expected resource missing)

### `discovery_field`

Checks a field from the `DiscoveryResult` using dot-notation path.

- `match: any` — finding if field has data
- `match: empty` — finding if field is empty/null

### `policy`

Evaluates policy compliance from discovery data.

### `custom`

Calls a named method on `WaraEngine` for complex evaluation logic.

## CAF Design Area Mapping

| CAF Area | Key | Checks Focus |
|----------|-----|-------------|
| Billing & Tenant | `billing_tenant` | Subscription organization, MG hierarchy |
| Identity & Access | `identity_access` | RBAC, PIM, managed identity, Key Vault auth |
| Resource Organization | `resource_org` | MG hierarchy, tagging, naming conventions |
| Network Topology | `network` | Hub-spoke, peerings, DNS, firewall, public IPs |
| Security | `security` | TLS, encryption, Defender, Sentinel, Key Vault |
| Management | `management` | LAW, automation, diagnostics, retention |
| Governance | `governance` | Policy assignments, budgets, compliance |
| Platform Automation | `platform_automation` | IaC presence, CI/CD pipelines |

## CAF Lifecycle Mapping

Each check also maps to CAF lifecycle stages:

| Stage | Description |
|-------|-------------|
| `strategy` | Business alignment and justification |
| `plan` | Digital estate assessment and migration planning |
| `ready` | Landing zone readiness and prerequisites |
| `adopt` | Migration and modernization execution |
| `govern` | Policy enforcement, compliance, cost management |
| `manage` | Operational monitoring, remediation, optimization |

## ALZ Design Area Mapping

| ALZ Area | Key | Maps to IaC Module |
|----------|-----|--------------------|
| Billing & Tenant | `billing_tenant` | `billing-and-tenant/` |
| Identity | `identity` | `identity/` |
| Management Groups | `management_groups` | `billing-and-tenant/` |
| Policy | `policy` | `policies/`, `governance/` |
| Networking | `networking` | `connectivity/`, `networking/` |
| Logging | `logging` | `logging/`, `management/` |
| Security | `security` | `security/`, `platform-security/` |
| Platform DevOps | `platform_devops` | CI/CD pipelines |

## Writing New Checks

See `.github/instructions/wara-checks.instructions.md` for conventions.

Quick reference:

```yaml
- id: SEC-010                      # Pillar prefix + sequential number
  title: "Short description"       # Human-readable
  pillar: security                 # One of the 5 pillars
  caf_area: security               # CAF design area key
  alz_area: security               # ALZ design area key
  severity: high                   # critical | high | medium | low
  confidence: high                 # high | medium | low
  scope: subscription              # tenant | management_group | subscription | resource_group
  query_type: resource_graph       # resource_graph | discovery_field | policy | custom
  query: |                         # KQL or dot-path
    resources
    | where ...
  match: any                       # any | empty | custom
  recommendation: "Fix guidance"
  remediation_steps:
    - "Step 1"
  references:
    - "https://learn.microsoft.com/..."
  mappings:
    waf_pillar: [security]
    caf_lifecycle: [govern, manage]
```
