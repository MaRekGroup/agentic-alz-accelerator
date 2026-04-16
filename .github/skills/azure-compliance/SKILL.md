---
name: azure-compliance
description: "Compliance framework mapping and Azure Policy alignment for Landing Zones. USE FOR: policy assignment planning, regulatory mapping (CIS, NIST, PCI-DSS, HIPAA, SOC 2). DO NOT USE FOR: security baseline enforcement (use security-baseline)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: azure-governance
---

# Azure Compliance Skill

Compliance framework mapping for Azure Landing Zones.

## Supported Compliance Frameworks

### ISO 27001
| Control | Azure Implementation |
|---------|---------------------|
| A.9.1 Access control | Entra ID + Conditional Access + PIM |
| A.10.1 Cryptography | TLS 1.2+, Azure Key Vault, disk encryption |
| A.12.4 Logging | Log Analytics, Azure Monitor, Activity Log |
| A.13.1 Network security | NSGs, Azure Firewall, Private Endpoints |
| A.17.1 Business continuity | Zone redundancy, Azure Backup, DR |

### SOC 2
| Trust Service Criteria | Azure Implementation |
|----------------------|---------------------|
| CC6.1 Logical access | Entra ID RBAC, PIM, Conditional Access |
| CC6.6 System boundaries | NSGs, Azure Firewall, Private Endpoints |
| CC7.2 Monitoring | Azure Monitor, Defender for Cloud, Sentinel |
| CC8.1 Change management | Azure Policy, IaC (Bicep/Terraform), GitOps |

### PCI-DSS
| Requirement | Azure Implementation |
|------------|---------------------|
| 1. Network security | Azure Firewall, NSGs, network segmentation |
| 3. Protect stored data | TDE, disk encryption, Key Vault |
| 7. Restrict access | RBAC, PIM, least privilege |
| 10. Logging | Log Analytics, diagnostic settings |
| 11. Security testing | Defender for Cloud, vulnerability assessments |

## Azure Policy Initiatives

| Initiative | Description |
|-----------|-------------|
| `Azure Security Benchmark` | Microsoft's baseline security controls |
| `CIS Microsoft Azure Foundations` | CIS benchmark compliance |
| `ISO 27001:2013` | ISO 27001 control mapping |
| `PCI DSS v4` | Payment card industry compliance |
| `SOC 2 Type 2` | Service organization controls |
| `NIST SP 800-53 Rev 5` | Federal information security |

## Security Baseline Mapping

Our 6 non-negotiable rules map to compliance frameworks:

| Rule | ISO 27001 | SOC 2 | PCI-DSS |
|------|-----------|-------|---------|
| TLS 1.2 | A.10.1.1 | CC6.7 | 4.1 |
| HTTPS-only | A.10.1.1 | CC6.7 | 4.1 |
| No public blob | A.9.4.1 | CC6.1 | 7.1 |
| Managed Identity | A.9.2.3 | CC6.1 | 8.3 |
| AD-only SQL auth | A.9.4.2 | CC6.1 | 8.3 |
| No public network | A.13.1.1 | CC6.6 | 1.3 |
