# Agent Workflow

The multi-step platform engineering workflow — how agents execute each step with
artifact handoffs and approval gates.

## Overview

The Agentic ALZ Accelerator uses a multi-agent orchestration system where specialized
AI agents coordinate through artifact handoffs to transform Azure Landing Zone
requirements into deployed, governed, and continuously monitored infrastructure.

The system supports dual IaC tracks — Bicep and Terraform — sharing common requirements,
architecture, design, and governance steps (1–3.5) then diverging into track-specific
planning, code generation, and deployment (steps 4–6) before converging for
documentation (step 7) and continuous operations (steps 8–9).

The accelerator supports both **greenfield** (new environment) and **brownfield**
(existing environment) scenarios. For brownfield, an optional Step 0 runs a
WAF-aligned assessment of the current estate before the standard workflow begins.

## Workflow Steps

### Step 0: Assessment (🔍 Assessor) [Brownfield Only]
- Discover existing Azure environment via Resource Graph
- Run WAF Reliability Assessment (WARA) against 28-check catalog
- Generate current-state and target-state architecture documentation
- Output: `00-assessment-*.{md,json,mmd}` in `agent-output/assessment/<scope>/`

### Step 1: Requirements (📜 Scribe)
- Gather landing zone requirements through interactive conversation
- Map requirements to all 8 CAF design areas
- Classify complexity (Simple / Standard / Complex)
- Output: `01-requirements.md`

### Step 2: Architecture (🏛️ Oracle)
- WAF pillar assessment (Reliability, Security, Cost, Operations, Performance)
- CAF design area mapping and recommendations
- Real-time cost estimation via Azure Pricing MCP
- Output: `02-architecture-assessment.md`

### Step 3: Design (🎨 Artisan) [Optional]
- Architecture diagrams and ADRs
- Output: `03-design-*.{drawio,png,md}`

### Step 3.5: Governance (🛡️ Warden)
- Azure Policy discovery via REST API
- Policy effect classification (Deny, Audit, Modify, DINE)
- Security baseline enforcement rules
- Output: `04-governance-constraints.md/.json`

### Step 4: Planning (📐 Strategist)
- Implementation plan using governance constraints as input
- AVM module selection (Bicep or Terraform track)
- Resource dependency mapping
- CAF naming convention validation
- Output: `04-implementation-plan.md`

### Step 5: Implementation (⚒️ Forge)
- Generate IaC templates following AVM standards
- Security baseline enforcement at code generation
- Preflight validation via subagents (lint + what-if/plan)
- Output: `infra/{bicep,terraform}/{project}/`

### Step 6: Deployment (🚀 Envoy)
- Pre-deploy security review (Challenger + security baseline validator)
- What-if/plan preview before apply
- Post-deployment resource verification
- Output: `06-deployment-summary.md`

### Step 7: Documentation (📚 Chronicler)
- Design document, operations runbook, resource inventory
- As-built cost estimate, compliance matrix, backup/DR plan
- Output: `07-*.md` documentation suite

### Step 8: Monitor (🔭 Sentinel) [Continuous]
- Compliance scans every 30 minutes
- Drift detection every hour via Resource Graph
- Security posture from Defender for Cloud
- Full audit daily at 6 AM
- Output: `08-compliance-report.md`

### Step 9: Remediate (🔧 Mender) [Event-Driven]
- Auto-remediation for critical/high violations
- Snapshot before remediation for rollback
- Escalation for medium/low severity
- Output: `09-remediation-log.md`

## Approval Gates

| Gate | After Step | User Action |
|------|-----------|-------------|
| Gate 1 | Requirements | Confirm requirements complete |
| Gate 2 | Architecture | Approve WAF/CAF assessment |
| Gate 3 | Governance | Approve governance constraints |
| Gate 4 | Planning | Approve implementation plan |
| Gate 5 | Code Gen | Approve lint/review/what-if results |
| Gate 6 | Deployment | Verify deployed resources |

> **Never skip gates.** The Challenger agent reviews outputs at gates 1, 2, 4, and 5.

## MCP Tool Integration

Agents connect to Azure services via 3 MCP servers:

| MCP Server | Tools | Used By |
|-----------|-------|---------|
| Azure Pricing | Cost estimation, region comparison, SKU pricing (18 tools) | Architect, Planner, Chronicler |
| Azure Platform | Resource Graph, Policy, Deployment, Monitor, RBAC, WARA Assessment (27 tools, consolidated) | All agents |
| Draw.io | Architecture diagram generation with Azure icons | Artisan |

## Agent Tools (`src/tools/`)

Agents invoke these Azure SDK integrations during workflow execution:

| Tool | Module | Used By |
|------|--------|---------|
| Bicep Deployer | `bicep_deployer.py` | Envoy, Mender |
| Terraform Deployer | `terraform_deployer.py` | Envoy, Mender |
| Policy Checker | `policy_checker.py` | Warden, Sentinel |
| Resource Graph | `resource_graph.py` | Sentinel, Mender, Warden |
| Drift Detector | `drift_detector.py` | Sentinel |
| Diagram Generator | `azure_diagram_generator.py` | Artisan, Chronicler |
| Python Diagrams | `python_diagram_generator.py` | Artisan |
| TDD Generator | `tdd_generator.py` | Chronicler |
| Discovery Collector | `discovery_collector.py` | Assessor |
| WARA Engine | `wara_engine.py` | Assessor |
| Report Generator | `report_generator.py` | Assessor, Chronicler |
| Assessment CLI | `assess_cli.py` | Assessor (via GitHub Actions) |

## Profile Configuration

Agent behavior is governed by a 3-tier YAML profile inheritance system:

1. **Base** (`profiles/base-platform.yaml`) — shared defaults
2. **Child** (`profiles/platform-{connectivity,identity,management,security}.yaml`) — LZ-specific
3. **Override** (`profiles/overrides/{dev,prod}/platform-*.yaml`) — environment-specific

See `src/config/profile_loader.py` for the merge logic.

## Test Coverage

107 tests validate agent workflows across 6 test files:

| Test File | Covers |
|-----------|--------|
| `test_deployment_agent.py` | Profile loading, what-if, deploy, validation |
| `test_monitoring_agent.py` | Compliance scan, drift detection, security posture |
| `test_remediation_agent.py` | Strategies, single/multi remediation, history |
| `test_assess_cli.py` | CLI summary, fallback subscription, exit codes |
| `test_assessment_agent.py` | Init, full pipeline, defaults, fallback, discovery-only |
| `test_integration_assessment.py` | E2E pipeline, check catalog integrity |
