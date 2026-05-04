# WARA Assessment Report — 7522c19f-e3b7-46ab-a3f4-e6281173bfcc

> Assessed on 2026-05-04T17:35:30.187786+00:00

## Executive Summary

| Metric | Value |
|--------|-------|
| Overall Score | **92.6/100** |
| Checks Run | 221 |
| Checks Passed | 216 |
| Findings | 5 |

## Pillar Scores

| Pillar | Score | Critical | High | Medium | Low |
|--------|-------|----------|------|--------|-----|
| Security | 95.0 | 0 | 0 | 1 | 0 |
| Reliability | 100.0 | 0 | 0 | 0 | 0 |
| Cost Optimization | 100.0 | 0 | 0 | 0 | 0 |
| Operational Excellence | 68.0 | 0 | 3 | 0 | 1 |
| Performance Efficiency | 100.0 | 0 | 0 | 0 | 0 |

## Findings

### 🟠 High — No policy assignments found (`OPE-002`)

- **Pillar**: Operational Excellence
- **CAF Area**: governance
- **ALZ Area**: policy
- **Confidence**: high
- **Resources affected**: 0

**Recommendation**: Assign Azure Policy initiatives (e.g., ASB, CIS) for governance enforcement.

**Remediation**:
1. Assign Azure Security Benchmark initiative at MG or subscription scope

**References**:
- https://learn.microsoft.com/azure/governance/policy/overview

### 🟠 High — Management group hierarchy not CAF-aligned (`OPE-004`)

- **Pillar**: Operational Excellence
- **CAF Area**: resource_org
- **ALZ Area**: management_groups
- **Confidence**: medium
- **Resources affected**: 0

**Recommendation**: Adopt CAF enterprise-scale MG hierarchy: platform, landing zones, sandbox, decommissioned.

**Remediation**:
1. Run bootstrap workflow to create CAF-aligned MG hierarchy
2. Move subscriptions to appropriate MGs

**References**:
- https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-management-groups

### 🟠 High — No hub VNet or firewall detected (`OPE-006`)

- **Pillar**: Operational Excellence
- **CAF Area**: network
- **ALZ Area**: networking
- **Confidence**: medium
- **Resources affected**: 0

**Recommendation**: Deploy a hub VNet with Azure Firewall for centralized network governance.

**Remediation**:
1. Deploy connectivity landing zone with hub-spoke topology

**References**:
- https://learn.microsoft.com/azure/architecture/networking/architecture/hub-spoke

### 🟡 Medium — No Sentinel workspace detected (`SEC-009`)

- **Pillar**: Security
- **CAF Area**: security
- **ALZ Area**: security
- **Confidence**: medium
- **Resources affected**: 0

**Recommendation**: Enable Microsoft Sentinel for SIEM/SOAR capabilities.

**Remediation**:
1. Onboard Sentinel to the management Log Analytics workspace

**References**:
- https://learn.microsoft.com/azure/sentinel/quickstart-onboard

### 🔵 Low — No automation accounts found (`OPE-003`)

- **Pillar**: Operational Excellence
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: medium
- **Resources affected**: 0

**Recommendation**: Deploy an Automation Account for runbook-based operations.

**Remediation**:
1. Create automation account in management subscription

**References**:
- https://learn.microsoft.com/azure/automation/overview
