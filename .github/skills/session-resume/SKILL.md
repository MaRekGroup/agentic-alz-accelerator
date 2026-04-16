---
name: session-resume
description: "Workflow session state restoration and context recovery for multi-step ALZ deployments. USE FOR: resuming interrupted workflows, restoring agent session state. DO NOT USE FOR: new workflow initialization (use workflow-engine)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: tooling-workflow
---

# Session Resume Skill

Restore context from a previous workflow session.

## How to Resume

1. Check `agent-output/{project}/` for existing artifacts
2. Map artifacts to completed steps:

| Artifact Present | Step Completed |
|-----------------|---------------|
| `01-requirements.md` | Step 1: Requirements |
| `02-architecture-assessment.md` | Step 2: Architecture |
| `03-design-*` | Step 3: Design |
| `04-governance-constraints.*` | Step 3.5: Governance |
| `04-implementation-plan.md` | Step 4: IaC Planning |
| Files in `infra/{bicep,terraform}/` | Step 5: Code Generation |
| `06-deployment-summary.md` | Step 6: Deployment |
| `07-*.md` | Step 7: Documentation |
| `08-compliance-report.md` | Step 8: Monitoring |
| `09-remediation-log.md` | Step 9: Remediation |

3. Read the last completed artifact to restore context
4. Inform the user: "Found artifacts through Step {N}. Ready to continue with Step {N+1}?"
5. Resume from the next uncompleted step

## Context Recovery

When resuming, load:
- The requirements document (always — it's the foundation)
- The last 2 completed artifacts (for recent context)
- The governance constraints (always — they constrain downstream work)

## Session State

The orchestrator tracks session state including:
- Current step
- Complexity classification
- Gate approval status
- IaC framework (Bicep or Terraform)
- Target region and environments
