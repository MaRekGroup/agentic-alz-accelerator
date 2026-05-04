# WARA Assessment Report — 7522c19f-e3b7-46ab-a3f4-e6281173bfcc

> Assessed on 2026-05-04T18:19:20.499872+00:00

## Executive Summary

| Metric | Value |
|--------|-------|
| Overall Score | **52.0/100** |
| Checks Run | 221 |
| Checks Passed | 187 |
| Findings | 34 |

## Pillar Scores

| Pillar | Score | Critical | High | Medium | Low |
|--------|-------|----------|------|--------|-----|
| Security | 30.0 | 1 | 3 | 4 | 0 |
| Reliability | 30.0 | 0 | 5 | 4 | 0 |
| Cost Optimization | 55.0 | 0 | 3 | 3 | 0 |
| Operational Excellence | 57.0 | 0 | 2 | 3 | 4 |
| Performance Efficiency | 88.0 | 0 | 1 | 0 | 1 |

## Findings

### 🔴 Critical — Defender for Cloud enabled on subscriptions (`SEC-010`)

- **Pillar**: Security
- **CAF Area**: security
- **ALZ Area**: security
- **Confidence**: high
- **Resources affected**: 39

**Recommendation**: Enable Defender for Cloud Standard tier on all subscriptions.

**Remediation**:
1. Enable via: az security pricing create --name default --tier Standard

**References**:
- https://learn.microsoft.com/azure/defender-for-cloud/enable-enhanced-security

### 🟠 High — Configure Service Health Alerts (Subscriptions) (`APRL-OPE-9729C89D`)

- **Pillar**: Operational Excellence
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 10

**Recommendation**: Service health gives a personalized health view of Azure services and regions used, offering the best place for notifications on outages, planned maintenance, and health advisories by knowing the services used.

**References**:
- https://learn.microsoft.com/azure/service-health/alerts-activity-log-service-notifications-portal

### 🟠 High — Ensure that storage accounts are zone or region redundant (storageAccounts) (`APRL-REL-E6C7E1CC`)

- **Pillar**: Reliability
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 11

**Recommendation**: Redundancy ensures storage accounts meet availability and durability targets amidst failures, weighing lower costs against higher availability. Locally redundant storage offers the least durability at the lowest cost.

**References**:
- https://learn.microsoft.com/azure/storage/common/storage-redundancy

### 🟠 High — Use Standard SKU and Zone-Redundant IPs when applicable (publicIPAddresses) (`APRL-REL-C63B81FB`)

- **Pillar**: Reliability
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 2

**Recommendation**: Public IP addresses in Azure can be of standard SKU, available as non-zonal, zonal, or zone-redundant. Zone-redundant IPs are accessible across all zones, resisting any single zone failure, thereby providing higher resilience.

**References**:
- https://learn.microsoft.com/azure/virtual-network/ip-services/public-ip-addresses#availability-zone

### 🟠 High — Run production workloads on two or more VMs using VMSS Flex (virtualMachines) (`APRL-REL-273F6B30`)

- **Pillar**: Reliability
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 1

**Recommendation**: Production VM workloads should be deployed on multiple VMs and grouped in a VMSS Flex instance to intelligently distribute across the platform, minimizing the impact of platform faults and updates.

**References**:
- https://learn.microsoft.com/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-orchestration-modes#what-has-changed-with-flexible-orchestration-mode

### 🟠 High — Deploy VMs across Availability Zones (virtualMachines) (`APRL-REL-2BD0BE95`)

- **Pillar**: Reliability
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 1

**Recommendation**: Azure Availability Zones, within each Azure region, are tolerant to local failures, protecting applications and data against unlikely Datacenter failures by being physically separate.

**References**:
- https://learn.microsoft.com/azure/virtual-machines/create-portal-availability-zone?tabs=standard

### 🟠 High — Mission Critical Workloads should consider using Premium or Ultra Disks (virtualMachines) (`APRL-PER-DF0FF862`)

- **Pillar**: Performance Efficiency
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 1

**Recommendation**: Compared to Standard HDD and SSD, Premium SSD, SSD v2, and Ultra Disks offer improved performance, configurability, and higher single-instance VM uptime SLAs. The lowest SLA of all disks on a VM applies, so it is best to use Premium or Ultra Disks for the highest uptime SLA.

**References**:
- https://learn.microsoft.com/azure/virtual-machines/disks-types#disk-type-comparison

### 🟠 High — No budget resources found (`COS-001`)

- **Pillar**: Cost Optimization
- **CAF Area**: governance
- **ALZ Area**: policy
- **Confidence**: high
- **Resources affected**: 0

**Recommendation**: Create budget resources with 80/100/120% forecast alerts.

**Remediation**:
1. Deploy budget resource via IaC with parameterized thresholds

**References**:
- https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-create-budgets

### 🟠 High — Resource groups missing CostCenter tag (`COS-017`)

- **Pillar**: Cost Optimization
- **CAF Area**: governance
- **ALZ Area**: policy
- **Confidence**: high
- **Resources affected**: 22

**Recommendation**: Apply CostCenter tag to all resource groups for cost allocation and chargeback.

**Remediation**:
1. Tag resource group: az tag update --resource-id <rg-id> --operation merge --tags CostCenter=<value>

**References**:
- https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-tagging

### 🟠 High — Long-running VMs without Reserved Instances (`COS-009`)

- **Pillar**: Cost Optimization
- **CAF Area**: governance
- **ALZ Area**: policy
- **Confidence**: medium
- **Resources affected**: 1

**Recommendation**: Purchase Reserved Instances for VMs running 24/7 to save up to 72% vs pay-as-you-go.

**Remediation**:
1. Review Advisor RI recommendations and purchase via Azure portal or API

**References**:
- https://learn.microsoft.com/azure/cost-management-billing/reservations/save-compute-costs-reservations

### 🟠 High — No hub VNet or firewall detected (`OPE-006`)

- **Pillar**: Operational Excellence
- **CAF Area**: network
- **ALZ Area**: networking
- **Confidence**: medium
- **Resources affected**: 0

**Recommendation**: Deploy a hub VNet with Azure Firewall for centralized network governance.

**Remediation**:
1. Deploy connectivity landing zone with hub-spoke topology

**References**:
- https://learn.microsoft.com/azure/architecture/networking/architecture/hub-spoke

### 🟠 High — VMs without availability zones (`REL-001`)

- **Pillar**: Reliability
- **CAF Area**: network
- **ALZ Area**: networking
- **Confidence**: high
- **Resources affected**: 1

**Recommendation**: Deploy VMs across availability zones for high availability.

**Remediation**:
1. Redeploy VMs into availability zones (requires VM recreate)

**References**:
- https://learn.microsoft.com/azure/reliability/availability-zones-overview

### 🟠 High — DDoS Protection Plan on hub VNet (`SEC-014`)

- **Pillar**: Security
- **CAF Area**: network
- **ALZ Area**: networking
- **Confidence**: high
- **Resources affected**: 1

**Recommendation**: Enable DDoS Network Protection on hub virtual networks.

**Remediation**:
1. Create DDoS protection plan and associate with hub VNet

**References**:
- https://learn.microsoft.com/azure/ddos-protection/ddos-protection-overview

### 🟠 High — Managed Identity preferred over service principal secrets (`SEC-025`)

- **Pillar**: Security
- **CAF Area**: identity_access
- **ALZ Area**: identity
- **Confidence**: medium
- **Resources affected**: 1

**Recommendation**: Assign managed identity to compute resources instead of using service principal secrets.

**Remediation**:
1. Enable system-assigned or user-assigned managed identity on the resource

**References**:
- https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview

### 🟠 High — Storage accounts require secure transfer (SMB encryption) (`SEC-029`)

- **Pillar**: Security
- **CAF Area**: security
- **ALZ Area**: security
- **Confidence**: high
- **Resources affected**: 11

**Recommendation**: Require secure transfer and enable infrastructure encryption on storage accounts.

**Remediation**:
1. Enable HTTPS-only and infrastructure encryption on storage accounts

**References**:
- https://learn.microsoft.com/azure/storage/common/storage-require-secure-transfer

### 🟡 Medium — Configure Network Watcher Connection monitor (networkWatchers) (`APRL-OPE-1E28BBC1`)

- **Pillar**: Operational Excellence
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 7

**Recommendation**: Improves monitoring for Azure and Hybrid connectivity

**References**:
- https://learn.microsoft.com/azure/network-watcher/connection-monitor-overview

### 🟡 Medium — Ensure Time-To-Live (TTL) is set appropriately to ensure RTOs can be met (privateDnsZones) (`APRL-REL-3538AA48`)

- **Pillar**: Reliability
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: medium
- **Resources affected**: 10

**Recommendation**: Azure Private DNS allows the Time-To-Live (TTL) for record sets in the zone to be set to a value between 1 and 2147483647 seconds. You should ensure that the TTL for the DNS record sets in your DNS Zones are set appropriately to meet your RTO targets.

**References**:
- https://learn.microsoft.com/azure/reliability/reliability-dns

### 🟡 Medium — Enable Virtual Network Flow Logs (virtualNetworks) (`APRL-OPE-06B77BE9`)

- **Pillar**: Operational Excellence
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 7

**Recommendation**: Improves monitoring and security for Azure and Hybrid connectivity

**References**:
- https://learn.microsoft.com/azure/network-watcher/vnet-flow-logs-overview

### 🟡 Medium — Use NAT gateway for outbound connectivity to avoid SNAT Exhaustion (publicIPAddresses) (`APRL-REL-1ADBA190`)

- **Pillar**: Reliability
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 1

**Recommendation**: Prevent connectivity failures due to SNAT port exhaustion by employing NAT gateway for outbound traffic from virtual networks, ensuring dynamic scaling and secure internet connections.

**References**:
- https://learn.microsoft.com/azure/advisor/advisor-reference-reliability-recommendations#use-nat-gateway-for-outbound-connectivity

### 🟡 Medium — Replicate VMs using Azure Site Recovery (virtualMachines) (`APRL-REL-CFE22A65`)

- **Pillar**: Reliability
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 1

**Recommendation**: Replicating Azure VMs via Site Recovery entails continuous, asynchronous disk replication to a target region. Recovery points are generated every few minutes, ensuring a Recovery Point Objective (RPO) in minutes.

**References**:
- https://learn.microsoft.com/azure/architecture/checklist/resiliency-per-service#virtual-machines

### 🟡 Medium — Backup VMs with Azure Backup service (virtualMachines) (`APRL-REL-1981F704`)

- **Pillar**: Reliability
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 1

**Recommendation**: Enable backups for your virtual machines with Azure Backup to secure and quickly recover your data. This service offers simple, secure, and cost-effective solutions for backing up and recovering data from the Microsoft Azure cloud.

**References**:
- https://learn.microsoft.com/azure/backup/backup-overview

### 🟡 Medium — Orphan network interfaces (unattached) (`COS-004`)

- **Pillar**: Cost Optimization
- **CAF Area**: network
- **ALZ Area**: networking
- **Confidence**: high
- **Resources affected**: 1

**Recommendation**: Delete orphan NICs left behind after VM deletion.

**Remediation**:
1. Verify NIC is not needed, then delete: az network nic delete --ids <id>

**References**:
- https://learn.microsoft.com/azure/virtual-network/virtual-network-network-interface

### 🟡 Medium — No Cost Management scheduled exports (`COS-020`)

- **Pillar**: Cost Optimization
- **CAF Area**: governance
- **ALZ Area**: policy
- **Confidence**: medium
- **Resources affected**: 1

**Recommendation**: Configure scheduled Cost Management exports for cost data analysis and FinOps reporting.

**Remediation**:
1. Create export: az costmanagement export create --scope <sub-id> --name daily-export

**References**:
- https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-export-acm-data

### 🟡 Medium — Potentially over-provisioned VMs (B-series recommended) (`COS-011`)

- **Pillar**: Cost Optimization
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: medium
- **Resources affected**: 2

**Recommendation**: Right-size over-provisioned VMs per Azure Advisor recommendations.

**Remediation**:
1. Resize VM to recommended SKU: az vm resize --size <recommended-size>

**References**:
- https://learn.microsoft.com/azure/advisor/advisor-cost-recommendations

### 🟡 Medium — Resources missing required tags (`OPE-005`)

- **Pillar**: Operational Excellence
- **CAF Area**: resource_org
- **ALZ Area**: policy
- **Confidence**: high
- **Resources affected**: 22

**Recommendation**: Apply required tags (Environment, Owner, CostCenter) to all resource groups.

**Remediation**:
1. Assign tagging policy at MG scope to enforce required tags
2. Remediate existing resources with tagging task

**References**:
- https://learn.microsoft.com/azure/azure-resource-manager/management/tag-resources

### 🟡 Medium — Public IP addresses detected (`SEC-008`)

- **Pillar**: Security
- **CAF Area**: network
- **ALZ Area**: networking
- **Confidence**: medium
- **Resources affected**: 2

**Recommendation**: Review public IP addresses — remove unnecessary public exposure.

**Remediation**:
1. Audit each public IP for necessity
2. Replace with Private Endpoints where possible

**References**:
- https://learn.microsoft.com/azure/virtual-network/ip-services/public-ip-addresses

### 🟡 Medium — Diagnostic settings on security-critical resources (`SEC-018`)

- **Pillar**: Security
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: medium
- **Resources affected**: 16

**Recommendation**: Configure diagnostic settings on Key Vaults, NSGs, and Firewalls to ship logs to Log Analytics.

**Remediation**:
1. Create diagnostic setting: az monitor diagnostic-settings create --resource {id} --workspace {law-id}

**References**:
- https://learn.microsoft.com/azure/azure-monitor/essentials/diagnostic-settings

### 🟡 Medium — JIT VM access enabled for management (`SEC-020`)

- **Pillar**: Security
- **CAF Area**: security
- **ALZ Area**: security
- **Confidence**: medium
- **Resources affected**: 1

**Recommendation**: Enable Just-In-Time VM access to reduce attack surface for management ports.

**Remediation**:
1. Configure JIT access in Defender for Cloud for VMs requiring management access

**References**:
- https://learn.microsoft.com/azure/defender-for-cloud/just-in-time-access-overview

### 🟡 Medium — Activity log exported to Log Analytics (`SEC-026`)

- **Pillar**: Security
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: medium
- **Resources affected**: 1

**Recommendation**: Export Activity Log to Log Analytics workspace for audit and threat detection.

**Remediation**:
1. Create subscription-level diagnostic setting to ship Activity Log to LAW

**References**:
- https://learn.microsoft.com/azure/azure-monitor/essentials/activity-log

### 🔵 Low — Monitor changes in Network Security Groups with Azure Monitor (networkSecurityGroups) (`APRL-OPE-8BB4A57B`)

- **Pillar**: Operational Excellence
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 15

**Recommendation**: Create Alerts with Azure Monitor for operations like creating or updating Network Security Group rules to catch unauthorized/undesired changes to resources and spot attempts to bypass firewalls or access resources from the outside.

**References**:
- https://learn.microsoft.com/azure/azure-monitor/essentials/activity-log?tabs=powershell

### 🔵 Low — Deploy Network Watcher in all regions where you have networking services (networkWatchers) (`APRL-OPE-4E133BD0`)

- **Pillar**: Operational Excellence
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 14

**Recommendation**: Azure Network Watcher offers tools for monitoring, diagnosing, viewing metrics, and managing logs for IaaS resources. It helps maintain the health of VMs, VNets, application gateways, load balancers, but not for PaaS or Web analytics.

**References**:
- https://learn.microsoft.com/azure/network-watcher/network-watcher-overview

### 🔵 Low — When AccelNet is enabled, you must manually update the GuestOS NIC driver (virtualMachines) (`APRL-OPE-73D1BB04`)

- **Pillar**: Operational Excellence
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 1

**Recommendation**: When Accelerated Networking is enabled, the default Azure VNet interface in GuestOS is swapped for a Mellanox, and its driver comes from a 3rd party. Marketplace images have the latest Mellanox drivers, but post-deployment, updating the driver is the user's responsibility.

**References**:
- https://learn.microsoft.com/azure/virtual-network/accelerated-networking-overview

### 🔵 Low — Enable VM Insights (virtualMachines) (`APRL-OPE-B72214BB`)

- **Pillar**: Operational Excellence
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: high
- **Resources affected**: 1

**Recommendation**: VM Insights monitors VM and scale set performance, health, running processes, and dependencies. It enhances the predictability of application performance and availability by pinpointing performance bottlenecks and network issues, and it clarifies if problems are related to other dependencies.

**References**:
- https://learn.microsoft.com/azure/azure-monitor/vm/vminsights-overview

### 🔵 Low — Storage accounts using legacy SKU (`PER-001`)

- **Pillar**: Performance Efficiency
- **CAF Area**: management
- **ALZ Area**: logging
- **Confidence**: medium
- **Resources affected**: 11

**Recommendation**: Evaluate if ZRS or GRS replication is appropriate for production workloads.

**Remediation**:
1. Assess replication needs per workload; upgrade to ZRS/GRS where needed

**References**:
- https://learn.microsoft.com/azure/storage/common/storage-redundancy
