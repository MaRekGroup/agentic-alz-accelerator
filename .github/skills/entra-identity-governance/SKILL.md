---
name: entra-identity-governance
description: "Architectural guidance for Microsoft Entra identity governance in Azure Landing Zones. USE FOR: PIM at scale, PIM for Groups, access reviews, entitlement management, lifecycle workflows, separation of duties, time-bound privileged access, and audit design. DO NOT USE FOR: Conditional Access policies (use entra-conditional-access), hybrid identity sync (use entra-connect-hybrid-identity), workload identity federation (use workload-identity-federation), or baseline Azure RBAC role mapping (use azure-rbac)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: azure-identity
---

# Entra Identity Governance Skill

Architectural guidance for Microsoft Entra identity governance in Azure Landing Zones.

## Overview

This skill covers privileged access governance after role design exists: PIM at scale, PIM for Groups, access reviews, entitlement management, lifecycle workflows, separation of duties, time-bound assignments, and audit monitoring.

It deepens `azure-rbac/SKILL.md` lines 44–53 from a five-row PIM baseline into per-role activation matrices, approval policies, review cadence, and monitoring guidance. Keep `azure-rbac/SKILL.md` lines 16–43 for management group scope design and least-privilege role mapping, keep `azure-rbac/SKILL.md` lines 63–84 for built-in role selection, and keep `azure-rbac/SKILL.md` lines 54–61 with `entra-conditional-access` for Conditional Access policy design.

Use `entra-app-registration/SKILL.md` for app registrations, federated credentials, and workload identities. This skill reinforces `AGENTS.md` §"Security Baseline" rule 4 — managed identity preferred — for automation that administers PIM schedules or entitlement workflows.

## CAF Design Area Mapping

| Capability | CAF Design Area | Why it matters in ALZ |
|---|---|---|
| PIM for Azure resource roles | Identity & Access | Replaces standing admin rights with just-in-time access at management group and subscription scope |
| PIM for Groups | Identity & Access | Scales privilege through group-based operations instead of per-user role churn |
| Access reviews | Governance | Forces recurring validation of privileged, guest, and app access |
| Entitlement management | Identity & Access | Standardizes self-service access with approvals, expiration, and catalog ownership |
| Lifecycle workflows | Platform Automation & DevOps | Automates joiner-mover-leaver controls and reduces stale access |
| Separation of duties | Governance | Prevents the same persona from holding conflicting admin paths across the estate |

## WAF Pillar Mapping

| Pillar | Priority | Identity governance contribution |
|---|---|---|
| Security | Primary | Removes permanent privilege, enforces approval, and creates auditable elevation trails |
| Operational Excellence | Primary | Automates JML, reviews, and package workflows so governance scales with tenant growth |
| Reliability | Secondary | Reduces operator error by using standard elevation paths instead of ad hoc break/fix access |
| Cost Optimization | Secondary | Cuts manual review effort and rework caused by uncontrolled privilege sprawl |

## Architecture Patterns

### PIM Activation Workflow Pattern

- Use eligible assignments as the default state for Owner, User Access Administrator, Policy Contributor, and other privileged Azure resource roles.
- Require MFA, justification, ticket/reference, and approval for tier-0 and tier-1 roles before activation.
- Use ARM/Bicep schedule requests for Azure resource roles and Microsoft Graph for directory role governance.
- Allow permanent active assignments only for controlled break-glass identities, with separate monitoring and no daily operations use.

### Group-Based Privileged Access Pattern

- Grant Azure roles to PIM-enabled groups, then manage user eligibility inside the group instead of issuing direct role assignments to individuals.
- Separate requestor groups from approver groups so the same operator cannot self-approve elevation.
- Use this pattern for platform operations teams that need repeatable access across many subscriptions or management groups.

### Quarterly Access Review Pattern

- Review privileged Azure role eligibility, PIM for Groups memberships, guest access, and high-impact enterprise app access on a fixed cadence.
- Route reviews to business owners for app access, to platform/security leads for admin roles, and to sponsors for guest users.
- Configure auto-remove on no response for guests and non-break-glass privileged paths.

### Entitlement Management Access Package Pattern

- Publish access through catalogs and access packages rather than unmanaged security groups.
- Pair each package with a time-bound assignment policy, approval stage, and catalog owner accountability.
- Use packages for integration teams, landing zone support teams, and temporary project squads that cross subscription boundaries.

```bash
# Authenticate with managed identity or OIDC first; do not use client secrets.
ACCESS_PACKAGE_ID="<access-package-id>"

az rest --method post \
  --url "https://graph.microsoft.com/v1.0/identityGovernance/entitlementManagement/assignmentPolicies" \
  --body "{
    \"displayName\": \"alz-platform-operators-30d\",
    \"description\": \"Self-service, approved access package for platform operators\",
    \"accessPackageId\": \"${ACCESS_PACKAGE_ID}\",
    \"allowedTargetScope\": \"allMemberUsers\",
    \"requestApprovalSettings\": {
      \"isApprovalRequired\": true
    },
    \"expiration\": {
      \"duration\": \"P30D\"
    }
  }"
```

### Lifecycle Workflows JML Pattern

- Use lifecycle workflows for joiner-mover-leaver automation tied to HR or other authoritative identity events.
- Trigger access package assignment/removal, group cleanup, Teams/email notifications, and review checkpoints during employment transitions.
- Treat mover events as riskier than joiners: remove old access before granting new access when the job function changes.

### Separation of Duties at MG Scope Pattern

- Split management group governance across distinct personas: platform operations, security governance, and access governance approvers.
- Never allow the same day-to-day identity to combine Owner, User Access Administrator, and policy-exemption approval on the same estate segment.
- Model separation of duties at the management group layer first, then inherit the pattern down to subscriptions and resource groups.

## PIM Configuration Reference Tables

### Activation Duration Recommendations

| Role | Typical ALZ scope | Max activation duration | Default assignment state | Notes |
|---|---|---:|---|---|
| Owner | Subscription / exception-only management group | 4 hours | Eligible | Approval required; no permanent active except break-glass |
| User Access Administrator | Management group / subscription | 1 hour | Eligible | Shortest window; gatekeeper for RBAC changes |
| Contributor | Subscription / resource group | 8 hours | Eligible | Use when operational tasks span a full change window |
| Policy Contributor | Management group | 2 hours | Eligible | Pair with change ticket and peer approval |
| Security Admin / Security Administrator | Management group / security subscription | 4 hours | Eligible | Approval required for production scopes |
| Network Contributor | Connectivity subscription / resource group | 4 hours | Eligible | Use PIM for Groups for network operations teams |
| Key Vault Administrator | Vault / resource group | 2 hours | Eligible | Prefer narrower data-plane roles when possible |
| Reader / Security Reader | Management group | Permanent active acceptable | Active | Non-privileged read access can remain standing |

### Approval Requirements by Role Tier

| Role tier | Roles | Approval | Approver pattern | Extra controls |
|---|---|---|---|---|
| Tier 0 | Owner, User Access Administrator | Required | Security lead + platform lead | MFA, justification, ticket ID, incident/change reference |
| Tier 1 | Policy Contributor, Security Admin, Key Vault Administrator | Required in prod | Service owner or security approver group | MFA, justification, notification to SOC |
| Tier 2 | Contributor, Network Contributor | Risk-based | Team lead or on-call approver for prod; optional for non-prod | MFA, justification |
| Tier 3 | Reader-class roles | Not required | None | Keep outside PIM unless tenant policy mandates reviewable eligibility |

### Notification Matrix

| Event | Notify | Why |
|---|---|---|
| Eligible assignment created or renewed | Identity governance mailbox, security governance owner | Detect privilege growth and renewals before they become routine |
| Activation requested for Tier 0 or Tier 1 role | Approver group, SOC/on-call security channel | Human approval and awareness before elevation |
| Activation approved and started | Requester manager, platform operations lead, audit mailbox | Establish operational awareness and audit trail |
| Activation denied or expired | Requester, approver group, identity governance mailbox | Close the loop and trigger follow-up if work remains |
| Access review overdue or auto-applied | Review owner, security governance owner | Escalate review debt and enforce removal decisions |

## Access Review Cadence

| Access type | Cadence | Reviewer | Default action on no response |
|---|---|---|---|
| Owner, User Access Administrator, Policy Contributor | Quarterly | Platform/security leads | Remove eligible or active access |
| PIM for Groups privileged memberships | Quarterly | Group owner + security approver | Remove membership |
| Guest users with admin or project access | Quarterly | Sponsoring business owner | Remove guest from group/package |
| Access packages for project teams and partner collaboration | Biannual | Catalog owner | Expire assignment |
| Standard internal app access with low privilege | Annual | Application owner | Keep only if explicitly attested |

## Brownfield Scenario

### PIM retrofit on a tenant with 5,000+ existing permanent role assignments and inherited group sprawl from years of M&A

1. Run Step 0 discovery to inventory direct role assignments, privileged groups, inactive guests, and duplicated admin paths across management groups and subscriptions.
2. Classify assignments into keep, convert-to-eligible, collapse-into-group, or remove; protect break-glass identities with separate controls and logging.
3. Build a privileged group model for recurring operations teams, then migrate direct user assignments into PIM for Groups before changing role schedules.
4. Convert permanent high-privilege assignments to eligible schedules in waves: tenant-root and management group first, subscriptions second, resource groups last.
5. Stand up quarterly access reviews and entitlement packages for integration teams so newly acquired users follow the same request and approval workflow.
6. Monitor activation anomalies, expired assignments, and review debt for at least two review cycles before declaring the retrofit complete.

## Diagnostic & Monitoring

Collect Microsoft Entra audit logs, sign-in logs, and PIM activation data into Log Analytics or Sentinel. Treat activation failures, repeated after-hours elevation, denied activations, and review debt as governance drift signals.

| Signal | Source | Use |
|---|---|---|
| Activation / approval / denial events | `AuditLogs` | Detect unusual elevation behavior |
| Role eligibility schedule changes | Azure Activity Log + `AuditLogs` | Detect admin-assigned privilege growth |
| Access review decisions | `AuditLogs` | Prove recertification and spot non-response auto-removals |
| Access package policy changes | `AuditLogs` / Microsoft Graph reports | Detect entitlement drift |

### KQL: Repeated PIM activations in a short window

```kql
AuditLogs
| where ActivityDisplayName in ("Activate eligible role assignment", "Activate role assignment", "Activated PIM role")
| summarize ActivationCount=count() by InitiatedBy=tostring(InitiatedBy.user.userPrincipalName), bin(TimeGenerated, 1h)
| where ActivationCount > 3
| order by TimeGenerated desc
```

### KQL: After-hours or rare privileged role activation

```kql
AuditLogs
| where ActivityDisplayName in ("Activate eligible role assignment", "Activate role assignment", "Activated PIM role")
| extend InitiatedBy=tostring(InitiatedBy.user.userPrincipalName)
| extend RoleName=tostring(TargetResources[0].displayName)
| extend HourOfDay=datetime_part("Hour", TimeGenerated)
| summarize ActivationCount=count(), LastSeen=max(TimeGenerated) by InitiatedBy, RoleName, HourOfDay
| where HourOfDay < 6 or HourOfDay > 20 or ActivationCount < 3
| order by LastSeen desc
```

## Anti-Patterns

- Permanent Owner or User Access Administrator for day-to-day operations.
- Direct per-user eligible assignments at management group scale when PIM for Groups would centralize control.
- No approval on Owner, User Access Administrator, or production Policy Contributor activations.
- Access reviews that route to the requester, never auto-apply removals, or stay unresolved for multiple cycles.
- Access packages that grant overly broad admin rights or never expire.
- Lifecycle workflows that are disconnected from mover and leaver events, leaving stale access behind.

## References

| Topic | URL |
|---|---|
| Microsoft Entra ID Governance hub | https://learn.microsoft.com/en-us/entra/id-governance/ |
| Configure Microsoft Entra PIM | https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure |
| PIM for Groups overview | https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-for-groups-overview |
| Access reviews overview | https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview |
| Plan an access reviews deployment | https://learn.microsoft.com/en-us/entra/id-governance/deploy-access-reviews |
| Entitlement management overview | https://learn.microsoft.com/en-us/entra/id-governance/entitlement-management-overview |
| Microsoft Graph tutorial for access packages | https://learn.microsoft.com/en-us/graph/tutorial-access-package-api |
| Lifecycle workflows overview | https://learn.microsoft.com/en-us/entra/id-governance/what-are-lifecycle-workflows |
| Plan a lifecycle workflows deployment | https://learn.microsoft.com/en-us/entra/id-governance/lifecycle-workflows-deployment |
| Create entitlement assignment policies via Microsoft Graph | https://learn.microsoft.com/en-us/graph/api/entitlementmanagement-post-assignmentpolicies?view=graph-rest-1.0 |
