---
name: python-diagrams
description: "Architecture diagram generation using the Python diagrams library with Azure provider icons. USE FOR: programmatic PNG/SVG diagram generation, CI/CD diagram automation. DO NOT USE FOR: interactive Draw.io diagrams (use drawio)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: tooling-diagrams
---

# Python Diagrams Skill

Generate architecture diagrams using the Python `diagrams` library.

## Tool Location

`src/tools/python_diagram_generator.py` — `DiagramEngine` class

## Available Diagram Types

| Method | Output | Description |
|--------|--------|-------------|
| `generate_mg_hierarchy()` | Management group tree | MG hierarchy with subscription placement |
| `generate_hub_spoke()` | Network topology | Hub-spoke with CIDRs, NSGs, route tables |
| `generate_security_governance()` | Security architecture | Defender, Sentinel, Key Vault, policies |
| `generate_alz_architecture()` | Full ALZ overview | Complete landing zone estate |
| `generate_for_profile()` | Profile-specific | Based on landing zone profile |
| `generate_full_estate()` | All diagrams | Generates all diagram types |

## Usage

```python
from src.tools.python_diagram_generator import DiagramEngine

engine = DiagramEngine(output_dir="docs/diagrams")

# Generate all diagrams
engine.generate_full_estate()

# Generate specific diagram
engine.generate_hub_spoke()
```

## Output Location

Diagrams are saved to `agent-output/{customer}/diagrams/` as PNG files:
- `01-management-group-hierarchy.png`
- `02-hub-spoke-network-topology.png`
- `03-security-governance-monitoring.png`
- `alz-architecture.png`

## Draw.io Alternative

For interactive diagrams, use the Draw.io MCP server:
- Produces `.drawio` files that can be edited in VS Code
- Better for detailed architecture documentation
- Use Python diagrams for quick overviews

## Customization

The DiagramEngine accepts parameters for:
- Hub CIDR ranges
- Spoke names and CIDRs
- Management group structure
- Region names
- Environment configurations
