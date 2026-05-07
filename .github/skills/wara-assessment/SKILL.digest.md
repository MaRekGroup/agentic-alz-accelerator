<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# WARA Assessment Skill (Digest)

Evaluate Azure environments against WAF 5 pillars and CAF design areas.

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

| Severity | Deduction | Description |
|----------|-----------|-------------|
| Critical | −20 | Security baseline violation or data loss risk |
| High | −10 | WAF/CAF misalignment with operational impact |
| Medium | −5 | Best practice gap with moderate impact |
| Low | −2 | Minor improvement opportunity |

Overall score = equal-weighted average of all 5 pillar scores. Floor is 0.

## Confidence Levels

| Level | Meaning |
|-------|---------|
| High | Deterministic query, conclusive evidence |
| Medium | Possible false positives, manual review recommended |
| Low | Heuristic, context-dependent |

## Check Types

| Type | Description |
|------|-------------|
| `resource_graph` | KQL against Azure Resource Graph (`match: any` or `empty`) |
| `discovery_field` | Dot-notation field from DiscoveryResult |
| `policy` | Policy compliance from discovery data |
| `custom` | Named method on WaraEngine for complex logic |

## CAF Design Area Mapping

| CAF Area | Key | Checks Focus |
|----------|-----|-------------|
| Billing & Tenant | `billing_tenant` | Subscription org, MG hierarchy |
| Identity & Access | `identity_access` | RBAC, PIM, managed identity |
| Resource Organization | `resource_org` | MG hierarchy, tagging, naming |
| Network Topology | `network` | Hub-spoke, peerings, DNS, firewall |
| Security | `security` | TLS, encryption, Defender, Sentinel |
| Management | `management` | LAW, automation, diagnostics |
| Governance | `governance` | Policy assignments, budgets |
| Platform Automation | `platform_automation` | IaC presence, CI/CD |

## ALZ Design Area → IaC Module Mapping

| ALZ Area | Key | Maps to Module |
|----------|-----|----------------|
| Billing & Tenant | `billing_tenant` | `billing-and-tenant/` |
| Identity | `identity` | `identity/` |
| Management Groups | `management_groups` | `billing-and-tenant/` |
| Policy | `policy` | `policies/`, `governance/` |
| Networking | `networking` | `connectivity/`, `networking/` |
| Logging | `logging` | `logging/`, `management/` |
| Security | `security` | `security/`, `platform-security/` |

> _See SKILL.md for check YAML schema, CAF lifecycle mapping, and writing new checks._
