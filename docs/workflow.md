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

## Workflow Steps

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

Agents connect to Azure services via MCP servers:

| MCP Server | Tools | Used By |
|-----------|-------|---------|
| Azure Pricing | Cost estimation, region comparison, RI pricing | Architect, Planner, Chronicler |
| Azure Resource Graph | Resource queries, inventory, drift detection | Monitor, Remediate, Governance |
| Azure Policy | Policy discovery, compliance checking | Governance, Monitor, Challenger |
| Azure Deployment | Bicep/Terraform deploy, what-if, status | Deploy, Remediate |
| Azure Monitor | Secure score, recommendations, activity log | Monitor, Remediate, Chronicler |
