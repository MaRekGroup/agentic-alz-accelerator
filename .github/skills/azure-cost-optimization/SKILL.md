---
name: azure-cost-optimization
description: "Cost optimization patterns, SKU right-sizing, and reserved instance guidance for Azure Landing Zones. USE FOR: architecture cost reviews, resource sizing recommendations. DO NOT USE FOR: budget enforcement (use cost-governance), pricing lookups (use azure-pricing MCP)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: azure-cost
---

# Azure Cost Optimization Skill

Cost optimization patterns for Azure Landing Zones.

## Cost Estimation by Resource Type

| Resource | Typical Monthly Cost (prod) | Optimization |
|----------|---------------------------|-------------|
| Azure Firewall Premium | ~$1,800 | Use Basic for dev/test |
| VPN Gateway (VpnGw1) | ~$140 | Scale down in non-prod |
| Bastion (Standard) | ~$400 | Use Developer SKU for dev |
| Log Analytics (100GB/day) | ~$350 | Set retention policies, archive |
| Key Vault (Standard) | ~$3 + per-operation | Minimal cost |
| Defender for Cloud (P2) | ~$15/server/month | Essential for prod |
| Application Gateway (v2) | ~$250 | Use per-site for multi-tenant |

## Budget Alert Strategy

Every subscription must have budget alerts:

| Threshold | Type | Action |
|-----------|------|--------|
| 80% | Forecasted | Email notification |
| 100% | Forecasted | Email + action group (Slack/Teams) |
| 120% | Forecasted | Email + action group + escalation |

Budget amounts are parameterized per environment:
- **Dev**: 30% of prod budget
- **Staging**: 50% of prod budget
- **Prod**: Full budget amount

## Right-Sizing Rules

| Resource | Dev/Test | Staging | Production |
|----------|---------|---------|------------|
| VM SKU | B2ms | D2s_v5 | D4s_v5+ |
| Firewall | Basic | Standard | Premium |
| Bastion | Developer | Basic | Standard |
| VPN Gateway | VpnGw1 | VpnGw1 | VpnGw2+ |
| SQL DTU | S0 | S2 | S4+ or vCore |

## Cost Savings Patterns

1. **Dev/Test pricing** — Apply dev/test pricing to non-prod subscriptions
2. **Auto-shutdown** — Schedule VM shutdown for dev environments (6 PM–8 AM)
3. **Reserved Instances** — 1-year RI for stable prod workloads (30-40% savings)
4. **Spot VMs** — Use for batch processing, CI/CD agents
5. **Storage tiering** — Cool/Archive for infrequent access data
6. **Log retention** — 30 days hot, 90 days archive, delete after 365
7. **Resource cleanup** — Tag unattached disks and NICs for removal
