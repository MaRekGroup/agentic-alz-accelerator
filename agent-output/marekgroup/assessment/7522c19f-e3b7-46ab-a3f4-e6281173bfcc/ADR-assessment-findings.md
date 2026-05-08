# ADR — Assessment Findings for 7522c19f-e3b7-46ab-a3f4-e6281173bfcc

**Date**: 2026-05-08
**Status**: Proposed
**Deciders**: Platform team

## Context

A WARA/CAF assessment was performed on `7522c19f-e3b7-46ab-a3f4-e6281173bfcc` scoring **49.0/100** overall.
The assessment identified **36** findings across 221 checks.

## Critical/High Findings Requiring Decision

### 🔴 Critical — Defender for Cloud enabled on subscriptions (`SEC-010`)

**Problem**: Enable Defender for Cloud Standard tier on all subscriptions.

**Proposed remediation**:
1. Enable via: az security pricing create --name default --tier Standard

### 🟠 High — Configure Service Health Alerts (Subscriptions) (`APRL-OPE-9729C89D`)

**Problem**: Service health gives a personalized health view of Azure services and regions used, offering the best place for notifications on outages, planned maintenance, and health advisories by knowing the services used.

### 🟠 High — Ensure that storage accounts are zone or region redundant (storageAccounts) (`APRL-REL-E6C7E1CC`)

**Problem**: Redundancy ensures storage accounts meet availability and durability targets amidst failures, weighing lower costs against higher availability. Locally redundant storage offers the least durability at the lowest cost.

### 🟠 High — Use Standard SKU and Zone-Redundant IPs when applicable (publicIPAddresses) (`APRL-REL-C63B81FB`)

**Problem**: Public IP addresses in Azure can be of standard SKU, available as non-zonal, zonal, or zone-redundant. Zone-redundant IPs are accessible across all zones, resisting any single zone failure, thereby providing higher resilience.

### 🟠 High — Run production workloads on two or more VMs using VMSS Flex (virtualMachines) (`APRL-REL-273F6B30`)

**Problem**: Production VM workloads should be deployed on multiple VMs and grouped in a VMSS Flex instance to intelligently distribute across the platform, minimizing the impact of platform faults and updates.

### 🟠 High — Deploy VMs across Availability Zones (virtualMachines) (`APRL-REL-2BD0BE95`)

**Problem**: Azure Availability Zones, within each Azure region, are tolerant to local failures, protecting applications and data against unlikely Datacenter failures by being physically separate.

### 🟠 High — Mission Critical Workloads should consider using Premium or Ultra Disks (virtualMachines) (`APRL-PER-DF0FF862`)

**Problem**: Compared to Standard HDD and SSD, Premium SSD, SSD v2, and Ultra Disks offer improved performance, configurability, and higher single-instance VM uptime SLAs. The lowest SLA of all disks on a VM applies, so it is best to use Premium or Ultra Disks for the highest uptime SLA.

### 🟠 High — No budget resources found (`COS-001`)

**Problem**: Create budget resources with 80/100/120% forecast alerts.

**Proposed remediation**:
1. Deploy budget resource via IaC with parameterized thresholds

### 🟠 High — Azure Advisor cost recommendations pending (`COS-014`)

**Problem**: Review and act on Azure Advisor cost recommendations to reduce waste.

**Proposed remediation**:
1. Review recommendations: az advisor recommendation list --category Cost
2. Implement or dismiss each recommendation

### 🟠 High — Resource groups missing CostCenter tag (`COS-017`)

**Problem**: Apply CostCenter tag to all resource groups for cost allocation and chargeback.

**Proposed remediation**:
1. Tag resource group: az tag update --resource-id <rg-id> --operation merge --tags CostCenter=<value>

### 🟠 High — Long-running VMs without Reserved Instances (`COS-009`)

**Problem**: Purchase Reserved Instances for VMs running 24/7 to save up to 72% vs pay-as-you-go.

**Proposed remediation**:
1. Review Advisor RI recommendations and purchase via Azure portal or API

### 🟠 High — No hub VNet or firewall detected (`OPE-006`)

**Problem**: Deploy a hub VNet with Azure Firewall for centralized network governance.

**Proposed remediation**:
1. Deploy connectivity landing zone with hub-spoke topology

### 🟠 High — VMs without availability zones (`REL-001`)

**Problem**: Deploy VMs across availability zones for high availability.

**Proposed remediation**:
1. Redeploy VMs into availability zones (requires VM recreate)

### 🟠 High — DDoS Protection Plan on hub VNet (`SEC-014`)

**Problem**: Enable DDoS Network Protection on hub virtual networks.

**Proposed remediation**:
1. Create DDoS protection plan and associate with hub VNet

### 🟠 High — Managed Identity preferred over service principal secrets (`SEC-025`)

**Problem**: Assign managed identity to compute resources instead of using service principal secrets.

**Proposed remediation**:
1. Enable system-assigned or user-assigned managed identity on the resource

### 🟠 High — Storage accounts require secure transfer (SMB encryption) (`SEC-029`)

**Problem**: Require secure transfer and enable infrastructure encryption on storage accounts.

**Proposed remediation**:
1. Enable HTTPS-only and infrastructure encryption on storage accounts

## Decision

<!-- TO BE FILLED: Accept / Modify / Defer each finding -->

## Consequences

- Accepted findings will be remediated according to the roadmap in target-state-architecture.md
- Deferred findings will be tracked in the next assessment cycle
