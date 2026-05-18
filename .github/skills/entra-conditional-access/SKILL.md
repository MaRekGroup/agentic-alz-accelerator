---
name: entra-conditional-access
description: "Conditional Access design patterns for Microsoft Entra in Azure Landing Zones. USE FOR: CA baseline policies, named locations, authentication strength, cross-tenant access trust, continuous access evaluation, staged rollout, break-glass exclusions, and CA diagnostics. DO NOT USE FOR: PIM, access reviews, or entitlement management (use entra-identity-governance); hybrid identity sync or ADFS migration (use entra-connect-hybrid-identity); workload identity or managed identity federation (use workload-identity-federation); app registrations or service principals (use entra-app-registration)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: azure-identity
---

# Entra Conditional Access Skill

## Overview

Architectural guidance for Microsoft Entra Conditional Access in Azure Landing Zones. This skill covers policy design patterns for blocking legacy authentication, protecting privileged administration, requiring device trust, defining named locations, applying authentication strengths such as passwordless and phishing-resistant MFA, trusting external tenants deliberately, enabling Continuous Access Evaluation (CAE), and rolling policies out safely.

This skill is an additive enhancement of the baseline Conditional Access references already present in `azure-rbac`. It deepens that baseline into governance and implementation patterns that the Warden agent can enforce in governance constraints and the Forge agent can translate into repeatable automation. It reinforces the ALZ security baseline by protecting the identities that configure and operate rules 1-6; it does **not** replace resource-plane controls such as TLS, HTTPS-only, or public network disablement.

## CAF Design Area Mapping

| CAF design area | Relevance | Decisions this skill informs |
|-----------------|-----------|------------------------------|
| Identity & Access | Primary | Tenant-wide CA baseline, admin protection, authentication strengths, B2B trust, break-glass exclusions |
| Security | Secondary | Zero Trust device and location controls, phishing-resistant MFA, country/region blocking |
| Governance | Secondary | Exception model, staged rollout, policy naming, brownfield retrofit sequencing |
| Management | Secondary | Sign-in/audit log routing, workbook review, Sentinel monitoring, rollback evidence |

## WAF Pillar Mapping

| WAF pillar | Contribution from this skill | Example governance outcome |
|------------|------------------------------|-----------------------------|
| Security | Reduces credential replay, legacy auth exposure, weak admin sign-ins, and unmanaged-device access | Admin portals require strong auth and legacy auth is blocked |
| Reliability | Prevents tenant lockout through break-glass design and safer staged rollout; CAE shortens exposure windows after compromise | Emergency access remains available while stale sessions are revoked faster |
| Operational Excellence | Standardizes policy sets, report-only promotion, log review, and rollback criteria | Warden can hand explicit CA constraints to Forge and Sentinel |
| Performance Efficiency | Uses targeted auth strength and CAE instead of blunt token lifetime reductions or blanket prompts | Strong controls land on high-value flows without excessive friction everywhere |
| Cost Optimization | Lowers incident and recovery cost, reuses Azure Monitor/Sentinel data, and avoids redundant guest MFA when partner trust is verified | Approved partner tenants can satisfy MFA/device claims once, not repeatedly |

## Architecture Patterns

### Baseline CA Policy Set

| Policy | Target | Key conditions | Grant/session control | Design note |
|--------|--------|----------------|-----------------------|-------------|
| Block legacy authentication | All workforce users | Client app types = `exchangeActiveSync`, `other` | Block access | Start in report-only; this is usually the lowest-risk first enforcement win |
| Require MFA for security info registration | All users registering auth factors | User action = register security info; exclude trusted bootstrap paths only when justified | MFA from untrusted networks | Pair with Temporary Access Pass for first-run recovery |
| Require MFA or stronger for admin portals | Admin cohort only | Microsoft Admin Portals and Azure management access | Prefer auth strength over generic MFA | Protects the control plane that enforces the ALZ baseline |
| Require compliant or hybrid-joined device for admin tasks | Admin cohort only | Admin portals, Azure management, or sensitive enterprise apps | Require compliant device or hybrid joined device | Do not rely on a trusted IP bypass for privileged access |
| Require device trust for core workforce access | Workforce cohorts | M365, Azure portal, high-value SaaS | Require compliant device, hybrid joined device, or approved app pattern by platform | Roll out by cohort; mobile often needs a separate app-protection path |
| Respond to risk signals | Users with high user risk or high sign-in risk | Entra ID Protection risk signals | High user risk = password change + MFA; high sign-in risk = MFA or block | Requires P2 licensing; exclude break-glass accounts |
| Block disallowed countries/regions | All users or guest users | Named locations for denied geographies | Block access | Keep the allow/block list small and evidence-based |

### Admin Protection Pattern

| Element | Recommended pattern |
|---------|---------------------|
| Scope | Target a dedicated privileged group or specific admin roles, not all users |
| Resources | Cover Microsoft Admin Portals, Azure management entry points, and any tenant-critical SaaS admin planes |
| Authentication | Prefer phishing-resistant MFA strength for privileged admins, using methods such as FIDO2 security keys or Windows Hello for Business; accept passwordless MFA only where phishing-resistant methods are not yet ready |
| Device trust | Require compliant or hybrid-joined devices for privileged actions; privileged access workstations are the reference path |
| Named locations | Use locations as an additional risk signal or country block, not as a broad MFA bypass for admins |
| Exclusions | Exclude only documented break-glass accounts; no broad "IT exceptions" group |
| Monitoring | Alert on every admin sign-in that lands in failure, report-only failure, or user-action-required states |

### Zero-Trust Device Compliance Pattern

| Decision point | Guidance |
|----------------|----------|
| Admins | Enforce compliant or hybrid-joined device plus strong auth before wide user rollout |
| Workforce web/mobile | Split browser, desktop, and mobile if readiness differs; mobile often needs approved app or app protection controls first |
| BYOD handling | Decide explicitly: allow with app protection, allow web-only, or block; do not leave unmanaged devices as an accidental default |
| Report-only caveat | Device-compliance report-only policies can still trigger certificate prompts on macOS, iOS, and Android; exclude those platforms until piloted |
| Dependency check | Confirm Intune compliance policies and at least one known-good compliant device before enforcing |
| Brownfield use | In retrofit tenants, inventory current device states before attaching device controls to existing productivity apps |

### Cross-Tenant B2B Pattern

| Decision point | Recommended default | When to relax |
|----------------|---------------------|---------------|
| Inbound collaboration | Allow only approved partner tenants via explicit cross-tenant settings | Expand only after business owner and security owner approve the tenant |
| Inbound trust | Trust partner MFA, compliant device, and hybrid-joined claims only for vetted tenants | Trust after validating the partner's MFA/device posture and contractual expectations |
| Outbound access | Limit outbound access to approved partner tenants and apps | Expand when there is a durable business collaboration path |
| External collaboration controls | Pair cross-tenant settings with guest invite/domain restrictions | Relax only for managed partner onboarding processes |
| Guest CA policies | Apply dedicated guest CA policies; do not assume workforce policies fit guests cleanly | Reuse workforce controls only when sign-in patterns are demonstrably similar |
| Monitoring | Log guest sign-ins, tenant-to-tenant trust usage, and policy drift in cross-tenant settings | Never disable monitoring for partner exceptions |

### CAE Enablement Pattern

| Element | Guidance |
|---------|----------|
| Goal | Use CAE to shorten the gap between account state changes and effective enforcement |
| Best fit | Exchange Online, SharePoint Online, Teams, and Microsoft Graph-supported scenarios |
| High-value events | User disablement, password reset, refresh token revocation, high user risk, and network location change |
| Governance stance | Prefer CAE over aggressively shortening token lifetimes; short lifetimes hurt reliability without solving the core problem |
| Rollout | Validate that critical apps and clients in scope understand CAE before assuming near-real-time enforcement |
| Limitation | "Near real time" can still mean several minutes for some events; location-based enforcement is the fastest path |
| Ops tie-in | Keep explicit revoke-session runbooks; CAE improves response time but does not eliminate incident handling |

### Programmatic Policy Examples

Conditional Access is a Microsoft Entra policy surface managed through Microsoft Graph. In Bicep, treat CA as a Graph-driven control-plane operation and automate it with a managed-identity-backed deployment script or pipeline step. In Terraform, use the AzureAD provider resource and keep new policies in report-only until sign-in evidence is clean.

#### Bicep example — create an admin MFA policy through Microsoft Graph

```bicep
param managedIdentityResourceId string
param breakGlassObjectId string
param adminGroupObjectId string

resource caAdminPolicy 'Microsoft.Resources/deploymentScripts@2023-08-01' = {
  name: 'ds-ca-admin-mfa'
  location: resourceGroup().location
  kind: 'AzureCLI'

  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityResourceId}': {}
    }
  }

  properties: {
    azCliVersion: '2.64.0'
    retentionInterval: 'P1D'
    cleanupPreference: 'OnSuccess'
    scriptContent: '''
      cat > ca-policy.json <<'JSON'
      {
        "displayName": "CA100-Admin-RequireMFA",
        "state": "enabledForReportingButNotEnforced",
        "conditions": {
          "users": {
            "includeGroups": ["${adminGroupObjectId}"],
            "excludeUsers": ["${breakGlassObjectId}"]
          },
          "applications": {
            "includeApplications": ["MicrosoftAdminPortals"]
          }
        },
        "grantControls": {
          "operator": "OR",
          "builtInControls": ["mfa"]
        }
      }
      JSON

      az rest \
        --method POST \
        --url "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies" \
        --headers "Content-Type=application/json" \
        --body @ca-policy.json
    '''
  }
}
```

> Use a managed identity with Microsoft Graph permissions such as `Policy.ReadWrite.ConditionalAccess`. Replace generic MFA with an authentication strength when the tenant is ready for passwordless or phishing-resistant enforcement.

#### Terraform example — block legacy authentication in report-only mode

```hcl
resource "azuread_conditional_access_policy" "block_legacy_auth" {
  display_name = "CA010-BlockLegacyAuth"
  state        = "enabledForReportingButNotEnforced"

  conditions {
    applications {
      included_applications = ["All"]
    }

    client_app_types = ["exchangeActiveSync", "other"]

    users {
      included_groups = [azuread_group.workforce_users.id]
      excluded_groups = [azuread_group.breakglass.id]
    }
  }

  grant_controls {
    operator          = "AND"
    built_in_controls = ["block"]
  }
}
```

#### Azure CLI example — same Graph path outside IaC

```bash
az rest \
  --method POST \
  --url "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies" \
  --headers "Content-Type=application/json" \
  --body @ca-policy.json
```

## Staged Rollout Procedure

| Phase | Policy state | What to do | Promote when | Roll back if |
|-------|--------------|------------|--------------|--------------|
| 1. Prepare scope | Disabled or draft JSON | Define admin cohort, workforce cohorts, named locations, and break-glass exclusions; inventory legacy auth and unmanaged devices | Exclusions and pilot groups are approved | Break-glass accounts are missing, unnamed, or untested |
| 2. Pilot in report-only | `enabledForReportingButNotEnforced` | Start with block legacy auth and admin protections before broad workforce device controls | Sign-in logs show expected hits and no critical admin lockouts | Break-glass or production admin sign-ins show report-only failure without an approved mitigation |
| 3. Log analysis | Report-only | Review Conditional Access insights workbook, sign-in logs, and audit logs; fix false positives, missing device compliance, and guest trust gaps | Failure reasons are understood and remediation owners are assigned | Legacy workflows still depend on blocked protocols or unmanaged device access with no compensating design |
| 4. Limited enforcement | Enabled for one ring | Enforce on a narrow cohort, keep later rings in report-only, and watch help-desk volume and admin access | Pilot ring runs clean for a defined observation window | Admin productivity drops, service desk spikes, or partner access breaks unexpectedly |
| 5. Broad enforcement | Enabled | Expand by ring, remove temporary exclusions, and keep rollback artifacts ready | Policies stay stable and exceptions are documented | Anyone proposes permanent broad exclusions instead of root-cause remediation |

## Break-Glass Account Strategy

| Control area | Pattern |
|--------------|---------|
| Account count | Maintain at least two cloud-only emergency access accounts in the `*.onmicrosoft.com` domain |
| CA exclusions | Exclude break-glass accounts from CA policies that could prevent tenant recovery, but exclude nothing else by default |
| Role assignment | Limit to the minimum emergency administrative scope needed for tenant recovery; do not use these accounts for routine work |
| Authentication path | Use a tested emergency sign-in path that does not depend on the same everyday controls you may need to recover from |
| Operational handling | Store credentials or hardware separately, document who can retrieve them, and test the accounts on a defined cadence |
| Monitoring | Alert on every sign-in, password change, role change, or CA policy edit involving break-glass accounts |
| Governance | Document the exclusion in governance constraints and review it whenever policy scope or admin cohorts change |

Break-glass exclusions are a safety valve, not a convenience tier. If a policy requires excluding a broad admin group to work, the policy design is wrong.

## Brownfield Scenario

**Cross-skill sequencing:** Run after `entra-identity-governance` has converted permanent privileged assignments to PIM-eligible — CA policies are most effective when applied to the active-session window, not standing privilege. Once baseline CA is enforced, hand off workload-credential cleanup to `workload-identity-federation`.

### Scenario S3 (Regulated Workloads): Layering CA on an existing Entra tenant without locking out admins or breaking legacy workflows

Use this retrofit playbook when the tenant already has live productivity traffic, partial CA coverage, and unknown dependency on legacy protocols.

| Step | Playbook action | Expected output |
|------|-----------------|-----------------|
| 1 | Export current CA policies, named locations, excluded users/groups, sign-in logs, and audit logs | A known-good baseline and a list of existing exceptions |
| 2 | Identify privileged admins, break-glass accounts, legacy-auth users, unmanaged-device cohorts, and partner tenants | Clear pilot rings and a lockout-prevention plan |
| 3 | Create new baseline policies in report-only mode rather than editing working policies first | Safe comparison between current and target behavior |
| 4 | Remediate dependencies: register stronger auth methods, deploy device compliance, decide partner trust, and isolate legacy protocols | Fewer false positives when moving to enforcement |
| 5 | Enforce by ring: block legacy auth first, then admin protection, then user device controls, then partner tightening | Zero-trust improvement without a tenant-wide outage |

In brownfield tenants, prefer **layering** over **rewriting**. Keep the existing policy set intact until report-only evidence shows the replacement set behaves as intended.

## Diagnostic & Monitoring

| Signal | Source | What to watch | Why it matters |
|--------|--------|---------------|----------------|
| Policy outcome by sign-in | Sign-in logs (`SigninLogs`) | Success, failure, user-action-required, and not-applied outcomes per policy | Tells you whether the policy is doing what you think it is doing |
| Policy and exclusion drift | Audit logs (`AuditLogs`) | Policy create/update/delete, named location changes, exclusion changes | Detects weakening or accidental misconfiguration |
| Legacy auth usage | Sign-in logs | `ClientAppUsed` values such as `Other clients` or `Exchange ActiveSync` | Shows whether blocking legacy auth will break real traffic |
| Break-glass use | Sign-in logs + audit logs | Any sign-in or credential event touching emergency accounts | Emergency access should be rare and always investigated |
| Workbook trend analysis | Conditional Access insights and reporting workbook | Failure trends, report-only results, policy hotspots | Best operator view before moving rings to enforce |

### KQL — Conditional Access outcomes by policy

```kusto
SigninLogs
| where TimeGenerated > ago(7d)
| mv-expand cap = ConditionalAccessPolicies
| extend PolicyName = tostring(cap.displayName),
         PolicyResult = tostring(cap.result)
| summarize SignIns = count(),
            Failures = countif(PolicyResult in ("failure", "reportOnlyFailure")),
            UserActionRequired = countif(PolicyResult == "reportOnlyUserActionRequired")
  by PolicyName
| order by Failures desc, SignIns desc
```

### KQL — Legacy authentication attempts still hitting the tenant

```kusto
SigninLogs
| where TimeGenerated > ago(7d)
| where ClientAppUsed in ("Other clients", "Exchange ActiveSync")
| summarize Attempts = count(),
            CAFailures = countif(ConditionalAccessStatus == "failure")
  by UserPrincipalName, AppDisplayName, ClientAppUsed, IPAddress
| order by Attempts desc
```

### KQL — Break-glass account usage

```kusto
let BreakGlass = dynamic([
  "bg-admin1@contoso.onmicrosoft.com",
  "bg-admin2@contoso.onmicrosoft.com"
]);
SigninLogs
| where TimeGenerated > ago(30d)
| where UserPrincipalName in~ (BreakGlass)
| project TimeGenerated, UserPrincipalName, AppDisplayName, IPAddress,
          ConditionalAccessStatus, ResultType, ResultDescription
| order by TimeGenerated desc
```

### KQL — Conditional Access policy changes

```kusto
AuditLogs
| where TimeGenerated > ago(30d)
| where Category =~ "Policy"
| where OperationName has "Conditional Access"
| extend Actor = coalesce(
    tostring(InitiatedBy.user.userPrincipalName),
    tostring(InitiatedBy.app.displayName)
  )
| project TimeGenerated, Actor, OperationName, Result, TargetResources, AdditionalDetails
| order by TimeGenerated desc
```

## Anti-Patterns

| Anti-pattern | Why it fails | Better pattern |
|--------------|--------------|----------------|
| Turning policies on before report-only review | Causes avoidable lockouts and noisy rollbacks | Use report-only, review evidence, then enforce by ring |
| No break-glass exclusion | A single bad policy can lock out every admin | Maintain narrowly scoped emergency exclusions and test them |
| Using trusted IPs as an admin MFA bypass | Converts network location into an attacker objective | Keep strong auth for admins regardless of location; use location mostly as an added block or exception signal |
| Enforcing device compliance before Intune/device readiness | Creates false failures and help-desk spikes | Prove compliance readiness first and split platforms when needed |
| Trusting every external tenant's MFA or device claims | Extends your trust boundary without validation | Use explicit partner allowlists and per-tenant trust decisions |
| Assuming CAE eliminates revocation or incident runbooks | CAE improves speed, not governance discipline | Keep revoke-session, disable-user, and monitoring runbooks active |

## References

| Topic | URL |
|-------|-----|
| Conditional Access overview | https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview |
| Common Conditional Access templates | https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-policy-common |
| Report-only mode | https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-report-only |
| Authentication strengths | https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths |
| Secure security info registration | https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-all-users-security-info-registration |
| Block legacy authentication | https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-block-legacy-authentication |
| Require device compliance | https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-all-users-device-compliance |
| Admin device compliance and strong auth | https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-alt-admin-device-compliand-hybrid |
| Named locations and network conditions | https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-assignment-network |
| Block by location | https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-block-by-location |
| Cross-tenant access overview | https://learn.microsoft.com/en-us/entra/external-id/cross-tenant-access-overview |
| Continuous Access Evaluation | https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation |
| Emergency access accounts | https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access |
| Sign-in logs | https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins |
| Audit logs | https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-audit-logs |
| Integrate Entra logs with Azure Monitor | https://learn.microsoft.com/en-us/entra/identity/monitoring-health/howto-integrate-activity-logs-with-azure-monitor-logs |
| Conditional Access insights and reporting workbook | https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-insights-reporting |
| Microsoft Graph Conditional Access policy resource | https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesspolicy?view=graph-rest-1.0 |
