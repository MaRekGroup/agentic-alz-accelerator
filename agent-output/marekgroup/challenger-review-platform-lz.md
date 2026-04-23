# ⚔️ Challenger — Adversarial Architecture Review

> **Agent**: Challenger (⚔️)
> **Scope**: All 4 deployed platform landing zones (Management, Connectivity, Identity, Security)
> **Complexity Tier**: Standard (4 resource types across 4 subscriptions, multi-sub architecture, custom policies)
> **Review Pass**: 1 of 2
> **Date**: 2025-06-17

---

## Executive Summary

| Dimension | Verdict | Must-Fix | Should-Fix | Consider |
|-----------|---------|----------|------------|----------|
| CAF Alignment | ⚠️ Gaps | 1 | 2 | 1 |
| WAF Pillars | ⚠️ Gaps | 2 | 3 | 2 |
| Security Baseline | 🔴 Violations | 3 | 2 | 0 |
| Cost Governance | ✅ Solid | 0 | 1 | 1 |
| AVM Compliance | ⚠️ Partial | 1 | 2 | 0 |
| Naming & Tagging | ⚠️ Gaps | 1 | 1 | 0 |
| **TOTAL** | | **8** | **11** | **4** |

**Verdict: 🔴 DEPLOYMENT BLOCKED — 8 must-fix findings require resolution.**

---

## 1. CAF Alignment

### MUST-FIX

**CAF-1: Management Group hierarchy not deployed**

- `infra/bicep/modules/billing-and-tenant/main.bicep` exists but is **never called** by any workflow or parameter file. All 4 platform LZs deploy directly to subscriptions with no management group structure.
- **Impact**: No policy inheritance, no subscription vending, no org-level governance. This is foundational to CAF enterprise-scale.
- **Required**: Deploy management group hierarchy BEFORE platform LZs; assign subscriptions to appropriate MG children.

### SHOULD-FIX

**CAF-2: Identity LZ is a thin shell**

- `infra/bicep/parameters/platform-identity-prod.bicepparam` deploys only two managed identities and two RBAC role assignments. No Active Directory Domain Services, no Entra ID configuration, no Conditional Access references.
- **Impact**: CAF Identity & Access design area is barely addressed. A real landing zone needs identity governance beyond two service principals.

**CAF-3: Connectivity lacks cross-subscription peering**

- Hub-spoke is deployed but there's no VNet peering from spoke subscriptions (Management, Identity, Security) back to the hub. The hub exists in isolation.
- **Impact**: No network connectivity between platform subscriptions. Defender, Sentinel, and Key Vault can't reach resources across subscriptions via private networking.

### CONSIDER

**CAF-4: No subscription vending or landing zone factory**

- Only 4 hardcoded platform profiles exist. No mechanism for creating application landing zones (corp/online), which is the primary consumer of the platform.

---

## 2. WAF Pillars

### MUST-FIX

**WAF-1: Zero high-availability / disaster recovery design (Reliability)**

- **Single-region deployment only** (`southcentralus`). No secondary region, no geo-replication, no Recovery Services Vault, no ASR configuration.
- Log Analytics data, Sentinel data, Key Vault secrets — all single-region with no backup.
- Security workspace retention is 730 days but there's no backup or replication of that data.
- **Impact**: Total data loss if `southcentralus` has a regional outage.

**WAF-2: Azure Firewall disabled in production (Security)**

- `infra/bicep/parameters/platform-connectivity-prod.bicepparam` has `deployAzureFirewall = false`. The entire hub-spoke topology has **no network traffic inspection** in production.
- The DDoS Protection Plan is also disabled (`enableDdosProtection = false`).
- **Impact**: No east-west or north-south traffic filtering. Any workload in a spoke can reach any other workload and the internet directly, defeating the purpose of hub-spoke.

### SHOULD-FIX

**WAF-3: Log Analytics public ingestion/query enabled (Security)**

- `infra/bicep/modules/logging/main.bicep` lines 37–38: `publicNetworkAccessForIngestion: 'Enabled'` and `publicNetworkAccessForQuery: 'Enabled'`.
- This is the centralized logging workspace. It should enforce private-only access in production.

**WAF-4: No activity log diagnostic settings deployed**

- `infra/bicep/modules/logging/main.bicep` has a comment "requires subscription-scope deployment" but the activity log diagnostic setting is never deployed anywhere. Platform activity logs are not being captured.

**WAF-5: Automation Account has no managed identity**

- `infra/bicep/modules/logging/main.bicep` deploys `Microsoft.Automation/automationAccounts` with no `identity` block. Compare to `infra/bicep/modules/platform-security/main.bicep` which correctly uses AVM with `systemAssigned: true`.

### CONSIDER

**WAF-6: Management workspace retention only 90 days**

- `infra/bicep/parameters/platform-management-prod.bicepparam`: `retentionDays = 90`. Most compliance frameworks (SOC 2, HIPAA, PCI-DSS) require 365+ days. Security workspace has 730 days, but the management workspace where most operational logs go has only 90.

**WAF-7: Budget amounts seem arbitrary**

- Management $500, Identity $200, Connectivity $2,000, Security $1,000. No documented sizing rationale. Connectivity at $2,000 with Firewall+DDoS disabled seems over-budgeted; Security at $1,000 with 11 Defender plans + Sentinel seems under-budgeted.

---

## 3. Security Baseline (6 Non-Negotiable Rules)

### MUST-FIX

**SEC-1: Log Analytics workspace violates Rule #6 — Public network access in production**

- `infra/bicep/modules/logging/main.bicep`: `publicNetworkAccessForIngestion: 'Enabled'`, `publicNetworkAccessForQuery: 'Enabled'`
- Rule #6: "Public network disabled (prod)". This is the **centralized logging workspace** — the most sensitive data plane in the platform.
- **Required**: Set both to `'Disabled'` and deploy Private Link scope + private endpoints.

**SEC-2: SOAR playbooks are empty scaffolds deployed to production**

- `infra/bicep/modules/platform-security/soar/main.bicep`: All 4 Logic Apps have `actions: {}` — they're completely empty. They have `state: 'Enabled'` but do nothing.
- These are deployed with `UserAssigned` managed identity that has no RBAC assignments, meaning if they DID have logic, they couldn't execute.
- **Impact**: False sense of security automation. Incident response is non-functional.

**SEC-3: Threat Intelligence connector disabled in production**

- `infra/bicep/parameters/platform-security-prod.bicepparam`: `enableThreatIntelligence = false`
- Sentinel without TI feeds has significantly reduced detection capability.

### SHOULD-FIX

**SEC-4: Defender securityContacts uses deprecated 2020-01-01-preview API**

- `infra/bicep/modules/platform-security/defender/main.bicep`: `Microsoft.Security/securityContacts@2020-01-01-preview`. This API version may stop working.

**SEC-5: No network security on Bastion subnet**

- `infra/bicep/modules/connectivity/hub-spoke/main.bicep`: Bastion is deployed but the `AzureBastionSubnet` is explicitly excluded from NSG assignment. While Azure requires a specific NSG for Bastion, the module skips it entirely instead of providing the required Bastion-specific NSG rules.

---

## 4. Cost Governance ✅

Cost governance is the **strongest area** of this deployment. Every module has budget resources with proper 80/100/120% forecast alerts.

### SHOULD-FIX

**COST-1: Budget `startDate` uses `utcNow()` — redeployments reset the budget**

- Every module uses `param now string = utcNow('yyyy-MM-01')`. This means every redeployment creates a **new budget period starting from the current month**, losing historical budget tracking. Budget start dates should be fixed values in parameter files.

### CONSIDER

**COST-2: No action groups on 100% and 120% thresholds**

- Budget notifications at all 3 tiers go to email only. The 100% and 120% thresholds should trigger action groups for automated responses (e.g., stopping non-essential workloads, sending Teams/Slack alerts).

---

## 5. AVM Compliance

### MUST-FIX

**AVM-1: Most modules are hand-rolled instead of AVM**

- Only 2 AVM modules used: `avm/res/key-vault/vault:0.6.0` and `avm/res/automation/automation-account:0.9.0` (both in platform-security only).
- Missing AVM where available:
  - `avm/res/operational-insights/workspace` for Log Analytics (3 hand-rolled workspaces)
  - `avm/res/network/virtual-network` for VNets
  - `avm/res/network/azure-firewall` for Firewall
  - `avm/res/network/bastion-host` for Bastion
  - `avm/ptn/network/hub-networking` for entire hub topology
- **Impact**: AVM modules include built-in diagnostic settings, RBAC, private endpoints, and tagging. The hand-rolled modules lack these. This is an AVM-first policy violation.

### SHOULD-FIX

**AVM-2: AVM module versions may be outdated**

- `avm/res/key-vault/vault:0.6.0` — current may be higher. No dependabot or automated version checking.

**AVM-3: No diagnostic settings on most resources**

- Hand-rolled modules (Bastion, Gateways, NSGs, Key Vault in security module, Logic Apps) have no `diagnosticSettings` blocks. AVM modules include these by default, which is another reason for AVM-first.

---

## 6. Naming & Tagging

### MUST-FIX

**TAG-1: Missing required tags on resource groups**

- Per `AGENTS.md`: Required tags are `Environment`, `Owner`, `CostCenter`, `Project`, `ManagedBy`.
- Actual tags across all `.bicepparam` files: only `environment`, `managedBy`, and `platform`. Missing: **`Owner`**, **`CostCenter`**, **`Project`**.
- Also: tag keys use `camelCase` (`managedBy`) instead of `PascalCase` (`ManagedBy`) as specified.

### SHOULD-FIX

**TAG-2: Prefix inconsistency between modules**

- Parameter files use `prefix = 'mrg'`. The `main.bicep` root template uses `var prefix = 'alz-${managementGroupName}'`. Platform modules use their own prefix patterns. This creates inconsistent naming: some resources are `mrg-*` and others would be `alz-*`.

---

## 7. CI/CD & Operational Concerns

### MUST-FIX

**OPS-1: Workflow `resolve` step leaks secrets through `toJson(secrets)`**

- `.github/workflows/reusable-deploy.yml` resolve step: `ALL_SECRETS: ${{ toJson(secrets) }}` passes ALL repository secrets as an environment variable. While the shell script only extracts specific keys, any compromise of the runner process could dump all secrets.
- **Required**: Remove `toJson(secrets)` and pass individual secrets explicitly.

### SHOULD-FIX

**OPS-2: `continue-on-error: true` on What-If step**

- The plan stage has `continue-on-error: true` on the what-if command. This means deployment can proceed even if what-if reveals destructive changes or errors. The whole point of what-if is to gate the deployment.

**OPS-3: No lock on critical resources**

- No `CanNotDelete` resource locks on Log Analytics workspaces, Key Vaults, or hub VNet. An accidental deployment or RBAC mistake could delete the centralized logging or networking infrastructure.

---

## Findings Summary by Severity

### 🔴 Must-Fix (8) — Blocks Deployment

| ID | Finding | Impact |
|----|---------|--------|
| CAF-1 | Management group hierarchy not deployed | No policy inheritance, no org governance |
| WAF-1 | No HA/DR — single region only | Total data loss risk |
| WAF-2 | Azure Firewall disabled in production | No network traffic inspection |
| SEC-1 | LAW public network access enabled (prod) | Security baseline Rule #6 violation |
| SEC-2 | SOAR playbooks are empty shells | False security automation |
| SEC-3 | Threat Intelligence disabled | Reduced Sentinel detection |
| AVM-1 | Most modules hand-rolled instead of AVM | Missing diagnostics, RBAC, PE |
| TAG-1 | Missing required tags (Owner, CostCenter, Project) | Governance non-compliance |

### 🟡 Should-Fix (11)

| ID | Finding |
|----|---------|
| CAF-2 | Identity LZ is minimal (no AD/Entra) |
| CAF-3 | No VNet peering between subscriptions |
| WAF-3 | LAW public ingestion/query enabled |
| WAF-4 | Activity log diagnostics not deployed |
| WAF-5 | Automation Account lacks managed identity |
| SEC-4 | Deprecated securityContacts API version |
| SEC-5 | No Bastion NSG rules |
| COST-1 | Budget startDate resets on redeploy |
| AVM-2 | AVM module versions potentially outdated |
| AVM-3 | Missing diagnostic settings on most resources |
| TAG-2 | Prefix inconsistency (mrg vs alz) |

### 🔵 Consider (4)

| ID | Finding |
|----|---------|
| CAF-4 | No subscription vending mechanism |
| WAF-6 | 90-day retention may not meet compliance |
| WAF-7 | Budget amounts lack sizing rationale |
| COST-2 | No action groups on higher budget thresholds |

### ⚠️ Operational Risk

| ID | Finding |
|----|---------|
| OPS-1 | `toJson(secrets)` leaks all secrets to runner env |
| OPS-2 | `continue-on-error` on what-if bypasses safety |
| OPS-3 | No resource locks on critical infrastructure |

---

## Recommended Remediation Priority

1. **OPS-1** — Fix `toJson(secrets)` immediately (security vulnerability)
2. **SEC-1** — Disable public access on Log Analytics workspace
3. **WAF-2** — Enable Azure Firewall (or document explicit risk acceptance)
4. **CAF-1** — Deploy management group hierarchy
5. **TAG-1** — Add missing required tags
6. **AVM-1** — Migrate to AVM modules iteratively
7. **WAF-1** — Design and document DR strategy (even if not deployed now)
8. **SEC-2/SEC-3** — Either implement SOAR playbooks or disable them; enable TI

---

**This is Pass 1 of 2 for Standard complexity. Pass 2 will re-review after must-fix items are addressed.**
