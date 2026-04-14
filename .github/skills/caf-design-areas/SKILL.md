# CAF Design Areas Skill

Domain knowledge for mapping Azure Landing Zone components to Cloud Adoption
Framework (CAF) design areas.

## The 8 Design Areas

### A. Billing & Active Directory Tenant

**IaC Module:** `billing-and-tenant/`
**Scope:** Tenant-level

- Enterprise Agreement enrollment
- Management group root creation
- Tenant-wide settings
- Subscription creation and placement

### B. Identity & Access Management

**Bicep Module:** `identity/`
**Terraform Module:** `identity/`

- Entra ID (Azure AD) configuration
- RBAC role assignments (built-in + custom)
- Privileged Identity Management (PIM)
- Conditional access policies
- Managed identity for platform services
- Break-glass accounts

### C. Resource Organization

**Bicep Module:** `governance/`, `policies/`
**Terraform Module:** `policies/`

- Management group hierarchy (Platform, Landing Zones, Sandbox, Decommissioned)
- Subscription vending and placement
- Resource group naming conventions
- Tagging strategy (mandatory: Environment, Owner, CostCenter, Project)

### D. Network Topology & Connectivity

**Bicep Module:** `connectivity/` (hub-spoke, vwan, gateways, private-dns), `networking/`
**Terraform Module:** `connectivity/`, `networking/`

- Hub-spoke topology with Azure Firewall
- Virtual WAN alternative
- ExpressRoute and VPN gateways
- Private DNS zones (20 default privatelink zones)
- DDoS Protection
- Network Security Groups
- IP address management

### E. Security

**Bicep Module:** `security/`, `platform-security/` (sentinel, defender, soar)
**Terraform Module:** `security/`, `platform-security/`

- Microsoft Defender for Cloud (all plans)
- Microsoft Sentinel (SIEM)
- SOAR playbooks (Block-IP, Isolate-VM, Revoke-Session, Enrich-TI)
- Key Vault for secrets management
- Security baseline enforcement (6 core rules)
- Security-dedicated Log Analytics workspace

### F. Management

**Bicep Module:** `management/`, `logging/`
**Terraform Module:** `platform-management/`, `logging/`

- Central Log Analytics workspace
- Azure Monitor and action groups
- Automation Account
- Update Management
- Azure Backup and Recovery Services Vault
- Diagnostic settings for all resources

### G. Governance

**Bicep Module:** `governance/`, `policies/`
**Terraform Module:** `policies/`

- Azure Policy (built-in initiatives: ASB, CIS, ISO 27001, NIST)
- Custom policies (deny public IP, require TLS, enforce HTTPS, deny public blob, require tags)
- Budget alerts with forecast thresholds
- Cost Management
- Compliance reporting

### H. Platform Automation & DevOps

**Implemented via:** `pipelines/`, `scripts/`, `.github/workflows/`

- GitHub Actions CI/CD with OIDC authentication
- Bicep and Terraform validation pipelines
- Security baseline validator (pre-commit + CI)
- Cost governance validator (pre-commit + CI)
- Self-hosted runner support via `vars.RUNNER_LABEL`

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
