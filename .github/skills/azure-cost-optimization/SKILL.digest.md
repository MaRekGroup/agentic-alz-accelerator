<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Cost Optimization Skill (Digest)

Cost optimization patterns, SKU right-sizing, and reserved instance guidance for ALZ.

## Cost Estimation by Resource Type

| Resource | Typical Monthly Cost (prod) | Optimization |
|----------|---------------------------|-------------|
| Azure Firewall Premium | ~$1,800 | Use Basic for dev/test |
| VPN Gateway (VpnGw1) | ~$140 | Scale down in non-prod |
| Bastion (Standard) | ~$400 | Use Developer SKU for dev |
| Log Analytics (100GB/day) | ~$350 | Set retention policies, archive |
| Key Vault (Standard) | ~$3 + per-op | Minimal cost |
| Defender for Cloud (P2) | ~$15/server/month | Essential for prod |
| Application Gateway (v2) | ~$250 | Use per-site for multi-tenant |

## Budget Alert Strategy

| Threshold | Type | Action |
|-----------|------|--------|
| 80% | Forecasted | Email notification |
| 100% | Forecasted | Email + action group |
| 120% | Forecasted | Email + action group + escalation |

Budget sizing: Dev=30%, Staging=50%, Prod=100%.

## Right-Sizing Rules

| Resource | Dev/Test | Staging | Production |
|----------|---------|---------|------------|
| VM SKU | B2ms | D2s_v5 | D4s_v5+ |
| Firewall | Basic | Standard | Premium |
| Bastion | Developer | Basic | Standard |
| VPN Gateway | VpnGw1 | VpnGw1 | VpnGw2+ |
| SQL DTU | S0 | S2 | S4+ or vCore |

## Cost Savings Patterns

1. Dev/Test pricing for non-prod subscriptions
2. Auto-shutdown VMs in dev (6 PM–8 AM)
3. 1-year Reserved Instances for stable prod (30–40% savings)
4. Spot VMs for batch/CI-CD
5. Storage tiering (Cool/Archive)
6. Log retention: 30d hot, 90d archive, delete after 365
7. Tag unattached disks/NICs for removal

> _See SKILL.md for full details._
