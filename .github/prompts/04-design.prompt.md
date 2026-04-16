---
mode: orchestrator
description: "Generate architecture diagrams and ADRs"
---

# Step 3: Design

Act as the Artisan (🎨). Generate architecture diagrams and Architecture Decision
Records (ADRs) based on the architecture assessment.

## Process

1. Read `agent-output/{project}/02-architecture-assessment.md`
2. Generate diagrams using the Python diagram engine (`src/tools/python_diagram_generator.py`) or Draw.io MCP
3. Create ADRs for key architectural decisions

## Diagrams to Generate

- Management group hierarchy with subscription placement
- Hub-spoke network topology with CIDRs and NSGs
- Security, governance, and monitoring architecture
- Full ALZ estate overview

## Output

Produce in `agent-output/{project}/`:
- `03-design-diagram.drawio` (or `.png` from Python diagrams engine)
- `03-design-adr-*.md` for key decisions
