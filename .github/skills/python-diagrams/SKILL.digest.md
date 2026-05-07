<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Python Diagrams Skill (Digest)

Generate architecture diagrams using the Python `diagrams` library with Azure provider icons.

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

## Output Location

Diagrams saved to `agent-output/{customer}/diagrams/` as PNG files: `01-management-group-hierarchy.png`, `02-hub-spoke-network-topology.png`, `03-security-governance-monitoring.png`, `alz-architecture.png`.

## Customization

Accepts parameters for: hub CIDR ranges, spoke names/CIDRs, MG structure, region names, environment configurations.

## Draw.io Alternative

For interactive `.drawio` diagrams editable in VS Code, use the `drawio` skill instead. Python diagrams are best for quick overviews and CI/CD automation.

> _See SKILL.md for usage examples._
