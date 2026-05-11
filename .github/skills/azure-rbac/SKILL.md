---
name: azure-rbac
description: "Role-Based Access Control patterns, PIM configuration, and identity governance for Azure Landing Zones. USE FOR: RBAC role assignments, management group access strategy, least-privilege design. DO NOT USE FOR: compliance framework mapping (use azure-compliance)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: azure-identity
---

# Azure RBAC Skill

Role-Based Access Control patterns for Azure Landing Zones.

## Management Group RBAC Strategy

| Scope | Role | Principal | Purpose |
|-------|------|-----------|---------|
| Tenant Root | Owner | Break-glass accounts only | Emergency access |
| `mg-platform` | Contributor | Platform Team | Manage platform resources |
| `mg-landingzones` | Reader | Security Team | Audit access |
| `mg-landingzones` | Network Contributor | Network Team | Manage networking |
| Subscription | Owner | Subscription Owner (PIM) | Manage subscription |
| Resource Group | Contributor | App Team (PIM) | Manage workload resources |

## Least Privilege Patterns

### Platform Team
- `Contributor` at `mg-platform` (with PIM JIT activation)
- `Reader` at tenant root group
- `User Access Administrator` only via PIM with approval

### Application Teams
- `Contributor` on their subscription/resource group only
- No access to platform subscriptions
- `Key Vault Secrets User` for secret access (not `Key Vault Administrator`)

### Security Team
- `Security Reader` at tenant root
- `Security Admin` at `mg-platform` (PIM-activated)
- `Microsoft Sentinel Contributor` on Sentinel workspace

## PIM (Privileged Identity Management) Configuration

| Setting | Value |
|---------|-------|
| Maximum activation duration | 8 hours |
| Require justification | Yes |
| Require MFA | Yes |
| Require approval for | Owner, User Access Administrator |
| Approvers | Security Team lead + Platform Team lead |

## Conditional Access Policies

| Policy | Condition | Control |
|--------|-----------|---------|
| Require MFA for Azure Management | Cloud app = Azure Management | MFA required |
| Block legacy authentication | Client app = Other clients | Block |
| Require compliant device | All cloud apps | Require compliant/hybrid-joined device |
| Named locations | Trusted IPs | Allow without MFA |

## Built-in Roles for ALZ

| Role | Scope | Use Case |
|------|-------|----------|
| `Reader` | Management group | Audit/visibility |
| `Contributor` | Subscription | Resource management |
| `Network Contributor` | Resource group | Network management |
| `Key Vault Secrets User` | Key Vault | Secret consumption |
| `Monitoring Contributor` | Subscription | Monitoring setup |
| `Cost Management Reader` | Subscription | Cost visibility |
| `Policy Contributor` | Management group | Policy management |
| `Blueprint Contributor` | Management group | Blueprint management |

## Managed Identity Strategy

Prefer managed identity over service principals:

1. **System-assigned** — For single-purpose resources (VMs, App Services)
2. **User-assigned** — For shared identity across multiple resources
3. **Federated credentials** — For GitHub Actions OIDC (no secrets stored)

Never create service principal secrets for automation. Use OIDC federation or managed identity.

## Microsoft Learn References

> Fetch full content using `mcp_microsoftdocs:microsoft_docs_fetch` with query string `from=learn-agent-skill`, or `fetch_webpage` with `from=learn-agent-skill&accept=text/markdown`.

### Troubleshooting

| Topic | URL |
|-------|-----|
| Audit Azure RBAC changes using Activity Log | https://learn.microsoft.com/en-us/azure/role-based-access-control/change-history-report |
| Resolve common issues with Azure RBAC conditions | https://learn.microsoft.com/en-us/azure/role-based-access-control/conditions-faq |
| Troubleshoot Azure RBAC role assignment conditions | https://learn.microsoft.com/en-us/azure/role-based-access-control/conditions-troubleshoot |
| Resolve Azure RBAC role and custom role limit issues | https://learn.microsoft.com/en-us/azure/role-based-access-control/troubleshoot-limits |
| Diagnose and resolve common Azure RBAC issues | https://learn.microsoft.com/en-us/azure/role-based-access-control/troubleshooting |

### Best Practices

| Topic | URL |
|-------|-----|
| Apply security-focused best practices for Azure RBAC | https://learn.microsoft.com/en-us/azure/role-based-access-control/best-practices |
| Example patterns for delegating RBAC with ABAC conditions | https://learn.microsoft.com/en-us/azure/role-based-access-control/delegate-role-assignments-examples |
| Choose appropriate Azure RBAC scopes for access | https://learn.microsoft.com/en-us/azure/role-based-access-control/scope-overview |

### Decision Making

| Topic | URL |
|-------|-----|
| Scale Azure RBAC assignments using ABAC and attributes | https://learn.microsoft.com/en-us/azure/role-based-access-control/conditions-custom-security-attributes-example |
| Transfer Azure subscriptions between Entra directories | https://learn.microsoft.com/en-us/azure/role-based-access-control/transfer-subscription |

### Custom Roles

| Topic | URL |
|-------|-----|
| Understand and configure Azure RBAC custom roles | https://learn.microsoft.com/en-us/azure/role-based-access-control/custom-roles |
| Create Azure custom roles in the portal | https://learn.microsoft.com/en-us/azure/role-based-access-control/custom-roles-portal |

### Security — Built-in Roles Reference

| Topic | URL |
|-------|-----|
| Reference all Azure RBAC built-in roles | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles |
| Networking roles | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/networking |
| Security roles | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/security |
| Storage roles | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |
| Identity roles | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/identity |
| Management and governance roles | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/management-and-governance |
| Privileged roles | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/privileged |

### Configuration

| Topic | URL |
|-------|-----|
| Azure ABAC conditions format and syntax | https://learn.microsoft.com/en-us/azure/role-based-access-control/conditions-format |
| ABAC conditions for Azure Blob Storage | https://learn.microsoft.com/en-us/azure/role-based-access-control/conditions-azure-blob-storage |
| Manage RBAC conditions via CLI | https://learn.microsoft.com/en-us/azure/role-based-access-control/conditions-role-assignments-cli |

### Integrations & Coding Patterns

| Topic | URL |
|-------|-----|
| Assign roles using Azure CLI | https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-cli |
| Assign roles using PowerShell | https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-powershell |
| Assign roles using ARM/Bicep templates | https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-template |
| Assign roles using REST API | https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-rest |
| List role assignments using Azure CLI | https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-list-cli |
