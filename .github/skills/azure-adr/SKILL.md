---
name: azure-adr
description: "Creates Azure Architecture Decision Records with WAF mapping, alternatives, and consequences for Enterprise Landing Zone decisions. USE FOR: ADR creation, architecture decisions, trade-off analysis, WAF pillar justification. DO NOT USE FOR: Bicep/Terraform code generation, diagram creation, cost estimates."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool; no external dependencies required.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: document-creation
---

# Azure Architecture Decision Records (ADR) Skill

Create formal Architecture Decision Records that document significant Enterprise
Landing Zone infrastructure decisions with Azure-specific context, WAF pillar
analysis, and CAF design area alignment.

## When to Use This Skill

| Trigger | Use Case |
|---------|----------|
| "Create an ADR for..." | Document a specific architectural decision |
| "Document the decision to use..." | Record technology/pattern choice |
| "Record why we chose..." | Capture decision rationale |
| After Step 2 (Architecture) | Document key design decisions |
| After Step 6 (Deploy) | Document implementation deviations |

## Output Format

ADRs are saved to the customer's agent-output folder:

```text
agent-output/{customer}/
├── 03-des-adr-0001-{short-title}.md    # Design phase ADRs (Step 3)
└── 07-ab-adr-0001-{short-title}.md     # As-built phase ADRs (Step 7)
```

### Naming Convention

- **Prefix**: `03-des-adr-` (design) or `07-ab-adr-` (as-built)
- **Number**: 4-digit sequence (0001, 0002, etc.)
- **Title**: Lowercase with hyphens (e.g., `hub-spoke-over-vwan`)

## ADR Template

```markdown
# ADR-{NNNN}: {Title}

## Status
{Proposed | Accepted | Deprecated | Superseded by ADR-NNNN}

## Date
{YYYY-MM-DD}

## Context
{What is the problem or opportunity? What forces are at play?}

## Decision
{What is the change that we are proposing and/or doing?}

## CAF Design Area
{Which CAF design area(s) does this decision affect?}
- [ ] Billing & Tenant
- [ ] Identity & Access
- [ ] Resource Organization
- [ ] Network Topology & Connectivity
- [ ] Security
- [ ] Management
- [ ] Governance
- [ ] Platform Automation & DevOps

## Alternatives Considered

### Option A: {Name}
- **Pros**: ...
- **Cons**: ...
- **Why rejected**: ...

### Option B: {Name}
- **Pros**: ...
- **Cons**: ...
- **Why rejected**: ...

## WAF Pillar Analysis

| Pillar | Impact | Notes |
|--------|--------|-------|
| Reliability | {+/-/neutral} | ... |
| Security | {+/-/neutral} | ... |
| Cost Optimization | {+/-/neutral} | ... |
| Operational Excellence | {+/-/neutral} | ... |
| Performance Efficiency | {+/-/neutral} | ... |

## Consequences

### Positive
- ...

### Negative
- ...

## Implementation Notes
{Actionable guidance for the Forge agent (Bicep/Terraform)}

## Security Baseline Impact
{Which of the 6 security baseline rules are affected?}
```

## Common ALZ ADR Topics

| Category | Example Decisions |
|----------|-------------------|
| **Network** | Hub-spoke vs Virtual WAN, Azure Firewall vs NVA, private endpoints strategy |
| **Identity** | PIM vs static RBAC, Entra ID-only vs hybrid, managed identity strategy |
| **Governance** | Custom policy vs built-in, management group hierarchy depth |
| **Security** | Sentinel vs third-party SIEM, Defender plan selection, key management |
| **Management** | Central LAW vs distributed, diagnostic settings strategy |
| **Connectivity** | ExpressRoute vs VPN, DNS architecture, cross-region peering |
| **Platform** | Bicep vs Terraform, AVM module selection, deployment pipeline design |

## Integration with Workflow

| Step | Agent | ADR Type | Prefix |
|------|-------|----------|--------|
| Step 2 (Architect) | Oracle | Design ADR | `03-des-adr-` |
| Step 3 (Design) | Artisan | Design ADR | `03-des-adr-` |
| Step 5 (Code Gen) | Forge | As-built ADR | `07-ab-adr-` |
| Step 7 (Documentation) | Chronicler | As-built ADR | `07-ab-adr-` |

## Generation Workflow

1. **Gather context** from requirements (`01-requirements.md`) and architecture (`02-architecture-assessment.md`)
2. **Determine number** — check existing ADRs in `agent-output/{customer}/` for next sequence
3. **Determine phase** — Design (`03-des-`) before deployment, As-Built (`07-ab-`) after
4. **Generate document** using template above
5. **Include WAF analysis** — impact on all 5 pillars
6. **Map to CAF design area** — which of the 8 areas are affected
7. **Document alternatives** — at least 2 alternatives with rejection reasons

## Quality Checklist

- [ ] ADR number is sequential
- [ ] File name follows naming convention
- [ ] Status is Proposed (design) or Accepted (as-built)
- [ ] Context explains the problem clearly
- [ ] Decision is unambiguous
- [ ] At least 2 alternatives documented with rejection reasons
- [ ] WAF pillar analysis covers all 5 pillars
- [ ] CAF design area(s) identified
- [ ] Security baseline impact assessed
- [ ] At least 1 positive and 1 negative consequence

## Guardrails

**DO:** One decision per ADR · Include WAF analysis · Map to CAF design areas ·
Document security baseline impact · Reference requirements that drove the decision.

**DON'T:** Combine multiple decisions · Skip alternatives · Generate IaC code ·
Create diagrams (use `drawio` skill) · Hard-code resource names.
