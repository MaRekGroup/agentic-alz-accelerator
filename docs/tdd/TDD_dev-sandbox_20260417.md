# As-Built Technical Design Document

## dev-sandbox

> **Profile**: sandbox · **Environment**: dev · **Generated**: 2026-04-17 22:48 UTC

| Field | Value |
|-------|-------|
| Subscription | mrg-lz-sandbox |
| Subscription ID | `<SUB-10-ID>` |
| Location | southcentralus |
| IaC Framework | Bicep |
| Deployment ID | (manual) |
| Document Version | 1.0 (auto-generated) |

---

## 1. Executive Summary

This Technical Design Document (TDD) describes the as-built state of the
'dev-sandbox' landing zone deployed to subscription
'mrg-lz-sandbox' in southcentralus.
This landing zone provides development and testing with budget enforcement, relaxed policies, and standalone networking.

The deployment was executed using Bicep via the GitHub Actions
CI/CD pipeline with OIDC authentication and environment approval gates.
All resources comply with the CAF enterprise-scale baseline policies.

### Key Facts

| Attribute | Value |
|-----------|-------|
| Landing Zone | dev-sandbox |
| Profile | sandbox |
| Subscription | mrg-lz-sandbox (`<SUB-10-ID>`) |
| Region | southcentralus |
| Environment | dev |
| IaC Framework | Bicep |
| Deployment ID | (manual/CLI) |

---

## 2. Architecture Diagram

The following diagram illustrates the as-built architecture of this landing zone,
including all deployed resources, networking topology, and security controls.
Icons follow the official Microsoft Azure Architecture Icon set.

![dev-sandbox Architecture — As-Built](TDD_dev-sandbox_20260417_architecture.png)

*Figure 1: dev-sandbox Architecture — As-Built*

---

## 3. Resource Inventory

Complete inventory of Azure resources deployed in this landing zone,
queried from Azure Resource Graph at generation time.

### 3.1 Resource Summary by Type

| Resource | Count | Configuration |
|----------|-------|---------------|
| Virtual Network (Standalone) | 1 | Sandbox CIDR 10.10.0.0/16 |
| Subnets | 2 | Dev, Test |
| Budget | 1 | $500/month cap |
| Azure Policy Assignments | 5+ | Sandbox baseline (no public IPs) |

---
## 4. Network Topology

This sandbox landing zone uses a standalone virtual network with no peering to the hub. It is isolated by design for development and testing.

| Network Component | Configuration |
|-------------------|---------------|
| Standalone VNet CIDR | 10.10.0.0/16 |
| Dev Subnet | 10.10.1.0/24 |
| Test Subnet | 10.10.2.0/24 |
| Hub Peering | None (isolated) |

---
## 5. Security Posture

Security controls applied to this landing zone as part of the CAF
enterprise-scale baseline. All controls are enforced via Azure Policy
and validated during deployment.

### 5.1 Non-Negotiable Security Rules

| # | Rule | Description | Status |
|---|------|-------------|--------|
| 1 | Diagnostic Settings | All resources ship logs to central Log Analytics workspace | Enforced |
| 2 | HTTPS Only | All web endpoints require TLS 1.2+ | Enforced |
| 3 | No Public IPs | Disallowed on compute (except for allowed profiles) | Enforced |
| 4 | Encryption at Rest | All storage & databases use platform-managed or CMK encryption | Enforced |
| 5 | NSG on Every Subnet | Network Security Groups required on all subnets | Enforced |
| 6 | Defender for Cloud | Enabled on all resource types (per profile plan count) | Enforced |

### 5.2 Defender for Cloud Plans

| Defender Plan | Status |
|---------------|--------|
| Servers | Enabled |
| ARM | Enabled |

### 5.3 Azure Policy Assignments

The following policy initiatives are assigned at the management group level
and inherited by this subscription:

| Initiative | Scope |
|------------|-------|
| CAF Foundation | Core governance (tagging, allowed locations, allowed SKUs) |
| CAF Security Baseline | CIS benchmark controls, encryption, network rules |
| Defender for Cloud | Auto-enable Defender plans and security configurations |
| Monitoring | Diagnostic settings, Log Analytics agent, dependency agent |
| Network | NSG rules, flow logs, VNet service endpoints |

---

## 6. Compliance Status

Post-deployment compliance scan results. The CI/CD pipeline validates
compliance after every deployment and fails the pipeline if compliance
falls below 80%.

### 6.1 Compliance Summary

| Metric | Value |
|--------|-------|
| Compliance Percentage | Populated at deployment time |
| Total Policies Evaluated | Populated at deployment time |
| Compliant Resources | Populated at deployment time |
| Non-Compliant Resources | Populated at deployment time |
| Exempt Resources | Populated at deployment time |

> *This section is auto-populated with live data when the TDD is
> generated as part of the CI/CD pipeline (post-deployment verify stage).
> For pre-deployment TDDs, values show 'Populated at deployment time'.*

---

## 7. Cost Governance

| Control | Configuration |
|---------|---------------|
| Monthly Budget | $500 |
| Alert Thresholds | 80/100% |
| Alert Recipients | Platform team + subscription owner |
| Cost Anomaly Detection | Enabled |
| Tag Requirements | Environment, Owner, CostCenter, Project |

---

## 8. Operational Model

### 8.1 Monitoring & Alerting

| Scan Type | Frequency | Source |
|-----------|-----------|--------|
| Compliance Scan | Every 30 minutes | monitor.yml |
| Drift Detection | Every hour | monitor.yml |
| Full Audit Report | Daily 6 AM UTC | monitor.yml |
| Cost Alerts | Real-time | Azure Cost Management |
| Security Alerts | Real-time | Defender for Cloud → Sentinel |

### 8.2 Change Management

All infrastructure changes follow the GitOps workflow:

| Step | Action | Responsible |
|------|--------|-------------|
| 1 | Create feature branch | Developer |
| 2 | Push changes & open PR | Developer |
| 3 | Automated PR validation (lint, security, cost, what-if) | 5-pr-validate.yml |
| 4 | Peer review & approval | Platform team |
| 5 | Merge to main | Developer |
| 6 | Trigger deploy workflow | Platform team |
| 7 | Environment approval gate | Required reviewers |
| 8 | Deployment + post-deploy verification | Reusable pipeline |
| 9 | TDD auto-generated | tdd_generator.py |

### 8.3 Disaster Recovery

| Component | Protection | Recovery Time |
|-----------|------------|---------------|
| IaC Templates | Git repository | Minutes |
| Configuration | subscriptions.json | Minutes |

---

## 9. Appendix

### 9.1 Full Estate Architecture

Overview of the complete Azure Landing Zone estate showing all platform
and application landing zones.

![Full Azure Landing Zone Estate](TDD_dev-sandbox_20260417_estate.svg)

*Figure 2: Full Azure Landing Zone Estate*

### 9.2 Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-17 | Auto-generated by CI/CD pipeline | Initial as-built TDD |

### 9.3 References

| Document | Location |
|----------|----------|
| CAF Enterprise-Scale | <https://aka.ms/caf/enterprise-scale> |
| Azure Landing Zone Accelerator | <https://aka.ms/alz/accelerator> |
| Landing Zone Profiles | `src/config/landing_zone_profiles.yaml` |
| Subscription Config | `environments/subscriptions.json` |
| CI/CD Workflows | `.github/workflows/` |