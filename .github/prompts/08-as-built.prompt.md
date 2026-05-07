---
agent: documentation
description: "Generate post-deployment Enterprise Landing Zone as-built documentation"
---

# Step 7: As-Built Documentation

Act as the Chronicler (📚). Generate comprehensive post-deployment documentation
for the Enterprise Landing Zone estate.

## Process

1. Read session state: `alz-recall show {customer} --json`
2. Read all previous artifacts (00 through 06) — use compression tiers if context is high
3. Query Azure Resource Graph for actual deployed state
4. Document each platform LZ (management, connectivity, identity, security) with deployed resources
5. Document management group hierarchy using customer `{prefix}` naming convention
6. Document hub-spoke topology: VNet CIDRs, peering state, Bastion, firewall
7. Validate all deployed resources against the 6 non-negotiable security baseline rules
8. Include WARA compliance summary (221 checks, per-pillar pass/fail)
9. Generate as-built design document
10. Create operational runbooks
11. Document security posture and compliance status

## Output

Produce in `agent-output/{customer}/`:
- `07-design-document.md` — Full as-built architecture (MG hierarchy, platform LZs, network topology)
- `07-operational-runbook.md` — Day-2 operations procedures
- `07-security-posture.md` — Security baseline compliance + Defender status
- `07-cost-baseline.md` — Deployed cost baseline and budget configuration

Record completion: `alz-recall complete-step {customer} 7 --json`

## Skills to reference

- `.github/skills/docs-writer/SKILL.md` — Documentation conventions
- `.github/skills/azure-diagnostics/SKILL.md` — Monitoring patterns
