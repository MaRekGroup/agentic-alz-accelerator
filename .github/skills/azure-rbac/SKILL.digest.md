<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure RBAC Skill (Digest)

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

- **Platform Team:** Contributor at mg-platform (PIM JIT), Reader at tenant root
- **App Teams:** Contributor on their sub/RG only, no platform access, Key Vault Secrets User (not Admin)
- **Security Team:** Security Reader at tenant root, Security Admin at mg-platform (PIM), Sentinel Contributor

## PIM Configuration

| Setting | Value |
|---------|-------|
| Max activation duration | 8 hours |
| Require justification | Yes |
| Require MFA | Yes |
| Require approval for | Owner, User Access Administrator |

## Conditional Access Policies

| Policy | Control |
|--------|---------|
| Azure Management | MFA required |
| Legacy authentication | Block |
| All cloud apps | Require compliant/hybrid-joined device |
| Trusted IPs | Allow without MFA |

## Built-in Roles for ALZ

| Role | Scope | Use Case |
|------|-------|----------|
| Reader | Management group | Audit/visibility |
| Contributor | Subscription | Resource management |
| Network Contributor | Resource group | Network management |
| Key Vault Secrets User | Key Vault | Secret consumption |
| Monitoring Contributor | Subscription | Monitoring setup |
| Cost Management Reader | Subscription | Cost visibility |
| Policy Contributor | Management group | Policy management |

## Managed Identity Strategy

1. **System-assigned** — single-purpose resources
2. **User-assigned** — shared identity across resources
3. **Federated credentials** — GitHub Actions OIDC (no secrets)
4. Never create service principal secrets — use OIDC or managed identity

> _See SKILL.md for full details._
