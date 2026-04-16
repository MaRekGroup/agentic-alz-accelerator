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
