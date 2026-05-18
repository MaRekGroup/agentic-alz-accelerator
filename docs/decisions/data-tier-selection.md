# ADR: Data Tier Selection (SQL Database vs Cosmos DB vs Storage Accounts)

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-18 |
| **Decision Makers** | Linus (Architect), Yeselam (Sponsor) |
| **Related Skills** | `azure-sql-database`, `azure-cosmos-db`, `azure-storage-accounts` (Wave 4), `azure-private-link`, `azure-key-vault`, `azure-policy`, `cost-governance` (existing) |

## Context

Azure's persistence layer offers three first-class services for enterprise landing zones: SQL Database (relational ACID transactions), Cosmos DB (globally distributed document store), and Storage Accounts (object/blob/file durability). Without explicit boundary criteria, teams select the wrong data tier and produce expensive migration debt — partition key immutability in Cosmos means a wrong choice requires full container recreation, Entra-only auth in SQL is a one-way switch that cannot be reversed, and storage account HNS enablement is set at creation time and cannot be toggled afterward. These irrevocable decisions make tier selection a hard-gate architecture concern that must be locked before implementation begins.

Approximately 75% of brownfield engagements assessed by this accelerator involve at least one mis-tiered data workload: a relational transactional system forced into Cosmos paying 3-10× cost for partition-key-aligned queries it never uses, a globally distributed metadata tier running on SQL with failover groups providing read scale but not the active-active writes the workload requires, or a multi-tenant SaaS platform using append blobs as a pseudo-transactional store without ACID guarantees. These mis-tierings trace to absent decision criteria at the architecture phase.

This ADR establishes the canonical decision boundary between Azure SQL Database, Azure Cosmos DB, and Azure Storage Accounts. The Wave 4 data platform SKILL.md files reference this document for tier selection — they do NOT redefine these boundaries inline. Each SKILL.md goes deep on its tier's internals; this ADR stays in the boundary layer. This is the "design vs. automate" split: this ADR designs the decision tree; the SKILL.md files describe HOW to configure within each tier's boundary.

## Decision Tree

### Choose Azure SQL Database When

| Criterion | Rationale |
|-----------|-----------|
| Workload requires ACID transactions with relational schema | SQL provides full transaction isolation levels, foreign key constraints, and stored procedures |
| Structured data with complex joins, aggregations, and reporting queries | SQL optimizer handles multi-table joins; Cosmos requires denormalization |
| Regulatory compliance mandates auditable relational integrity (financial, healthcare) | SQL audit logging + TDE + failover groups satisfy S3 regulatory continuity mandates |
| VNet-native deployment with Windows Authentication required | SQL Managed Instance provides full VNet integration and Windows Auth compatibility |
| Workload needs sub-second failover with <5s RPO via geo-replication | Failover groups with auto-failover provide transparent DNS-based recovery |

### Choose Azure Cosmos DB When

| Criterion | Rationale |
|-----------|-----------|
| Workload requires globally distributed active-active writes across regions | Multi-region write with conflict resolution is Cosmos-native; SQL failover groups are active-passive |
| Document or key-value data model with partition-key-aligned access patterns | Cosmos partition architecture delivers single-digit-ms reads at any scale when partition key matches queries |
| Sub-10ms latency SLA at global scale with tunable consistency | Five consistency levels from Strong to Eventual allow precise latency-consistency trade-off |
| Event-driven architectures consuming change feed for real-time processing | Cosmos change feed is a first-class primitive; SQL change tracking requires polling |
| AI/ML metadata or feature stores requiring multi-region read/write distribution | S2 platform architecture maps 1:1 to Cosmos multi-region write capabilities |

### Choose Azure Storage Accounts When

| Criterion | Rationale |
|-----------|-----------|
| Workload is object/blob storage for unstructured data (images, documents, backups, logs) | Storage is purpose-built for durable object persistence at the lowest cost per GB |
| Large-scale file/blob lifecycle management with automated tiering (Hot→Cool→Cold→Archive) | Lifecycle policies automate cost optimization; no equivalent exists in SQL or Cosmos |
| Multi-tenant SaaS requiring per-tenant blob isolation with immutability for audit trails | Container-level RBAC + immutability policies provide tenant-scoped compliance guarantees |
| Static content serving via CDN with private origin | Storage + CDN + private endpoint pattern is the canonical static asset architecture |
| Queue/Table storage for lightweight messaging or semi-structured metadata | Storage Tables and Queues provide simple, low-cost primitives without database overhead |

### Edge Cases

| Pattern | Recommended Tier | Rationale |
|---------|-----------------|-----------|
| Time-series telemetry (append-heavy, range queries) | Cosmos (TTL + partition by time) OR Storage (append blobs + lifecycle) | Volume and query pattern determine: high-throughput queries → Cosmos; archival/batch → Storage |
| Cache layer (low-latency key-value reads) | Out-of-scope — Azure Cache for Redis (future wave) | Neither SQL nor Cosmos nor Storage is a cache; do not misuse Cosmos as a cache tier |
| Full-text and vector search | Out-of-scope — Azure AI Search (future wave) | Search is a distinct concern requiring specialized indexing infrastructure |

## Trade-Off Matrix (WAF Pillars)

| WAF Pillar | SQL Database | Cosmos DB | Storage Accounts |
|------------|-------------|-----------|-----------------|
| **Reliability** | Failover groups provide auto-failover with <5s RPO at additional replica cost; zone-redundant HA is built-in for Business Critical tier. Geo-replication is mandatory for S3 regulated workloads. | Multi-region writes with automatic failover deliver the highest availability ceiling; zone-redundant replicas per region. Continuous backup with 1-second PITR granularity eliminates backup-window gaps. | GRS/GZRS provides cross-region durability with 16-nines; account failover is manual (customer-initiated) with potential data loss for last-replication-window writes. Soft delete and versioning provide object-level recovery. |
| **Security** | Entra-only authentication (Security Baseline Rule #5) eliminates SQL auth attack surface; TDE with CMK provides encryption at rest; Advanced Threat Protection detects anomalous access. Private endpoints enforce network isolation. | Entra data-plane RBAC with account-key disable removes shared-secret exposure; CMK encryption at rest; per-region private endpoints prevent cross-region data exfiltration. Always-encrypted client-side option for field-level protection. | Public blob access disable (Security Baseline Rule #3) is the #1 brownfield finding; shared key disable forces Entra RBAC for all data-plane access; immutability policies provide tamper-proof audit compliance. CMK via Key Vault encrypts at rest. |
| **Cost Optimization** | Reserved capacity (1/3-year) reduces compute cost by 30-65%; serverless tier for dev/test eliminates idle cost; Hyperscale named replicas share storage cost. Right-sizing via DTU/vCore analysis is critical. | Autoscale (10% min of max RU) optimizes bursty workloads; serverless for dev/test; reserved capacity for stable throughput. Multi-region writes multiply cost 2× per additional write region — budget impact frequently underestimated. | Access tier lifecycle (Hot→Cool→Cold→Archive) can reduce storage cost by 80%+; reserved capacity for predictable volumes. Redundancy selection (LRS vs GRS) directly controls cost — over-replicating without business need wastes budget. |
| **Performance Efficiency** | vCore model allows precise CPU/memory allocation; Hyperscale provides elastic scale with page-server architecture; read replicas offload analytics queries. Intelligent Performance Insights surface tuning opportunities. | Partition key strategy determines throughput ceiling — hot partitions create performance cliffs regardless of provisioned RUs. Hierarchical partition keys expand addressing. Dedicated throughput per container isolates workloads. | Premium block blob provides sub-ms latency for hot-path workloads; HNS enables analytics-optimized hierarchical access. Standard accounts scale to exabytes but with higher per-operation latency. Large-file upload patterns (block staging) required above 256MB. |
| **Operational Excellence** | Automated backups with PITR, maintenance windows, elastic jobs for cross-database automation. Long-term backup retention for compliance. Update Manager integration for Managed Instance OS patching. | Minimal operational surface — no patching, no version upgrades, no cluster management. Change feed enables event-driven automation. Throughput alerts via Azure Monitor detect RU pressure before throttling impacts applications. | Lifecycle policies automate tier transitions without operator intervention. Blob inventory reports provide estate visibility. Diagnostic settings feed Log Analytics for access pattern analysis. Last-access-time tracking enables data-driven lifecycle decisions. |

## Brownfield Assessment Lens

When the Assessor agent (Step 0) evaluates an existing estate's persistence layer, it must classify each data workload against this decision tree and recommend tier transitions where the current choice produces architecture debt. The assessment cross-references each Wave 4 skill's brownfield playbook to identify irrevocable hard-gate boundaries that constrain migration sequencing.

| Current State | Assessment Signal | Recommended Action |
|---------------|-------------------|--------------------|
| SQL Database running a document-model workload with no joins | No foreign keys, single-table access, JSON columns dominating | Candidate for Cosmos migration — evaluate against decision tree; confirm global distribution need before migrating |
| Cosmos DB running relational-pattern queries with cross-partition fan-out | High RU consumption, cross-partition queries >80% of traffic | Over-engineered — candidate for SQL replatform (eliminate RU cost for relational access patterns) |
| Storage append blobs used as transactional event store | High append rates, application-layer retry logic for consistency | Mis-tiered — migrate event store to Cosmos (change feed) or SQL (transactions) based on scale/query pattern |
| SQL Database with failover groups attempting multi-region active-active writes | Write conflicts, application-layer routing between regions | Under-powered for the access pattern — candidate for Cosmos multi-region write architecture |
| Storage accounts with public blob access enabled in production | Security Baseline Rule #3 violation, Sentinel finding | Immediate remediation required — disable public access per storage skill brownfield playbook step 5 |

**Hard-gate boundaries from the W4 brownfield playbooks:**

The `azure-sql-database` skill's playbook step 6 is an irrevocable ⛔ HARD GATE — switching to Entra-only authentication permanently disables SQL auth. All applications MUST use Entra tokens before this gate is crossed. The `azure-cosmos-db` skill's playbook has two ⛔ HARD GATES: step 4 (consistency level change affects all readers immediately) and step 7 (disabling key-based auth permanently invalidates account keys). The `azure-storage-accounts` skill's playbook has two ⛔ HARD GATES: step 5 (disabling public blob access breaks all anonymous read patterns) and step 7 (disabling shared key access invalidates all existing account-key SAS tokens).

**Key assessment questions per workload:**

Is the current tier choice still appropriate given the decision tree criteria above? If not, are migration costs justified by the debt elimination? What is the irrevocable hard-gate boundary for the target tier — and is the organization ready to cross it? Has the prerequisite skill work (private link, key vault, identity governance) been completed to enable the hard-gate transition safely?

**Design vs. automate boundary in brownfield:** The Assessor determines WHAT the target tier should be (design — this ADR). The per-skill brownfield playbooks define HOW to migrate into that tier safely (automate — the SKILL.md files). Both consume this ADR's decision criteria but apply them at different operational phases.

**Brownfield data-tier assessment flow:**

```
Existing Data Workload (assess) ──► Correctly Tiered ──► Optimize within tier
         │                                                    (use per-skill playbook)
         │
         └──► Mis-Tiered (decision tree mismatch) ──► Evaluate migration cost
                                                              │
                                                              ▼
                                                        Migration justified?
                                                        YES → Execute per-skill
                                                              brownfield playbook
                                                        NO  → Document as accepted
                                                              technical debt
```

Each arrow represents an assessment outcome, not an inevitable migration. Workloads that are correctly tiered receive optimization within their current tier; mis-tiered workloads require cost-benefit analysis before migration is recommended.

## Scenario Mapping

| Scenario | Code | Recommended Tier(s) | Rationale |
|----------|------|---------------------|-----------|
| Multi-Region AI Platform | S2 | Cosmos DB (primary: metadata + feature store) + Storage (model artifacts, training data) | Cosmos multi-region active-active writes serve AI metadata distribution; Storage provides durable artifact persistence at scale |
| Regulated Financial Services | S3 | SQL Database (primary: transactional core) + Storage (audit trails, document archives) | SQL delivers ACID transactions with regulatory failover groups; Storage immutability provides tamper-proof compliance archives |
| ISV Multi-Tenant SaaS | S5 | Storage (primary: per-tenant blob isolation) + SQL (tenant metadata, billing state) + Cosmos (real-time analytics feeds) | Storage per-tenant isolation is the architecture question; SQL handles relational tenant state; Cosmos handles event-driven tenant analytics |
| Cloud-Native Modernization | S8 | No W4 skill targets S8 as primary — S8 benefits indirectly from W4 patterns degraded to simpler single-tenant configurations | S8 omission is intentional; highest-friction brownfield boundaries (S2, S3, S5) prioritized for this wave |

## Anti-Patterns

Using Cosmos DB for relational transactional workloads is the most expensive data-tier mistake in brownfield estates. Cosmos's partition-key-aligned document model provides no benefit for workloads that require multi-table joins, foreign key constraints, and serializable transaction isolation. Teams that choose Cosmos for "future scale" on workloads that will never exceed single-region capacity pay 3-10× the cost of equivalent SQL Database configurations — and lose ACID guarantees they silently depend on. The correct approach is to start with SQL and graduate to Cosmos only when the decision tree criteria (global distribution, document model, sub-10ms latency) are independently satisfied.

Using SQL Database for globally distributed active-active writes misunderstands what failover groups provide. SQL failover groups deliver read-scale secondaries and automatic failover for disaster recovery — they do NOT provide multi-region active-active write capability. Applications writing to multiple regions simultaneously require Cosmos's multi-region write architecture with conflict resolution policies. Attempting to simulate active-active writes on SQL through application-layer routing produces split-brain consistency failures that are undetectable until audit time.

Using Storage Accounts as a transactional database via append blobs provides no ACID guarantees and creates performance cliffs at scale. Append blobs have a maximum block count of 50,000 and a maximum size of approximately 195GB — hitting these limits silently fails writes. Teams using append blobs as an event log or state store without understanding these limits produce data loss under load. The correct approach for transactional event storage is SQL (small-to-medium volume with relational queries) or Cosmos (high-volume with partition-key-aligned access).

Splitting a single dataset across SQL and Cosmos to "have both" relational queries and document flexibility produces consistency hell and double cost. Cross-service transactions do not exist — there is no distributed transaction coordinator spanning SQL and Cosmos. Every write must be independently committed to both stores with application-layer compensation logic for failures. Data synchronization lag between stores means queries return different results depending on which store serves them. The correct approach is to pick ONE tier per bounded context and design the schema to fit that tier's strengths.

Defaulting to maximum replication topology without business justification wastes budget at enterprise scale. Multi-region writes in Cosmos multiply RU cost 2× per additional write region — a 3-region active-active deployment costs 4-6× a single-region deployment. GRS/GZRS in Storage doubles storage cost versus LRS/ZRS. SQL geo-replication adds a full secondary replica cost. Each replication decision must be justified by explicit RPO/RTO requirements, regulatory data sovereignty mandates, or latency-sensitive geographic distribution — not by "we might need it someday" precautionary architecture.

## Prerequisites and Caveats

| Factor | Impact | Guidance |
|--------|--------|----------|
| `entra-identity-governance` (W1) | Entra admin provisioning required before SQL Entra-only auth or Cosmos key-disable hard gates can be crossed | Confirm Entra admin and contained-user provisioning is complete before scheduling hard-gate transitions |
| `workload-identity-federation` (W1) | Application-to-data auth via managed identity or federated credentials must be configured before disabling legacy auth | All application connections must use Entra tokens; validate in pre-production before crossing hard gates |
| `azure-private-link` | Network isolation is a prerequisite for all three tiers in production landing zones | Private endpoints must be provisioned per-region before disabling public network access |
| `azure-key-vault` | CMK infrastructure required for TDE (SQL), encryption at rest (Cosmos), and storage encryption | Key Vault with appropriate access policies must exist in each region where data services deploy |
| `azure-policy` | Policy enforcement (deny public access, require TDE/CMK, require Entra-only) is the final step in each brownfield playbook | Policy assignments follow configuration changes — never precede them, as they would block in-progress remediation |
| `cost-governance` | Budget alerts must account for multi-region write multipliers (Cosmos), geo-replication costs (SQL/Storage), and reserved capacity commitments | Surface cost multipliers during architecture assessment; never assume single-region pricing for multi-region designs |
| Regional pricing variance | Azure service pricing varies by region (up to 20% delta for some SKUs) | Validate pricing in target region during Step 2 architecture assessment; do not assume US pricing globally |
| Regulatory data sovereignty | Some jurisdictions mandate data residency that constrains replication topology choices | Data sovereignty requirements may override cost-optimal replication decisions; document as explicit constraints |
| BYOK key locality | CMK keys must be accessible from all regions where encrypted data resides | Multi-region deployments require Key Vault instances (or HSM) in each region with key replication configured |

## References

### Wave 4 SKILL.md Files (Authored After This ADR)

- [`.github/skills/azure-sql-database/SKILL.md`](../../.github/skills/azure-sql-database/SKILL.md) — SQL Database and Managed Instance architecture, failover groups, Entra-only auth, TDE with CMK
- [`.github/skills/azure-cosmos-db/SKILL.md`](../../.github/skills/azure-cosmos-db/SKILL.md) — Cosmos DB multi-region writes, consistency levels, partition strategy, RU provisioning
- [`.github/skills/azure-storage-accounts/SKILL.md`](../../.github/skills/azure-storage-accounts/SKILL.md) — Storage account isolation, lifecycle policies, immutability, replication topology

### Existing Skills (Cross-Referenced)

- [`.github/skills/azure-private-link/SKILL.md`](../../.github/skills/azure-private-link/SKILL.md) — Private endpoint patterns (hard prereq for all three data tiers)
- [`.github/skills/azure-key-vault/SKILL.md`](../../.github/skills/azure-key-vault/SKILL.md) — CMK lifecycle, key rotation, multi-region key replication
- [`.github/skills/cost-governance/SKILL.md`](../../.github/skills/cost-governance/SKILL.md) — Budget alerts, reserved capacity, multi-region cost modeling
- [`.github/skills/workload-identity-federation/SKILL.md`](../../.github/skills/workload-identity-federation/SKILL.md) — Managed identity and federated credentials for app-to-data auth

### Prior ADRs

- [`docs/decisions/compute-tier-selection.md`](./compute-tier-selection.md) — Wave 2 ADR establishing AKS/ACA/VM decision boundaries
- [`docs/decisions/billing-tenant-hierarchy.md`](./billing-tenant-hierarchy.md) — Wave 3 ADR establishing MG hierarchy/vending decision boundaries

### Microsoft Learn References

- [Azure SQL Database high availability and disaster recovery](https://learn.microsoft.com/azure/azure-sql/database/business-continuity-high-availability-disaster-recover-hadr-overview) — Failover groups, geo-replication, zone-redundant HA
- [Azure Cosmos DB consistency levels](https://learn.microsoft.com/azure/cosmos-db/consistency-levels) — Five consistency models with latency/availability trade-offs
- [Azure Storage redundancy](https://learn.microsoft.com/azure/storage/common/storage-redundancy) — LRS, ZRS, GRS, GZRS replication models and failover procedures

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-18 | Linus | v1.0 — Initial publication (Linus-6, Wave 4). Establishes canonical SQL/Cosmos/Storage decision boundary referenced by the W4 data platform SKILL.md files. |
