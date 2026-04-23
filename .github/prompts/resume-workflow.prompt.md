---
mode: orchestrator
description: "Resume an interrupted APEX workflow from the last completed step"
---

# Resume Workflow

Resume a previously interrupted APEX workflow session.

## Process

1. Check `agent-output/{customer}/{project}/` for existing artifacts
2. Determine the last completed step based on artifact presence:
   - `01-requirements.md` → Step 1 done
   - `02-architecture-assessment.md` → Step 2 done
   - `03-design-*` → Step 3 done
   - `04-governance-constraints.*` → Step 3.5 done
   - `04-implementation-plan.md` → Step 4 done
   - IaC files in `infra/` → Step 5 done
   - `06-deployment-summary.md` → Step 6 done
   - `07-*.md` → Step 7 done
3. Read the last completed artifact to restore context
4. Resume from the next uncompleted step

## Ask the user

"I found artifacts through Step {N}. Ready to continue with Step {N+1}?"
