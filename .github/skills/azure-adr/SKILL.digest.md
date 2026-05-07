<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure ADR Skill (Digest)

Creates Architecture Decision Records for Enterprise Landing Zone decisions with WAF mapping and CAF alignment.

## When to Use

| Trigger | Use Case |
|---------|----------|
| "Create an ADR for..." | Document a specific architectural decision |
| After Step 2 (Architecture) | Document key design decisions |
| After Step 6 (Deploy) | Document implementation deviations |

## Output & Naming

- **Design ADRs:** `agent-output/{customer}/03-des-adr-NNNN-{short-title}.md`
- **As-built ADRs:** `agent-output/{customer}/07-ab-adr-NNNN-{short-title}.md`
- Number: 4-digit sequential; title: lowercase with hyphens

## Template Sections

Status → Date → Context → Decision → CAF Design Area (8 checkboxes) → Alternatives Considered (≥2) → WAF Pillar Analysis (5-pillar table: impact +/-/neutral) → Consequences (positive + negative) → Implementation Notes → Security Baseline Impact

> _See SKILL.md for the full template markdown._

## Common ALZ ADR Topics

| Category | Example Decisions |
|----------|-------------------|
| Network | Hub-spoke vs Virtual WAN, Azure Firewall vs NVA, private endpoints |
| Identity | PIM vs static RBAC, managed identity strategy |
| Governance | Custom policy vs built-in, MG hierarchy depth |
| Security | Sentinel vs third-party SIEM, Defender plan selection |
| Platform | Bicep vs Terraform, AVM module selection |

## Workflow Integration

| Step | Agent | ADR Prefix |
|------|-------|------------|
| Step 2/3 | Oracle/Artisan | `03-des-adr-` |
| Step 5/7 | Forge/Chronicler | `07-ab-adr-` |

## Quality Checklist

- [ ] Sequential ADR number with correct naming convention
- [ ] ≥2 alternatives with rejection reasons
- [ ] WAF analysis covers all 5 pillars
- [ ] CAF design area(s) identified
- [ ] Security baseline impact assessed
- [ ] ≥1 positive and ≥1 negative consequence

> _See SKILL.md for full generation workflow and guardrails._
