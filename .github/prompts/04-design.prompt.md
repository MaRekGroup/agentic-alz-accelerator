---
mode: orchestrator
description: "Generate Enterprise Landing Zone architecture diagrams and ADRs"
---

# Step 3: Design

Act as the Artisan (🎨). Generate architecture diagrams and Architecture Decision
Records (ADRs) for the Enterprise Landing Zone based on the architecture assessment.

## Process

1. Read `agent-output/{customer}/02-architecture-assessment.md`
2. Generate diagrams using the Python diagram engine (`src/tools/python_diagram_generator.py`) or Draw.io MCP
3. Create ADRs for key architectural decisions
4. Record design decisions: `alz-recall decide {customer} --key diagram_type --value {drawio|python} --json`

## Diagrams to Generate

- Management group hierarchy using customer `{prefix}` and platform/app LZ subscription placement
- Hub-spoke network topology with CIDRs, peering, Bastion, optional firewall
- Security, governance, and monitoring architecture
- Full ALZ estate overview showing all 4 platform LZs

## Output

Produce in `agent-output/{customer}/`:
- `03-design-diagram.drawio` (or `.png` from Python diagrams engine)
- `03-design-adr-*.md` for key decisions
