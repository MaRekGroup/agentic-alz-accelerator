<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Session Resume Skill (Digest)

Restore context from a previous workflow session by scanning existing artifacts.

## Artifact → Step Mapping

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

## Resume Procedure

1. Scan `agent-output/{customer}/{project}/` for existing artifacts
2. Map artifacts to completed steps using the table above
3. Read the last completed artifact to restore context
4. Inform user: "Found artifacts through Step {N}. Ready to continue with Step {N+1}?"
5. Resume from the next uncompleted step

## Context Recovery

When resuming, always load: requirements document (foundation), last 2 completed artifacts (recent context), and governance constraints (downstream constraints).

## Session State

Orchestrator tracks: current step, complexity classification, gate approval status, IaC framework, target region, and environments.
