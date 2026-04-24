# ADR-0001: Brownfield Discovery and WARA/CAF Assessment

| Field | Value |
|-------|-------|
| **Status** | Proposed |
| **Date** | 2026-04-23 |
| **Decision Makers** | Platform Engineering Team |
| **Scope** | Agentic ALZ Accelerator |

## Context

The Agentic ALZ Accelerator currently supports only **greenfield** deployments —
the workflow starts at "gather requirements" and generates IaC from scratch. This
limits adoption by organizations that already have:

- Existing management group hierarchies (possibly non-ALZ)
- Existing subscriptions with deployed resources
- Existing policy assignments, RBAC, and networking
- Partial ALZ adoption (some landing zones already built)

Additionally, there is no assessment capability that evaluates an existing
environment against the Azure Well-Architected Framework (WAF) pillars or
Cloud Adoption Framework (CAF) design areas.

## Decision

Add **brownfield discovery** and **WARA/CAF assessment** as optional pre-workflow
steps (Step 0 and Step 0.5) that:

1. Discover existing Azure state via read-only APIs (Resource Graph, ARM, Policy)
2. Evaluate findings against a declarative rules catalog aligned to WAF pillars
   and CAF design areas
3. Produce scored reports (Markdown + JSON) with prioritized recommendations
4. Optionally feed into the existing workflow via "onboard" mode

The existing greenfield workflow remains completely unchanged.

## Options Considered

### Option A: Extend Existing Monitoring Agent

Expand the Sentinel agent to include assessment capabilities alongside its
existing compliance scanning.

**Pros:** No new agent; reuses existing infrastructure.
**Cons:** Monitoring agent is scoped to deployed LZs, not arbitrary tenants.
Its scheduling model (periodic scans) doesn't fit one-shot assessment.
Mixing assessment and monitoring creates a bloated agent with conflicting
concerns.

### Option B: New Assessment Agent with Shared Tools (Selected)

Create a dedicated Assessment agent (🔍 Assessor) that reuses existing tools
(`ResourceGraphClient`, `PolicyChecker`, `DriftDetector`) and adds new ones
(`discovery.py`, `wara_engine.py`, `report_generator.py`).

**Pros:** Clean separation of concerns. Reuses existing tool layer. Rules
are declarative and extensible. Assessment is scope-aware (tenant/MG/sub/RG).
**Cons:** New agent to maintain. Some overlap with monitoring agent's
compliance checks.

### Option C: External Assessment Tool (e.g., Azure Advisor Export)

Use Azure Advisor recommendations and Defender for Cloud secure score as the
sole assessment source.

**Pros:** No custom rules to maintain. Leverages Microsoft's built-in
intelligence.
**Cons:** No CAF design area mapping. No custom rules for ALZ-specific
patterns. No offline/repo-only assessment. Limited to Azure's built-in
checks which don't cover all WAF pillars equally.

### Option D: Full Rewrite with Assessment-First Architecture

Redesign the entire accelerator around assessment as the primary entry point.

**Pros:** Coherent architecture from the ground up.
**Cons:** Massive scope. Breaks existing workflows. Not incremental.
Violates the "extend, don't replace" principle.

## Decision Rationale

**Option B** was selected because it:

- Follows the existing multi-agent pattern (each agent has a clear responsibility)
- Reuses existing tools rather than building from scratch
- Keeps assessment and monitoring as separate concerns with a shared tool layer
- Enables incremental delivery (discovery first, then rules, then reports)
- Does not modify any existing workflow paths
- Supports the "read-only by default" safety principle

## Architecture Impact

### New Files

| Type | Path | Purpose |
|------|------|---------|
| Tool | `src/tools/discovery.py` | Read-only Azure inventory collectors |
| Tool | `src/tools/wara_engine.py` | Rule evaluation engine with WAF/CAF scoring |
| Tool | `src/tools/report_generator.py` | Markdown, JSON, optional SARIF output |
| Config | `src/config/wara_checks.yaml` | Declarative check catalog |
| Agent | `.github/agents/assessment.md` | Assessor agent definition |
| Agent | `src/agents/assessment_agent.py` | Assessor agent implementation |
| Skills | `.github/skills/{brownfield-discovery,wara-assessment,assessment-report}/SKILL.md` | Domain knowledge |
| Instruction | `.github/instructions/wara-checks.instructions.md` | Check authoring conventions |
| Workflow | `pipelines/github-actions/assess.yml` | GitHub Actions entry point |
| Docs | `docs/operator-guide-assessment.md` | Operator guide |

### Modified Files

| File | Change |
|------|--------|
| `src/agents/orchestrator.py` | Add ASSESS/ONBOARD run modes |
| `.github/agents/orchestrator.md` | Document new modes |
| `.github/agent-registry.json` | Register assessment agent |
| `src/config/settings.py` | Add AssessSettings |
| `mcp/azure-platform/server.py` | Add discovery MCP tools |
| `src/tools/python_diagram_generator.py` | Add `generate_from_discovery()` |
| Workflow DAG template | Add Step 0/0.5 nodes |
| CAF/security skills | Add assessment-specific criteria |

### Unchanged

All existing IaC modules, deployment workflows, monitoring/remediation agents,
validators, profiles, and the 10-step APEX workflow DAG.

## Security Impact

### Read-Only Assessment (Default)

- Requires only `Reader`, `Policy Reader`, and `Security Reader` roles
- No Azure state changes
- No new service principals — uses existing OIDC identity
- No secret creation or management

### Remediation Mode (Opt-In)

- Requires explicit `--allow-remediation` flag
- Gate approval before any write operations
- Snapshot before changes for rollback
- Scoped to specific subscriptions (not tenant-wide)

### Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Assessment reveals sensitive data in reports | Reports stored locally in `agent-output/{customer}/`; no automatic upload |
| Remediation causes outage | Snapshot/rollback pattern; gated approval; critical-only auto-remediate |
| Scope creep to destructive operations | Default mode is read-only; remediation requires double opt-in |
| OIDC identity over-permissioned for assessment | Document minimum required roles per mode |

## Operational Impact

- **New dependency:** None — reuses existing Azure SDK and Resource Graph
- **New permissions:** `Reader` + `Policy Reader` + `Security Reader` at target scope
- **New scheduling:** Optional scheduled assessment via `assess.yml` workflow
- **Monitoring overlap:** Assessment findings complement (not replace) Day-2 monitoring; assessment is point-in-time while monitoring is continuous

## Tradeoffs

| Tradeoff | Decision |
|----------|----------|
| Custom rules vs Azure Advisor only | Custom rules — more coverage, CAF/ALZ mapping, offline capability |
| Single agent vs split discover/assess agents | Single agent with internal phases — simpler orchestration |
| YAML rules vs Python rules | YAML — extensible without code changes; Python fallback for complex logic |
| Mermaid vs Draw.io for generated diagrams | Mermaid — renders in GitHub natively; Draw.io for manual diagrams |
| SARIF output | Nice-to-have — implemented after core MD/JSON output is stable |

## Consequences

### Positive

- Brownfield adoption path unlocked
- Assessment provides quantified WAF/CAF scoring
- Declarative rules are easy to extend and audit
- Existing users are unaffected

### Negative

- New agent and tools to maintain
- Rules catalog requires ongoing curation as Azure evolves
- Some assessment checks overlap with monitoring agent's compliance scans

### Neutral

- Assessment output format becomes a de facto API contract (JSON schema)
- May drive future refactoring of monitoring agent to share rules with assessment
