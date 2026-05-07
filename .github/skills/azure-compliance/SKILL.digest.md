<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Compliance Skill (Digest)

Compliance framework mapping and Azure Policy alignment for Landing Zones.

## Supported Frameworks

| Framework | Key Controls → Azure Implementation |
|-----------|--------------------------------------|
| ISO 27001 | Access control (Entra+PIM), Cryptography (TLS+KV), Logging (LAW), Network security (NSG+FW+PE), BC (zone redundancy) |
| SOC 2 | Logical access (RBAC+PIM), System boundaries (NSG+FW+PE), Monitoring (Defender+Sentinel), Change mgmt (Policy+IaC) |
| PCI-DSS | Network security (FW+NSG), Data protection (TDE+KV), Access (RBAC+PIM), Logging (LAW), Testing (Defender) |

## Azure Policy Initiatives

| Initiative | Description |
|-----------|-------------|
| Azure Security Benchmark | Microsoft's baseline security controls |
| CIS Microsoft Azure Foundations | CIS benchmark compliance |
| ISO 27001:2013 | ISO 27001 control mapping |
| PCI DSS v4 | Payment card industry compliance |
| SOC 2 Type 2 | Service organization controls |
| NIST SP 800-53 Rev 5 | Federal information security |

## Security Baseline → Compliance Mapping

| Rule | ISO 27001 | SOC 2 | PCI-DSS |
|------|-----------|-------|---------|
| TLS 1.2 | A.10.1.1 | CC6.7 | 4.1 |
| HTTPS-only | A.10.1.1 | CC6.7 | 4.1 |
| No public blob | A.9.4.1 | CC6.1 | 7.1 |
| Managed Identity | A.9.2.3 | CC6.1 | 8.3 |
| AD-only SQL auth | A.9.4.2 | CC6.1 | 8.3 |
| No public network | A.13.1.1 | CC6.6 | 1.3 |

> _See SKILL.md for detailed per-framework control tables._
