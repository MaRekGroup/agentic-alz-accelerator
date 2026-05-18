# Project Context

- **Owner:** Yeselam Tesfaye
- **Project:** agentic-alz-accelerator
- **Stack:** Azure Landing Zone accelerator, Python, Bicep, Terraform, GitHub Actions, Markdown, YAML, and JSON
- **Description:** Multi-agent Azure Landing Zone accelerator with HVE workflow roles, agent prompts, skills, and deployment automation
- **Created:** 2026-05-08T21:31:32.689+00:00

## Core Context

Linus maps to the HVE architect role and owns target-state design reasoning.

## Recent Updates

📌 Team hired on 2026-05-08T21:31:32.689+00:00 by Yeselam Tesfaye

## Current Status

**2026-05-18:** Messaging positioning sprint completed. Three value propositions confirmed and decision merged to `.squad/decisions.md`. Awaiting Yeselam validation before sprint slice execution (S1: problem audit + value prop analysis).

## Key Learnings

**Three Differentiated Value Propositions (Confirmed across 2026-05-08 to 2026-05-14):**

1. **Enforcement (PRIMARY):** Three-tier (code → deploy → monitor+remediate)
   - Code-gen validators: 6 security rules + cost governance block PRs
   - Deployment gates: What-if preview + complexity-scaled approval
   - Continuous ops: 30-min compliance scans, 1-hr drift detection, auto-remediation with rollback
   - Unique vs ALZ: Official ALZ provides templates; we enforce compliance post-deployment continuously

2. **Knowledge Transfer (SECONDARY):** Algorithmic documentation with CAF traceability
   - Brownfield assessment (Step 0): Current-state + WAF/CAF evaluation + target-state roadmap
   - Greenfield workflow (Steps 1-7): Generated artifacts (requirements → architecture → design → code → deployment → docs)
   - CAF design area traceability: 8 areas mapped through every artifact end-to-end
   - Unique vs ALZ: Official ALZ is greenfield reference; we generate as-built docs + assess existing estates algorithmically

3. **Timeline (TERTIARY):** Parallelized orchestration with complexity-scaled gates
   - Concurrency: Design (Step 3) and Governance (Step 3.5) run parallel after Gate 2
   - Complexity tiers: Simple (1× pass), Standard (2×), Complex (3×)
   - AVM-first generation prevents rework loops
   - Impact: 8–12 weeks (manual) → 2–4 weeks (orchestrated)

**Messaging Strategy:** Lead with enforcement (broadest TAM: compliance/security teams), secondary knowledge (differentiates from generic IaC), tertiary speed (bonus for delivery teams).

**Full positioning analysis:** Archived to `.squad/agents/linus/history-archive.md`
