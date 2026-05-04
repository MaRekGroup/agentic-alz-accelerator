# Operational Excellence — Detailed Assessment Report

> **Scope**: `7522c19f-e3b7-46ab-a3f4-e6281173bfcc` | **Assessed**: 2026-05-04T17:35:30.187786+00:00

---

## Overview

Maintain operational health of your workload. Operational excellence includes IaC practices, policy-driven governance, logging, alerting, and automation.

## Score

| Metric | Value |
|--------|-------|
| **Pillar Score** | **68.0/100** |
| Critical findings | 0 |
| High findings | 3 |
| Medium findings | 0 |
| Low findings | 1 |
| Total findings | 4 |

**Assessment**: 🟡 Fair — significant gaps require attention.

## Related CAF Design Areas

| Design Area | Relevance |
|-------------|-----------|
| Governance | Primary |
| Management | Primary |
| Platform Automation & DevOps | Primary |

## Findings Summary

| # | ID | Severity | Title | Confidence | Resources |
|---|-----|----------|-------|-----------|-----------|
| 1 | `OPE-002` | 🟠 High | No policy assignments found | high | 0 |
| 2 | `OPE-004` | 🟠 High | Management group hierarchy not CAF-aligned | medium | 0 |
| 3 | `OPE-006` | 🟠 High | No hub VNet or firewall detected | medium | 0 |
| 4 | `OPE-003` | 🔵 Low | No automation accounts found | medium | 0 |

## Detailed Findings

### OPE-002: No policy assignments found

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | governance |
| ALZ Area | policy |
| Resources Affected | 0 |

**Recommendation**: Assign Azure Policy initiatives (e.g., ASB, CIS) for governance enforcement.

**Remediation Steps**:

1. Assign Azure Security Benchmark initiative at MG or subscription scope

**References**:

- [https://learn.microsoft.com/azure/governance/policy/overview](https://learn.microsoft.com/azure/governance/policy/overview)

---

### OPE-004: Management group hierarchy not CAF-aligned

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | medium |
| CAF Area | resource_org |
| ALZ Area | management_groups |
| Resources Affected | 0 |

**Recommendation**: Adopt CAF enterprise-scale MG hierarchy: platform, landing zones, sandbox, decommissioned.

**Remediation Steps**:

1. Run bootstrap workflow to create CAF-aligned MG hierarchy
2. Move subscriptions to appropriate MGs

**References**:

- [https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-management-groups](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-management-groups)

---

### OPE-006: No hub VNet or firewall detected

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | medium |
| CAF Area | network |
| ALZ Area | networking |
| Resources Affected | 0 |

**Recommendation**: Deploy a hub VNet with Azure Firewall for centralized network governance.

**Remediation Steps**:

1. Deploy connectivity landing zone with hub-spoke topology

**References**:

- [https://learn.microsoft.com/azure/architecture/networking/architecture/hub-spoke](https://learn.microsoft.com/azure/architecture/networking/architecture/hub-spoke)

---

### OPE-003: No automation accounts found

| Attribute | Value |
|-----------|-------|
| Severity | 🔵 Low |
| Confidence | medium |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 0 |

**Recommendation**: Deploy an Automation Account for runbook-based operations.

**Remediation Steps**:

1. Create automation account in management subscription

**References**:

- [https://learn.microsoft.com/azure/automation/overview](https://learn.microsoft.com/azure/automation/overview)

---

## Remediation Priority Matrix

| Priority | ID | Title | Effort | Impact |
|----------|-----|-------|--------|--------|
| 1 | `OPE-002` | No policy assignments found | Low | High |
| 2 | `OPE-004` | Management group hierarchy not CAF-aligned | Medium | High |
| 3 | `OPE-006` | No hub VNet or firewall detected | Low | High |
| 4 | `OPE-003` | No automation accounts found | Low | Medium |
