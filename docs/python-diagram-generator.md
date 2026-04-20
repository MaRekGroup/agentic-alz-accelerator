# Python Diagram Generator — Technical Documentation

## Overview

The Python Diagram Generator produces architecture diagrams for Azure Landing Zone
Technical Design Documents (TDDs). It uses the
[mingrammer/diagrams](https://diagrams.mingrammer.com/) library with Graphviz
auto-layout and official Azure architecture icons.

| Attribute | Value |
|-----------|-------|
| Source | `src/tools/python_diagram_generator.py` |
| Class | `DiagramEngine` |
| Output format | PNG (via Graphviz `dot` engine) |
| Icon source | `diagrams.azure.*` — official Microsoft Azure icon set |
| Layout engine | Graphviz (automatic — no manual x/y coordinates) |
| Dependencies | `diagrams`, `graphviz` (system package) |

## Architecture

```text
┌──────────────────────┐     ┌─────────────────────┐
│  tdd_generator.py    │────▶│ DiagramEngine       │
│  (TDDGenerator)      │     │                     │
│  - generate()  docx  │     │ generate_tdd_diagram│──▶ Per-LZ PNG
│  - generate_markdown  │     │ generate_full_estate│──▶ Estate PNG
└──────────────────────┘     │ generate_mg_hierarchy│──▶ Shared PNG
                             │ generate_hub_spoke   │──▶ Shared PNG
                             │ generate_security_*  │──▶ Shared PNG
                             │ generate_alz_arch    │──▶ Shared PNG
                             └─────────────────────┘
                                      │
                                      ▼
                              Graphviz dot engine
                                      │
                                      ▼
                                 PNG output
```

## Diagram Types

### Shared Platform Diagrams (4)

Generated to `docs/diagrams/` by `generate_all_diagrams()`:

| Method | Filename | Direction | Description |
|--------|----------|-----------|-------------|
| `generate_mg_hierarchy()` | `01-management-group-hierarchy.png` | TB | MG tree with subscription placement and policy inheritance |
| `generate_hub_spoke()` | `02-hub-spoke-network-topology.png` | LR | Hub VNet, spokes, subnets, Firewall, DNS, on-prem gateway |
| `generate_security_governance()` | `03-security-governance-monitoring.png` | TB | Governance, identity, security, and monitoring flows |
| `generate_alz_architecture()` | `alz-architecture.png` | TB | Full ALZ overview: platform subs, LZ subs, cross-cutting |

### TDD Per-Landing-Zone Diagrams (10)

Generated to `docs/tdd/` by `generate_tdd_diagram()`, dispatched by profile:

| Profile | Method | Direction | Key Components |
|---------|--------|-----------|---------------|
| `platform-management` | `_tdd_management()` | TB | LAW, Sentinel, Monitor, App Insights, Automation, Budget |
| `platform-connectivity` | `_tdd_connectivity()` | TB | Hub VNet (GW + FW + Bastion), DNS, DDoS, UDR |
| `platform-identity` | `_tdd_identity()` | LR | Entra ID, Entra DS, Entra Connect, PIM, Key Vault |
| `platform-security` | `_tdd_security()` | LR | Sentinel, Defender, Key Vault, Secure Score, Policy |
| `corp` | `_tdd_app_lz()` | LR | Spoke VNet, NSG, ContainerApps, Private Endpoints, Cosmos DB |
| `online` | `_tdd_app_lz()` | LR | Spoke VNet, NSG, Front Door, App GW + WAF, Cosmos DB |
| `sap` | `_tdd_app_lz()` | LR | Spoke VNet, NSG, VM, Internal LB, SAP HANA DB |
| `sandbox` | `_tdd_app_lz()` | LR | Spoke VNet, NSG, ContainerApps, Private Endpoints, Cosmos DB |

### Full Estate Overview (1)

| Method | Filename | Description |
|--------|----------|-------------|
| `generate_full_estate()` | `alz-estate-overview.png` | All platform + app LZs grouped by profile, cross-cutting services |

## Integration with TDD Generator

The `TDDGenerator` class in `src/tools/tdd_generator.py` calls `DiagramEngine` in
two places:

### 1. Word Document (`.docx`) Generation

```python
# In TDDGenerator._generate_png_diagram()
engine = DiagramEngine(output_dir="docs/tdd")
png_path = engine.generate_tdd_diagram(
    profile=self.profile,           # e.g. "platform-management"
    project_name=self.project_name, # e.g. "management"
    subscription_name=self.subscription_name,
    location=self.location,
)
# PNG inserted into Word doc via python-docx
```

### 2. Markdown (`.md`) Generation

```python
# In TDDGenerator.generate_markdown()
png_path = self._generate_png_diagram(output_dir="docs/tdd")
# Falls back to SVG (azure_diagram_generator.py) if PNG generation fails
# Estate overview generated once, shared across all TDDs
```

The fallback chain is: **PNG (python-diagrams)** → **SVG (azure_diagram_generator)**.

### Generated File Mapping

Each TDD markdown file references two images:

| Image | Source | Location |
|-------|--------|----------|
| `TDD_{name}_architecture.png` | `DiagramEngine.generate_tdd_diagram()` | `docs/tdd/` |
| `alz-estate-overview.png` | `DiagramEngine.generate_full_estate()` | `docs/tdd/` |

## Icon Registry

The `ICON_MAP` dictionary maps string keys to `diagrams.azure.*` icon classes:

| Category | Keys |
|----------|------|
| General | `management_group`, `subscription`, `resource_group`, `cost_management` |
| Networking | `vnet`, `subnet`, `firewall`, `application_gateway`, `front_door`, `load_balancer`, `vpn_gateway`, `expressroute`, `vwan`, `dns`, `private_endpoint`, `bastion`, `nsg`, `route_table` |
| Compute | `vm`, `container_app`, `function_app` |
| Identity | `active_directory`, `entra_ds`, `entra_connect`, `managed_identity` |
| Security | `key_vault`, `defender`, `sentinel` |
| Governance | `policy`, `compliance`, `automation`, `blueprints` |
| Monitor | `monitor`, `log_analytics`, `app_insights` |
| Data | `cosmos_db`, `mysql`, `storage`, `blob` |
| Integration | `event_grid` |

Used by `_icon(icon_type, label)` for dynamic icon instantiation in
`generate_full_estate()`.

## Usage

### CLI — Generate All TDDs

```bash
python -m src.tools.tdd_generator \
  --all \
  --config environments/subscriptions.json \
  --format both \
  --output-dir docs/tdd
```

### CLI — Single TDD

```bash
python -m src.tools.tdd_generator \
  --project management \
  --profile platform-management \
  --subscription-id "<SUB-ID>" \
  --subscription-name mrg-platform-management \
  --location southcentralus \
  --format markdown
```

### Programmatic — Shared Diagrams Only

```python
from src.tools.python_diagram_generator import DiagramEngine, generate_all_diagrams

# All 4 shared diagrams
paths = generate_all_diagrams(output_dir="docs/diagrams", mg_prefix="mrg")

# Or use the engine directly
engine = DiagramEngine(output_dir="docs/diagrams")
engine.generate_hub_spoke()
```

### Programmatic — Profile Diagrams

```python
engine = DiagramEngine(output_dir="docs/diagrams")
paths = engine.generate_for_profile(
    profile_name="platform-management",
    config={"management_group_prefix": "mrg"},
)
# Returns 4 PNGs: mg-hierarchy, hub-spoke, security-governance, alz-architecture
```

## Graph Attributes

All diagrams use consistent Graphviz graph attributes:

| Attribute | Shared Diagrams | TDD Diagrams |
|-----------|----------------|--------------|
| `bgcolor` | `white` | `white` |
| `pad` | `0.5` | `0.8` |
| `ranksep` | `0.8` – `1.2` | `1.0` |
| `nodesep` | default | `0.6` |

## Edge Conventions

| Style | Color | Meaning |
|-------|-------|---------|
| Solid | `darkblue` | MG hierarchy, ownership |
| Solid | `green` | Landing zone connections, VNet peering |
| Solid | `red` | Security alerts |
| Solid | `steelblue` | Identity relationships |
| Solid | `orange` | Monitoring data flow, alert rules |
| Dashed | `purple` | Policy enforcement, DNS resolution |
| Dashed | `orange` | Diagnostic settings, log shipping |
| Dashed | `gray` | Supporting relationships (RBAC, backup) |
| Dotted | `purple` | Policy assignment |

## Dependencies

| Package | Type | Purpose |
|---------|------|---------|
| `diagrams` | Python (pip) | Diagram DSL with Azure icons |
| `graphviz` | System (apt) | Graph layout engine (`dot`) |
| `pillow` | Python (pip) | PNG image handling |

All three are listed in `requirements.txt` and pre-installed in the dev container.

## Relationship to Other Diagram Systems

This project maintains two parallel diagram systems:

| System | Output | Source of Truth | Used By |
|--------|--------|----------------|---------|
| **Python Diagrams** (this tool) | PNG | `python_diagram_generator.py` | TDD docs (per-LZ + estate) |
| **Draw.io XML** | `.drawio` | `docs/diagrams/*.drawio` | Architecture docs, VS Code viewer |

The drawio files are hand-crafted XML with embedded Azure SVG icons from the
drawio-mcp-server asset library. They are the editable source for the 4 shared
architecture diagrams but require a separate export step for PNG/SVG output.

The python-diagrams PNGs are auto-generated and self-contained — no export step
needed. They are the primary image source for TDD documents.
