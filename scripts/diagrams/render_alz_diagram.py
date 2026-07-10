"""
render_alz_diagram — Graphviz-driven renderer for zone-based ALZ architecture diagrams.

Consumes a JSON document conforming to ``.github/skills/drawio/alz-diagram-schema.json``
and produces two artifacts from a **single Graphviz layout pass** so they are always
consistent:

1. A PNG rendered by Graphviz (``dot -Tpng``) with real Azure icons and edge routing
   that avoids overlapping nodes.
2. An editable ``.drawio`` built from the *same* Graphviz geometry (``dot -Tjson``):
   identical node positions, cluster bounding boxes, and edge waypoints, with the same
   Azure icons embedded as base64.

Using one layout engine for both outputs eliminates the earlier problems where the PNG
and Draw.io were laid out independently — overlapping labels, edges crossing through
icons, and straight horizontal-only connectors.

The shared icon registry is :data:`ICON_MAP` (``azureResourceType`` -> ``diagrams`` icon
class), which resolves to the icon PNG files bundled with the ``diagrams`` package.

Key exports:
    - ``ICON_MAP`` — resource-type -> diagrams icon class registry.
    - ``render`` — render one spec to PNG + Draw.io.
    - ``app`` — Typer CLI entry point.
"""

from __future__ import annotations

import base64
import importlib
import importlib.util
import json
import logging
import subprocess
from pathlib import Path
from typing import Annotated

import typer

logger = logging.getLogger(__name__)

# ── Icon registry ─────────────────────────────────────────────────────────
# Maps an ARM ``azureResourceType`` to a ``diagrams`` Azure icon class, expressed
# as ``(module_path, class_name)`` so the class is imported lazily. This is the
# single source of truth for BOTH the PNG and the Draw.io renderers.
ICON_MAP: dict[str, tuple[str, str]] = {
    "Microsoft.Authorization/policyAssignments": ("diagrams.azure.managementgovernance", "Policy"),
    "Microsoft.Automation/automationAccounts": ("diagrams.azure.managementgovernance", "AutomationAccounts"),
    "Microsoft.AzureActiveDirectory": ("diagrams.azure.identity", "AzureActiveDirectory"),
    "Microsoft.Compute/virtualMachines": ("diagrams.azure.compute", "VM"),
    "Microsoft.Consumption/budgets": ("diagrams.azure.general", "CostBudgets"),
    "Microsoft.Insights/actionGroups": ("diagrams.azure.web", "NotificationHubNamespaces"),
    "Microsoft.KeyVault/vaults": ("diagrams.azure.security", "KeyVaults"),
    "Microsoft.Logic/workflows": ("diagrams.azure.integration", "LogicApps"),
    "Microsoft.ManagedIdentity/userAssignedIdentities": ("diagrams.azure.identity", "ManagedIdentities"),
    "Microsoft.Network/azureFirewalls": ("diagrams.azure.network", "Firewall"),
    "Microsoft.Network/bastionHosts": ("diagrams.azure.networking", "Bastions"),
    "Microsoft.Network/networkSecurityGroups": ("diagrams.azure.networking", "NetworkSecurityGroups"),
    "Microsoft.Network/privateDnsZones": ("diagrams.azure.network", "DNSPrivateZones"),
    "Microsoft.Network/virtualNetworkGateways": ("diagrams.azure.network", "VirtualNetworkGateways"),
    "Microsoft.Network/virtualNetworks": ("diagrams.azure.network", "VirtualNetworks"),
    "Microsoft.OperationalInsights/workspaces": ("diagrams.azure.analytics", "LogAnalyticsWorkspaces"),
    "Microsoft.Security/pricings": ("diagrams.azure.security", "MicrosoftDefenderForCloud"),
    "Microsoft.SecurityInsights/alertRules": ("diagrams.azure.security", "Sentinel"),
}

# Fallback icon per schema ``category`` when the resource type is unknown.
CATEGORY_FALLBACK: dict[str, tuple[str, str]] = {
    "compute": ("diagrams.azure.compute", "VM"),
    "networking": ("diagrams.azure.network", "VirtualNetworks"),
    "security": ("diagrams.azure.security", "KeyVaults"),
    "identity": ("diagrams.azure.identity", "AzureActiveDirectory"),
    "management": ("diagrams.azure.general", "Subscriptions"),
    "monitoring": ("diagrams.azure.analytics", "LogAnalyticsWorkspaces"),
    "storage": ("diagrams.azure.storage", "StorageAccounts"),
    "data": ("diagrams.azure.database", "CosmosDb"),
    "integration": ("diagrams.azure.integration", "LogicApps"),
    "ai": ("diagrams.azure.ml", "CognitiveServices"),
}

# Icons for external / on-premises nodes (which carry no ``azureResourceType``).
EXTERNAL_ICON: tuple[str, str] = ("diagrams.onprem.network", "Internet")
ONPREM_ICON: tuple[str, str] = ("diagrams.generic.place", "Datacenter")

GENERIC_ICON: tuple[str, str] = ("diagrams.azure.general", "Resource")

# Zone fill colours by ALZ tier / kind.
TIER_COLORS: dict[str, str] = {
    "platform": "#E3F2FD",
    "landing-zone": "#E8F5E9",
    "sandbox": "#FFF8E1",
    "decommissioned": "#F5F5F5",
}
KIND_COLORS: dict[str, str] = {
    "tenant": "#ECEFF1",
    "mg": "#EDE7F6",
    "subscription": "#E1F5FE",
    "rg": "#F1F8E9",
    "vnet": "#E0F7FA",
    "subnet": "#F9FBE7",
    "external": "#FBE9E7",
    "onprem": "#EFEBE9",
}

# ── Layout / rendering constants ──────────────────────────────────────────
ICON_PX = 58  # Draw.io icon side length in pixels.
GV_NODESEP = "0.55"  # Graphviz inter-node separation (inches).
GV_RANKSEP = "0.9"  # Graphviz inter-rank separation (inches).
GV_PT_PER_IN = 72.0  # Graphviz JSON reports node width/height in inches at 72 pt/in.
LABEL_WRAP = 20  # Max characters per caption line before wrapping.
EDGE_COLOR = "#546E7A"


def _icon_class(module_path: str, class_name: str) -> type:
    """Import and return a ``diagrams`` icon class from its module path."""
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def _resolve_ref(node: dict) -> tuple[str, str]:
    """Return the ``(module, class)`` icon reference for a node."""
    rtype = node.get("azureResourceType")
    if rtype and rtype in ICON_MAP:
        return ICON_MAP[rtype]
    kind = (node.get("kind") or "").lower()
    name = (node.get("name") or node.get("label") or "").lower()
    if kind == "onprem" or "on-prem" in name or "on prem" in name:
        return ONPREM_ICON
    if kind == "external" or "internet" in name:
        return EXTERNAL_ICON
    category = node.get("category")
    if category and category in CATEGORY_FALLBACK:
        return CATEGORY_FALLBACK[category]
    return GENERIC_ICON


def _icon_file(node: dict) -> Path:
    """Resolve the on-disk PNG icon file backing a node's ``diagrams`` class.

    The ``diagrams`` package ships its icon resources under a top-level
    ``resources/`` directory that sits alongside the package (``site-packages/
    resources/azure/...``), so the icon path is ``<site-packages>/<_icon_dir>/<_icon>``.
    """
    cls = _icon_class(*_resolve_ref(node))
    spec = importlib.util.find_spec("diagrams")
    if not spec or not spec.origin:
        raise RuntimeError("Unable to locate the 'diagrams' package for icon resources.")
    site_packages = Path(spec.origin).parent.parent
    return site_packages / cls._icon_dir / cls._icon


def _zone_fill(zone: dict) -> str:
    """Pick a container fill colour for a zone dict."""
    tier = zone.get("tier")
    if tier and tier in TIER_COLORS:
        return TIER_COLORS[tier]
    return KIND_COLORS.get(zone.get("kind", ""), "#FFFFFF")


def _zone_label(zone: dict) -> str:
    """Compose a zone label, appending CIDR when present."""
    return f"{zone['label']} ({zone['cidr']})" if zone.get("cidr") else zone.get("label", "")


def _node_label(node: dict) -> str:
    """Return the display label for a node."""
    if "name" in node:
        return node["name"]
    return node.get("label") or node["id"]


def _inject_actor_nodes(spec: dict) -> None:
    """Turn empty external/onprem zones into icon actor nodes.

    In the schema, ``Internet`` and ``On-Premises`` are commonly modelled as
    ``external``/``onprem`` zones with no child zones or nodes. Rendered as bare
    containers they would be invisible, so we inject a synthetic node carrying the
    correct external/on-prem icon and blank the zone's own label to avoid duplication.
    """
    zone_has_child = {z.get("parent") for z in spec.get("zones", []) if z.get("parent")}
    zones_with_nodes = {n.get("zone") for n in spec.get("nodes", [])}
    for zone in spec.get("zones", []):
        if zone.get("kind") not in ("external", "onprem"):
            continue
        if zone["id"] in zone_has_child or zone["id"] in zones_with_nodes:
            continue
        spec.setdefault("nodes", []).append(
            {
                "id": f"{zone['id']}__actor",
                "name": zone.get("label") or zone["id"],
                "kind": zone["kind"],
                "zone": zone["id"],
            }
        )
        zone["label"] = ""


def _sanitize(identifier: str) -> str:
    """Return a Graphviz/Draw.io-safe token derived from a schema id."""
    return "".join(c if c.isalnum() else "_" for c in identifier)


def _endpoint(ref: str, node_gv: dict[str, str], zones: dict, first_descendant) -> str | None:
    """Resolve an edge endpoint (node id or zone id) to a concrete node id."""
    if ref in node_gv:
        return ref
    if ref in zones:
        return first_descendant(ref)
    return None


def _esc(text: str) -> str:
    """XML-escape a Draw.io attribute value."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _wrap(text: str, width: int = LABEL_WRAP) -> list[str]:
    """Word-wrap a caption into lines no wider than ``width`` characters."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [text]


def _html_label(icon: Path, caption: str) -> str:
    """Build a Graphviz HTML-like label: an icon above a wrapped caption."""
    caption_html = "<BR/>".join(_esc(line) for line in _wrap(caption))
    return (
        '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">'
        f'<TR><TD FIXEDSIZE="TRUE" WIDTH="{ICON_PX}" HEIGHT="{ICON_PX}">'
        f'<IMG SRC="{icon}" SCALE="TRUE"/></TD></TR>'
        f'<TR><TD><FONT POINT-SIZE="11">{caption_html}</FONT></TD></TR></TABLE>>'
    )


# ── Graphviz DOT construction ─────────────────────────────────────────────
def _build_dot(spec: dict) -> tuple[str, dict[str, str], dict[str, dict]]:
    """Build the Graphviz DOT source for a spec.

    Returns ``(dot_text, node_gv, san_to_zone)`` where ``node_gv`` maps a schema
    node id to its Graphviz node name and ``san_to_zone`` maps a sanitized zone
    token back to the zone dict.
    """
    zones = {z["id"]: z for z in spec.get("zones", [])}
    children: dict[str, list[str]] = {zid: [] for zid in zones}
    roots: list[str] = []
    for zid, zone in zones.items():
        parent = zone.get("parent")
        if parent and parent in zones:
            children[parent].append(zid)
        else:
            roots.append(zid)

    nodes_by_zone: dict[str, list[dict]] = {}
    for node in spec.get("nodes", []):
        nodes_by_zone.setdefault(node.get("zone", ""), []).append(node)

    node_gv: dict[str, str] = {}
    san_to_zone: dict[str, dict] = {}
    lines: list[str] = []

    def gv_node(node_id: str) -> str:
        return f"n_{_sanitize(node_id)}"

    def gv_cluster(zone_id: str) -> str:
        return f"cluster_{_sanitize(zone_id)}"

    def emit_cluster(zone_id: str, depth: int) -> None:
        zone = zones[zone_id]
        san_to_zone[_sanitize(zone_id)] = zone
        pad = "  " * depth
        lines.append(f"{pad}subgraph {gv_cluster(zone_id)} {{")
        lines.append(
            f'{pad}  label="{_esc(_zone_label(zone))}"; style="filled,rounded"; '
            f'fillcolor="{_zone_fill(zone)}"; color="#90A4AE"; fontsize=13; '
            'fontname="Helvetica"; labeljust="l"; labelloc="t"; margin=12; penwidth=1;'
        )
        for child_id in children.get(zone_id, []):
            emit_cluster(child_id, depth + 1)
        for node in nodes_by_zone.get(zone_id, []):
            node_gv[node["id"]] = gv_node(node["id"])
            lines.append(f"{pad}  {gv_node(node['id'])} [label={_html_label(_icon_file(node), _node_label(node))}];")
        lines.append(f"{pad}}}")

    for root_id in roots:
        emit_cluster(root_id, 1)

    for node in spec.get("nodes", []):
        if node["id"] not in node_gv:
            node_gv[node["id"]] = gv_node(node["id"])
            lines.append(f"  {gv_node(node['id'])} [label={_html_label(_icon_file(node), _node_label(node))}];")

    def first_descendant(zone_id: str) -> str | None:
        for node in nodes_by_zone.get(zone_id, []):
            if node["id"] in node_gv:
                return node["id"]
        for child_id in children.get(zone_id, []):
            found = first_descendant(child_id)
            if found:
                return found
        return None

    for edge in spec.get("edges", []):
        from_node = _endpoint(edge["from"], node_gv, zones, first_descendant)
        to_node = _endpoint(edge["to"], node_gv, zones, first_descendant)
        if not from_node or not to_node or from_node == to_node:
            continue
        label = edge.get("label", "")
        step = edge.get("step")
        if step is not None:
            label = f"{step}. {label}".strip(". ")
        attrs = [f'label="{_esc(label)}"'] if label else []
        style = edge.get("style", "solid")
        if style in ("dashed", "dotted"):
            attrs.append(f"style={style}")
        attrs += ["fontsize=11", 'fontname="Helvetica"', f'color="{EDGE_COLOR}"', "arrowsize=0.8"]
        if edge["from"] in zones:
            attrs.append(f"ltail={gv_cluster(edge['from'])}")
        if edge["to"] in zones:
            attrs.append(f"lhead={gv_cluster(edge['to'])}")
        lines.append(f"  {gv_node(from_node)} -> {gv_node(to_node)} [{', '.join(attrs)}];")

    header = [
        "digraph G {",
        f"  compound=true; rankdir=TB; nodesep={GV_NODESEP}; ranksep={GV_RANKSEP}; splines=spline;",
        '  bgcolor="white"; fontname="Helvetica"; pad=0.4;',
        "  node [shape=plaintext, margin=0];",
    ]
    return "\n".join([*header, *lines, "}"]), node_gv, san_to_zone


# ── Draw.io emission from Graphviz JSON geometry ──────────────────────────
def _b64_icon_style(node: dict, cache: dict[str, str]) -> str:
    """Return a Draw.io image style embedding the icon PNG as base64."""
    module_path, class_name = _resolve_ref(node)
    key = f"{module_path}.{class_name}"
    if key not in cache:
        cache[key] = base64.b64encode(_icon_file(node).read_bytes()).decode("ascii")
    return (
        "shape=image;verticalLabelPosition=bottom;labelPosition=center;verticalAlign=top;"
        f"align=center;imageAspect=1;html=1;whiteSpace=wrap;image=data:image/png,{cache[key]}"
    )


def _bezier_point(seg: list[tuple[float, float]], t: float) -> tuple[float, float]:
    """Evaluate a cubic Bézier segment (4 control points) at parameter ``t``."""
    mt = 1 - t
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = seg
    a, b, c, d = mt**3, 3 * mt**2 * t, 3 * mt * t**2, t**3
    return (a * x0 + b * x1 + c * x2 + d * x3, a * y0 + b * y1 + c * y2 + d * y3)


def _edge_waypoints(edge_obj: dict, height: float) -> list[tuple[float, float]]:
    """Sample a Graphviz JSON edge spline into smooth interior waypoints (y-flipped).

    Graphviz stores the route as cubic Bézier control points. Sampling each segment
    yields a dense polyline that follows the same node-avoiding route as the PNG,
    so the Draw.io connectors curve around icons instead of cutting through them.
    """
    for draw in edge_obj.get("_draw_", []):
        if draw.get("op") in ("b", "B") and draw.get("points"):
            ctrl = [(px, height - py) for px, py in draw["points"]]
            samples: list[tuple[float, float]] = []
            for i in range(0, len(ctrl) - 3, 3):
                seg = ctrl[i : i + 4]
                for step in (0.2, 0.4, 0.6, 0.8):
                    samples.append(_bezier_point(seg, step))
            return samples
    return []


def _render(spec: dict, png_path: Path, drawio_path: Path) -> None:
    """Render the spec to PNG and Draw.io from one Graphviz layout pass."""
    dot_text, node_gv, san_to_zone = _build_dot(spec)
    dot_bytes = dot_text.encode("utf-8")

    subprocess.run(["dot", "-Tpng", "-o", str(png_path)], input=dot_bytes, check=True)
    completed = subprocess.run(["dot", "-Tjson"], input=dot_bytes, capture_output=True, check=True)
    geometry = json.loads(completed.stdout)

    _, _, _width, height = (float(v) for v in geometry["bb"].split(","))
    objects = geometry.get("objects", [])
    gv_to_node_id = {gv: nid for nid, gv in node_gv.items()}
    node_by_id = {n["id"]: n for n in spec.get("nodes", [])}

    cells: list[str] = []
    icon_cache: dict[str, str] = {}
    node_cell: dict[str, str] = {}  # graphviz node name -> drawio cell id
    zone_cell: dict[str, str] = {}  # sanitized zone token -> drawio cell id

    # Clusters first (largest area first so parents render behind children).
    clusters = [o for o in objects if str(o.get("name", "")).startswith("cluster_") and o.get("bb")]

    def cluster_area(obj: dict) -> float:
        x0, y0, x1, y1 = (float(v) for v in obj["bb"].split(","))
        return (x1 - x0) * (y1 - y0)

    for obj in sorted(clusters, key=cluster_area, reverse=True):
        x0, y0, x1, y1 = (float(v) for v in obj["bb"].split(","))
        san = obj["name"][len("cluster_") :]
        zone = san_to_zone.get(san, {})
        cell_id = f"zone-{san}"
        zone_cell[san] = cell_id
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fillColor={_zone_fill(zone)};strokeColor=#90A4AE;"
            "verticalAlign=top;align=left;spacingLeft=8;spacingTop=4;fontSize=12;fontStyle=1;arcSize=3;"
        )
        cells.append(
            f'<mxCell id="{cell_id}" value="{_esc(_zone_label(zone))}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x0:.0f}" y="{height - y1:.0f}" '
            f'width="{x1 - x0:.0f}" height="{y1 - y0:.0f}" as="geometry"/></mxCell>'
        )

    # Nodes: an invisible full-box cell (matching the Graphviz node box so edge
    # anchors/routes match the PNG) carries the caption at the bottom, with a
    # fixed-size icon child rendered on top.
    for obj in objects:
        name = str(obj.get("name", ""))
        if not name.startswith("n_") or "pos" not in obj:
            continue
        node_id = gv_to_node_id.get(name)
        node = node_by_id.get(node_id)
        if node is None:
            continue
        cx, cy = (float(v) for v in obj["pos"].split(","))
        box_w = float(obj.get("width", 1)) * GV_PT_PER_IN
        box_h = float(obj.get("height", 1)) * GV_PT_PER_IN
        nx = cx - box_w / 2
        ny = (height - cy) - box_h / 2
        cell_id = f"node-{_sanitize(node_id)}"
        icon_id = f"icon-{_sanitize(node_id)}"
        node_cell[name] = cell_id
        box_style = (
            "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=none;"
            "verticalAlign=bottom;align=center;fontSize=11;"
        )
        cells.append(
            f'<mxCell id="{cell_id}" value="{_esc(_node_label(node))}" style="{box_style}" vertex="1" parent="1">'
            f'<mxGeometry x="{nx:.0f}" y="{ny:.0f}" width="{box_w:.0f}" height="{box_h:.0f}" as="geometry"/></mxCell>'
        )
        icon_x = (box_w - ICON_PX) / 2
        icon_style = _b64_icon_style(node, icon_cache)
        cells.append(
            f'<mxCell id="{icon_id}" value="" style="{icon_style}" vertex="1" parent="{cell_id}">'
            f'<mxGeometry x="{icon_x:.0f}" y="4" width="{ICON_PX}" height="{ICON_PX}" as="geometry"/></mxCell>'
        )

    # Edges (with Graphviz-computed waypoints so routing matches the PNG).
    dash = {"dashed": "dashed=1;", "dotted": "dashed=1;dashPattern=1 3;", "solid": ""}
    spec_edges = _renderable_edges(spec, node_gv)
    for edge_obj, meta in zip(geometry.get("edges", []), spec_edges, strict=False):
        source = node_cell.get(meta["tail_gv"])
        target = node_cell.get(meta["head_gv"])
        if not source or not target:
            continue
        estyle = (
            f"edgeStyle=none;curved=1;html=1;endArrow=block;rounded=1;strokeColor={EDGE_COLOR};"
            f"{dash.get(meta['style'], '')}"
        )
        waypoints = _edge_waypoints(edge_obj, height)
        if waypoints:
            pts = "".join(f'<mxPoint x="{px:.0f}" y="{py:.0f}"/>' for px, py in waypoints)
            geo = f'<mxGeometry relative="1" as="geometry"><Array as="points">{pts}</Array></mxGeometry>'
        else:
            geo = '<mxGeometry relative="1" as="geometry"/>'
        cells.append(
            f'<mxCell id="edge-{meta["id"]}" value="{_esc(meta["label"])}" style="{estyle}" '
            f'edge="1" parent="1" source="{source}" target="{target}">{geo}</mxCell>'
        )

    body = "\n".join(cells)
    xml = (
        '<mxfile host="render_alz_diagram">'
        f'<diagram name="{_esc(spec.get("title", "ALZ Architecture"))}">'
        '<mxGraphModel dx="1024" dy="768" grid="1" gridSize="10" guides="1" '
        'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" math="0" shadow="0">'
        '<root><mxCell id="0"/><mxCell id="1" parent="0"/>'
        f"{body}"
        "</root></mxGraphModel></diagram></mxfile>"
    )
    drawio_path.write_text(xml, encoding="utf-8")


def _renderable_edges(spec: dict, node_gv: dict[str, str]) -> list[dict]:
    """Return edge metadata in the same order emitted into DOT (for JSON zip)."""
    zones = {z["id"]: z for z in spec.get("zones", [])}
    children: dict[str, list[str]] = {zid: [] for zid in zones}
    for zid, zone in zones.items():
        parent = zone.get("parent")
        if parent and parent in zones:
            children[parent].append(zid)
    nodes_by_zone: dict[str, list[dict]] = {}
    for node in spec.get("nodes", []):
        nodes_by_zone.setdefault(node.get("zone", ""), []).append(node)

    def first_descendant(zone_id: str) -> str | None:
        for node in nodes_by_zone.get(zone_id, []):
            if node["id"] in node_gv:
                return node["id"]
        for child_id in children.get(zone_id, []):
            found = first_descendant(child_id)
            if found:
                return found
        return None

    meta: list[dict] = []
    for index, edge in enumerate(spec.get("edges", [])):
        from_node = _endpoint(edge["from"], node_gv, zones, first_descendant)
        to_node = _endpoint(edge["to"], node_gv, zones, first_descendant)
        if not from_node or not to_node or from_node == to_node:
            continue
        label = edge.get("label", "")
        step = edge.get("step")
        if step is not None:
            label = f"{step}. {label}".strip(". ")
        meta.append(
            {
                "id": _sanitize(str(edge.get("id", index))),
                "tail_gv": node_gv[from_node],
                "head_gv": node_gv[to_node],
                "label": label,
                "style": edge.get("style", "solid"),
            }
        )
    return meta


def render(spec_path: Path, out_dir: Path | None = None) -> dict[str, Path]:
    """Render a single ALZ diagram spec to PNG + Draw.io.

    Returns a mapping of ``{"png": path, "drawio": path}``.
    """
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    _inject_actor_nodes(spec)
    out_dir = out_dir or spec_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = spec_path.stem
    png_path = out_dir / f"{stem}.png"
    drawio_path = out_dir / f"{stem}.drawio"

    logger.info("Rendering %s (PNG + Draw.io) via Graphviz", stem)
    _render(spec, png_path, drawio_path)
    return {"png": png_path, "drawio": drawio_path}


app = typer.Typer(help="Render zone-based ALZ diagram JSON specs to PNG + Draw.io with correct Azure icons.")


@app.command()
def main(
    specs: Annotated[list[Path], typer.Argument(help="One or more zone-based JSON spec files.")],
    out_dir: Annotated[
        Path | None,
        typer.Option("--out-dir", help="Output directory (defaults to each spec's directory)."),
    ] = None,
) -> None:
    """Render each JSON spec to a matching PNG and Draw.io file."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    for spec_path in specs:
        result = render(spec_path, out_dir)
        typer.echo(f"OK {spec_path.name} -> {result['png'].name}, {result['drawio'].name}")


if __name__ == "__main__":
    app()
