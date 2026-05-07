# Target-State Architecture — Brownfield + Assessment Enhancement

> **Canonical version:** [docs/accelerator/target-architecture.md](../../../docs/accelerator/target-architecture.md)
>
> This file is a historical snapshot. The target state described here is now
> fully implemented as of 2026-05-04.

> **Date:** 2026-04-23
> **Status:** ✅ Implemented
> **ADR:** [ADR-0001](../adr/ADR-0001-brownfield-assessment.md)

## Summary

Extend the Agentic ALZ Accelerator with two new capabilities:

1. **Brownfield Discovery** — Read-only inventory of existing Azure environments
2. **WARA/CAF Assessment** — Evaluate existing state against Well-Architected
   and Cloud Adoption Framework standards, producing scored findings and
   prioritized recommendations

These are added as **optional pre-workflow steps** (Step 0 and Step 0.5) that
feed into the existing 10-step APEX workflow. The existing greenfield flow
remains unchanged.

A third capability — **generated architecture documentation** — enables the
accelerator to produce current-state architecture docs, target-state docs,
Mermaid diagrams, and ADRs for any environment it assesses (greenfield or
brownfield). These are generated artifacts, not static files.

## What Changes

### New Components

| Component | Path | Purpose |
|-----------|------|---------|
| Discovery tool | `src/tools/discovery.py` | Read-only Azure inventory collectors (MGs, subs, resources, policies, RBAC, networking) |
| WARA engine | `src/tools/wara_engine.py` | Rule evaluation engine: 5 WAF pillars + 8 CAF areas, scoring, confidence |
| Report generator | `src/tools/report_generator.py` | Produces Markdown, JSON, and optional SARIF output |
| Check catalog | `src/config/wara_checks.yaml` | Declarative check definitions (extensible without code changes) |
| Assessment agent definition | `.github/agents/assessment.md` | 🔍 Assessor agent — orchestrates discover → assess → report |
| Assessment agent implementation | `src/agents/assessment_agent.py` | Python agent with Semantic Kernel integration |
| Brownfield discovery skill | `.github/skills/brownfield-discovery/SKILL.md` | KQL patterns for existing-state discovery |
| WARA assessment skill | `.github/skills/wara-assessment/SKILL.md` | WAF pillar checks, scoring model, severity definitions |
| Assessment report skill | `.github/skills/assessment-report/SKILL.md` | Report structure, templates, arch doc format |
| WARA checks instruction | `.github/instructions/wara-checks.instructions.md` | Conventions for writing `wara_checks.yaml` entries |
| Assessment workflow | `pipelines/github-actions/assess.yml` | GitHub Actions workflow for scheduled/on-demand assessment |
| Operator guide | `docs/operator-guide-assessment.md` | How to run assessments, required permissions, troubleshooting |
| Report templates | `src/config/templates/` | Jinja2/string templates for generated current-state docs, target-state docs, diagrams, ADRs |

### Modified Components

| Component | Change |
|-----------|--------|
| `src/agents/orchestrator.py` | Add `RunMode.ASSESS` and `RunMode.ONBOARD` modes |
| `.github/agents/orchestrator.md` | Document assess/onboard modes, Step 0/0.5 |
| `.github/agent-registry.json` | Add assessment agent entry |
| `src/config/settings.py` | Add `AssessSettings` class (scope, mode, output dir) |
| `.github/skills/caf-design-areas/SKILL.md` | Add brownfield assessment criteria per design area |
| `.github/skills/security-baseline/SKILL.md` | Add WARA security pillar mapping |
| `.github/skills/workflow-engine/templates/workflow-graph.json` | Add Step 0/0.5 DAG nodes |
| `mcp/azure-platform/server.py` | Add discovery tools (MG tree, subscription inventory, RBAC snapshot) |
| `src/tools/python_diagram_generator.py` | Add `generate_from_discovery()` for current-state diagrams |

### Unchanged Components

Everything else remains untouched — all existing IaC modules, platform LZ
deployment workflows, monitoring/remediation agents, validators, profiles, and
the existing 10-step workflow DAG.

## Architecture: Before and After

### Before (Current)

```
User → Requirements → Architecture → Design → Governance
     → Plan → Code → Deploy → Docs → Monitor ↔ Remediate
```

Entry point is always Step 1 (requirements). No way to start from an existing
environment.

### After (Target)

```
           ┌──────────────────────────────────────────┐
           │  Optional Pre-Workflow                    │
           │                                          │
           │  Step 0: Discover (read-only)            │
           │    ├─ MG hierarchy + subscriptions        │
           │    ├─ Resource inventory (Resource Graph) │
           │    ├─ Policy assignments + compliance     │
           │    ├─ RBAC assignments                    │
           │    ├─ Network topology                    │
           │    └─ Logging/monitoring/security posture │
           │                                          │
           │  Step 0.5: Assess                        │
           │    ├─ WAF 5-pillar scoring (0–100 each)  │
           │    ├─ CAF 8-area evaluation               │
           │    ├─ Findings with severity + confidence │
           │    └─ Prioritized recommendations         │
           └──────────┬───────────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │  Mode Decision          │
         │                         │
         │  assess-only → Report   │
         │  assess-and-plan → PR   │
         │  assess-and-remediate   │
         │    → Gated fixes        │
         │  onboard → Step 1       │
         │    (pre-filled reqs)    │
         └────────────┬────────────┘
                      │ (onboard only)
                      ▼
           Existing 10-step workflow
           (unchanged)
```

## Operational Modes

| Mode | Flag | Behavior | Changes Azure? |
|------|------|----------|----------------|
| `assess-only` | `--mode assess` | Discover + assess + report | No (read-only) |
| `assess-and-plan` | `--mode assess-and-plan` | Assess + generate remediation plan + PR checklist | No |
| `assess-and-remediate` | `--mode assess-and-remediate` | Assess + plan + execute fixes (gated) | Yes (with approval) |
| `onboard` | `--mode onboard` | Assess + pre-populate Step 1 requirements | No |
| `workflow` | `--mode workflow` | Existing greenfield flow | Yes |
| `deploy` | `--mode deploy` | Deploy only | Yes |
| `monitor` | `--mode monitor` | Continuous monitoring | No |

**Default is always read-only.** The `assess-and-remediate` mode requires
explicit `--allow-remediation` flag and gate approval before any changes.

## Assessment Rules Model

Each rule in `wara_checks.yaml` follows this structure:

```yaml
- id: SEC-001
  title: "TLS 1.2 minimum"
  pillar: security                    # WAF pillar
  caf_area: security                  # CAF design area
  alz_area: security                  # ALZ design area
  severity: critical                  # critical | high | medium | low
  confidence: high                    # high | medium | low
  scope: subscription                 # tenant | mg | subscription | rg
  query_type: resource_graph          # resource_graph | policy | advisor | defender | custom
  query: |
    resources
    | where type =~ 'microsoft.storage/storageaccounts'
    | where properties.minimumTlsVersion != 'TLS1_2'
  recommendation: "Set minimumTlsVersion to TLS1_2"
  remediation_steps:
    - "Update storage account TLS setting"
  references:
    - "https://learn.microsoft.com/azure/storage/common/transport-layer-security"
  mappings:
    waf_pillar: [security]
    caf_lifecycle: [govern, manage]
```

Evidence collection is **separated** from evaluation: discovery tools collect
raw state, and the WARA engine evaluates rules against that state.

## Scoring Model

Each WAF pillar is scored 0–100:

| Finding Severity | Deduction |
|-----------------|-----------|
| Critical | −20 |
| High | −10 |
| Medium | −5 |
| Low | −2 |

Overall score is a configurable weighted average across pillars (default: equal).
Confidence level on each finding helps operators prioritize reviews.

## Output Artifacts

The accelerator **generates** these artifacts for the assessed environment:

| Artifact | Format | Path | Description |
|----------|--------|------|-------------|
| Discovery inventory | JSON | `agent-output/assessment/00-discovery.json` | Raw inventory from Azure APIs |
| Assessment report | Markdown | `agent-output/assessment/00-assessment.md` | WAF/CAF scored findings |
| Findings (machine-readable) | JSON | `agent-output/assessment/00-assessment.json` | Structured findings for tooling |
| Current-state architecture | Markdown | `agent-output/assessment/00-current-state-architecture.md` | Generated doc describing the customer's environment as-is |
| Current-state diagram | Mermaid | `agent-output/assessment/00-current-state-diagram.mmd` | Generated topology from live Azure state |
| Target-state architecture | Markdown | `agent-output/assessment/00-target-state-architecture.md` | Generated doc describing ALZ-aligned target |
| ADR(s) | Markdown | `agent-output/assessment/adr/` | Generated decision records for recommended changes |
| Recommendations | JSON | `agent-output/assessment/00-recommendations.json` | Prioritized remediation list |
| SARIF (optional) | SARIF | `agent-output/assessment/00-assessment.sarif` | GitHub code scanning integration |

These are generated per-assessment-run, not static. The current-state and
target-state docs are populated from discovery data and rules evaluation.
ADRs are generated for significant architectural decisions the assessment
recommends (e.g., "adopt hub-spoke topology", "enable Defender for Cloud").

## Security Considerations

### Required Permissions (Read-Only Assessment)

| Scope | Role | Purpose |
|-------|------|---------|
| Management Group (root) | Reader | MG hierarchy discovery |
| Subscriptions | Reader | Resource inventory |
| Subscriptions | Policy Reader | Policy compliance state |
| Subscriptions | Security Reader | Defender for Cloud posture |

**No write permissions needed for assess-only mode.**

For `assess-and-remediate` mode, targeted write permissions are granted
per-resource-type through the existing OIDC identity, scoped to the specific
subscription being remediated.

### Safety Guarantees

- Default mode is **read-only** — no Azure state changes
- Remediation requires **explicit flag** (`--allow-remediation`)
- Remediation requires **gate approval** before execution
- Snapshot taken **before** any remediation for rollback
- No tenant-wide destructive operations
- No secret creation or sprawl
- All operations use existing OIDC identity (no new service principals)

## Migration Path

### For Greenfield Users

No change. The existing workflow works identically. Steps 0/0.5 are optional
and only invoked explicitly.

### For Brownfield Users

1. Run `--mode assess` to discover and assess existing environment
2. Review findings and recommendations
3. Optionally run `--mode onboard` to pre-fill requirements from discovery
4. Continue through existing workflow with delta-aware planning
5. Optionally run `--mode assess-and-remediate` for targeted fixes

### For Existing Deployed Estates

Run assessment against already-deployed platform LZs to identify drift,
compliance gaps, and optimization opportunities. Feeds into the existing
Day-2 monitoring and remediation loop.

## Generated Documentation Capability

The accelerator produces architecture documentation for **any** assessed
environment — not just its own. This works for both greenfield (post-deploy)
and brownfield (pre-onboard) scenarios.

### Current-State Architecture Doc (Generated)

Populated from discovery data, structured by CAF design area:

1. **Executive Summary** — tenant, subscription count, resource count, overall score
2. **Management Group Hierarchy** — Mermaid diagram + table
3. **Subscription Inventory** — name, MG placement, resource count, tags
4. **Per-CAF Design Area Assessment** — discovered state + findings per area
5. **WAF Pillar Scores** — table with score + finding counts per pillar
6. **Top Priority Recommendations** — from assessment rules

### Target-State Architecture Doc (Generated)

Describes the recommended ALZ-aligned end state:

1. **Proposed MG Hierarchy** — CAF enterprise-scale structure
2. **Subscription Placement** — where existing subs should move
3. **Policy Assignments** — recommended initiatives per MG level
4. **Networking Target** — hub-spoke/vWAN topology recommendation
5. **Delta Summary** — what changes vs current state, what stays

### Current-State Mermaid Diagram (Generated)

Generated from `00-discovery.json` showing actual MGs, subscriptions,
VNets, peerings, and key resources as discovered from Azure.

### ADR Generation (Generated)

For significant architectural recommendations, the accelerator generates
ADR-formatted decision records covering:

- Context (what was discovered)
- Decision (recommended change)
- Options considered
- Tradeoffs and risks
- Remediation steps
