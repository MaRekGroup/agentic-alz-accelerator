<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Profile Management Skill (Digest)

Landing Zone profile configuration with 3-tier YAML inheritance.

## 3-Tier Inheritance Model

```
base-platform.yaml          ← Shared defaults
    ↓ inherits
platform-{name}.yaml        ← LZ-specific configuration
    ↓ overrides
overrides/{env}/{name}.yaml  ← Environment-specific overrides
```

`ProfileLoader` in `src/config/profile_loader.py` merges layers via deep dictionary merge — child values override at the leaf level.

## Available Profiles

### platform-management

| Setting | Dev | Prod |
|---------|-----|------|
| Log retention | 30 days | 365 days |
| Sentinel | Disabled | Enabled |
| Backup | Disabled | Enabled |
| Budget | $1,500/month | $5,000+/month |

### platform-connectivity

| Setting | Dev | Prod |
|---------|-----|------|
| Topology | Hub-spoke (Basic) | Hub-spoke (Premium) |
| Firewall SKU | Standard | Premium (IDPS) |
| Bastion | Disabled | Enabled |
| Gateways | Disabled | ExpressRoute + VPN |
| Budget | $2,000/month | $10,000+/month |

### platform-identity

| Setting | Dev | Prod |
|---------|-----|------|
| Agent role | Reader | Custom "ALZ Platform Operator" |
| PIM | Disabled | Enabled |
| MFA | Not required | Required |
| Budget | $500/month | $2,000/month |

### platform-security

| Setting | Dev | Prod |
|---------|-----|------|
| Sentinel workspace | Shared with management | Dedicated SOC workspace |
| Defender plans | Free tier | All plans enabled |
| SOAR playbooks | Disabled | All 4 enabled |
| Budget | $1,000/month | $5,000+/month |

## Key Configuration Fields

| Field | Description |
|-------|-------------|
| `location` | Primary Azure region |
| `resource_group_name` | Resource group naming pattern |
| `tags` | Default tags (Environment, ManagedBy, etc.) |
| `budget.amount` | Monthly budget in USD |
| `budget.alert_emails` | Notification recipients |
| `networking.*` | Network topology settings |
| `security.*` | Security configuration |
| `monitoring.*` | Logging and monitoring settings |

## File Locations

Profiles live in `src/config/profiles/` with `base-platform.yaml` (Tier 1), `platform-{name}.yaml` (Tier 2), and `overrides/{dev,prod}/platform-{name}.yaml` (Tier 3).

> _See SKILL.md for full directory tree and usage examples._
