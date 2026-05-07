<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# CAF Design Areas Skill (Digest)

Maps Azure Landing Zone components to Cloud Adoption Framework (CAF) design areas
with IaC module references and management group hierarchy.

## The 8 Design Areas

| Area | IaC Module | Key Concerns |
|------|-----------|--------------|
| A. Billing & Tenant | `billing-and-tenant/` | EA enrollment, MG root, tenant settings, subscription creation |
| B. Identity & Access | `identity/` | Entra ID, RBAC, PIM, conditional access, managed identity |
| C. Resource Organization | `governance/`, `policies/` | MG hierarchy, subscription vending, naming, tagging |
| D. Network Topology | `connectivity/`, `networking/` | Hub-spoke, VWAN, ExpressRoute/VPN, Private DNS, DDoS, NSGs |
| E. Security | `security/`, `platform-security/` | Defender, Sentinel, SOAR, Key Vault, security baseline |
| F. Management | `management/`, `logging/` | Log Analytics, Azure Monitor, Automation, Backup, diagnostics |
| G. Governance | `governance/`, `policies/` | Azure Policy (ASB, CIS, ISO, NIST), custom policies, budgets |
| H. Platform Automation | `pipelines/`, `.github/workflows/` | GitHub Actions CI/CD, OIDC, validators, self-hosted runners |

## Management Group Hierarchy

```
Tenant Root
└── ALZ (root)
    ├── Platform
    │   ├── Management
    │   ├── Connectivity
    │   ├── Identity
    │   └── Security
    ├── Landing Zones
    │   ├── Online
    │   ├── Corp
    │   └── SAP
    ├── Sandbox
    └── Decommissioned
```

## Subscription Placement

| Management Group | Subscription Purpose |
|-----------------|---------------------|
| Platform/Management | Central logging, monitoring, automation |
| Platform/Connectivity | Hub VNet, Firewall, gateways, DNS |
| Platform/Identity | Entra ID, domain controllers |
| Platform/Security | Sentinel, Defender, SOC workspace |
| Landing Zones/Online | Internet-facing workloads |
| Landing Zones/Corp | Internal/corporate workloads |
| Landing Zones/SAP | SAP-specific workloads |
| Sandbox | Development and experimentation |

> _See SKILL.md for detailed per-area descriptions._
