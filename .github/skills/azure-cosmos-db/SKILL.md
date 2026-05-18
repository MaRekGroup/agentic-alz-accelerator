---
name: azure-cosmos-db
description: "Azure Cosmos DB topology design for globally distributed applications — multi-region active-active writes, consistency level selection, partition key strategy, RU provisioning models, and continuous backup. USE FOR: multi-region write configuration and conflict resolution policies, bounded staleness / session / eventual consistency tuning for AI metadata tiers, partition key design (synthetic keys, hierarchical keys, hot partition detection), RU provisioning decisions (manual vs autoscale vs serverless, database-shared vs container-dedicated), continuous backup with PITR, Entra data-plane RBAC and account-key disable, CMK encryption at rest, private endpoints per region, change feed for event-driven patterns, and brownfield hardening of existing AI platform Cosmos accounts. DO NOT USE FOR: Azure Cache for Redis (in-memory key-value, future wave), Azure AI Search (vector + lexical search, future wave), Synapse/Fabric/Data Factory/Purview (analytics, future wave), relational OLTP (use azure-sql-database), blob/file/object storage (use azure-storage-accounts), cross-cutting identity/network/cost/monitor/key/policy patterns (dedicated skills), SDK managed-identity auth setup (use workload-identity-federation), or the SQL-vs-Cosmos-vs-Storage tier selection decision (see docs/decisions/data-tier-selection.md)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: saul
  version: "1.0"
  category: azure-data-platform
  wave: "4"
---

# azure-cosmos-db

| Field | Value |
|-------|-------|
| **Skill ID** | `azure-cosmos-db` |
| **Domain** | Azure Data Platform — Globally Distributed NoSQL |
| **Hard Prereqs** | `azure-private-link` |
| **Soft Prereqs** | `azure-monitor`, `cost-governance`, `workload-identity-federation` (W1) |
| **Shared ADR** | [`docs/decisions/data-tier-selection.md`](../../../docs/decisions/data-tier-selection.md) |
| **Primary CAF Area** | Security, Management |
| **Brownfield Scenario** | S2 — Multi-Region AI Platform |
| **Wave** | 4 · 2026-05-18 · Saul |

Cosmos DB is the persistence tier for workloads that require globally distributed active-active writes, sub-10ms latency at scale, and a document or key-value data model with partition-key-aligned access patterns. This skill enables the Oracle to prescribe Cosmos DB topology decisions — multi-region write configuration, consistency level selection, partition key strategy, RU provisioning models, and continuous backup — with explicit trade-offs between consistency, latency, and cost for AI platform workloads.

**When to use this skill:** Use when the workload requires multi-region active-active writes, bounded staleness or session consistency for AI/ML metadata tiers, or change feed as a first-class event-driven primitive. Consult `docs/decisions/data-tier-selection.md` before applying this skill to confirm Cosmos is the correct tier for the workload.

## Overview

This skill covers the full operational surface of Azure Cosmos DB: account-level configuration (multi-region writes, consistency levels, automatic failover priority, zone-redundant replicas), container-level design (partition key strategy, indexing policy, RU provisioning model), security hardening (Entra data-plane RBAC, account-key disable, CMK encryption, per-region private endpoints), and operational observability (diagnostic settings, throughput alerts, change feed processor, continuous backup with PITR). All five Cosmos DB APIs — SQL/Core, MongoDB, Cassandra, Gremlin, Table — share the underlying resource model and are in scope; API-specific nuances are noted where they create distinct configuration surfaces. This skill does not cover MongoDB wire-protocol extensions or Cassandra CQL migration patterns in depth — those are workload-specific topics beyond the scope of a landing zone architecture skill.

The tier selection boundary — when to choose Cosmos DB over SQL Database or Storage Accounts — is defined in [`docs/decisions/data-tier-selection.md`](../../../docs/decisions/data-tier-selection.md). **Choose Cosmos when** the workload requires globally distributed active-active writes, a document or key-value model with partition-key-aligned queries, sub-10ms latency at global scale with tunable consistency, change feed for real-time event-driven processing, or an AI/ML metadata or feature store requiring multi-region read/write distribution. This skill goes deep on HOW to configure Cosmos DB within those boundaries — it does not redefine the decision tree. All three W4 data platform skills reference that ADR as the canonical boundary authority.

**Out of Scope:**
- SQL/relational OLTP with joins, foreign keys, and multi-table ACID transactions → `azure-sql-database`
- Blob, file, queue, and table storage for object persistence and lifecycle management → `azure-storage-accounts`
- Tier selection decision (SQL vs Cosmos vs Storage) → `docs/decisions/data-tier-selection.md`
- Cache layer (low-latency in-memory key-value reads) → Azure Cache for Redis (future wave)
- Full-text and vector search with lexical ranking and hybrid retrieval → Azure AI Search (future wave)

## When to Use This Skill

- Designing a Cosmos DB account topology for an AI platform metadata tier (feature store, experiment registry, model catalog)
- Configuring multi-region active-active writes with conflict resolution for geographically distributed write workloads
- Selecting a consistency level (Strong vs Bounded Staleness vs Session) with explicit latency/cost trade-off analysis
- Designing or evaluating a partition key strategy — including synthetic keys, hierarchical keys, and hot-partition remediation
- Choosing between manual provisioned, autoscale, and serverless throughput for a container
- Deciding between database-level shared throughput and container-level dedicated throughput for a production container group
- Enabling continuous backup (PITR) and planning the restore-to-new-account reconfiguration workflow
- Hardening a brownfield Cosmos account: migrating from account-key auth to Entra RBAC, disabling public network access, enabling CMK
- Configuring per-region private endpoints after `azure-private-link` has established the baseline endpoint pattern
- Designing change feed processor consumers for event-driven downstream pipelines
- Evaluating reserved capacity (1-year / 3-year RU commitments) against a stable provisioned throughput baseline
- Sizing continuous backup storage cost impact against account write rate and retention window requirements

## CAF Design Area Mapping

| CAF Design Area | Coverage | Primary |
|-----------------|----------|---------|
| Security | Entra RBAC (data-plane), CMK encryption at rest via Azure Key Vault, disable public network access, disable account-key-based authentication to eliminate shared-secret exposure | ✅ |
| Identity & Access | Entra data-plane RBAC roles (`Cosmos DB Built-in Data Reader`, `Cosmos DB Built-in Data Contributor`), workload identity for SDK auth via managed identity, disable account keys after all SDK connections migrate to Entra tokens | |
| Management | Diagnostic settings to Log Analytics (data-plane requests, RU consumption, throttle events), continuous backup policy (PITR window), Azure Monitor metrics for `NormalizedRUConsumption` and `TotalRequestUnits`, throughput alerts before throttling impacts consumers | ✅ |
| Network Topology | Private endpoints per configured region (each write region requires its own private endpoint in the corresponding VNet), VNet integration, disable public network access in all production accounts | |

## WAF Pillar Coverage

| WAF Pillar | Coverage | Primary |
|------------|----------|---------|
| Reliability | Multi-region writes with automatic failover and configurable priority ordering, zone-redundant replicas per region, continuous backup with 1-second PITR granularity, manual failover trigger for planned regional maintenance | ✅ |
| Performance Efficiency | Partition key strategy (synthetic keys, hierarchical keys, hot-partition detection), RU provisioning model selection (manual vs autoscale vs serverless), indexing policy tuning (include/exclude paths, composite indexes for ORDER BY), materialized views via change feed for read-optimized projections | ✅ |
| Cost Optimization | Autoscale 10% minimum billing floor analysis, serverless for dev/test with zero minimum, reserved capacity for stable provisioned baselines, multi-region write cost multiplier (2× RU per additional write region), database-shared vs container-dedicated throughput cost trade-off | |
| Security | Disable key-based auth permanently, Entra data-plane RBAC for all SDK and tooling connections, CMK via Key Vault with customer-controlled key rotation, network isolation via per-region private endpoints, always-encrypted client-side option for field-level attribute protection | |
| Operational Excellence | Change feed enables event-driven downstream processing without polling, continuous backup PITR for second-granularity recovery points, throughput alerts on `NormalizedRUConsumption` per partition detect hot-partition pressure before throttling impacts SLAs, diagnostic settings expose query patterns and latency distributions for ongoing tuning | |

## Architecture Patterns

### 1. Multi-Region Active-Active Writes

Multi-region write (previously "multi-master") enables simultaneous write operations to Cosmos DB from any configured region. Each region maintains a full replica; writes are accepted locally and replicated asynchronously using the account-level consistency model. The failover priority list determines which region becomes the single write region if multi-write mode must fall back during an outage event.

Configure multi-region writes via `enableMultipleWriteLocations: true` at account creation or update. Select a conflict resolution policy: **Last-Write-Wins (LWW)** uses a configurable timestamp property (default `_ts`, overridable to any numeric field) — the write with the highest value wins, the losing write is persisted to the conflicts feed for audit. **Custom conflict resolution** routes conflicting writes to a stored procedure for application-defined merge logic, appropriate for commutative workloads such as counters and CRDT-like accumulators. Set `failoverPriority` per region to control automatic failover ordering; region with priority `0` is the primary for single-write-mode fallback. When adding regions to an existing multi-write account, an initial replication window proportional to account data volume precedes the new region accepting writes.

**Gotchas:** Multi-region writes multiply write RU consumption by the number of configured write regions — a 3-region active-active configuration costs 3× the write RUs of a single-region deployment. LWW conflict resolution silently discards the lower-timestamp write; workloads with concurrent writes to the same item ID must audit the conflicts feed regularly, as dropped writes produce no error signal to the writing application. Removing a write region is online but requires a manual failover priority reorder to avoid leaving the removed region at priority 0.

### 2. Bounded Staleness for AI Metadata

Cosmos DB offers five consistency levels — Strong, Bounded Staleness, Session, Consistent Prefix, Eventual — representing a spectrum from highest consistency/highest cost/highest latency to lowest consistency/lowest cost/lowest latency. The choice is set at the account level; individual requests may relax but never strengthen beyond the account level.

For AI platform metadata tiers — feature stores, experiment registries, model version indexes, prompt-cache stores — **Bounded Staleness** is typically optimal. It guarantees reads lag writes by at most `K` operations or `T` seconds (configurable via `maxStalenessPrefix` and `maxIntervalInSeconds`), providing predictable freshness without the cross-region round-trip cost of Strong consistency. A 5–15 second window suits most ML feature pipelines — feature writes can tolerate seconds of propagation lag on read, but the window must be shorter than the pipeline's write interval to prevent downstream consumers from reading features that violate freshness SLAs. **Session consistency** — read-your-own-writes within a single client session — is sufficient for user-scoped AI workloads such as chat history stores or per-user recommendation caches. **Strong consistency** is available only within a single region or for multi-region reads that accept full cross-region round-trip latency, rarely justified for AI metadata where a bounded staleness window satisfies freshness requirements at significantly lower cost.

**Gotchas:** A consistency level change is global and immediate — see Hidden Assumptions. Bounded Staleness costs approximately 2× the read RU rate of Eventual consistency because the read quorum must confirm the staleness window is satisfied before returning.

### 3. Partition Key Strategy for Scale

The partition key is the single most consequential design decision in a Cosmos DB schema. It determines data distribution across physical partitions, query routing (single-partition direct vs cross-partition fan-out), and the throughput ceiling per container. A logical partition is bounded at 20GB; a physical partition is bounded at approximately 50GB and 10,000 RU/s. When a single partition key value exceeds 20GB of data, the container approaches an unserviceable state requiring full container recreation and data migration.

**Synthetic partition keys** combine multiple attribute values into a single string field (e.g., `"tenantId|featureGroup|modelVersion"`) to distribute writes across more partitions when no single natural attribute provides sufficient cardinality. **Hierarchical partition keys** (Cosmos DB SQL API, up to 3 levels) allow prefix-based routing — a key defined as `(tenantId, userId, sessionId)` lets queries filtered on `tenantId` alone route to a subset of physical partitions rather than performing a full cross-partition fan-out. **Hot partition detection** requires monitoring `NormalizedRUConsumption` per partition key range in Azure Monitor; a hot partition appears as a single range consistently near 100% while others are near idle. The only remediation is container recreation — there is no online re-partitioning path.

**Gotchas:** The partition key path is set at container creation and is immutable by any operation. A wrong choice requires creating a new container, migrating data using the change feed processor or bulk executor library, reestablishing RBAC assignments and private endpoints, and switching all application connection strings. For S2 AI metadata workloads, avoid timestamp-based partition keys — they create a hot "now" partition that concentrates all writes into a single range as the write volume scales.

### 4. RU Provisioning — Manual vs Autoscale vs Serverless vs Database-Shared vs Container-Dedicated

RU provisioning has two orthogonal dimensions: **throughput mode** (how RUs scale) and **throughput scope** (what containers share a pool). Throughput mode can be changed on an existing container; throughput scope cannot — changing scope requires container recreation and data migration.

**Throughput mode options:** Manual provisioned delivers a fixed RU/s allocation with immediate throttling (`429`) if demand exceeds the ceiling — predictable cost for stable workloads. Autoscale delivers elastic RU/s from 10% to 100% of the configured maximum, billed at the highest RU/s consumed each one-hour window — the **10% minimum billing floor** means `maxThroughput: 10000` incurs billing for at least 1,000 RU/s every hour regardless of traffic, making autoscale more expensive than manual for consistently idle containers. Serverless eliminates the minimum floor entirely (per-operation billing, no idle cost) but is limited to a single write region and a maximum throughput ceiling — appropriate only for dev/test environments and low-traffic containers with no active-active requirements.

**Throughput scope options:** Database-level shared throughput allocates a RU pool shared across all containers in the database (soft maximum 25 containers), cheaper per container but introducing noisy-neighbor risk — a single high-traffic container can consume the entire pool and throttle all others in the database. Container-level dedicated throughput gives each container its own isolated RU/s allocation, more expensive but completely predictable and required for containers with production SLAs or distinct workload profiles.

**S2 AI metadata recommendation:** Pair container-dedicated throughput on the feature-store container (high write volume during batch training, latency-sensitive inference reads) with database-shared throughput on lower-traffic metadata containers (experiment registry, model catalog, configuration store). Use autoscale on the feature-store container if writes have predictable training-job bursts; use manual provisioned for flat-traffic containers to avoid the autoscale 10% minimum floor. Throughput scope is set at container creation and cannot be changed — get this right before the container accumulates production data.

### 5. Continuous Backup with PITR

Cosmos DB supports **periodic backup** (legacy default: snapshots every 1–24 hours, retained 7–30 days, geo-redundant storage) and **continuous backup** (recommended: every mutation retained for a 7-day or 30-day window, 1-second PITR granularity). Continuous backup eliminates the backup-window gap where changes occurring between periodic snapshot intervals are unrecoverable. Migration from periodic to continuous is a one-way online operation that cannot be reversed — once enabled, the account cannot revert to periodic mode.

Initiate PITR restore via Portal, CLI (`az cosmosdb restore`), or ARM API by specifying `restoreTimestampInUtc` and a new target account name. The restore provisions a **new Cosmos DB account** containing all containers, stored procedures, user-defined functions, and throughput configuration as they existed at the specified timestamp — the source account remains fully operational during restore. Post-restore reconfiguration is substantial and must be planned before restore is needed: private endpoints must be recreated (the restored account has a new resource ID), Entra RBAC role assignments must be re-applied (not automatically transferred), CMK Key Vault access policies must be explicitly re-granted, and all application connection strings must be updated to the new account endpoint URI before traffic can be redirected.

**Gotchas:** PITR restore always creates a new account — downstream configuration reconfiguration is mandatory before the restored account is production-ready. Continuous backup storage is billed at the standard Cosmos DB storage rate for the accumulated change-log volume, growing proportionally with account write rate and retention window length.

## Diagnostic Queries

### Resource Graph: Cosmos accounts without continuous backup

```kusto
Resources
| where type == "microsoft.documentdb/databaseaccounts"
| extend backupType = properties.backupPolicy.type
| where backupType != "Continuous"
| project name, resourceGroup, subscriptionId, backupType,
          locations = properties.locations
| order by name asc
```

Returns Cosmos accounts still on periodic backup mode — the primary PITR coverage gap finding in brownfield S2 estates.

### Resource Graph: Cosmos accounts with public network access or key auth still active

```kusto
Resources
| where type == "microsoft.documentdb/databaseaccounts"
| extend publicAccess = properties.publicNetworkAccess
| extend keyAuthDisabled = properties.disableLocalAuth
| where publicAccess =~ "Enabled" or keyAuthDisabled != true
| project name, resourceGroup, subscriptionId, publicAccess, keyAuthDisabled
| order by name asc
```

Returns accounts where public network access is not disabled or account-key authentication has not been disabled — the two pre-conditions required before Steps 7 and 8 in the brownfield playbook.

### Resource Graph: Cosmos accounts in single-write-region mode (no multi-region writes)

```kusto
Resources
| where type == "microsoft.documentdb/databaseaccounts"
| extend multiWrite = properties.enableMultipleWriteLocations
| extend locationCount = array_length(properties.locations)
| where multiWrite != true and locationCount > 1
| project name, resourceGroup, subscriptionId, multiWrite, locationCount,
          locations = properties.locations
| order by locationCount desc
```

Returns accounts with multiple regions configured but multi-region writes not enabled — accounts that have geo-redundant replicas for read scale or DR but have not yet enabled active-active write capability. Useful for identifying brownfield accounts in Step 2 where the workload access pattern justifies upgrading to multi-region writes.

### Resource Graph: Cosmos containers by throughput mode (identify autoscale with inflated max)

```kusto
Resources
| where type == "microsoft.documentdb/databaseaccounts/sqldatabases/containers"
| extend throughput = properties.resource.throughput
| extend autoscaleMax = properties.resource.autoscaleSettings.maxThroughput
| extend dbAccount = split(id, "/")[8]
| project name, resourceGroup, dbAccount, throughput, autoscaleMax,
          subscriptionId
| order by autoscaleMax desc nulls last
```

Returns SQL API containers with their throughput configuration. Containers with large `autoscaleMax` values and low actual throughput are paying the 10% autoscale floor unnecessarily — the primary cost optimization finding in Step 6 of the brownfield playbook.

## Boundaries — DO NOT USE FOR

| Out-of-Scope | Use Instead |
|--------------|-------------|
| Azure Cache for Redis (in-memory key-value cache) | Future-wave candidate; explicitly out of W4 scope |
| Azure AI Search (vector + lexical search service for RAG) | Future-wave candidate; explicitly out of W4 scope |
| Synapse, Fabric, Data Factory, Purview (analytics platform services) | Future analytics-wave skills (explicitly out of W4) |
| Relational / transactional OLTP (joins, foreign keys, multi-table ACID) | `azure-sql-database` |
| Blob/object/file durability, lifecycle tier management, and immutability | `azure-storage-accounts` |
| Cross-cutting identity, network, cost, monitoring, key, and policy patterns | `azure-rbac`, `azure-private-link`, `cost-governance`, `azure-monitor`, `azure-key-vault`, `azure-policy` |
| Application-to-Cosmos managed-identity / SDK auth credential design | `workload-identity-federation` (W1) |
| When to pick SQL vs Cosmos vs Storage (tier selection decision boundary) | `docs/decisions/data-tier-selection.md` |

## Security Baseline Reinforcement

Cosmos DB intersects three of the six non-negotiable Security Baseline rules enforced by this accelerator.

| Rule | Cosmos DB Enforcement |
|------|-----------------------|
| **Rule 4 – Managed Identity preferred** | All SDK connections must use managed identity or workload-federated identity; account keys must be disabled after migration. Assign `Cosmos DB Built-in Data Contributor` to managed identity before executing Step 7 HARD GATE. |
| **Rule 5 – Azure AD-only authentication** | `disableLocalAuth: true` at account level disables account-key and resource-token authentication, forcing all data-plane access through Entra RBAC. This is the Step 7 HARD GATE and is irrevocable. |
| **Rule 6 – Public network disabled (prod)** | `publicNetworkAccess: Disabled` combined with per-region private endpoints enforces network isolation. Requires private endpoints provisioned in every consumer VNet before disabling public access (Step 8 Policy). |

## Brownfield Scenario (Scenario S2: Multi-Region AI Platform)

This skill sequences after `azure-private-link` (private endpoints per region) and benefits from `workload-identity-federation` (W1) for SDK auth via managed identity, enabling the Oracle to prescribe Cosmos tuning and security hardening for existing AI platform metadata tiers. Use this brownfield playbook in conjunction with the boundary semantics from `docs/decisions/data-tier-selection.md`.

Multi-region AI platforms accumulate Cosmos accounts organically as they scale: a metadata store provisioned during an early sprint, a feature vector index added for a model retraining pipeline, a chat history container bolted on for a conversational AI layer. Typical brownfield findings in S2 estates: account keys still in use across SDK connections (no Entra RBAC migration), single-region write configuration despite cross-region inference workloads that require low-latency writes from multiple geographies, autoscale max set too high during load testing and never reduced (paying the 10% floor on idle containers for months), partition keys chosen for development convenience rather than access-pattern alignment (creating hot partitions at production scale), no continuous backup configured (periodic backup with 24-hour intervals leaves large unrecoverable windows), and database-shared throughput applied uniformly to all containers including latency-sensitive feature store containers that require isolated throughput. The playbook below sequences remediation from the least-disruptive observability steps through the irrevocable hard-gate security changes, with rollback types specified for each step to support change management approval.

| Step | Action | Rollback Type |
|------|--------|---------------|
| 1 | Inventory existing Cosmos accounts (Resource Graph: consistency level, regions, throughput mode per container, backup policy, network access, auth mode) | Read-only |
| 2 | Assess: partition key optimal for current access patterns? `NormalizedRUConsumption` per partition? Multi-region writes enabled? Key-based auth active? Database-shared vs container-dedicated still appropriate per container's workload profile? | Read-only |
| 3 | Enable diagnostic settings + RU consumption alerts (`NormalizedRUConsumption` > 80%) to central Log Analytics workspace | Soft rollback (disable diagnostic settings and alert rules; no data loss) |
| 4 | ⛔ **HARD GATE** — Change consistency level (applies immediately to ALL active client connections across ALL regions; no per-connection grace period; a staleness window change alters data freshness guarantees for every downstream AI consumer simultaneously) | Time-windowed — change is instantaneous and global; reverting requires a second change operation causing a second disruption event; no staged rollout available |
| 5 | Add secondary write regions (multi-region active-active); configure conflict resolution policy (LWW or custom stored procedure) | Soft rollback (remove secondary write regions; account reverts to single-write mode; no data loss) |
| 6 | Migrate throughput model: reduce autoscale max to production-peak measurements; reconsider database-shared vs container-dedicated allocation per Step 2 workload assessment | Soft rollback (revert to prior manual provisioned values; transient throttling possible during RU reduction) |
| 7 | ⛔ **HARD GATE** — Disable key-based authentication (ALL SDK connections, CI/CD pipelines, monitoring agents, and migration tools MUST use Entra RBAC tokens before this step; account keys become permanently non-functional with no Azure-provided re-enable path) | Irrevocable — Azure provides no re-enable path for account-key auth after the account-level disable is applied |
| 8 | Enforce Azure Policy: `deny-cosmos-public-access`, `require-continuous-backup`, `require-entra-only-cosmos` | Soft rollback (remove policy assignment; no deployed resources modified) |

**Pre-HARD-GATE Verification Checklist:**

Before crossing **Step 4** (consistency level change): (a) load-test every downstream ML consumer against the target staleness window in a non-production environment; (b) confirm no application code assumes Strong consistency semantics — relaxing to Bounded Staleness exposes stale reads in applications that write to one region and immediately read from a different region without propagating session tokens; (c) confirm `maxIntervalInSeconds` is shorter than the feature pipeline's write interval so consumers cannot read features that violate freshness SLAs.

Before crossing **Step 7** (disable key-based auth): (a) every application, pipeline, monitoring agent, and migration tool connection must be validated as using Entra RBAC token-based auth in a non-production Cosmos account of the same API type; (b) the `Microsoft.DocumentDB/databaseAccounts/listKeys/action` permission must be revoked from all service principals that previously used key-based access; (c) validate the disable change end-to-end before the production gate is crossed, because key-disable behavior has API-specific nuances for non-SQL-API accounts.

## Prerequisites and Caveats

Before applying this skill to a brownfield S2 estate, verify the following. Unmet prerequisites are the primary cause of hard-gate failures that appear architecturally sound but break in production execution.

| Prerequisite | Impact | Guidance |
|--------------|--------|----------|
| `azure-private-link` complete | Without per-region private endpoints, disabling public network access at Step 8 causes immediate connectivity loss for all SDK clients | Provision private endpoints in every VNet that hosts SDK consumers before executing Step 8 |
| `workload-identity-federation` (W1) configured | Without Entra RBAC assignments on Cosmos data-plane, disabling key-based auth at Step 7 blocks all application connections | Assign `Cosmos DB Built-in Data Contributor` (or Reader) to every managed identity before Step 7 |
| All SDK connections validated on Entra tokens | Key-disable is irrevocable; any SDK connection still using connection strings with account keys breaks immediately | Run a shadow auth validation in non-production for every distinct application, pipeline, and tool that connects to the account |
| Consistency level change tested in pre-production | No staged rollout path exists; the change is global and immediate | Run ML consumer regression tests against the target staleness window before scheduling Step 4 for production |
| Change feed processor consumers identified | If change feed consumers exist, any consistency change or multi-region-write addition may alter the change feed event sequencing contract | Audit all change feed consumers for sequencing assumptions before Step 4 or Step 5 |
| Reserved capacity commitment evaluated | 1-year or 3-year RU reservations reduce cost 20–65% for stable provisioned baselines; commitment applies per-region | Model reserved capacity against 90-day provisioned RU baseline before committing; multi-region write multiplier changes the per-region reservation requirement |

## Hidden Assumptions

1. **Partition key is immutable** — Once a Cosmos DB container is created, the partition key path cannot be changed by any operation: portal, CLI, SDK, REST API, or Azure support request. A wrong partition key choice requires creating a new container from scratch, migrating all data using the change feed processor or bulk executor library, reestablishing Entra RBAC assignments and private endpoints, and switching all application connection strings to the new container. Migration windows for large containers span days; there is no online re-partitioning path.

2. **Multi-region write cost is 2× per additional write region** — Enabling multi-region writes multiplies write RU consumption by the number of configured write regions. A 3-region active-active deployment consumes 3× the write RUs of a single-region deployment; a 4-region deployment consumes 4×. For AI platform metadata tiers with high feature ingestion rates, the monthly cost delta between single-write and 3-region active-active frequently exceeds the compute cost of the AI training infrastructure — a multiplier consistently underestimated at architecture time because it applies to the provisioned RU/s ceiling, not merely to measured consumed RUs.

3. **Consistency level change is global and immediate** — Changing the account-level consistency level applies instantly to all active client connections across all regions, with no per-connection grace period, staged rollout, or notification mechanism. Applications relying on a specific consistency contract — particularly read-your-own-writes guarantees from Strong or Session consistency — will observe changed behavior immediately following the account-level update with no mechanism to preserve the prior consistency level for in-flight requests or active sessions.

4. **Continuous backup restore creates a NEW account** — PITR does not restore data in-place to the existing Cosmos DB account. The restore provisions a brand-new account with the restored data; the source account remains fully operational during restore. All downstream consumers must be reconfigured: private endpoint connections (new resource ID), Entra RBAC role assignments (not transferred automatically), CMK Key Vault access policies (must be explicitly re-granted), and application connection strings (new account endpoint URI) before traffic can be redirected to the restored account.

5. **Autoscale minimum is 10% of max** — Autoscale RU/s cannot scale below 10% of the configured `maxThroughput` under any condition. A container with `maxThroughput: 10000` is billed for at least 1,000 RU/s every hour regardless of whether any requests were processed. For containers with sparse or batch-only traffic — configuration stores, audit log containers — manual provisioned at a low fixed value or serverless produces significantly lower monthly cost than autoscale, despite autoscale's operational convenience for variable-traffic workloads.

## Anti-Patterns

Using Cosmos DB for relational or transactional OLTP workloads to avoid managing SQL infrastructure is the most expensive data-tier mistake in brownfield AI platform estates. Cosmos DB provides no foreign key constraints, no multi-item ACID transactions spanning multiple logical partitions, and no native join capability across partition boundaries. Workloads that require these semantics pay 3–10× the cost of equivalent SQL Database configurations in RU consumption, because cross-partition queries fan out to every physical partition and are charged proportional to data scanned rather than rows returned. The correct approach is to evaluate the decision criteria in `docs/decisions/data-tier-selection.md` at architecture time and choose SQL for workloads with relational semantics — before the partition key is set and the migration cost becomes significant.

Choosing a partition key based on cardinality analysis alone — without measuring actual query patterns against candidate keys under production-representative load — produces hot partitions that throttle the entire container regardless of provisioned RUs. High-cardinality attributes such as GUIDs distribute data evenly but route every query through a full cross-partition fan-out if queries filter on a different dimension than the partition key. The correct approach pairs cardinality analysis with query pattern analysis: the partition key must both distribute data evenly AND align with the most frequent query filter so that the majority of reads and writes resolve to a single logical partition without cross-partition overhead.

Enabling multi-region writes by default as a reliability precaution — without explicitly modeling the write RU cost multiplier against the workload's actual write rate — produces budget overruns that compound as additional write regions are added. For AI platform metadata tiers with high feature ingestion rates, the monthly cost delta between single-write and 3-region active-active frequently exceeds the compute cost of the AI training infrastructure. Multi-region writes must be justified by explicit latency, availability, or regulatory requirements — not provisioned speculatively for workloads that never simultaneously write from more than one geography.

Using database-level shared throughput as the default allocation for all containers — without measuring per-container workload isolation requirements — introduces noisy-neighbor throttling that is operationally difficult to diagnose. A single high-traffic container in a shared-throughput database can consume the entire RU pool during a burst, throttling all other containers simultaneously with `429` responses that are indistinguishable from account-level capacity exhaustion in application logs. The root cause requires correlating `NormalizedRUConsumption` per partition key range against the shared pool — a query most teams do not have pre-built at incident time. The correct approach uses container-dedicated throughput for any container with a distinct production SLA or latency requirement, reserving database-shared throughput for groups of low-traffic containers with similar, non-competing access profiles.

## References

| Topic | Source |
|-------|--------|
| Tier selection decision tree (SQL vs Cosmos vs Storage) | [`docs/decisions/data-tier-selection.md`](../../../docs/decisions/data-tier-selection.md) (this repo, W4 shared ADR) |
| Sibling W4 skill — relational persistence | [`.github/skills/azure-sql-database/SKILL.md`](../azure-sql-database/SKILL.md) (this repo) |
| Sibling W4 skill — blob/object/file storage | [`.github/skills/azure-storage-accounts/SKILL.md`](../azure-storage-accounts/SKILL.md) (this repo) |
| Prereq skill — private endpoint patterns per region | [`.github/skills/azure-private-link/SKILL.md`](../azure-private-link/SKILL.md) (this repo) |
| Soft prereq — RU consumption monitoring and alerting | [`.github/skills/azure-monitor/SKILL.md`](../azure-monitor/SKILL.md) (this repo) |
| Soft prereq — multi-region write cost modeling | [`.github/skills/cost-governance/SKILL.md`](../cost-governance/SKILL.md) (this repo) |
| Soft prereq — managed identity SDK auth | [`.github/skills/workload-identity-federation/SKILL.md`](../workload-identity-federation/SKILL.md) (this repo, W1) |
| Cosmos DB consistency levels and trade-offs | https://learn.microsoft.com/azure/cosmos-db/consistency-levels |
| Multi-region writes configuration and conflict resolution | https://learn.microsoft.com/azure/cosmos-db/how-to-multi-master |
| Partition key design best practices | https://learn.microsoft.com/azure/cosmos-db/partitioning-overview |
| Hierarchical partition keys | https://learn.microsoft.com/azure/cosmos-db/hierarchical-partition-keys |
| Continuous backup and point-in-time restore | https://learn.microsoft.com/azure/cosmos-db/continuous-backup-restore-introduction |
| Autoscale throughput — billing model | https://learn.microsoft.com/azure/cosmos-db/provision-throughput-autoscale |
| Disable key-based authentication | https://learn.microsoft.com/azure/cosmos-db/how-to-setup-rbac#disable-local-auth |
| Related ADR — compute tier selection (W2) | [`docs/decisions/compute-tier-selection.md`](../../../docs/decisions/compute-tier-selection.md) (this repo) |
| Related ADR — billing tenant hierarchy (W3) | [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md) (this repo) |

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-18 | Saul | Initial Wave 4 authoring — Cosmos DB multi-region writes, consistency levels, partition key strategy, RU provisioning (manual/autoscale/serverless/database-shared/container-dedicated W4 hook expanded), continuous backup PITR, 2 Resource Graph diagnostic queries, S2 Multi-Region AI Platform brownfield playbook (8 steps, ⛔ HARD GATE at Steps 4+7, soft rollback on 3/5/6/8), 5 hidden assumptions, 4 anti-patterns (paragraph form), 9/9 W3 compliance checklist pass |
