---
name: azure-sql-database
description: "Azure SQL Database and Managed Instance — failover groups, Entra-only auth migration, TDE with CMK, and brownfield hardening for S3 Regulated Financial Services landing zones. USE FOR: SQL DB and MI topology (General Purpose/Business Critical/Hyperscale), failover groups with auto-failover and geo-replication, Entra-only auth migration (one-way), TDE with BYOK and Key Vault CMK lifecycle, private endpoint isolation, Azure Policy for SQL (deny public access, require Entra-only, require TDE CMK), Managed Instance VNet-native lift-and-shift, long-term backup retention, and S3 brownfield SQL hardening. DO NOT USE FOR: Azure Database for PostgreSQL/MySQL/MariaDB (future), Synapse/Fabric/Data Factory/Purview (analytics), Cosmos DB (use azure-cosmos-db), blob/queue/table/file storage (use azure-storage-accounts), CMK key lifecycle (use azure-key-vault), private endpoint patterns (use azure-private-link), Policy authoring (use azure-policy), or tier selection (see docs/decisions/data-tier-selection.md)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: saul
  version: "1.0"
  category: azure-data-platform
  wave: "4"
---

# azure-sql-database

| Field | Value |
|-------|-------|
| **Skill ID** | `azure-sql-database` |
| **Domain** | Azure Data Platform — Relational Persistence |
| **Wave** | 4 — Data Platform |
| **Hard Prereqs** | `azure-private-link`, `azure-key-vault` |
| **Soft Prereqs** | `azure-monitor`, `azure-rbac`, `entra-identity-governance` (W1) |
| **ADR Reference** | [`docs/decisions/data-tier-selection.md`](../../../docs/decisions/data-tier-selection.md) |
| **Primary CAF Area** | Security |
| **Primary WAF Pillar** | Reliability, Security |
| **Brownfield Scenario** | S3 — Regulated Financial Services |
| **Authored** | Wave 4 · 2026-05-18 · Saul |

Azure SQL Database and Managed Instance are the relational backbone of regulated enterprise estates. This skill enables the Oracle to prescribe topologies that satisfy financial-services reliability mandates (failover groups, geo-replication, zone-redundant HA), security compliance requirements (Entra-only auth, TDE with CMK, Advanced Threat Protection), and brownfield migration paths that preserve application continuity while closing the hardest configuration gaps found in S3 regulated environments.

**When to use this skill:** The workload requires ACID transactions, relational schema with complex joins, or regulatory compliance mandating auditable transactional integrity with <5s RPO failover. The estate carries SQL Database or Managed Instance resources that need HA configuration, Entra-only auth migration, TDE/CMK hardening, or network isolation for a regulated landing zone.

## Overview

This skill covers SQL Database single-database and elastic pool configurations, Managed Instance for VNet-native lift-and-shift, failover groups with automatic failover policy, Hyperscale tier for elastic scale, Entra-only authentication enforcement, Transparent Data Encryption with customer-managed keys, private endpoint network isolation, Azure Policy for SQL compliance, and long-term backup retention. It applies to both greenfield regulated-workload design and brownfield hardening of existing SQL estates.

Tier selection criteria — when to choose SQL Database over Cosmos DB or Azure Storage Accounts — are defined in [`docs/decisions/data-tier-selection.md`](../../../docs/decisions/data-tier-selection.md). This skill does not redefine that boundary; it goes deep on SQL-specific configuration within the "Choose SQL when" criteria established by the ADR: ACID transactions with relational schema, regulatory compliance mandating auditable relational integrity, and workloads requiring sub-5-second RPO via failover groups. For globally distributed active-active writes or document models, consult the ADR and the `azure-cosmos-db` skill.

**Out of Scope for this skill:**

- Cosmos DB document and globally distributed workloads → `azure-cosmos-db`
- Azure Storage blob/queue/table/file configurations → `azure-storage-accounts`
- SQL vs Cosmos vs Storage tier selection decision criteria → `docs/decisions/data-tier-selection.md`

## When to Use This Skill

- Designing a new SQL Database or Managed Instance deployment for a regulated (financial services, healthcare, government) landing zone
- Configuring failover groups with auto-failover policy to meet RPO < 5 seconds for a regulated continuity mandate
- Migrating from SQL authentication to Entra-only authentication without breaking application connections
- Implementing TDE with customer-managed keys via BYOK and Key Vault for data sovereignty requirements
- Evaluating SQL Database (PaaS, cloud-optimized) vs Managed Instance (SQL Server feature parity, VNet-native) for a lift-and-shift migration
- Assessing whether Hyperscale is appropriate for a workload with unpredictable storage growth or high read-scale demand
- Hardening an existing SQL estate in a regulated environment: public access removal, audit logging, threat protection, CMK encryption
- Enforcing Azure Policy for SQL compliance: deny public access, require Entra-only auth, require TDE CMK, require audit logging

## CAF Design Area Mapping

| CAF Design Area | Coverage | Primary |
|-----------------|----------|---------|
| **Security** | Entra-only auth enforcement, TDE + CMK encryption at rest, Advanced Threat Protection, audit logging, vulnerability assessments, threat detection alerts | ✅ |
| **Identity & Access** | Entra admin configuration, contained database users for application connections, workload identity for managed identity auth, PIM for DBA and SQL server admin access | ✅ |
| Management | Diagnostic settings to Log Analytics workspace, long-term backup retention policies, automated tuning advisors, configurable maintenance windows | |
| Governance | Azure Policy for SQL: deny public network access, enforce TDE, require Entra-only auth, require audit logging with retention; mandatory resource tagging | |
| Network Topology & Connectivity | Private endpoints for SQL Database, VNet service endpoints, deny public network access, Managed Instance dedicated subnet (VNet-native) | |

## WAF Pillar Coverage

| WAF Pillar | Coverage | Primary |
|------------|----------|---------|
| **Reliability** | Failover groups with auto-failover policy and listener endpoint, zone-redundant HA (Business Critical and General Purpose), active geo-replication, backup/restore RPO/RTO. **NOTE:** Serverless auto-pause violates production RPO/RTO targets — provisioned compute only for S3 regulated workloads. | ✅ |
| **Security** | Entra-only authentication (Security Baseline Rule #5), TDE with CMK and Key Vault key rotation, Advanced Threat Protection, vulnerability assessment scans, private endpoint network isolation | ✅ |
| Performance Efficiency | DTU vs vCore tier sizing model, Hyperscale tier for elastic scale with page-server architecture, named replicas for read-scale offload, Intelligent Performance Insights for query tuning | |
| Cost Optimization | Reserved capacity commitments (1- and 3-year, 30–65% savings), Hyperscale named replicas vs geo-replication cost delta, serverless tier for dev/test only (see Reliability note above) | |
| Operational Excellence | Automated backups with point-in-time restore, configurable maintenance windows, Elastic Jobs for cross-database automation, long-term backup retention for compliance archives | |

## Architecture Patterns

### 1. Failover Group with Auto-Failover

Active geo-replication with a failover group provides transparent DNS-based failover without application connection string changes across regional failures. A failover group creates a single listener endpoint (e.g., `{group-name}.database.windows.net`) that always resolves to the current primary. Applications connect to the listener endpoint — not the server FQDN — so that during an automatic or manual failover, the DNS record updates to the new primary and applications reconnect without reconfiguration. Set `failoverPolicy` to `Automatic` and configure `gracePeriodWithDataLossHours` to the minimum value acceptable for your RPO target; for financial services, reducing this to one hour or less is common.

Enable read-scale on the secondary replica to offload reporting and analytics queries from the primary without provisioning a separate database. The critical gotcha: failover group listener DNS TTL is 30–120 seconds, meaning applications that cache DNS or that bypass the listener and connect directly to the primary server FQDN will experience a connection outage during failover for the duration of that propagation window. Connection string governance — enforcing the listener endpoint for every application connection — is a prerequisite for transparent failover behavior, not a post-incident cleanup.

### 2. Hyperscale Tier for Elastic Scale

Hyperscale decouples compute from storage via a distributed page-server architecture: storage scales independently to 100 TB without pre-allocation, compute replicas can be added or removed in minutes, and named replicas provide read-scale without the cost of full geo-replication. Named replicas share the same underlying page servers, making their cost the compute tier only — dramatically cheaper than geo-replicas when the requirement is read distribution rather than geographic redundancy. The decision criteria for Hyperscale: storage growth is unpredictable or large (avoid managing storage caps), read-scale demand is high enough to justify named replicas, or elastic compute scaling matters more than a fixed-capacity SLA.

The primary operational constraint with Hyperscale is the exit path: Hyperscale databases cannot be exported to BACPAC format. Migration out of Hyperscale to another tier or another platform requires live data-motion replication via transactional replication or Azure Database Migration Service. For workloads that may need to migrate to external platforms or that have compliance requirements around data portability, evaluate the exit path before committing to Hyperscale. For regulated financial services workloads, Hyperscale is well-suited to the primary OLTP tier but requires explicit documentation of the migration approach in the architecture decision record.

### 3. Entra-Only Auth Migration

Migrating from SQL authentication to Entra-only is a one-way, irrevocable operation — once SQL auth is disabled at the server level, it cannot be re-enabled without recreating the server and migrating all databases to a new server resource. The correct migration sequence is: (1) configure an Entra admin on the SQL server, (2) create contained database users mapped to Entra identities for every application connection, (3) validate each application authenticates successfully using Entra tokens in a pre-production environment, (4) switch to Entra-only only after all connections are validated.

The critical preparation phase is running applications in dual-mode: SQL logins and Entra contained users coexist during the migration window, allowing validation without disrupting production. Common failure modes are: applications with hardcoded connection strings using SQL usernames and passwords, middleware libraries or ORMs that do not support MSAL-based token acquisition and refresh, SQL Agent jobs or maintenance plans running under SQL logins that haven't been migrated, and vendor integrations that pre-date Entra auth support. The `audit-sql-entra-admin-configured` and `audit-sql-entra-only-auth` built-in policy definitions provide estate-wide inventory coverage before the migration begins.

### 4. TDE with Customer-Managed Keys (BYOK)

Service-managed TDE is enabled by default on all SQL databases. Upgrading to CMK/BYOK requires integrating with Azure Key Vault: provision a Key Vault with soft delete and purge protection enabled, generate or import an RSA key (2048-bit minimum), assign the SQL server's system-assigned managed identity the `Key Vault Crypto Service Encryption User` role, and then configure the TDE protector on the SQL server to reference the Key Vault key URI. The managed identity role assignment must be in place before configuring the TDE protector — attempting to set the protector without the role produces a cryptic permission error.

Two CMK gotchas specific to geo-replicated databases compound each other for regulated workloads: first, the TDE protector key must be accessible from every region where the database exists, including geo-replicas — a Key Vault deployed only in the primary region means the geo-replica cannot decrypt after failover (see Hidden Assumptions #5). Second, during key rotation, the old key version must remain accessible in Key Vault until all databases complete their rotation cycle — premature key deletion or version expiry leaves databases in an unrecoverable offline state requiring Microsoft support engagement. Rotation policy configuration in Key Vault must account for this overlap window, typically 24–48 hours.

### 5. Managed Instance for Lift-and-Shift

SQL Managed Instance provides near-100% SQL Server compatibility in a fully managed VNet-native PaaS deployment — the right choice when workloads depend on SQL Agent, cross-database queries, linked servers, CLR integration, Windows Authentication, or the full SQL Server Engine surface area. MI lives entirely within a dedicated delegated subnet (/27 minimum, /24 recommended for MI pools), with no public endpoint by default and full private network path for all connections. The MI link feature enables hybrid replication from on-premises SQL Server instances to a Managed Instance, enabling live cut-over migrations with near-zero downtime by keeping the MI replica synchronized until the cut-over window.

The decision boundary between SQL Database and Managed Instance: SQL DB is the right choice for new cloud-native applications and workloads that don't require SQL Server engine-specific features; MI is the right choice for lift-and-shift migrations where re-architecting application dependencies on SQL Agent jobs, cross-database transactions, or linked servers would require months of effort. The primary operational difference from SQL Database: Managed Instance has a maintenance window during which brief connection interruptions (typically < 5 seconds) can occur during service updates. Configure the maintenance window to off-peak hours and ensure all application connection pools implement retry logic with exponential backoff.

## Security Baseline Reinforcement

SQL Database and Managed Instance touch five of the six Security Baseline rules directly. Enforcing these rules at deployment time — not retroactively — is the primary value of this skill in regulated Corp-archetype subscriptions.

| Rule | SQL Database / Managed Instance Enforcement |
|------|---------------------------------------------|
| **Rule 1 – TLS 1.2 minimum** | Set `minimalTlsVersion: '1.2'` on the SQL server resource. Azure Policy `Deny` blocks SQL servers with `minimalTlsVersion < 1.2`. All connections — including SSMS, application drivers, and linked servers — must use TLS 1.2+. |
| **Rule 2 – HTTPS-only traffic** | SQL Database and MI only accept TLS-encrypted connections by design — clear-text is rejected at the service layer. No additional configuration required beyond `minimalTlsVersion`. |
| **Rule 3 – No public blob access** | Not directly applicable to SQL. However, MI automated backups target Azure Storage — ensure the backup storage account has `allowBlobPublicAccess: false` and `supportsHttpsTrafficOnly: true`. |
| **Rule 4 – Managed Identity preferred** | Enable system-assigned managed identity on the SQL server for Key Vault CMK access. Application connections must use managed identities via contained database users — eliminate service-account SQL logins. |
| **Rule 5 – Azure AD-only SQL auth** | `azureADOnlyAuthentication: true` on the SQL server. This is the direct enforcement target for Security Baseline Rule #5 for the data tier. Azure Policy: `Deny` for SQL servers without Entra-only auth in Corp archetype subscriptions. |
| **Rule 6 – Public network disabled (prod)** | `publicNetworkAccess: 'Disabled'` on SQL server. Private endpoint is the only data path. Azure Policy: `Deny` for `publicNetworkAccess: Enabled` on SQL servers in Corp and regulated subscriptions. |

## Decision Heuristics

| Condition | Recommendation |
|-----------|----------------|
| Workload requires ACID transactions with relational schema | SQL Database — confirm against "Choose SQL when" criteria in the shared ADR |
| SQL Server engine features required (SQL Agent, CLR, cross-database queries, linked servers, Windows Auth) | Managed Instance — SQL Database does not support these engine surfaces |
| Cloud-native new application with no SQL Server legacy dependencies | SQL Database (General Purpose or Business Critical) — simpler operational model than MI |
| Storage growth unpredictable, read-scale demand high, working set >4 TB | Evaluate Hyperscale — validate exit path constraint (no BACPAC) before committing |
| Dev/test environment requiring cost optimization with idle periods | SQL Database serverless — acceptable for non-production; irrevocably inappropriate for production |
| Production RPO requirement < 5 seconds | Failover group with `Automatic` policy and minimum grace period (1-hour or less) |
| Data sovereignty requiring CMK and geo-replication | BYOK via Key Vault; provision Key Vault in every deployed region before setting TDE protector |
| On-premises SQL Server lift-and-shift with complex feature dependencies | Managed Instance with MI Link for live migration; size subnet at /24 minimum |
| Existing SQL estate in regulated subscription with Defender for Cloud findings | Follow S3 brownfield 8-step playbook — start with Step 1 Resource Graph inventory |

## Boundaries — DO NOT USE FOR

### DO NOT USE FOR

| Out-of-Scope | Use Instead |
|--------------|-------------|
| Azure Database for PostgreSQL / MySQL / MariaDB | Future-wave candidate; explicitly out of W4 scope |
| Synapse dedicated/serverless SQL pools, Fabric, Data Factory, Purview | Future analytics-wave skills (explicitly out of W4) |
| Cosmos DB document / globally distributed active-active workloads | `azure-cosmos-db` |
| Blob / Queue / Table / Files storage configuration | `azure-storage-accounts` |
| Cross-cutting identity, network, cost, monitor, key, policy patterns | `azure-rbac`, `azure-private-link`, `cost-governance`, `azure-monitor`, `azure-key-vault`, `azure-policy` |
| Entra admin provisioning and identity governance workflows | `entra-identity-governance` (W1) |
| Application-to-SQL managed-identity / federated-credential auth setup | `workload-identity-federation` (W1) |
| SQL vs Cosmos vs Storage tier selection decision boundary | `docs/decisions/data-tier-selection.md` |

## Brownfield Scenario (Scenario S3: Regulated Financial Services)

This skill sequences after `azure-private-link` (network isolation established) and `azure-key-vault` (CMK infrastructure ready), enabling the Oracle to prescribe SQL security hardening without breaking existing application connections. Use this brownfield playbook in conjunction with the boundary semantics from `docs/decisions/data-tier-selection.md`.

Regulated financial services estates carry the heaviest SQL footprint and the strictest security baseline gaps. Typical findings from Step 0 assessments: SQL authentication still enabled with no Entra admin configured, TDE using service-managed keys with no CMK/BYOK, no failover group or geo-replication configured (RPO gaps violating continuity mandates), public network access enabled on the SQL server, audit logging missing or with insufficient retention for regulatory requirements, and — critically — serverless tier databases in production environments that violate always-on HA expectations. Any serverless-tier SQL databases in production must be migrated to provisioned compute before HA configuration begins.

### 8-Step Playbook

| Step | Action | Rollback Type |
|------|--------|---------------|
| 1 | Inventory existing SQL servers and databases via Resource Graph: auth mode (SQL / Entra / mixed), TDE protector type (service-managed vs CMK), public network access status, failover group membership, backup retention settings, tier (serverless vs provisioned), and Managed Instance vs SQL DB classification | Read-only |
| 2 | Assess compliance gaps: Is Entra admin configured? Are failover groups present with auto-failover policy? Is TDE using CMK with keys accessible in each deployed region? Are audit logs enabled with sufficient retention (≥90 days)? Are any databases on serverless tier in production (must remediate before Step 7)? | Read-only |
| 3 | Enable diagnostic settings and SQL audit logging routed to the central Log Analytics workspace; configure Advanced Threat Protection and enable vulnerability assessment scans with email notifications | Soft rollback (disable diagnostic settings and ATP; no data configuration changed) |
| 4 | Configure TDE with CMK: enable system-assigned managed identity on SQL server, grant `Key Vault Crypto Service Encryption User` role, configure TDE protector from existing Key Vault key; provision Key Vault replica in paired region as geo-replication prerequisite | Soft rollback (revert TDE protector to service-managed key within 24h before CMK dependency solidifies for application consumers) |
| 5 | Create contained database users for all application connections — map each application's managed identity or Entra service principal to the appropriate contained user in each database; validate Entra auth in pre-production with dual-mode (SQL logins and Entra users coexist) | Soft rollback (drop contained users; SQL logins remain active and applications continue unaffected) |
| 6 | ⛔ **HARD GATE** — Switch server to Entra-only authentication. This permanently disables SQL authentication on the server. All applications MUST be authenticated via Entra tokens. Verify all items in the Pre-Step-6 Checklist before proceeding. | Irrevocable — SQL auth cannot be re-enabled without recreating the SQL server; all SQL-auth-dependent applications break immediately and permanently |
| 7 | Configure failover group with auto-failover policy: provision secondary SQL server in the paired region (with Key Vault CMK access pre-established), add databases to the failover group, configure grace period, update all application connection strings to use the failover group listener endpoint | Soft rollback (remove databases from failover group; each server reverts to standalone operation; listener endpoint removed) |
| 8 | Assign Azure Policy: `deny-sql-public-network-access`, `require-sql-tde-cmk`, `require-sql-entra-only-auth`, `require-sql-audit-logging-retention` | Soft rollback (remove policy assignments; guardrails removed and drift begins immediately) |

### Pre-Step-6 Verification Checklist

Step 6 is irrevocable — Entra-only auth cannot be reversed without recreating the SQL server and migrating all databases. Before crossing this gate, verify all of the following: (1) every application connection has a corresponding contained database user mapped to an Entra identity and has been tested successfully end-to-end in a pre-production environment that mirrors production; (2) no SQL Agent jobs, maintenance plans, replication agents, or linked server connections use SQL authentication; (3) run a dry-run on a non-production server with an identical application workload profile — validate zero connection failures over a 24-hour observation window; (4) confirm all middleware libraries, ORMs, and connection pool implementations support MSAL-based Entra token acquisition and automatic refresh; (5) obtain explicit written sign-off from application owners, the DBA team, and the security team. Document each verification item as evidence before proceeding.

## Prerequisites and Caveats

Before applying this skill, verify these conditions hold for the target environment. Unmet prerequisites are the primary cause of SQL hardening steps that appear correct in design but break application connections in production.

| Prerequisite | Impact | Guidance |
|--------------|--------|----------|
| **`azure-private-link` private endpoints provisioned** | Disabling public network access (Step 8) without a private endpoint leaves SQL unreachable from all applications | Provision private endpoint per SQL server, validate private DNS resolution, confirm application connectivity before any public-access policy assignment |
| **`azure-key-vault` provisioned in each deployed region** | CMK with Key Vault only in the primary region means geo-replica cannot decrypt after failover — database offline at the worst moment | Follow the `azure-key-vault` multi-region topology pattern; grant the SQL server managed identity the `Key Vault Crypto Service Encryption User` role in each regional vault before configuring the TDE protector |
| **Entra admin configured on SQL server** | Contained database user creation (Step 5) requires an active Entra admin on the server | Set Entra admin before creating contained users; the admin must be a user or group in the same Entra tenant as the SQL server |
| **All application connection libraries support Entra auth (MSAL)** | Step 6 Entra-only switch breaks applications using drivers or ORMs without MSAL token acquisition and refresh support | Audit all connection libraries and driver versions; validate Entra auth in pre-production for each application before scheduling Step 6 |
| **Defender for Cloud SQL plan enabled** | Advanced Threat Protection and vulnerability assessments (Step 3) require Defender for SQL | Enable the Defender for SQL plan at subscription scope via Defender for Cloud settings; allow 24–48 hours for initial baseline scan |
| **Secondary SQL server provisioned in paired region** | Failover group configuration (Step 7) requires a pre-existing secondary server — it cannot be created during a failover event | Provision secondary server before Step 7; validate regional Key Vault access grants before adding databases to the failover group |
| **Serverless-tier production databases remediated** | Serverless databases cannot participate in failover groups and violate always-on HA for S3 regulated estates | Identify serverless production databases in Step 2 assessment; migrate to provisioned compute (scale-up within same server) before proceeding to Step 7 |

## Hidden Assumptions

1. **Hyperscale BACPAC export is not supported** — Hyperscale databases cannot be exported to BACPAC format. Migration out of Hyperscale to another tier or external platform requires live data-motion replication via transactional replication or Azure Database Migration Service. Brownfield teams that assume a BACPAC export-and-restore path for Hyperscale databases will discover this constraint only at migration execution time, often under deadline pressure.

2. **Entra-only auth is one-way** — Once SQL authentication is disabled at the server level, it cannot be re-enabled without recreating the SQL server and migrating all databases to a new server resource. Applications that still rely on SQL usernames and passwords will break immediately and permanently. There is no "soft disable" or rollback path after the switch. This is not a configuration flag that can be toggled back.

3. **Failover group DNS propagation is 30–120 seconds** — Applications that connect directly to the primary server FQDN rather than the failover group listener endpoint will experience a connection outage during automatic failover for the duration of DNS propagation. This outage is invisible when testing failovers manually against the listener endpoint. Connection string auditing — confirming every application uses the listener FQDN — must precede failover group activation in production.

4. **CMK rotation requires key version overlap** — When rotating TDE CMK keys in Key Vault, the previous key version must remain enabled and accessible for the full duration of the TDE key rotation operation on every database protected by that key. Premature deletion or disablement of the old key version — before all databases have completed their rotation cycle — leaves those databases in an offline encrypted state that requires Microsoft support to recover. Key rotation policy must explicitly define the overlap retention window (minimum 48 hours).

5. **Geo-replication requires CMK access in both regions** — Databases protected by TDE with CMK require that the SQL server's managed identity has Key Vault key access in every region where a replica exists, including geo-replicas created by failover groups. A Key Vault deployed only in the primary region means the geo-replica cannot decrypt data after a regional failover — the TDE protector key is unreachable. This failure is silent in steady state and only manifests during a failover event, making it one of the most dangerous silent mis-configurations in regulated SQL architectures.

## Anti-Patterns

### Anti-Pattern 1: Serverless Tier in Production S3 Workloads

Using SQL Database serverless tier for production workloads in S3 regulated estates violates the always-on HA baseline mandated by financial services continuity requirements. Serverless auto-pauses the compute layer after a configurable idle period — typically one to sixty minutes — and resumes on the first new connection with a cold-start latency of 15–30 seconds. For regulated workloads, this cold-start creates unpredictable response times for health checks and monitoring probes, breaks failover group participation (a paused database cannot respond to failover policy), and violates SLA expectations for always-on availability.

**Corrective action:** Identify serverless production databases during Step 2 assessment. Migrate to provisioned compute (General Purpose minimum; Business Critical for strict latency SLAs) before HA configuration begins. Reserve serverless exclusively for dev/test databases where cost reduction outweighs availability requirements. Serverless is not a remediation candidate — it is a tier that must not exist in S3 production at all.

### Anti-Pattern 2: CMK Without Multi-Region Key Vault Topology

Configuring TDE with CMK without provisioning a Key Vault instance accessible from every geo-replicated region creates a silent failure mode that only manifests during the regional disaster scenario the configuration was designed to protect against. The geo-replica's managed identity requires a direct network path and an explicit access grant to the TDE protector key in its local region — geo-redundant storage of the key alone does not satisfy the managed identity access grant requirement. The geo-replica appears healthy in steady state, passes all monitoring checks, and is considered available for failover. At the moment of actual regional failover, the replica cannot decrypt its data files and comes online in an error state.

**Corrective action:** Treat multi-region Key Vault topology as a first-class architectural concern in every CMK design. During Step 4, provision Key Vault in the paired region, replicate the TDE key, and grant the secondary SQL server's managed identity the `Key Vault Crypto Service Encryption User` role — all before adding any database to the failover group in Step 7. Never configure the TDE protector before the secondary-region Key Vault access grants are verified.

### Anti-Pattern 3: Disabling SQL Auth Without Complete Application Validation

Disabling SQL authentication before validating that every application, agent, job, middleware component, and vendor integration can successfully authenticate via Entra tokens is the highest-impact, highest-frequency error in the SQL brownfield hardening playbook. The disable operation is instantaneous, service-wide, and irrevocable. A single overlooked SQL-auth dependency — a legacy monitoring agent, a vendor ETL integration, a SQL Agent job running under a SQL login — produces a production outage the moment the switch is flipped, with no in-place recovery path. There is no rollback: the SQL server must be recreated to restore SQL auth capability.

**Corrective action:** The Pre-Step-6 Verification Checklist exists as a hard gate for this reason. Every item must be confirmed with documentation before proceeding. Run a 24-hour dry-run on an identical non-production server with the real application workload before scheduling the production switch. Treat Step 6 as a point-of-no-return requiring written sign-off from application owners, the DBA team, and the security team — not an operational toggle to be applied under delivery pressure.

### Anti-Pattern 4: Over-Provisioned Hyperscale Named Replicas

Defaulting to the maximum Hyperscale named replica count without measuring actual read-scale demand allocates compute cost without performance benefit. Each named replica is an independent compute instance billed continuously at the configured vCore-hour rate — unlike geo-replicas, named replicas share storage cost, but compute is fully separate. Provisioning the maximum allowed named replicas to handle peak read load that a fraction of those replicas could service wastes the remainder's compute budget for the full billing period, including off-peak hours when read demand drops.

**Corrective action:** Derive named replica count from a measured two-week read workload baseline: CPU and connection saturation per replica under peak load. Start with one named replica, validate read distribution, and scale out only if a single replica is saturated at peak. In most regulated financial services workloads, one or two named replicas cover reporting and analytics offload. Named replica scale-out is fast (minutes) — there is no penalty for starting conservative and scaling when real demand materializes.

## Diagnostic Queries

### KQL: SQL servers with SQL authentication still enabled (Entra-only not enforced)

```kql
Resources
| where type == "microsoft.sql/servers"
| where properties.administrators.azureADOnlyAuthentication != true
| project name, subscriptionId, resourceGroup,
          entraAdmin = tostring(properties.administrators.login),
          entraOnlyAuth = tostring(properties.administrators.azureADOnlyAuthentication),
          minTlsVersion = tostring(properties.minimalTlsVersion)
| order by name asc
```

### KQL: SQL servers with public network access enabled (Security Baseline Rule #6 violation)

```kql
Resources
| where type == "microsoft.sql/servers"
| where properties.publicNetworkAccess == "Enabled"
| project name, subscriptionId, resourceGroup,
          publicNetworkAccess = tostring(properties.publicNetworkAccess),
          minTlsVersion = tostring(properties.minimalTlsVersion)
| order by name asc
```

### KQL: SQL servers not covered by any failover group (RPO gap in regulated estates)

```kql
Resources
| where type == "microsoft.sql/servers"
| project serverName = name, serverId = id, subscriptionId, resourceGroup
| join kind=leftanti (
    Resources
    | where type == "microsoft.sql/servers/failovergroups"
    | extend serverResourceId = strcat(split(id, "/failoverGroups/")[0])
    | project serverResourceId
  ) on $left.serverId == $right.serverResourceId
| project serverName, subscriptionId, resourceGroup
| order by serverName asc
```

### KQL: SQL databases with service-managed TDE (CMK not configured)

```kql
Resources
| where type == "microsoft.sql/servers/databases"
| where name != "master"
| extend tdeProtector = tostring(properties.transparentDataEncryption.status)
| where tdeProtector != "CustomerManaged"
| project name, subscriptionId, resourceGroup,
          serverName = tostring(split(id, "/databases/")[0]),
          tdeStatus = tdeProtector
| order by serverName, name asc
```

## References

| Resource | Notes |
|----------|-------|
| **[`docs/decisions/data-tier-selection.md`](../../../docs/decisions/data-tier-selection.md)** | **Shared ADR — read first.** Canonical SQL vs Cosmos vs Storage decision boundary. Defines "Choose SQL when" criteria, cross-tier WAF trade-off matrix, brownfield assessment lens, and irrevocable hard-gate cross-references. Referenced in this skill's Overview, Brownfield intro, and Boundaries. |
| [`azure-cosmos-db`](../azure-cosmos-db/SKILL.md) | Wave 4 sibling. Globally distributed active-active document workloads — the Cosmos boundary as established by the shared ADR. |
| [`azure-storage-accounts`](../azure-storage-accounts/SKILL.md) | Wave 4 sibling. Blob/queue/table/file persistence, per-tenant isolation, lifecycle management, immutability for compliance. |
| [`azure-private-link`](../azure-private-link/SKILL.md) | **Hard prereq.** Private endpoint provisioning and private DNS zone integration for SQL Database and Managed Instance. Must be applied before disabling public network access in Step 8. |
| [`azure-key-vault`](../azure-key-vault/SKILL.md) | **Hard prereq.** CMK key lifecycle, key rotation policies, managed identity access grants, and multi-region Key Vault topology required for geo-replication CMK coverage. |
| [`azure-policy`](../azure-policy/SKILL.md) | Soft prereq. Policy definition and assignment syntax for SQL compliance initiatives: deny-public-access, require-TDE-CMK, require-Entra-only, require-audit-logging. |
| [`azure-monitor`](../azure-monitor/SKILL.md) | Soft prereq. Diagnostic settings pipeline to Log Analytics, alert rules for ATP threat detections and failed login anomalies. |
| [`azure-rbac`](../azure-rbac/SKILL.md) | Soft prereq. Management-plane RBAC for SQL server administration; PIM eligible assignments for DBA and SQL Contributor roles. |
| [`entra-identity-governance`](../entra-identity-governance/SKILL.md) | W1 soft prereq. Entra admin provisioning for SQL servers; access reviews for contained database user and role assignments. |
| [`workload-identity-federation`](../workload-identity-federation/SKILL.md) | W1 soft prereq. Managed identity and federated credential configuration for application-to-SQL authentication via Entra tokens; required before Step 5 contained user creation. |
| [Azure SQL high availability and disaster recovery](https://learn.microsoft.com/azure/azure-sql/database/business-continuity-high-availability-disaster-recover-hadr-overview) | Microsoft Learn: failover groups, geo-replication, zone-redundant HA architecture, RPO/RTO specifications per service tier. |
| [Entra-only authentication for Azure SQL](https://learn.microsoft.com/azure/azure-sql/database/authentication-azure-ad-only-authentication) | Microsoft Learn: one-way migration procedure, server admin configuration, contained database user creation, application migration guidance. |
| [TDE with customer-managed keys](https://learn.microsoft.com/azure/azure-sql/database/transparent-data-encryption-byok-overview) | Microsoft Learn: BYOK workflow, Key Vault integration, key rotation procedures, geo-replication TDE protector requirements. |
| [Failover groups for Azure SQL Database](https://learn.microsoft.com/azure/azure-sql/database/failover-group-sql-db) | Microsoft Learn: listener endpoint configuration, auto-failover policy, grace period tuning, read-scale secondary configuration. |
| [`docs/decisions/compute-tier-selection.md`](../../../docs/decisions/compute-tier-selection.md) | Wave 2 ADR. AKS/ACA/VM compute-tier boundaries; SQL Database and Managed Instance are the persistence tier these compute platforms connect to. |
| [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md) | Wave 3 ADR. Subscription placement for regulated SQL workloads — Corp archetype subscriptions enforce SQL security policies (Entra-only, deny public access) at vending time. |

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-18 | Saul | Initial Wave 4 authoring — SQL Database and Managed Instance patterns (failover group, Hyperscale, Entra-only migration, TDE CMK BYOK, Managed Instance lift-and-shift), brownfield S3 Regulated Financial Services 8-step playbook with ⛔ HARD GATE Step 6 and soft rollback annotations, Pre-Step-6 Verification Checklist, 5 concrete hidden assumptions, 4 anti-patterns, shared ADR cross-reference (`data-tier-selection.md`) in 4 locations. |
