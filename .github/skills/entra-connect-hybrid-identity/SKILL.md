---
name: entra-connect-hybrid-identity
description: "Hybrid identity synchronization and federation migration patterns for Azure Landing Zones. USE FOR: Cloud Sync, Entra Connect Sync, ADFS migration, pass-through authentication, password hash synchronization, seamless SSO, multi-forest topology, filter scoping, staged rollout, and sync disaster recovery. DO NOT USE FOR: Conditional Access (use entra-conditional-access), PIM or access reviews (use entra-identity-governance), workload identity federation (use workload-identity-federation), or Azure AD Domain Services (future skill: aadds-managed-domain)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: azure-identity
---

# Entra Connect Hybrid Identity Skill

## Overview

This skill covers the design choices that connect on-premises Active Directory to Microsoft Entra ID: Cloud Sync, Entra Connect Sync, password hash synchronization (PHS), pass-through authentication (PTA), Seamless SSO, ADFS migration, multi-forest scope control, staged rollout, and disaster recovery for sync infrastructure.

This skill is intentionally brownfield-leaning. Most greenfield Entra tenants start cloud-only and do not need sync or federation. Hybrid identity usually appears during mergers and acquisitions, datacenter exits, regulated migrations, or long-tail application modernization where an existing AD footprint must be retained during a transition.

Treat synchronization and authentication as related but separate decisions. **Cloud Sync vs. Entra Connect Sync** chooses the sync plane. **PHS vs. PTA vs. federation** chooses the sign-in plane. Default to **Cloud Sync + PHS** unless a legacy dependency, device-sync requirement, or federation-only control forces a different path.

> **Implementation note:** No Bicep or Terraform is required for this skill. Hybrid identity state mostly lives in Microsoft Entra admin center, Microsoft Graph, Microsoft Entra Connect wizards, and PowerShell modules rather than in ARM-native resource models.

## CAF Design Area Mapping

| CAF Design Area | Priority | Hybrid identity contribution |
|-----------------|----------|------------------------------|
| **Identity & Access** | **Primary** | Establishes source of authority, sign-in method, and coexistence model between AD and Entra |
| Governance | Secondary | Constrains pilot scope, break-glass access, and object authority during migration |
| Management | Secondary | Requires health monitoring, rollback planning, and operational runbooks |

## WAF Pillar Mapping

| WAF Pillar | Priority | Why it matters |
|------------|----------|----------------|
| **Security** | **Primary** | Reduces dependence on aging federation infrastructure and tightens identity control-plane design |
| **Reliability** | **Primary** | Authentication must stay available through pilot, cutover, failover, and rollback |
| Operational Excellence | Secondary | Successful migration depends on disciplined discovery, staged rollout, and monitoring |

## Decision Tree: Which Sync Method?

| Tenant profile | Recommended sync plane | Recommended sign-in plane | Why |
|----------------|------------------------|----------------------------|-----|
| New hybrid deployment with standard user and group sync | **Cloud Sync** | **PHS** | Default modern pattern; lightweight, cloud-managed, and resilient |
| Existing Entra Connect deployment that must keep device sync or unsupported legacy features | **Entra Connect Sync** | **PHS** | Keep Connect when Cloud Sync feature parity is insufficient |
| Security team requires on-premises password validation or immediate account-state enforcement | Cloud Sync or Connect Sync | **PTA** with Seamless SSO | Keeps password validation on-prem without full federation |
| Existing ADFS with no durable federation-only requirement | Cloud Sync or Connect Sync | **Migrate to PHS** by staged rollout | Microsoft recommends cloud authentication; PHS is the baseline |
| Existing ADFS with temporary third-party or smart-card dependency that cannot move yet | Sync choice depends on topology | **Temporary federation**, then staged migration | Keep federation only as an explicit exception with an exit plan |
| Multi-forest M&A integration with disconnected forests | **Cloud Sync per forest** | **PHS** | Best fit for disconnected forests and brownfield coexistence |
| Legacy multi-forest with complex writeback or custom join rules | **Entra Connect Sync** | **PHS** or PTA | Connect still fits advanced legacy join or writeback requirements |

## Architecture Patterns

### 1. Cloud Sync Baseline Pattern (default for new hybrid deployments)

| Element | Guidance |
|---------|----------|
| Use when | New hybrid rollout, brownfield tenant modernization, or disconnected-forest M&A |
| Topology | Deploy at least one Cloud Sync agent per forest; prefer multiple active agents for resilience |
| Authentication | PHS by default; add Seamless SSO where legacy domain-joined experience still matters |
| Security | Harden agent hosts as Tier 0 or control-plane assets; outbound-only connectivity is the preferred path |
| Operations | Start with OU or pilot-group scoping, validate hard match, then expand deliberately |

**Azure CLI preflight for Cloud Sync rollout**

```bash
# Create a pilot security group used by Cloud Sync scoping filters
az ad group create \
  --display-name "grp-hybrid-sync-pilot" \
  --mail-nickname "grp-hybrid-sync-pilot"

# Review directory synchronization feature flags before pilot cutover
az rest \
  --method GET \
  --url "https://graph.microsoft.com/v1.0/directory/onPremisesSynchronization"

# Capture the pilot group ID for runbooks and staged rollout documentation
az ad group show \
  --group "grp-hybrid-sync-pilot" \
  --query "{id:id,displayName:displayName}" \
  -o json
```

### 2. ADFS-to-Cloud Authentication Migration Pattern (staged rollout)

| Element | Guidance |
|---------|----------|
| Use when | AD FS exists only because it was the historical default, not because it still provides a required control |
| Target state | Managed authentication with PHS as baseline; PTA only when on-prem validation is truly required |
| Coexistence model | Keep federation in place for rollback while pilot users move through staged rollout |
| User experience | Pair cloud auth with Seamless SSO or PRT-backed SSO so the cutover does not feel like a downgrade |
| Exit condition | Convert federated domains to managed only after pilot cohorts, helpdesk, and app owners sign off |

### 3. Multi-Forest Cloud Sync Pattern (one agent per forest)

| Element | Guidance |
|---------|----------|
| Use when | Acquired subsidiaries, disconnected forests, or hybrid estates that cannot consolidate directory infrastructure first |
| Topology | Install Cloud Sync in each forest that must contribute objects to the tenant |
| Identity join model | Ensure UPN and alias hygiene before pilot; Cloud Sync does not magically reconcile dirty source data |
| Source anchor | Prefer `ms-DS-ConsistencyGuid` when cross-forest movement or future merges are expected |
| Governance watchpoint | An object must be in scope of only one sync tool at a time |

### 4. High-Availability Sync Server Pattern (Entra Connect Sync staging mode)

| Element | Guidance |
|---------|----------|
| Use when | Entra Connect Sync must remain because Cloud Sync cannot yet replace a required capability |
| Topology | One active Connect Sync server plus one staging-mode server in a separate failure domain |
| Staging behavior | The staging server imports and synchronizes, but does not export changes while it remains passive |
| Failover concern | Password sync and password writeback do not operate from the staging server until it is promoted |
| Recovery rule | Promote only after validating current configuration, export set, and post-promotion health |

### 5. Source Anchor Migration Pattern (`objectGUID` → `ms-DS-ConsistencyGuid`)

| Element | Guidance |
|---------|----------|
| Use when | Users may move across forests, an M&A program will merge directories, or rebuild/DR must preserve hard match |
| Safe timing | Decide and normalize before objects are first exported to Entra wherever possible |
| Benefit | Preserves identity continuity through move, rebuild, and staged cutover |
| Risk | Source anchor regret is expensive because immutable ID cannot be changed casually after sync takes ownership |
| Governance rule | Never treat source anchor as a cleanup task after production cutover |

### 6. Filter Scoping Pattern (OU-based + group-based)

| Filter type | Best use | Guidance |
|-------------|----------|----------|
| OU scope | Durable production boundary | Best default for predictable rollout and operational ownership |
| Security-group scope | Pilot only | Useful for tight early cohorts, but avoid nested-group assumptions and long-term dependence |
| Attribute-based filtering | Advanced exception handling | Use only when OU or group boundaries cannot represent the migration wave clearly |
| User exclusions | Break-glass and service accounts | Keep emergency accounts, legacy service identities, and risky admin accounts out of pilot turbulence |

## Pre-Migration Discovery Checklist

| Discovery area | What to inventory before cutover | Why it matters |
|----------------|----------------------------------|----------------|
| Forest and domain topology | Forest count, trusts, domain suffixes, domain controllers, and writable DC reachability | Determines Cloud Sync vs. Connect Sync viability |
| Authentication dependencies | ADFS farms, relying parties, third-party MFA hooks, smart-card requirements, and custom claim rules | Identifies what still blocks managed authentication |
| Identity hygiene | Duplicate UPNs, duplicate proxy addresses, stale disabled users, guest overlap, and admin account sprawl | Dirty data causes hard-match and sign-in failures |
| Source anchor state | `objectGUID` vs. `ms-DS-ConsistencyGuid`, hard-match candidates, and cross-forest move history | Prevents immutable ID failures during migration |
| Sync scope | Which OUs, groups, attributes, and service accounts are actually required in the cloud | Avoids syncing more than needed |
| Writeback and join dependencies | Password writeback, device sync, hybrid join, and application-specific writeback requirements | These often force continued Connect Sync use |
| Security posture | Emergency access accounts, Tier 0 admin paths, Conditional Access readiness, and privileged break-glass ownership | Brownfield cutovers fail when the control plane is not protected |
| Operational readiness | Helpdesk scripts, monitoring access, rollback commands, and owner sign-off by app team | Makes the cutover survivable, not just technically correct |

## Brownfield Scenario

**Cross-skill sequencing:** This is the entry point for a hybrid identity retrofit — no Wave 1 skill must run before it. Once sync stabilizes and federated domains are converted to managed authentication, hand off privileged-access governance to `entra-identity-governance`, then layer CA via `entra-conditional-access`, then close out workload secrets via `workload-identity-federation`.

**Scenario S4 (Brownfield M&A): "ADFS-to-Entra cutover for an acquired 3,000-person subsidiary with 47 Azure subscriptions post-M&A."**

This is the canonical retrofit use case for this skill: the acquired subsidiary already runs AD FS, has its own AD forest footprint, and must be integrated into the landing zone without breaking user sign-in, privileged admin flows, or subscription governance.

### Eight-step migration playbook with rollback gate at every step

| Step | Action | Exit criteria | Rollback gate |
|------|--------|---------------|---------------|
| 1 | **Stabilize the control plane.** Create cloud-only emergency access accounts, document subsidiary domain ownership, export federation settings, and identify the privileged admins who touch the 47 subscriptions. | Break-glass accounts tested, federation settings exported, identity owners named. | If control-plane access is not independently recoverable, stop before any sync or auth change. |
| 2 | **Map every dependency.** Inventory forests, UPN suffixes, AD FS relying parties, third-party MFA hooks, app-specific claim rules, and service accounts. | Every sign-in path is classified as cloud-ready, exception, or blocker. | If any business-critical relying party is still undocumented, do not pilot. Stay federated and close the gap first. |
| 3 | **Normalize identity data and source anchor.** Resolve duplicate UPNs and proxy addresses, decide `ms-DS-ConsistencyGuid` strategy, and pre-stage hard-match candidates. | Pilot cohort objects are clean and anchor strategy is approved. | If hard-match confidence is weak or duplicates remain unresolved, pause and remediate before enabling sync. |
| 4 | **Build coexistence safely.** Deploy Cloud Sync per forest unless a retained Connect Sync dependency forces staging-mode Connect. Enable PHS, preserve AD FS as the live fallback, and keep emergency accounts outside pilot scope. | Sync jobs are healthy, pilot scope is isolated, and no object is in scope of two sync tools. | If any pilot object is double-scoped or sync health is unstable, disable the new scope and keep AD FS authoritative. |
| 5 | **Run a contained pilot.** Move platform admins, helpdesk, and business champions through staged rollout using PHS first; add PTA only if a documented control requires it. Validate mail, M365, line-of-business apps, and admin portals. | Pilot sign-ins succeed, helpdesk can triage failures, and user experience is acceptable. | Remove the pilot group from staged rollout and return those users to federation if sign-in reliability drops or app claims break. |
| 6 | **Expand by app and business wave.** Migrate low-risk business units first, then sensitive apps, then cross-tenant admins. Keep a dependency register for every subscription owner and workload operator. | Each cohort closes with sign-in success, no unresolved auth regression, and owner sign-off. | Freeze the next cohort if failure patterns trend up, and return the affected wave to the previous auth path before continuing. |
| 7 | **Convert domains to managed authentication.** Only after stable cohorts, convert federated domains, keep federation recovery scripts ready, and watch sign-in logs hour by hour. | Managed authentication is stable, app exceptions are closed, and monitoring shows no widening failure pattern. | Re-federate the domain from the saved federation configuration if browser sign-ins, admin portals, or privileged paths regress. |
| 8 | **Decommission deliberately.** Keep AD FS in a reversible state through the observation window, then remove trusts, retire legacy agents, and hand ongoing monitoring to governance and Sentinel. | No material auth regressions remain, runbooks are updated, and ownership is transferred. | Do not destroy rollback evidence early. Keep exported settings and a documented federation recovery path until the estate is demonstrably stable. |

### Brownfield watchpoints for this scenario

- Keep break-glass accounts cloud-only and outside the sync blast radius.
- Treat duplicate UPN or proxy-address conflicts and hidden claim dependencies as cutover blockers.

## Pilot-to-Production Rollout

| Cohort | Who belongs here | What success looks like | Promotion rule |
|--------|------------------|-------------------------|----------------|
| Cohort 0 | Identity engineers, platform admins, helpdesk leads | Sync health is stable and rollback steps are proven | Advance only after helpdesk can explain the new sign-in path |
| Cohort 1 | Low-risk office users and business champions | Daily sign-in works, browser SSO is acceptable, no silent lockouts | Advance only after user comms and support scripts are validated |
| Cohort 2 | Departmental app users with common SaaS dependencies | Line-of-business access works under managed auth | Advance only after app owners confirm no missing claim dependency |
| Cohort 3 | Sensitive admins, finance, and regulated users | Stronger controls do not break privileged or compliance workflows | Advance only after audit and security teams sign off |
| Cohort 4 | Remaining long-tail population and service-adjacent users | Residual exceptions are documented and controlled | Finish only after the exception register is empty or explicitly approved |

## Diagnostic & Monitoring

| Signal | Where to monitor | What to look for |
|--------|------------------|------------------|
| Sync health | Cloud Sync portal, `AADCloudSyncTools`, or Microsoft Entra Connect Health | Agent offline, export errors, scope mismatch, duplicate object handling |
| Sign-in health | Entra sign-in logs and Log Analytics `SigninLogs` | Unexpected rise in failures, auth path drift, pilot users still hitting federation |
| Password writeback | Entra Connect Health, provisioning logs, audit logs, and agent event logs | Reset failures, long lag, or writeback not active where users expect it |
| Rollback readiness | Exported federation settings and sync configuration backups | Ability to reverse domain conversion or promote staging server without guesswork |

### KQL: authentication path drift after staged rollout

```kql
SigninLogs
| where TimeGenerated > ago(24h)
| extend authPath = case(tostring(AuthenticationProcessingDetails) has "federat", "Federated", tostring(AuthenticationMethodsUsed) has "PTA" or tostring(AuthenticationProcessingDetails) has "Pass-through Authentication", "PTA", tostring(AuthenticationMethodsUsed) has "PHS" or tostring(AuthenticationProcessingDetails) has "Password Hash", "PHS", "Other")
| summarize successes = countif(ResultType == 0), failures = countif(ResultType != 0) by authPath, bin(TimeGenerated, 1h)
| order by TimeGenerated desc
```

### KQL: pilot users still falling back to federation or failing sign-in

```kql
let PilotUsers = dynamic(["pilot1@contoso.com", "pilot2@contoso.com"]);
SigninLogs
| where TimeGenerated > ago(24h) and UserPrincipalName in (PilotUsers)
| where ResultType != 0 or tostring(AuthenticationProcessingDetails) has "federat"
| project TimeGenerated, UserPrincipalName, AppDisplayName, ResultType, ResultDescription, AuthenticationMethodsUsed, AuthenticationProcessingDetails, CorrelationId
| order by TimeGenerated desc
```

### KQL: password reset and writeback failures

```kql
AuditLogs
| where TimeGenerated > ago(24h)
| where Category =~ "Self-service Password Management"
| where Result =~ "failure"
| project TimeGenerated, ActivityDisplayName, ResultReason, InitiatedBy, TargetResources, CorrelationId
| order by TimeGenerated desc
```

## Anti-Patterns

| Anti-pattern | Why it fails | Better pattern |
|--------------|--------------|----------------|
| Big-bang ADFS cutover | Turns identity into a single irreversible event | Use staged rollout and app-wave expansion |
| Leaving staged rollout in place indefinitely | Creates an ambiguous steady state with hidden drift | Finish pilot, then convert or retreat |
| Syncing the same object from Cloud Sync and Connect Sync | Causes ownership ambiguity and broken exports | Keep each object in scope of only one sync tool |
| Treating source anchor as an afterthought | Creates hard-match failures and identity duplication later | Decide anchor strategy before production rollout |
| Decommissioning AD FS before claim dependencies are retired | Hidden app dependencies surface only after business impact | Keep federation rollback evidence until the observation window closes |
| Keeping federation without an explicit exception record | Normalizes legacy risk and prevents closure | Document the exact blocking feature and review it like technical debt |

## References

| Topic | URL |
|-------|-----|
| Cloud Sync overview | https://learn.microsoft.com/en-us/entra/identity/hybrid/cloud-sync/what-is-cloud-sync |
| Cloud Sync configuration | https://learn.microsoft.com/en-us/entra/identity/hybrid/cloud-sync/how-to-configure |
| Cloud Sync topologies | https://learn.microsoft.com/en-us/entra/identity/hybrid/cloud-sync/plan-cloud-sync-topologies |
| Cloud Sync pilot migration | https://learn.microsoft.com/en-us/entra/identity/hybrid/cloud-sync/tutorial-pilot-aadc-aadccp |
| Choose auth method | https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/choose-ad-authn |
| Federation to cloud auth migration | https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/migrate-from-federation-to-cloud-authentication |
| Staged rollout | https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-staged-rollout |
| PTA | https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-pta |
| PHS | https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-password-hash-synchronization |
| Seamless SSO | https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-sso |
| Source anchor design concepts | https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/plan-connect-design-concepts |
| Staging mode and DR | https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-sync-staging-server |
| Connect Health operations | https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-health-operations |
| SigninLogs reference | https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs |
