---
mode: orchestrator
description: "Generate post-deployment as-built documentation"
---

# Step 7: As-Built Documentation

Act as the Chronicler (📚). Generate comprehensive post-deployment documentation.

## Process

1. Read all previous artifacts (01 through 06)
2. Query Azure Resource Graph for actual deployed state
3. Generate as-built design document
4. Create operational runbooks
5. Document security posture and compliance status

## Output

Produce in `agent-output/{customer}/{project}/`:
- `07-design-document.md` — Full as-built architecture document
- `07-operational-runbook.md` — Day-2 operations procedures
- `07-security-posture.md` — Security baseline compliance report
- `07-cost-baseline.md` — Deployed cost baseline and budget configuration
