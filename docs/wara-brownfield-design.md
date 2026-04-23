# WARA/Brownfield Enhancement — Design Document

> **Branch:** `features-enhancement-wara`
> **Status:** Planned — not yet implemented
> **Date:** 2026-04-22

## Overview

Enhance the Agentic ALZ Accelerator to support **brownfield** environments (existing
tenant/MG/subscriptions) and add an **Assess** feature that outputs WARA (Well-Architected
Review Assessment) + CAF-aligned findings and recommendations with current-state
architecture documentation.

## Problem Statement

The current accelerator is **greenfield-only**: the workflow starts at "gather requirements"
and generates IaC from scratch. There is no mechanism to:

1. Discover what already exists in an Azure tenant
2. Assess the existing environment against Well-Architected and CAF standards
3. Produce a current-state architecture document and diagram
4. Onboard an existing environment into the accelerator workflow

## Design Principles

- **Read-only by default** — `--mode assess` never modifies Azure resources
- **Reuse existing tools** — `resource_graph.py`, `policy_checker.py`, `drift_detector.py`
- **Declarative checks** — `wara_checks.yaml` catalog, easy to extend without code changes
- **Existing workflow untouched** — new Steps 0/0.5 are optional pre-workflow; the 10-step
  DAG stays the same

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Brownfield Entry Point                             │
│                                                     │
│  python -m src.agents.orchestrator                  │
│    --mode assess                                    │
│    --scope /providers/.../managementGroups/mrg       │
│    --output agent-output/{customer}/assessment/      │
│                                                     │
│  OR: --mode onboard (assess + generate import IaC) │
└─────────────┬───────────────────────────────────────┘
              │
   ┌──────────▼──────────┐
   │  Step 0: Discover    │  ← src/tools/discovery.py
   │  • MG hierarchy      │    Uses: Resource Graph
   │  • Subscriptions     │    Uses: ARM Management API
   │  • Resource inventory│    Uses: resource_graph.py (existing)
   │  • Policy assignments│    Uses: policy_checker.py (existing)
   │  • RBAC assignments  │    Uses: Authorization API
   │  • Network topology  │    Uses: Resource Graph
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Step 0.5: Assess    │  ← src/agents/assessment_agent.py
   │                      │  ← src/tools/wara_engine.py
   │  WAF 5 Pillars:      │    Data Source:
   │  ├─ Reliability      │    Resource Graph + Advisor
   │  ├─ Security         │    Defender Secure Score + Policy
   │  ├─ Cost Optim.      │    Advisor + Budget checks
   │  ├─ Oper. Excellence │    Diagnostic settings + Monitor
   │  └─ Performance      │    SKU analysis + Resource Graph
   │                      │
   │  CAF 8 Areas:        │    Data Source:
   │  ├─ Billing/Tenant   │    Discovery (MGs, subs)
   │  ├─ Identity/Access  │    RBAC + PIM status
   │  ├─ Resource Org     │    MG hierarchy + tags
   │  ├─ Network          │    VNet topology, NSGs
   │  ├─ Security         │    Defender, KV, encryption
   │  ├─ Management       │    LAW, diagnostics, backup
   │  ├─ Governance       │    Policy assignments
   │  └─ Platform Auto.   │    Detect IaC presence
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Outputs:            │
   │  • 00-discovery.json │  Raw inventory
   │  • 00-assessment.md  │  WARA-aligned report
   │  • 00-assessment.json│  Machine-readable findings
   │  • 00-current-state- │  Per-CAF-area architecture doc
   │    architecture.md   │
   │  • 00-current-state- │  Visual topology (PNG + drawio)
   │    diagram.png/.drawio│
   │  • 00-recommendations│  Prioritized fix list
   │    .json             │
   │                      │
   │  If --mode onboard:  │
   │  → Feed into Step 1  │  (pre-filled requirements)
   └──────────────────────┘
```

## Scoring Model

Each WAF pillar gets a 0–100 score:

| Finding Severity | Point Deduction |
|-----------------|-----------------|
| Critical | −20 |
| High | −10 |
| Medium | −5 |
| Low | −2 |

- Base score = 100 per pillar
- Overall score = weighted average (configurable weights, default equal)

## Check Catalog (`wara_checks.yaml`)

Check IDs use pillar prefixes:

| Prefix | Pillar |
|--------|--------|
| `REL-` | Reliability |
| `SEC-` | Security |
| `COS-` | Cost Optimization |
| `OPE-` | Operational Excellence |
| `PER-` | Performance Efficiency |

Example check:

```yaml
checks:
  - id: REL-001
    pillar: reliability
    caf_area: management
    name: "Availability zones enabled"
    severity: high
    query_type: resource_graph
    query: |
      resources
      | where type in~ ('microsoft.compute/virtualmachines', ...)
      | where isnull(zones) or array_length(zones) == 0
    recommendation: "Enable availability zones for production workloads"
    wara_category: "HA & Resiliency"

  - id: SEC-001
    pillar: security
    caf_area: security
    name: "TLS 1.2 minimum"
    severity: critical
    source: governance_agent  # reuse existing SECURITY_BASELINE
    recommendation: "Set minimumTlsVersion to TLS1_2"
```

## Current-State Architecture Document (`00-current-state-architecture.md`)

Auto-generated from discovery data, structured by CAF design area:

1. **Executive Summary** — tenant, sub count, resource count, overall score
2. **Management Group Hierarchy** — Mermaid diagram + table
3. **Subscription Inventory** — name, MG placement, resource count, tags
4. **Per-CAF Design Area Assessment** (A–H) — discovered state + findings
5. **WARA Pillar Scores** — table with score + finding counts
6. **Top 10 Priority Recommendations** — from assessment

## Current-State Diagram

New method in `python_diagram_generator.py`:

```python
def generate_from_discovery(self, discovery_data: dict) -> str:
    """Generate architecture diagram from brownfield discovery data."""
```

Takes `00-discovery.json` and produces a topology diagram showing actual
MGs, subscriptions, VNets, peerings, and key resources.

## New Files (9)

| # | Type | File | Purpose |
|---|------|------|---------|
| 1 | Skill | `.github/skills/wara-assessment/SKILL.md` | WAF 5-pillar check catalog, scoring, severity defs |
| 2 | Skill | `.github/skills/brownfield-discovery/SKILL.md` | KQL patterns for discovering existing state |
| 3 | Skill | `.github/skills/assessment-report/SKILL.md` | Report structure, templates, arch doc format |
| 4 | Agent | `.github/agents/assessment.md` | 🔍 Assessor agent definition |
| 5 | Instruction | `.github/instructions/wara-checks.instructions.md` | Conventions for wara_checks.yaml |
| 6 | Python | `src/agents/assessment_agent.py` | Assessor agent implementation |
| 7 | Python | `src/tools/wara_engine.py` | Check engine: 5-pillar + 8-area checks, scoring |
| 8 | Python | `src/tools/discovery.py` | Brownfield discovery: MGs, subs, resources, policies |
| 9 | YAML | `src/config/wara_checks.yaml` | Declarative check catalog |

## Modified Files (9)

| # | Type | File | Change |
|---|------|------|--------|
| 1 | Agent | `.github/agents/orchestrator.md` | Add assess/onboard modes, Step 0/0.5 |
| 2 | Skill | `.github/skills/caf-design-areas/SKILL.md` | Add brownfield assessment criteria |
| 3 | Skill | `.github/skills/security-baseline/SKILL.md` | Add WARA security pillar mapping |
| 4 | JSON | `.github/agent-registry.json` | Add assessment agent entry |
| 5 | Python | `src/agents/orchestrator.py` | Add RunMode.ASSESS/ONBOARD, wire agent |
| 6 | Python | `src/config/settings.py` | Add AssessSettings class |
| 7 | JSON | `.github/skills/workflow-engine/templates/workflow-graph.json` | Add Step 0/0.5 nodes |
| 8 | Python | `mcp/azure-platform/server.py` | Add 3 discovery tools |
| 9 | Python | `src/tools/python_diagram_generator.py` | Add generate_from_discovery() |

## Agent Registry Entry

```json
"assessment": {
  "agent": ".github/agents/assessment.md",
  "codename": "Assessor",
  "emoji": "🔍",
  "step": 0,
  "scope": "estate",
  "delegation": "autonomous",
  "skills": [
    "wara-assessment", "brownfield-discovery", "assessment-report",
    "caf-design-areas", "security-baseline", "azure-compliance",
    "azure-cost-optimization", "azure-diagnostics", "azure-rbac"
  ],
  "invokable": true,
  "description": "Brownfield discovery and WARA/CAF-aligned assessment"
}
```

## Workflow Modes

| Mode | CLI Flag | Behavior |
|------|----------|----------|
| `assess` | `--mode assess` | Read-only: discover + assess + report |
| `onboard` | `--mode onboard` | Assess then pre-populate Step 1 requirements |
| `workflow` | `--mode workflow` | Existing greenfield flow (unchanged) |
| `deploy` | `--mode deploy` | Deploy only (unchanged) |
| `monitor` | `--mode monitor` | Continuous monitoring (unchanged) |
| `full` | `--mode full` | Deploy + monitor (unchanged) |

## Reused Existing Components

| Existing Component | Reused For |
|-------------------|-----------|
| `resource_graph.py` — `query()`, `get_resource_inventory()` | Discovery |
| `policy_checker.py` — `get_compliance_state()`, `get_violations()` | WARA policy pillar |
| `drift_detector.py` — `MONITORED_PROPERTIES` | Security/reliability checks |
| `governance_agent.py` — `SECURITY_BASELINE`, `EXTENDED_CHECKS` | Security pillar checks |
| MCP `get_secure_score`, `get_recommendations` | Security + reliability |
| MCP `find_public_resources` | Security findings |
| MCP `check_diagnostic_settings` | Operational excellence |
| `python_diagram_generator.py` | Current-state diagrams |
