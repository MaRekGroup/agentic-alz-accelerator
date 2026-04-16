---
mode: orchestrator
description: "Perform WAF assessment and CAF design area mapping"
---

# Step 2: Architecture Assessment

Act as the Oracle (🏛️). Perform a Well-Architected Framework assessment and
CAF design area mapping based on the requirements in `01-requirements.md`.

## Process

1. Read `agent-output/{project}/01-requirements.md`
2. Assess against all 5 WAF pillars: Security, Reliability, Cost, Performance, Operations
3. Map each requirement to the appropriate CAF design area and IaC module
4. Estimate cost ranges for the proposed architecture
5. Identify risks and recommendations

## Output

Produce `02-architecture-assessment.md` with:
- WAF pillar scoring (1-5 per pillar)
- CAF design area → IaC module mapping
- Cost estimation (monthly ranges per environment)
- Risk register with mitigations
- Architecture recommendations

## Skills to reference

- `.github/skills/caf-design-areas/SKILL.md`
- `.github/skills/cost-governance/SKILL.md`
