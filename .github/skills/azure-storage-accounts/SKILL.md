---
name: azure-storage-accounts
description: "Azure Storage Account topology design for multi-tenant blob isolation, lifecycle management, immutability, and security hardening in Azure Landing Zones. USE FOR: standard storage account workloads (Blob, Queue, Table, Files basic SMB, Static Website), multi-tenant per-blob isolation (account-per-tenant vs container-per-tenant vs path-per-tenant), lifecycle management with Hot/Cool/Cold/Archive tiering, immutability for compliance (FINRA, SEC 17a-4), private endpoint + storage firewall topology, disabling shared key auth in favour of Entra RBAC and user-delegation SAS, CMK encryption, blob inventory, and brownfield public-access violation remediation. DO NOT USE FOR: HNS-enabled or ADLS Gen2 analytics accounts (future analytics-wave skill), Azure NetApp Files or Azure Files Premium deep SMB/NFS workloads, Azure Managed Disks, Synapse, Fabric, Data Factory, Purview, Azure Cache for Redis, or Azure AI Search (all future-wave), relational OLTP workloads (use azure-sql-database), globally distributed document workloads (use azure-cosmos-db), or cross-cutting identity/network/cost/policy patterns (use azure-rbac, azure-private-link, cost-governance, azure-monitor, azure-key-vault, azure-policy). When to pick SQL vs Cosmos vs Storage: see docs/decisions/data-tier-selection.md."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: saul
  version: "1.0"
  category: azure-storage
  wave: "4"
---

# azure-storage-accounts

| Field | Value |
|-------|-------|
| **Skill ID** | `azure-storage-accounts` |
| **Domain** | Azure Storage / Data Platform — Persistence Layer |
| **Wave** | Wave 4 — Data Platform |
| **Hard Prereqs** | `azure-private-link`, `azure-policy` |
| **Soft Prereqs** | `azure-key-vault`, `azure-monitor`, `cost-governance`, `azure-rbac`, `workload-identity-federation` (W1) |
| **Shared ADR** | [`docs/decisions/data-tier-selection.md`](../../../docs/decisions/data-tier-selection.md) |
| **Primary CAF Areas** | Security, Identity & Access |
| **Primary WAF Pillars** | Reliability, Security |
| **Brownfield Scenario** | S5 — ISV Multi-Tenant SaaS |
| **Authored** | Wave 4 · 2026-07-14 · Saul |

Enable the Oracle to architect Storage Account topologies for multi-tenant SaaS, regulated, and AI workloads — with hardening patterns that address the #1 brownfield violation: public blob access enabled at the account level. This skill covers the full standard-account lifecycle from creation-time security baseline through CMK encryption, private endpoint topology, immutability for compliance, lifecycle tier management, and the two irrevocable hard gates (disable public access; disable shared key) that define the safety boundary of ISV estate remediation.

**When to use this skill:** Use when an ISV, regulated, or AI platform estate needs blob isolation, lifecycle automation, immutability, or security hardening at the storage account layer. Use when the Sentinel detects a public-blob-access violation and the brownfield playbook is needed to remediate without breaking existing tenant integrations.

## When to Use This Skill

- Designing per-tenant blob isolation for an ISV SaaS platform with multiple customers sharing an Azure estate (account-per-tenant vs container-per-tenant decision)
- Brownfield estate has public blob access violations flagged by Sentinel or Defender for Cloud — remediation requires the 8-step playbook in this skill
- Storage accounts are still using shared key authentication (account keys) with no Entra RBAC migration plan in place
- Lifecycle management policies are absent and the estate pays Hot-tier cost for data that should have transitioned to Archive months ago
- Regulated workloads (FINRA, SEC 17a-4, CFTC 1.31, HIPAA) require WORM-compliant immutable storage for audit trails
- Multi-tenant SaaS tenants require cryptographic isolation below the account level (encryption scopes with per-tenant CMK keys)
- Brownfield storage accounts have SFTP, NFS 3.0, or HNS features enabled and the team needs to understand the lock-in before making replication or auth changes
- Storage accounts are not behind private endpoints and are relying on storage firewall rules only — need to migrate to private endpoint topology without a traffic black hole

## Overview

This skill covers standard Azure Storage Account workloads: Blob (block blob, append blob, page blob), Queue, Table, Files (basic SMB at standard-account tier), and Static Website hosting. It addresses access control (Entra RBAC, user-delegation SAS, shared key disable), encryption at rest (service-managed and CMK via Key Vault, encryption scopes per tenant), network isolation (private endpoints per sub-resource, storage firewall, VNet rules), data durability (replication models, soft delete, versioning, object replication), lifecycle management (Hot/Cool/Cold/Archive tier transitions), and immutability (time-based retention, legal holds, WORM compliance).

The shared ADR [`docs/decisions/data-tier-selection.md`](../../../docs/decisions/data-tier-selection.md) establishes the canonical boundary for "Choose Storage when…" — use it when the question is SQL vs Cosmos vs Storage, not for how to configure within Storage. This skill goes deep on configuration. Per sponsor decision Q2/Q5, the following are explicitly out of scope for this wave: HNS-enabled accounts and ADLS Gen2 analytics workloads (future analytics-wave skill), Azure NetApp Files, Azure Files Premium, and Azure Managed Disks (future-wave candidates). HNS is noted as a pattern variant and feature-gating risk but is not deep-dived here.

**Out of scope:** `azure-sql-database` (relational OLTP), `azure-cosmos-db` (globally distributed active-active), and the shared ADR (tier selection decision boundary).

## CAF Design Area Mapping

| CAF Design Area | Coverage | Primary |
|-----------------|----------|---------|
| **Security** | Entra RBAC at account/container/blob scope, disable shared key, CMK with double encryption, blob immutability, soft delete, encryption scopes, SAS expiry policy | ✅ |
| **Identity & Access** | Entra RBAC data-plane roles (`Storage Blob Data Reader/Contributor/Owner`), disable shared key auth, user-delegation SAS (7-day max lifetime), workload identity for app access, per-container RBAC grants | ✅ |
| Management | Diagnostic settings to Log Analytics, blob inventory reports, storage analytics, lifecycle management policies, last-access-time tracking, soft delete retention | |
| Governance | Azure Policy: deny public access, enforce TLS 1.2, require private endpoint, deny shared key; resource locks for immutable accounts; mandatory tagging | |
| Network Topology | Private endpoints per sub-resource (blob/queue/table/file/web), storage firewall + VNet rules, trusted-services bypass, disable public network access | |

## WAF Pillar Coverage

| WAF Pillar | Coverage | Primary |
|------------|----------|---------|
| **Reliability** | Replication models (LRS/ZRS/GRS/GZRS/RA-GRS), customer-initiated account failover, soft delete, point-in-time restore for blob containers, versioning, object replication, immutability for compliance durability | ✅ |
| **Security** | Disable public blob access (Security Baseline Rule #3), disable shared key auth, CMK with double encryption, private endpoints, blob immutability, encryption scopes per tenant | ✅ |
| Cost Optimization | Access tier lifecycle (Hot→Cool→Cold→Archive), lifecycle policy automation, reserved capacity for predictable volumes, redundancy right-sizing (LRS vs ZRS vs GRS), premium vs standard tier selection | |
| Performance Efficiency | Performance tiers (Standard/Premium block blob), block blob vs page blob access patterns, CDN integration for static content, account scalability targets, large-file upload with block staging | |
| Operational Excellence | Lifecycle automation with feature-gating assessment (SFTP/NFS/HNS must be inventoried before any change), blob inventory reports, diagnostic logging, last-access-time tracking for data-driven lifecycle decisions, storage tasks | |

## Architecture Patterns

### 1. Multi-Tenant Blob Isolation

ISV SaaS platforms face a three-way isolation decision: **account-per-tenant** (strongest isolation, highest cost — a dedicated storage account per customer with independent encryption keys, network ACLs, and compliance policy), **container-per-tenant** (shared account, container-scoped Entra RBAC isolation — the pragmatic middle ground), or **path-prefix-per-tenant** (shared account and container, application-enforced name prefix — provides no platform-level access isolation and is appropriate for dev/test only). Container-per-tenant with `Storage Blob Data Contributor` scoped at the container level is the recommended production baseline for most ISV estates; it avoids per-tenant provisioning overhead while maintaining an Azure-enforced access boundary per tenant.

Key config knobs: assign `Storage Blob Data Reader` at container scope for read-only tenant access; `Storage Blob Data Contributor` for read/write; `Storage Blob Data Owner` for tenants requiring full lifecycle control including POSIX ACL management. RBAC role assignments at container scope are applied via ARM and propagate within seconds, but Entra token caches can hold stale role mappings for up to one hour — factor this into migration testing windows when switching from shared key to Entra. Per-account limits: a single storage account supports up to 5,000 container-scoped RBAC role assignments — ISV platforms with thousands of tenants in a single account will exhaust this limit. Account-per-tenant avoids this ceiling entirely.

Encryption scopes (`EncryptionScope` resource at account level) extend CMK key boundaries below the account level, enabling per-tenant cryptographic isolation without per-tenant accounts. Each encryption scope maps to a distinct Key Vault key — a compromised key affects only the containers using that scope. Key rotation is independent per scope. Gotcha: encryption scopes cannot be deleted once created; they can be disabled but remain in the account's scope list permanently, which becomes a management overhead concern for ISV platforms with high tenant churn.

### 2. Lifecycle Management with Tiering

Lifecycle management policies define rules that transition blobs between access tiers (Hot→Cool→Cold→Archive) or delete them based on last-modified date, last-access time, or blob age. Rules evaluate against each blob once per 24-48 hour evaluation cycle — not immediately — a critical timing assumption for brownfield teams expecting instant tier transitions. Rules can be scoped to specific containers, blob prefixes, or blob index match conditions, enabling per-tenant retention SLAs from a single policy resource.

Each tier carries a minimum storage period that triggers early-deletion charges if blobs are moved before the minimum: Cool requires 30 days, Cold requires 90 days, Archive requires 180 days. Typical ISV cost optimization: blobs not accessed for 30 days → Cool (saves ~50% vs Hot), blobs not accessed for 90 days → Cold (saves ~65%), blobs not accessed for 365 days → Archive (saves ~80%). Key config: enable `lastAccessTimePolicy` at account level before creating last-access-based rules — the property defaults to disabled and the lifecycle engine ignores `daysAfterLastAccessTimeGreaterThan` filters on accounts where it is off. Gotcha: lifecycle policies do not apply to premium block blob accounts (Standard tier only) — ISV estates using premium accounts for hot-path latency must manage tier transitions manually or use object replication to migrate aged blobs to a standard-tier archive account.

Last-access-time tracking must be enabled before the first lifecycle policy references it; enabling it retroactively does not backfill historical access timestamps — blobs that were accessed before tracking was enabled will appear as never accessed until their next access event, causing premature tiering for recently-accessed data. Validate last-access timestamps in a test container before deploying production lifecycle rules.

### 3. Immutability for Compliance

Blob immutability provides WORM (Write Once, Read Many) storage for regulated audit trails. Two policy types: **time-based retention** (blobs cannot be modified or deleted until the retention period expires) and **legal holds** (indefinite block until the hold is explicitly released). Both types can be configured at container level (always-on, all blobs in the container) or blob-version level (more granular control for versioning-enabled accounts). Versioned immutability allows different retention periods per blob version — appropriate when ISV tenants have different contractual retention requirements stored in the same container. Container-level immutability is simpler to operate and audit; use it when all blobs in the container share the same regulatory mandate.

Key config: time-based retention requires setting the `immutabilityPeriodSinceCreationInDays` property; start with the `unlocked` state to validate the period before locking. Regulatory mandates (FINRA Rule 4370, SEC Rule 17a-4, CFTC 1.31, HIPAA audit log requirements) require locked time-based policies — unlocked policies satisfy no regulatory obligation and should be treated as test-only. Legal holds are controlled via the `legalHold.hasLegalHold` property on the container and require the `Storage Blob Data Owner` role or the `Microsoft.Storage/storageAccounts/blobServices/containers/immutabilityPolicies/write` permission to modify.

Gotcha 1: locking is irrevocable for the configured retention period — the wrong period is a permanent cost commitment. Gotcha 2: append blobs in immutable containers cannot be written to after the policy is applied, even during the unlocked state for version-level immutability — ISV workloads using append blobs for audit log streaming must migrate to block blobs before enabling immutability. Combined use (legal hold AND time-based retention locked) provides defence-in-depth for regulated audit trails where both a regulatory minimum period and ongoing litigation hold must coexist independently.

### 4. Private Endpoint + Disable Public Access

Storage accounts expose sub-resource-specific private endpoints: `blob`, `queue`, `table`, `file`, and `web` (Static Website). Each sub-resource requires a separate private endpoint resource — a single endpoint does not cover all sub-resources. For ISV estates with multi-tenant blob access, the `blob` sub-resource endpoint is mandatory; `table` and `queue` endpoints should be provisioned if those sub-resources are in use. Key config: each private endpoint requires a Network Interface in the spoke VNet, a private DNS zone link, and a DNS zone group resource to auto-register the A record — missing the DNS zone group is the most common cause of name resolution failures after private endpoint provisioning.

DNS configuration requires a private DNS zone per sub-resource (`privatelink.blob.core.windows.net`, `privatelink.queue.core.windows.net`, etc.) linked to the spoke VNet where the private endpoints reside. For hub-spoke topologies, create the private DNS zones in the hub network resource group and link them to spoke VNets via DNS zone links — do NOT create duplicate zones in spoke VNets, as duplicate zones cause DNS resolution split-brain. Brownfield migration from firewall-only (storage firewall + VNet service endpoints) to private endpoint follows a strict ordering: (1) provision private endpoint, (2) create DNS zone and validate resolution, (3) test application connectivity through private endpoint, (4) disable public network access. Reversing this order causes a traffic black hole — disabling public access before DNS resolves correctly produces an outage.

Gotcha 1: the storage firewall "trusted Azure services bypass" (`bypass: AzureServices`) does not apply once `publicNetworkAccess: Disabled` is set — Azure services (Azure Backup, ADF, Azure Monitor) must reach the storage account through private endpoints after public access is disabled. Gotcha 2: ISV estates using Azure Backup for blob backup must provision a private endpoint with sub-resource `blob` before disabling public access, as the Backup vault uses the storage's management plane which is also affected by the public network access setting.

### 5. Disable Shared Key — Migrate to Entra RBAC + User-Delegation SAS

Disabling shared key authentication is operationally one-way: while `allowSharedKeyAccess` is technically re-enableable, doing so creates a security regression that triggers immediate policy violations and Sentinel findings. All applications must migrate before the gate is crossed to one of two auth paths: **direct Entra RBAC** (managed identity or service principal assigned a built-in Storage data-plane role: `Storage Blob Data Reader` for read-only, `Storage Blob Data Contributor` for read/write, `Storage Blob Data Owner` for full lifecycle including ACL management) or **user-delegation SAS** (short-lived SAS derived from an Entra principal's OAuth token, maximum 7-day lifetime, no account key required).

The migration path: enumerate all SAS tokens in use (search application logs and Key Vault secrets for SAS query strings containing `sv=`; tokens using account keys have `sig=` values derived from the account key, not a JWT), identify long-lived account-key SAS (lifetime > 7 days is a hard signal of account-key dependency), migrate each application to Entra RBAC or user-delegation SAS, validate by temporarily setting `allowSharedKeyAccess: false` on a development account, then apply to production. Azure SDKs support Entra credential chains (`DefaultAzureCredential`) natively — application auth changes are typically 2–5 lines for modern SDK versions. Key config: user-delegation SAS tokens require the calling principal to have at minimum `Storage Blob Delegator` role at the account scope in addition to any container-level data role.

Gotcha 1: Azure Storage Explorer (desktop application) requires the "Sign in with Azure Active Directory" option to work after shared key is disabled — teams using Storage Explorer with connection strings or access keys will be locked out. Gotcha 2: SAS tokens distributed to external partners or embedded in CI/CD pipeline configurations often persist without being tracked in any secrets inventory — manual application log and configuration search is required before this gate is safe to cross.

## Security Baseline Reinforcement

Storage accounts are one of the most directly impacted resources by the 6-rule security baseline. Baseline enforcement is injected at subscription vending time via policy assignments and validated continuously by the Sentinel.

| Rule | Storage Account Enforcement |
|------|----------------------------|
| **Rule 1 – TLS 1.2 minimum** | `minimumTlsVersion: 'TLS1_2'` — enforced via `Deny` policy at landing zone scope. Accounts with `TLS1_0` or `TLS1_1` are blocked on create/update. |
| **Rule 2 – HTTPS-only traffic** | `supportsHttpsTrafficOnly: true` — enforced via `Deny` policy. HTTP access to storage REST API is rejected at the service layer. |
| **Rule 3 – No public blob access** | `allowBlobPublicAccess: false` — the #1 brownfield finding; enforced via `deny-storage-public-access` policy. This rule is the primary driver of the brownfield playbook Step 5 gate. |
| **Rule 4 – Managed Identity preferred** | `identity: { type: 'SystemAssigned' }` — enforced via `Audit` policy; storage accounts used by compute workloads should have system-assigned identity to enable key-less CMK rotation and managed identity data-plane access patterns. |
| **Rule 5 – Azure AD-only SQL auth** | Not applicable to Storage Accounts. Equivalent control: `allowSharedKeyAccess: false` (disable account key auth) enforced via `deny-shared-key` policy — brownfield playbook Step 7. |
| **Rule 6 – Public network disabled (prod)** | `publicNetworkAccess: 'Disabled'` — enforced via `Deny` policy for Corp and SaaS-Tenant archetype subscriptions. Requires private endpoint provisioning (brownfield playbook Step 6) before this rule can be enforced without an outage. |

## Decision Heuristics

| Condition | Recommendation |
|-----------|----------------|
| ISV platform with fewer than 500 tenants, no per-tenant regulatory mandate | Container-per-tenant isolation with container-scoped Entra RBAC; one or two shared storage accounts per region |
| ISV platform with regulated tenants (FINRA, HIPAA, PCI-DSS) | Account-per-tenant with per-account CMK keys via Key Vault, or container-per-tenant with encryption scopes for cryptographic isolation |
| Account has `publicBlobAccess: true` flagged by Sentinel | Apply brownfield playbook Step 5; confirm no anonymous-read dependencies before disabling |
| Shared key auth still enabled; no Entra RBAC migration | Apply brownfield playbook Steps 5-7 in sequence; do NOT skip Step 5 (public access disable) before Step 7 (shared key disable) |
| Replication change needed (LRS → GRS) | Plan 72+ hour sync window; do NOT change replication model during a high-traffic period |
| SFTP or HNS is enabled on existing account | Treat as immutable feature — do not attempt to disable. Document as architectural constraint. Plan new account for workloads that don't require SFTP/HNS. |
| Lifecycle policies absent, all blobs in Hot tier | Enable last-access-time tracking first, then deploy lifecycle rules scoped per container; expect 24-48 hour evaluation lag before first tier transition |
| Immutability required; retention period uncertain | Deploy in `unlocked` state, validate period with legal/compliance team, then lock — never lock without validation |
| Brownfield account has no private endpoint | Apply brownfield playbook Steps 6 then Step 5; DNS must resolve via private endpoint before public access is disabled |

## Boundaries

### DO NOT USE FOR

| Out-of-Scope | Use Instead |
|--------------|-------------|
| Azure NetApp Files, Azure Managed Disks, Azure Files Premium (deep SMB/NFS file-share workloads) | Future-wave candidates; explicitly out of W4 per sponsor decision Q2/Q5 (this skill covers Files at standard-account level only) |
| HNS-enabled / ADLS Gen2 analytics storage accounts | Future analytics-wave skill; HNS feature-gating is covered as a brownfield assessment callout (Hidden Assumption 6) but is not deep-dived here |
| Synapse, Fabric, Data Factory, Purview, Azure Cache for Redis, Azure AI Search | Future-wave candidates; explicitly out of W4 scope per sponsor decision Q5 |
| Relational / transactional OLTP workloads | `azure-sql-database` |
| Document / globally distributed active-active workloads | `azure-cosmos-db` |
| Cross-cutting identity, network, cost, monitoring, key, policy patterns | `azure-rbac`, `azure-private-link`, `cost-governance`, `azure-monitor`, `azure-key-vault`, `azure-policy` |
| Application-to-Storage managed-identity / federated-credential auth setup | `workload-identity-federation` (W1) |
| When to pick SQL vs Cosmos vs Storage (tier selection decision boundary) | [`docs/decisions/data-tier-selection.md`](../../../docs/decisions/data-tier-selection.md) |

## Brownfield Scenario (Scenario S5: ISV Multi-Tenant SaaS)

This skill sequences after `azure-private-link` (endpoint topology established) and `azure-policy` (deny-public-access enforcement baseline in place), enabling the Oracle to prescribe Storage Account hardening for ISV multi-tenant SaaS estates without breaking existing tenant integrations. Use this brownfield playbook in conjunction with the boundary semantics from [`docs/decisions/data-tier-selection.md`](../../../docs/decisions/data-tier-selection.md).

ISV multi-tenant SaaS storage accounts are the #1 source of "public blob access" violations the Sentinel monitor detects. Typical brownfield findings in S5 estates: shared key auth still enabled (no Entra RBAC migration), public blob access enabled at account level, no private endpoints (relying on storage firewall rules only), lifecycle policies absent (all blobs remain in Hot tier indefinitely at maximum cost), no immutability for tenant audit trails, and SFTP or HNS features enabled without architectural assessment of the lock-in implications. The 8-step playbook below addresses each finding in dependency order, with hard gates at the two irrevocable actions.

| Step | Action | Rollback Type |
|------|--------|---------------|
| 1 | Inventory existing storage accounts via Resource Graph: account kind, replication model, access tier, public access flag, network ACLs, shared key auth status, SFTP/NFS/HNS feature status, lifecycle policy presence | Read-only |
| 2 | Assess findings: public blob access enabled? Shared key auth active? Lifecycle policies defined? Encryption: CMK or service-managed? Immutability configured for tenant audit trails? SFTP/NFS/HNS enabled (account-creation-time feature lock-in)? | Read-only |
| 3 | Enable diagnostic settings + blob inventory to Log Analytics workspace; enable last-access-time tracking if lifecycle automation is planned | Soft rollback (disable diagnostic settings; last-access tracking disabled) |
| 4 | Configure CMK from existing Key Vault (or provision new Key Vault instance); enable double encryption if regulated-tier tenants require cryptographic isolation | Soft rollback (revert to service-managed encryption within 24h; Key Vault key can be deactivated) |
| 5 | ⛔ **HARD GATE** — Disable public blob access at account level. This action affects ALL containers in the account simultaneously — any container currently serving anonymous reads breaks immediately. Confirm pre-HARD-GATE checklist (below) is complete before proceeding. | Time-windowed: re-enabling public access restores anonymous reads but creates a security regression window; if the account was already flagged in a compliance report, re-enabling generates a new violation finding. |
| 6 | Configure private endpoints per sub-resource (blob/queue/table/file/web as applicable); update private DNS zones; validate end-to-end name resolution before removing any firewall rules | Soft rollback (remove private endpoints; existing storage firewall VNet rules remain in effect) |
| 7 | ⛔ **HARD GATE** — Disable shared key authentication. All existing SAS tokens generated from account keys become immediately and permanently invalid. Only user-delegation SAS (Entra-backed, 7-day max lifetime) survives. Applications relying on long-lived account-key SAS will break. Confirm pre-HARD-GATE checklist (below) is complete before proceeding. | Irrevocable in effect: re-enabling shared key is technically possible but creates a security regression; all previously invalidated SAS tokens do NOT become valid again — they must be regenerated, requiring re-coordination with every application that held one. |
| 8 | Enforce Azure Policy: `deny-storage-public-access`, `require-tls-12`, `require-private-endpoint`, `deny-shared-key` | Soft rollback (remove policy assignment; drift begins immediately as non-compliant configurations can be applied without policy enforcement) |

**Pre-HARD-GATE Verification Checklist:**

Before Step 5 (disable public access): (a) run blob inventory to identify every container with `publicAccess: Blob` or `publicAccess: Container`; (b) confirm each container's public-access dependency has been migrated to Entra RBAC or CDN with private origin authentication; (c) validate that no application is relying on anonymous read for tenant-facing content delivery — if so, configure CDN with private origin and SAS token or Entra auth before proceeding.

Before Step 7 (disable shared key): (a) search application logs and Key Vault secret stores for SAS token strings containing `sv=` (URL-encoded account-key SAS); (b) confirm all integrations have migrated to user-delegation SAS or direct Entra RBAC; (c) validate the migration in a non-production account with `allowSharedKeyAccess: false` before applying to production accounts.

## Hidden Assumptions

1. **Lifecycle policy evaluation latency is 24-48 hours.** Rules do not execute immediately on creation. The first evaluation cycle runs within 24-48 hours; brownfield teams expecting instant tier transitions will see continued Hot-tier billing for 1-2 days. There is no mechanism to force an immediate lifecycle evaluation run on a specific account.

2. **Storage account replication change takes 72+ hours.** Changing the replication redundancy model (e.g., LRS to GRS) requires a full data-sync to the secondary region. During this window the secondary is not accessible for failover reads or failover operations. No accelerated path exists — replication conversion always runs at the background sync rate. Plan replication changes outside of periods where DR capability is critically needed.

3. **Disabling public access is account-level only — not per-container.** There is no Azure property to disable public access on a single container while leaving others enabled. The `allowBlobPublicAccess: false` property operates at the account level and affects all containers simultaneously. A single container with a legitimate anonymous-read requirement blocks the entire account from the hardened configuration until that dependency is resolved.

4. **Shared key disable invalidates all existing account-key SAS tokens.** SAS tokens generated using storage account keys become invalid the moment `allowSharedKeyAccess` is set to `false`. There is no grace period. Only user-delegation SAS tokens (derived from Entra OAuth tokens, maximum 7-day lifetime) survive the transition. Long-lived SAS tokens distributed to third-party partners or embedded in configuration files represent the primary breakage risk — inventory these before crossing this gate.

5. **Immutability policy is irreversible once locked.** Time-based retention policies in the locked state can be extended but never shortened. A locked policy cannot be unlocked, modified, or deleted for any container until every blob's retention period expires. Setting the wrong retention period is a permanent cost commitment. Validate retention duration in pre-production with an unlocked policy and obtain legal/compliance sign-off before locking any regulated container.

6. **HNS / SFTP / NFS feature gating is set at account-creation time.** HNS (hierarchical namespace / ADLS Gen2 mode) cannot be enabled or disabled on an existing account — it is set once at creation and is permanent. SFTP requires account-level feature enablement and disables certain standard blob features (e.g., blob index tags, query acceleration). NFS 3.0 requires premium block blob account type and is incompatible with several geo-replication options. ISV brownfield estates often have accounts with these features enabled without the team realising the downstream lock-in — the Step 1 inventory MUST surface SFTP/NFS/HNS status before any replication or auth changes are applied.

## Anti-Patterns

<!-- Four anti-patterns covering the most common brownfield failure modes in S5 ISV estates. -->

Using a single storage account for all tenants in a multi-tenant SaaS estate is the most dangerous isolation failure. One tenant's misconfiguration, encryption key compromise, or data exfiltration incident exposes all other tenants' data because the blast radius is bounded only at the account level. Container-per-tenant with container-scoped Entra RBAC is the minimum acceptable isolation for production SaaS workloads; account-per-tenant with encryption scopes or distinct CMK keys is the recommended baseline for regulated tenants. Path-prefix-per-tenant with no platform-level access control is not an isolation pattern — it is a naming convention and provides no security boundary that Azure can enforce.

Enabling public blob access "temporarily" for a development or integration test scenario without account-level guardrails is the primary cause of production public-blob-access violations. Once workloads begin relying on anonymous read — even unintentionally, through hardcoded URLs propagated to CDN configurations or shared documentation — the dependency becomes invisible and permanent. The correct pattern is to use user-delegation SAS tokens with explicit expiry (maximum 7 days) for all development access scenarios, and to configure the `deny-storage-public-access` policy at the landing zone scope so that even temporary enablement is blocked by platform controls before it can reach production.

Defaulting to GRS replication for all storage accounts without measuring the actual DR requirement pays 2× storage cost for redundancy the workload will never need. LRS provides eleven nines of durability within a single datacenter — sufficient for workloads that tolerate regional outages or whose data can be regenerated. ZRS provides single-region, three-zone durability at lower cost than GRS for workloads needing zone-resilience without cross-region replication. GRS and GZRS are appropriate only when zero-data-loss for cross-regional outages is a documented business requirement with an explicit RPO/RTO target. Each replication choice must be justified, not defaulted to maximum replication as a precaution.

Locking immutability time-based retention policies before validating the retention period in a test environment is an irreversible mistake. The Azure platform enforces locked policies permanently — there is no support ticket, no billing waiver, and no exception process that can shorten a locked retention period. ISV estates that lock 7-year retention on the wrong container pay 7 years of storage cost for data that should have been archived at 1 year. The correct practice: configure retention policies in the unlocked state during the first sprint, validate that the period matches contractual and regulatory requirements, obtain legal and compliance sign-off, then lock. Once locked, the period can only increase.

## Diagnostic Queries

### KQL: Storage accounts with public blob access enabled (Security Baseline Rule #3 violations)

```kql
Resources
| where type == "microsoft.storage/storageaccounts"
| where properties.allowBlobPublicAccess == true
| project name, resourceGroup, location,
          replication = tostring(properties.sku.name),
          accessTier = tostring(properties.accessTier),
          sharedKeyEnabled = tostring(properties.allowSharedKeyAccess)
| order by resourceGroup asc, name asc
```

### KQL: Storage accounts with shared key authentication enabled (Step 7 gate candidates)

```kql
Resources
| where type == "microsoft.storage/storageaccounts"
| where properties.allowSharedKeyAccess != false
| project name, resourceGroup, location,
          publicAccessEnabled = tostring(properties.allowBlobPublicAccess),
          httpsOnly = tostring(properties.supportsHttpsTrafficOnly),
          minimumTlsVersion = tostring(properties.minimumTlsVersion)
| order by resourceGroup asc, name asc
```

Returns accounts where `allowSharedKeyAccess` is `true` or not explicitly set to `false` (null defaults to enabled). Accounts where this property is absent require the same remediation as accounts where it is explicitly `true`.

### KQL: Storage accounts without private endpoints (network isolation gap)

```kql
Resources
| where type == "microsoft.storage/storageaccounts"
| where isnull(properties.privateEndpointConnections)
      or array_length(properties.privateEndpointConnections) == 0
| project name, resourceGroup, location,
          publicNetworkAccess = tostring(properties.publicNetworkAccess),
          networkDefaultAction = tostring(properties.networkAcls.defaultAction)
| order by resourceGroup asc, name asc
```

### KQL: Storage accounts with SFTP, NFS, or HNS features enabled (feature lock-in inventory)

```kql
Resources
| where type == "microsoft.storage/storageaccounts"
| where properties.isSftpEnabled == true
      or properties.isNfsV3Enabled == true
      or properties.isHnsEnabled == true
| project name, resourceGroup, location,
          sftpEnabled = tostring(properties.isSftpEnabled),
          nfsEnabled = tostring(properties.isNfsV3Enabled),
          hnsEnabled = tostring(properties.isHnsEnabled),
          accountKind = tostring(kind)
| order by resourceGroup asc, name asc
```

Run this query in Step 1 of the brownfield playbook to surface all accounts with creation-time feature lock-in before applying any replication or auth changes.

## References

| Resource | Notes |
|----------|-------|
| **[`docs/decisions/data-tier-selection.md`](../../../docs/decisions/data-tier-selection.md)** | **Shared ADR — read first.** Canonical SQL/Cosmos/Storage decision boundary. Defines "Choose Storage when…" semantics, hard-gate boundary inventory, and S5 scenario mapping referenced by this skill's Overview and Brownfield Scenario. |
| [`azure-sql-database`](../azure-sql-database/SKILL.md) | Wave 4 sibling. Relational OLTP persistence for regulated workloads (S3). |
| [`azure-cosmos-db`](../azure-cosmos-db/SKILL.md) | Wave 4 sibling. Globally distributed document store for AI platforms (S2). |
| [`azure-private-link`](../azure-private-link/SKILL.md) | **Hard prereq.** Private endpoint topology for all storage sub-resources (blob/queue/table/file/web). Must be established before brownfield playbook Step 6. |
| [`azure-policy`](../azure-policy/SKILL.md) | **Hard prereq.** `deny-storage-public-access`, `require-tls-12`, `deny-shared-key`, `require-private-endpoint` policy authoring and assignment syntax. |
| [`azure-key-vault`](../azure-key-vault/SKILL.md) | Soft prereq. CMK lifecycle, key rotation, encryption scope key binding per tenant. |
| [`azure-monitor`](../azure-monitor/SKILL.md) | Soft prereq. Diagnostic settings pipeline, blob access pattern analysis, lifecycle audit logging. |
| [`cost-governance`](../cost-governance/SKILL.md) | Soft prereq. Lifecycle cost modeling, replication cost delta analysis, reserved capacity planning. |
| [`azure-rbac`](../azure-rbac/SKILL.md) | Soft prereq. Storage data-plane RBAC role assignments at account/container/blob scope. |
| [`workload-identity-federation`](../workload-identity-federation/SKILL.md) | W1 soft prereq. Managed identity and federated credentials for application-to-storage auth. |
| [Azure Storage redundancy](https://learn.microsoft.com/azure/storage/common/storage-redundancy) | LRS, ZRS, GRS, GZRS replication models, durability targets, and customer-initiated failover procedures. |
| [Blob lifecycle management](https://learn.microsoft.com/azure/storage/blobs/lifecycle-management-overview) | Lifecycle policy rule definitions, tier transition semantics, last-access-time tracking, evaluation scheduling. |
| [Immutable storage for Azure Blob Storage](https://learn.microsoft.com/azure/storage/blobs/immutable-storage-overview) | Time-based retention vs legal holds, locked vs unlocked policies, regulatory compliance (FINRA, SEC 17a-4, CFTC 1.31). |
| [Prevent authorization with Shared Key](https://learn.microsoft.com/azure/storage/common/shared-key-authorization-prevent) | Disable shared key auth, impact on existing SAS tokens, user-delegation SAS migration guidance. |
| [Use private endpoints for Azure Storage](https://learn.microsoft.com/azure/storage/common/storage-private-endpoints) | Sub-resource endpoint types, DNS zone configuration, brownfield migration from service endpoints. |
| [`docs/decisions/compute-tier-selection.md`](../../../docs/decisions/compute-tier-selection.md) | W2 ADR — compute tier decision boundary. Related for AI workloads using Storage for model artifacts and training data. |
| [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md) | W3 ADR — subscription/MG hierarchy decision boundary. Related for per-tenant subscription isolation decisions in large ISV estates. |

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-07-14 | Saul | Initial Wave 4 authoring — multi-tenant blob isolation patterns (account/container/path + encryption scopes), lifecycle management, immutability (FINRA/SEC 17a-4/CFTC 1.31), private endpoint topology, shared-key-to-Entra-RBAC migration, S5 ISV brownfield 8-step playbook (⛔ HARD GATE Steps 5+7, Soft rollback Steps 3/4/6/8), 6 hidden assumptions (incl. HNS/SFTP/NFS feature gating W4 hook), 4 anti-pattern paragraphs, 4 KQL diagnostic queries, shared ADR cross-reference in 4 locations (`data-tier-selection.md`). |
