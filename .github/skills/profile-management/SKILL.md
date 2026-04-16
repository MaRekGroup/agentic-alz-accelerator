---
name: profile-management
description: "Landing Zone profile configuration system with 3-tier inheritance (base → size → environment). USE FOR: profile selection, parameter inheritance, environment-specific overrides. DO NOT USE FOR: IaC module structure (use iac-common)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: azure-configuration
---

# Profile Management Skill

Domain knowledge for the Landing Zone profile configuration system.

## 3-Tier Inheritance Model

Profiles use a YAML-based inheritance system with 3 tiers:

```
base-platform.yaml          ← Shared defaults for all platform LZs
    ↓ inherits
platform-{name}.yaml        ← LZ-specific configuration
    ↓ overrides
overrides/{env}/{name}.yaml  ← Environment-specific overrides (dev/prod)
```

The `ProfileLoader` class in `src/config/profile_loader.py` merges these layers
using deep dictionary merge — child values override parent values at the leaf level.

## Available Profiles

### platform-management
Central logging, monitoring, and automation.

| Setting | Dev | Prod |
|---------|-----|------|
| Log retention | 30 days | 365 days |
| Sentinel | Disabled | Enabled |
| Backup | Disabled | Enabled |
| Budget | $1,500/month | $5,000+/month |

### platform-connectivity
Hub networking, firewall, and DNS.

| Setting | Dev | Prod |
|---------|-----|------|
| Topology | Hub-spoke (Basic) | Hub-spoke (Premium) |
| Firewall SKU | Standard | Premium (IDPS enabled) |
| Bastion | Disabled | Enabled |
| Gateways | Disabled | ExpressRoute + VPN |
| Budget | $2,000/month | $10,000+/month |

### platform-identity
RBAC, PIM, and conditional access.

| Setting | Dev | Prod |
|---------|-----|------|
| Agent role | Reader | Custom "ALZ Platform Operator" |
| PIM | Disabled | Enabled |
| MFA | Not required | Required |
| Conditional access | Disabled | Enabled |
| Budget | $500/month | $2,000/month |

### platform-security
Sentinel, Defender for Cloud, and SOAR.

| Setting | Dev | Prod |
|---------|-----|------|
| Sentinel workspace | Shared with management | Dedicated SOC workspace |
| Defender plans | Free tier | All plans enabled |
| SOAR playbooks | Disabled | All 4 enabled |
| Retention | 30 days | 365 days |
| Budget | $1,000/month | $5,000+/month |

## File Locations

```
src/config/profiles/
├── base-platform.yaml                    # Tier 1: shared defaults
├── platform-connectivity.yaml            # Tier 2: connectivity-specific
├── platform-identity.yaml                # Tier 2: identity-specific
├── platform-management.yaml              # Tier 2: management-specific
├── platform-security.yaml                # Tier 2: security-specific
└── overrides/
    ├── dev/
    │   ├── platform-connectivity.yaml    # Tier 3: dev overrides
    │   ├── platform-identity.yaml
    │   ├── platform-management.yaml
    │   └── platform-security.yaml
    └── prod/
        ├── platform-connectivity.yaml    # Tier 3: prod overrides
        ├── platform-identity.yaml
        ├── platform-management.yaml
        └── platform-security.yaml
```

## Usage

```python
from src.config.profile_loader import ProfileLoader

loader = ProfileLoader()

# Load a profile with environment override
profile = loader.load_profile("platform-connectivity", environment="prod")

# List available profiles
profiles = loader.list_profiles()
```

## Key Configuration Fields

All profiles share these base fields from `base-platform.yaml`:

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
