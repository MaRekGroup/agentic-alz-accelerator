"""
Azure Architecture Diagram Generator — produces SVG diagrams with official Azure icons.

Generates deployment-specific architecture diagrams for each landing zone profile.
Diagrams use Microsoft's official Azure Architecture Icon set colors and grouping.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from html import escape as xml_escape

logger = logging.getLogger(__name__)

# ─── Azure Icon Registry ──────────────────────────────────────────────────────
# Official Azure Architecture SVG icon paths (from azure.microsoft.com/patterns/icons)
# Using inline SVG definitions for portability (no external downloads required)

class AzureColor(str, Enum):
    """Official Azure architecture diagram color palette."""
    BLUE        = "#0078D4"    # Azure primary blue
    DARK_BLUE   = "#003067"    # Management group / governance
    GREEN       = "#57A300"    # Networking / connectivity
    PURPLE      = "#7719AA"    # Security / identity
    ORANGE      = "#FF8C00"    # Monitoring / alerts
    RED         = "#E81123"    # Firewall / threat protection
    TEAL        = "#008272"    # DevOps / automation
    GRAY        = "#6B6B6B"    # Generic / infrastructure
    LIGHT_GRAY  = "#F2F2F2"    # Background panels
    WHITE       = "#FFFFFF"


@dataclass
class DiagramNode:
    """A resource node in the architecture diagram."""
    id: str
    label: str
    icon_type: str         # maps to AZURE_ICONS
    x: float = 0
    y: float = 0
    width: float = 120
    height: float = 100
    group: str = ""
    sublabel: str = ""


@dataclass
class DiagramEdge:
    """A connection between two nodes."""
    source: str
    target: str
    label: str = ""
    style: str = "solid"   # solid, dashed
    color: str = AzureColor.GRAY


@dataclass
class DiagramGroup:
    """A visual grouping box (subscription, resource group, etc.)."""
    id: str
    label: str
    x: float = 0
    y: float = 0
    width: float = 400
    height: float = 300
    color: str = AzureColor.BLUE
    icon_type: str = ""


# ─── Azure Icon SVG Paths ─────────────────────────────────────────────────────
# Simplified SVG path data for common Azure service icons (32x32 viewport)

AZURE_ICONS: dict[str, dict] = {
    "subscription": {
        "color": AzureColor.BLUE,
        "path": "M16 2L4 8v16l12 6 12-6V8L16 2zm0 3.2L25 9.6v12.8L16 26.8 7 22.4V9.6L16 5.2z",
        "label": "Subscription",
    },
    "resource_group": {
        "color": AzureColor.GRAY,
        "path": "M4 6h24v20H4V6zm2 2v16h20V8H6z M10 12h12v2H10z M10 16h8v2H10z",
        "label": "Resource Group",
    },
    "vnet": {
        "color": AzureColor.GREEN,
        "path": "M16 2C8.27 2 2 8.27 2 16s6.27 14 14 14 14-6.27 14-14S23.73 2 16 2zm0 26C9.37 28 4 22.63 4 16S9.37 4 16 4s12 5.37 12 12-5.37 12-12 12zm-2-18h4v4h4v4h-4v4h-4v-4H10v-4h4V10z",
        "label": "Virtual Network",
    },
    "subnet": {
        "color": "#0063B1",
        "path": "M4 8h24v16H4V8zm2 2v12h20V10H6zm4 3h12v2H10zm0 4h8v2H10z",
        "label": "Subnet",
    },
    "nsg": {
        "color": AzureColor.GREEN,
        "path": "M16 2L4 8v16l12 6 12-6V8L16 2zm-2 22.5L6 20.9V11l8 3.6v9.9zm4 0V14.6l8-3.6v9.9l-8 3.6z",
        "label": "NSG",
    },
    "firewall": {
        "color": AzureColor.RED,
        "path": "M16 2c-2 4-6 6-6 10 0 4 2.69 6 6 6s6-2 6-6c0-4-4-6-6-10zm0 14c-2.21 0-4-1.34-4-3.5 0-2.07 2-3.83 4-6.5 2 2.67 4 4.43 4 6.5 0 2.16-1.79 3.5-4 3.5zM8 20h16v4c0 2-3.58 4-8 4s-8-2-8-4v-4z",
        "label": "Azure Firewall",
    },
    "log_analytics": {
        "color": AzureColor.ORANGE,
        "path": "M4 4h24v24H4V4zm2 2v20h20V6H6zm4 14l4-6 3 4 5-8v12H10v-2z",
        "label": "Log Analytics",
    },
    "sentinel": {
        "color": "#0078D4",
        "path": "M16 2C8.27 2 2 8.27 2 16s6.27 14 14 14 14-6.27 14-14S23.73 2 16 2zm0 4c5.52 0 10 4.48 10 10s-4.48 10-10 10S6 21.52 6 16 10.48 6 16 6zm0 4a6 6 0 100 12 6 6 0 000-12zm0 2a4 4 0 110 8 4 4 0 010-8z",
        "label": "Microsoft Sentinel",
    },
    "key_vault": {
        "color": AzureColor.PURPLE,
        "path": "M16 2a6 6 0 00-6 6c0 2.22 1.21 4.16 3 5.2V28h6V13.2c1.79-1.04 3-2.98 3-5.2a6 6 0 00-6-6zm0 8a2 2 0 110-4 2 2 0 010 4z",
        "label": "Key Vault",
    },
    "storage": {
        "color": "#0078D4",
        "path": "M4 8l12-4 12 4v2L16 14 4 10V8zm0 6l12 4 12-4v2l-12 4-12-4v-2zm0 6l12 4 12-4v2l-12 4-12-4v-2z",
        "label": "Storage Account",
    },
    "policy": {
        "color": AzureColor.TEAL,
        "path": "M16 2L4 7v9c0 7.46 5.12 14.43 12 16 6.88-1.57 12-8.54 12-16V7L16 2zm0 4l8 3.4v6.6c0 5.34-3.42 10.33-8 11.8-4.58-1.47-8-6.46-8-11.8V9.4L16 6z",
        "label": "Azure Policy",
    },
    "defender": {
        "color": AzureColor.PURPLE,
        "path": "M16 2L4 7v9c0 7.46 5.12 14.43 12 16 6.88-1.57 12-8.54 12-16V7L16 2zm-2 20l-5-5 1.41-1.41L14 19.17l7.59-7.59L23 13l-9 9z",
        "label": "Defender for Cloud",
    },
    "ddos": {
        "color": AzureColor.RED,
        "path": "M16 2L4 7v9c0 7.46 5.12 14.43 12 16 6.88-1.57 12-8.54 12-16V7L16 2zm0 4l8 3.4v6.6c0 5.34-3.42 10.33-8 11.8V6z",
        "label": "DDoS Protection",
    },
    "express_route": {
        "color": AzureColor.GREEN,
        "path": "M2 16h6l3-6 4 12 4-12 3 6h6",
        "label": "ExpressRoute",
    },
    "vpn_gateway": {
        "color": AzureColor.GREEN,
        "path": "M16 2l-8 6v16l8 6 8-6V8l-8-6zm0 3.2L22 9v4h-4v6h-4v-6H10V9l6-3.8z",
        "label": "VPN Gateway",
    },
    "automation": {
        "color": AzureColor.TEAL,
        "path": "M16 2L4 8v16l12 6 12-6V8L16 2zm-4 18l-3-3 1.4-1.4L12 17.2l5.6-5.6L19 13l-7 7z",
        "label": "Automation Account",
    },
    "recovery_vault": {
        "color": AzureColor.TEAL,
        "path": "M16 2c-7.73 0-14 6.27-14 14s6.27 14 14 14 14-6.27 14-14S23.73 2 16 2zm0 24c-5.52 0-10-4.48-10-10S10.48 6 16 6s10 4.48 10 10-4.48 10-10 10zm-1-15h2v6h-2zm0 8h2v2h-2z",
        "label": "Recovery Services Vault",
    },
    "monitor": {
        "color": AzureColor.ORANGE,
        "path": "M4 4h24v18H4V4zm2 2v14h20V6H6zm4 10h2v2h-2zm4-4h2v6h-2zm4-2h2v8h-2zm4-4h2v12h-2z",
        "label": "Azure Monitor",
    },
    "management_group": {
        "color": AzureColor.DARK_BLUE,
        "path": "M14 2h4v4h-4V2zM8 10h16v4H8v-4zm-6 8h10v4H2v-4zm16 0h10v4H18v-4zM16 6v4M8 14v4m16-4v4",
        "label": "Management Group",
    },
    "active_directory": {
        "color": AzureColor.PURPLE,
        "path": "M16 2C8.27 2 2 8.27 2 16s6.27 14 14 14 14-6.27 14-14S23.73 2 16 2zm0 6a4 4 0 110 8 4 4 0 010-8zm0 18c-3.31 0-6.31-1.34-8.49-3.51C9.37 19.98 12.5 18 16 18s6.63 1.98 8.49 4.49A11.952 11.952 0 0116 26z",
        "label": "Entra ID",
    },
    "private_dns": {
        "color": AzureColor.GREEN,
        "path": "M16 2L4 8v16l12 6 12-6V8L16 2zm0 4l8 4v10l-8 4-8-4V10l8-4zm-3 7h6v2h-6zm0 4h4v2h-4z",
        "label": "Private DNS Zone",
    },
    "waf": {
        "color": AzureColor.RED,
        "path": "M16 2L4 7v9c0 7.46 5.12 14.43 12 16 6.88-1.57 12-8.54 12-16V7L16 2zm0 6a2 2 0 110 4 2 2 0 010-4zm-1 6h2v8h-2v-8z",
        "label": "WAF",
    },
    "app_service": {
        "color": AzureColor.BLUE,
        "path": "M16 2L4 8v16l12 6 12-6V8L16 2zm-3 10l6 4-6 4v-8z",
        "label": "App Service",
    },
    "sap": {
        "color": "#0FAAFF",
        "path": "M4 6h24v20H4V6zm8 4v12h2V10h-2zm4 2v10h2V12h-2zm4-4v14h2V8h-2z",
        "label": "SAP on Azure",
    },
    "budget": {
        "color": AzureColor.TEAL,
        "path": "M16 2C8.27 2 2 8.27 2 16s6.27 14 14 14 14-6.27 14-14S23.73 2 16 2zm1 21h-2v-2h2v2zm0-4h-2V9h2v10z",
        "label": "Budget / Cost",
    },
    "anf": {
        "color": AzureColor.BLUE,
        "path": "M4 8h24v16H4V8zm2 2v12h20V10H6zm3 3h14v2H9zm0 4h10v2H9z",
        "label": "Azure NetApp Files",
    },
}


class AzureDiagramGenerator:
    """Generates SVG architecture diagrams with Azure-themed icons and colors."""

    SVG_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"
     width="{width}" height="{height}"
     font-family="Segoe UI, -apple-system, sans-serif">
  <defs>
    <style>
      .group-box {{ fill: {bg}; stroke: {border}; stroke-width: 1.5; rx: 8; }}
      .group-label {{ font-size: 13px; font-weight: 600; fill: {label_color}; }}
      .node-label {{ font-size: 11px; fill: #333; text-anchor: middle; }}
      .node-sublabel {{ font-size: 9px; fill: #777; text-anchor: middle; }}
      .edge {{ stroke: #999; stroke-width: 1.2; fill: none; }}
      .edge-dashed {{ stroke-dasharray: 6 3; }}
      .edge-label {{ font-size: 9px; fill: #666; text-anchor: middle; }}
      .title {{ font-size: 18px; font-weight: 700; fill: #0078D4; }}
      .subtitle {{ font-size: 12px; fill: #555; }}
      .icon-bg {{ rx: 6; ry: 6; }}
    </style>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.12"/>
    </filter>
  </defs>
"""

    def __init__(self):
        self.nodes: list[DiagramNode] = []
        self.edges: list[DiagramEdge] = []
        self.groups: list[DiagramGroup] = []
        self.title = ""
        self.subtitle = ""

    def _render_icon(self, icon_type: str, x: float, y: float, size: float = 32) -> str:
        """Render an Azure icon as SVG at the specified position."""
        icon = AZURE_ICONS.get(icon_type)
        if not icon:
            # Fallback: generic blue square
            return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="4" fill="{AzureColor.BLUE}" opacity="0.7"/>'

        color = icon["color"]
        # Scale path from 32x32 viewport to target size
        scale = size / 32
        return f"""<g transform="translate({x},{y}) scale({scale})">
      <rect width="32" height="32" class="icon-bg" fill="{color}" opacity="0.12"/>
      <path d="{icon['path']}" fill="{color}"/>
    </g>"""

    def _render_node(self, node: DiagramNode) -> str:
        """Render a single diagram node."""
        icon_size = 36
        icon_x = node.x + (node.width - icon_size) / 2
        icon_y = node.y + 8
        label = xml_escape(node.label)
        sublabel = xml_escape(node.sublabel) if node.sublabel else ""

        svg = f"""  <!-- {label} -->
    <g filter="url(#shadow)">
      <rect x="{node.x}" y="{node.y}" width="{node.width}" height="{node.height}"
            rx="8" fill="white" stroke="#E0E0E0" stroke-width="1"/>
      {self._render_icon(node.icon_type, icon_x, icon_y, icon_size)}
      <text x="{node.x + node.width/2}" y="{node.y + 56}" class="node-label">{label}</text>"""

        if sublabel:
            svg += f"""
      <text x="{node.x + node.width/2}" y="{node.y + 70}" class="node-sublabel">{sublabel}</text>"""

        svg += "\n    </g>\n"
        return svg

    def _render_group(self, group: DiagramGroup) -> str:
        """Render a visual grouping box."""
        icon_svg = ""
        if group.icon_type:
            icon_svg = self._render_icon(group.icon_type, group.x + 8, group.y + 6, 20)

        label_x = group.x + (36 if group.icon_type else 12)
        label = xml_escape(group.label)
        return f"""  <!-- Group: {label} -->
    <rect x="{group.x}" y="{group.y}" width="{group.width}" height="{group.height}"
          rx="8" fill="{group.color}" fill-opacity="0.06"
          stroke="{group.color}" stroke-width="1.5" stroke-dasharray="6 3"/>
    {icon_svg}
    <text x="{label_x}" y="{group.y + 20}" class="group-label" fill="{group.color}">{label}</text>
"""

    def _render_edge(self, edge: DiagramEdge) -> str:
        """Render an edge (connection) between two nodes."""
        src = next((n for n in self.nodes if n.id == edge.source), None)
        tgt = next((n for n in self.nodes if n.id == edge.target), None)
        if not src or not tgt:
            return ""

        x1 = src.x + src.width / 2
        y1 = src.y + src.height
        x2 = tgt.x + tgt.width / 2
        y2 = tgt.y

        # Determine if horizontal or vertical connection
        if abs(y1 - tgt.y) < 20:  # Mostly horizontal
            y1 = src.y + src.height / 2
            y2 = tgt.y + tgt.height / 2
            x1 = src.x + src.width
            x2 = tgt.x

        dash_class = ' class="edge-dashed"' if edge.style == "dashed" else ""
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        svg = f"""    <path d="M{x1},{y1} C{x1},{mid_y} {x2},{mid_y} {x2},{y2}"
          stroke="{edge.color}" stroke-width="1.2" fill="none"{dash_class}
          marker-end="url(#arrow)"/>"""

        if edge.label:
            svg += f"""
    <text x="{mid_x}" y="{mid_y - 6}" class="edge-label">{xml_escape(edge.label)}</text>"""

        return svg

    def generate_svg(self) -> str:
        """Generate the complete SVG string."""
        # Calculate canvas size from content
        max_x = max(
            [g.x + g.width for g in self.groups] +
            [n.x + n.width for n in self.nodes] +
            [800]
        )
        max_y = max(
            [g.y + g.height for g in self.groups] +
            [n.y + n.height for n in self.nodes] +
            [600]
        )
        width = max_x + 40
        height = max_y + 60

        svg = self.SVG_HEADER.format(
            width=width, height=height,
            bg=AzureColor.LIGHT_GRAY,
            border="#D0D0D0",
            label_color=AzureColor.DARK_BLUE,
        )

        # Arrow marker definition
        svg += """  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#999"/>
    </marker>
  </defs>
"""

        # Title block
        if self.title:
            svg += f'  <text x="20" y="30" class="title">{xml_escape(self.title)}</text>\n'
        if self.subtitle:
            svg += f'  <text x="20" y="48" class="subtitle">{xml_escape(self.subtitle)}</text>\n'

        title_offset = 60 if self.title else 10

        # Shift all elements by title offset
        for g in self.groups:
            svg += self._render_group(
                DiagramGroup(g.id, g.label, g.x, g.y + title_offset,
                             g.width, g.height, g.color, g.icon_type)
            )

        shifted_nodes = []
        for n in self.nodes:
            shifted = DiagramNode(n.id, n.label, n.icon_type,
                                  n.x, n.y + title_offset,
                                  n.width, n.height, n.group, n.sublabel)
            shifted_nodes.append(shifted)
            svg += self._render_node(shifted)

        # Temporarily use shifted nodes for edge rendering
        original_nodes = self.nodes
        self.nodes = shifted_nodes
        for e in self.edges:
            svg += self._render_edge(e)
        self.nodes = original_nodes

        svg += "</svg>"
        return svg


# ─── Pre-built Profile Diagrams ──────────────────────────────────────────────

def generate_management_diagram(subscription_name: str, location: str,
                                 log_retention: int = 365) -> str:
    """Generate the Management Landing Zone architecture diagram."""
    gen = AzureDiagramGenerator()
    gen.title = "Platform Management Landing Zone — As-Built"
    gen.subtitle = f"{subscription_name}  ·  {location}  ·  Log retention: {log_retention} days"

    # Subscription group
    gen.groups.append(DiagramGroup("sub", f"Subscription: {subscription_name}",
                                   10, 10, 780, 460, AzureColor.BLUE, "subscription"))

    # Row 1: Core monitoring
    gen.groups.append(DiagramGroup("monitoring", "Monitoring & Analytics",
                                   30, 50, 740, 140, AzureColor.ORANGE, "monitor"))
    gen.nodes.extend([
        DiagramNode("law", "Log Analytics", "log_analytics", 50, 80, 130, 90,
                    sublabel=f"{log_retention}d retention"),
        DiagramNode("sentinel", "Microsoft Sentinel", "sentinel", 200, 80, 130, 90,
                    sublabel="SIEM + SOAR"),
        DiagramNode("monitor", "Azure Monitor", "monitor", 350, 80, 130, 90,
                    sublabel="Alerts & Metrics"),
        DiagramNode("action", "Action Groups", "automation", 500, 80, 130, 90,
                    sublabel="Email / Teams / SMS"),
    ])

    # Row 2: Automation & backup
    gen.groups.append(DiagramGroup("ops", "Operations & Continuity",
                                   30, 210, 740, 140, AzureColor.TEAL, "automation"))
    gen.nodes.extend([
        DiagramNode("auto", "Automation Acct", "automation", 50, 240, 130, 90,
                    sublabel="Runbooks"),
        DiagramNode("update", "Update Manager", "automation", 200, 240, 130, 90,
                    sublabel="Weekly patches"),
        DiagramNode("change", "Change Tracking", "monitor", 350, 240, 130, 90,
                    sublabel="File & service"),
        DiagramNode("vault", "Recovery Vault", "recovery_vault", 500, 240, 130, 90,
                    sublabel="Daily + Weekly"),
    ])

    # Row 3: Governance
    gen.groups.append(DiagramGroup("gov", "Governance",
                                   30, 370, 740, 90, AzureColor.TEAL, "policy"))
    gen.nodes.extend([
        DiagramNode("policy", "Azure Policy", "policy", 50, 385, 130, 60,
                    sublabel="Baseline policies"),
        DiagramNode("defender", "Defender for Cloud", "defender", 200, 385, 130, 60,
                    sublabel="All plans enabled"),
        DiagramNode("budget", "Cost Management", "budget", 350, 385, 130, 60,
                    sublabel="Budget alerts"),
    ])

    # Edges: data flows
    gen.edges.extend([
        DiagramEdge("law", "sentinel", "feeds", color=AzureColor.ORANGE),
        DiagramEdge("sentinel", "monitor", "alerts", color=AzureColor.ORANGE),
        DiagramEdge("monitor", "action", "notify", color=AzureColor.ORANGE),
        DiagramEdge("auto", "update", "schedules", color=AzureColor.TEAL),
        DiagramEdge("update", "change", "tracks", color=AzureColor.TEAL),
    ])

    return gen.generate_svg()


def generate_connectivity_diagram(subscription_name: str, location: str,
                                   hub_cidr: str = "10.0.0.0/16",
                                   topology: str = "hub-spoke") -> str:
    """Generate the Connectivity Landing Zone architecture diagram."""
    gen = AzureDiagramGenerator()
    gen.title = "Platform Connectivity Landing Zone — As-Built"
    gen.subtitle = f"{subscription_name}  ·  {location}  ·  Topology: {topology}"

    gen.groups.append(DiagramGroup("sub", f"Subscription: {subscription_name}",
                                   10, 10, 780, 520, AzureColor.GREEN, "subscription"))

    # Hub VNet group
    gen.groups.append(DiagramGroup("hub", f"Hub VNet ({hub_cidr})",
                                   30, 50, 740, 200, AzureColor.GREEN, "vnet"))
    gen.nodes.extend([
        DiagramNode("fw", "Azure Firewall", "firewall", 50, 90, 130, 90,
                    sublabel="Premium SKU"),
        DiagramNode("gw", "VPN Gateway", "vpn_gateway", 200, 90, 130, 90,
                    sublabel="VpnGw2"),
        DiagramNode("er", "ExpressRoute GW", "express_route", 350, 90, 130, 90,
                    sublabel="Ultra Performance"),
        DiagramNode("bastion", "Azure Bastion", "vnet", 500, 90, 130, 90,
                    sublabel="Standard SKU"),
    ])

    # DNS & DDoS row
    gen.groups.append(DiagramGroup("dns_grp", "DNS & Protection",
                                   30, 270, 740, 120, AzureColor.GREEN, "private_dns"))
    gen.nodes.extend([
        DiagramNode("dns", "Private DNS Zones", "private_dns", 50, 295, 130, 75,
                    sublabel="20+ zones"),
        DiagramNode("ddos", "DDoS Protection", "ddos", 200, 295, 130, 75,
                    sublabel="Standard plan"),
        DiagramNode("nsg", "NSG Flow Logs", "nsg", 350, 295, 130, 75,
                    sublabel="Traffic Analytics"),
    ])

    # Spoke peerings
    gen.groups.append(DiagramGroup("spokes", "Spoke VNet Peerings",
                                   30, 410, 740, 110, AzureColor.BLUE, "vnet"))
    gen.nodes.extend([
        DiagramNode("spoke_corp", "Corp Spoke", "vnet", 50, 435, 120, 65,
                    sublabel="10.2.0.0/16"),
        DiagramNode("spoke_online", "Online Spoke", "vnet", 190, 435, 120, 65,
                    sublabel="10.1.0.0/16"),
        DiagramNode("spoke_sap", "SAP Spoke", "vnet", 330, 435, 120, 65,
                    sublabel="10.5.0.0/16"),
        DiagramNode("spoke_sandbox", "Sandbox", "vnet", 470, 435, 120, 65,
                    sublabel="10.10.0.0/16"),
    ])

    gen.edges.extend([
        DiagramEdge("fw", "spoke_corp", "peering", style="dashed", color=AzureColor.GREEN),
        DiagramEdge("fw", "spoke_online", "peering", style="dashed", color=AzureColor.GREEN),
        DiagramEdge("fw", "spoke_sap", "peering", style="dashed", color=AzureColor.GREEN),
        DiagramEdge("gw", "er", "", color=AzureColor.GREEN),
    ])

    return gen.generate_svg()


def generate_identity_diagram(subscription_name: str, location: str) -> str:
    """Generate the Identity Landing Zone architecture diagram."""
    gen = AzureDiagramGenerator()
    gen.title = "Platform Identity Landing Zone — As-Built"
    gen.subtitle = f"{subscription_name}  ·  {location}"

    gen.groups.append(DiagramGroup("sub", f"Subscription: {subscription_name}",
                                   10, 10, 640, 380, AzureColor.PURPLE, "subscription"))

    gen.groups.append(DiagramGroup("ad", "Active Directory Domain Services",
                                   30, 50, 600, 140, AzureColor.PURPLE, "active_directory"))
    gen.nodes.extend([
        DiagramNode("dc1", "Domain Controller 1", "active_directory", 50, 80, 130, 90,
                    sublabel=f"{location} AZ-1"),
        DiagramNode("dc2", "Domain Controller 2", "active_directory", 200, 80, 130, 90,
                    sublabel=f"{location} AZ-2"),
        DiagramNode("aadcon", "Entra Connect", "active_directory", 370, 80, 130, 90,
                    sublabel="Hybrid sync"),
    ])

    gen.groups.append(DiagramGroup("pim", "Privileged Access",
                                   30, 210, 600, 160, AzureColor.PURPLE, "key_vault"))
    gen.nodes.extend([
        DiagramNode("pim", "PIM", "defender", 50, 240, 130, 90,
                    sublabel="JIT elevation"),
        DiagramNode("paw", "PAW Devices", "defender", 200, 240, 130, 90,
                    sublabel="Hardened admin"),
        DiagramNode("kv", "Key Vault", "key_vault", 370, 240, 130, 90,
                    sublabel="Secrets & certs"),
    ])

    gen.edges.extend([
        DiagramEdge("dc1", "dc2", "replication", color=AzureColor.PURPLE),
        DiagramEdge("dc2", "aadcon", "sync", color=AzureColor.PURPLE),
        DiagramEdge("pim", "paw", "requires", style="dashed", color=AzureColor.PURPLE),
    ])

    return gen.generate_svg()


def generate_security_diagram(subscription_name: str, location: str) -> str:
    """Generate the Security Landing Zone architecture diagram."""
    gen = AzureDiagramGenerator()
    gen.title = "Platform Security Landing Zone — As-Built"
    gen.subtitle = f"{subscription_name}  ·  {location}  ·  Dedicated SecOps"

    gen.groups.append(DiagramGroup("sub", f"Subscription: {subscription_name}",
                                   10, 10, 780, 380, AzureColor.RED, "subscription"))

    gen.groups.append(DiagramGroup("siem", "SIEM & Threat Intelligence",
                                   30, 50, 740, 140, AzureColor.RED, "sentinel"))
    gen.nodes.extend([
        DiagramNode("sec_sentinel", "Sentinel (SecOps)", "sentinel", 50, 80, 150, 90,
                    sublabel="Dedicated workspace"),
        DiagramNode("sec_defender", "Defender for Cloud", "defender", 220, 80, 150, 90,
                    sublabel="All 6 plans"),
        DiagramNode("soar", "SOAR Playbooks", "automation", 390, 80, 150, 90,
                    sublabel="Logic Apps"),
        DiagramNode("ti", "Threat Intel", "sentinel", 560, 80, 150, 90,
                    sublabel="TAXII feeds"),
    ])

    gen.groups.append(DiagramGroup("response", "Incident Response & Forensics",
                                   30, 210, 740, 160, AzureColor.PURPLE, "defender"))
    gen.nodes.extend([
        DiagramNode("ir_kv", "Forensics Vault", "key_vault", 50, 240, 150, 90,
                    sublabel="Evidence storage"),
        DiagramNode("ir_law", "Forensics LAW", "log_analytics", 220, 240, 150, 90,
                    sublabel="Long-term retention"),
        DiagramNode("ir_auto", "Auto-Remediation", "automation", 390, 240, 150, 90,
                    sublabel="Policy-driven"),
        DiagramNode("ir_alerts", "Alert Rules", "monitor", 560, 240, 150, 90,
                    sublabel="Sev 0-2 → PagerDuty"),
    ])

    gen.edges.extend([
        DiagramEdge("sec_sentinel", "sec_defender", "ingests", color=AzureColor.RED),
        DiagramEdge("sec_defender", "soar", "triggers", color=AzureColor.RED),
        DiagramEdge("soar", "ti", "enriches", color=AzureColor.RED),
        DiagramEdge("soar", "ir_auto", "remediates", style="dashed", color=AzureColor.PURPLE),
        DiagramEdge("ir_auto", "ir_alerts", "notifies", color=AzureColor.ORANGE),
    ])

    return gen.generate_svg()


def generate_app_lz_diagram(profile: str, lz_name: str, display_name: str,
                             subscription_name: str, location: str,
                             vnet_cidr: str = "") -> str:
    """Generate an Application Landing Zone architecture diagram based on profile."""
    gen = AzureDiagramGenerator()
    gen.title = f"Application Landing Zone: {display_name} — As-Built"
    gen.subtitle = f"{subscription_name}  ·  {location}  ·  Profile: {profile}"

    if profile == "corp":
        return _generate_corp_diagram(gen, display_name, subscription_name, location,
                                       vnet_cidr or "10.2.0.0/16")
    elif profile == "online":
        return _generate_online_diagram(gen, display_name, subscription_name, location,
                                         vnet_cidr or "10.1.0.0/16")
    elif profile == "sap":
        return _generate_sap_diagram(gen, display_name, subscription_name, location,
                                      vnet_cidr or "10.5.0.0/16")
    elif profile == "sandbox":
        return _generate_sandbox_diagram(gen, display_name, subscription_name, location,
                                          vnet_cidr or "10.10.0.0/16")
    else:
        # Generic fallback
        gen.groups.append(DiagramGroup("sub", f"Subscription: {subscription_name}",
                                       10, 10, 500, 200, AzureColor.BLUE, "subscription"))
        gen.nodes.append(DiagramNode("app", display_name, "app_service", 50, 60, 150, 90))
        return gen.generate_svg()


def _generate_corp_diagram(gen, display_name, sub_name, location, cidr):
    gen.groups.append(DiagramGroup("sub", f"Subscription: {sub_name}",
                                   10, 10, 780, 430, AzureColor.BLUE, "subscription"))

    gen.groups.append(DiagramGroup("vnet_g", f"Corp VNet ({cidr})",
                                   30, 50, 740, 180, AzureColor.GREEN, "vnet"))
    gen.nodes.extend([
        DiagramNode("app_sub", "App Subnet", "subnet", 50, 85, 120, 75, sublabel="/24"),
        DiagramNode("data_sub", "Data Subnet", "subnet", 190, 85, 120, 75, sublabel="/24"),
        DiagramNode("shared_sub", "Shared Services", "subnet", 330, 85, 120, 75, sublabel="/24"),
        DiagramNode("pe_sub", "Private Endpoints", "subnet", 470, 85, 120, 75, sublabel="/26"),
    ])

    gen.groups.append(DiagramGroup("svc", "Services",
                                   30, 250, 740, 170, AzureColor.BLUE, "app_service"))
    gen.nodes.extend([
        DiagramNode("kv", "Key Vault", "key_vault", 50, 285, 120, 75, sublabel="PE enabled"),
        DiagramNode("stor", "Storage Acct", "storage", 190, 285, 120, 75, sublabel="PE enabled"),
        DiagramNode("diag", "Diagnostics", "log_analytics", 330, 285, 120, 75,
                    sublabel="→ Central LAW"),
        DiagramNode("nsg1", "NSG Rules", "nsg", 470, 285, 120, 75, sublabel="Deny-all inbound"),
        DiagramNode("pol", "Azure Policy", "policy", 610, 285, 120, 75, sublabel="Corp baseline"),
    ])

    gen.edges.extend([
        DiagramEdge("app_sub", "pe_sub", "private link", style="dashed", color=AzureColor.GREEN),
        DiagramEdge("kv", "diag", "logs", color=AzureColor.ORANGE),
        DiagramEdge("stor", "diag", "logs", color=AzureColor.ORANGE),
    ])
    return gen.generate_svg()


def _generate_online_diagram(gen, display_name, sub_name, location, cidr):
    gen.groups.append(DiagramGroup("sub", f"Subscription: {sub_name}",
                                   10, 10, 780, 430, AzureColor.BLUE, "subscription"))

    gen.groups.append(DiagramGroup("edge_g", "Edge Protection",
                                   30, 50, 740, 130, AzureColor.RED, "waf"))
    gen.nodes.extend([
        DiagramNode("waf", "WAF Policy", "waf", 50, 75, 120, 80, sublabel="OWASP 3.2"),
        DiagramNode("ddos", "DDoS Standard", "ddos", 200, 75, 120, 80, sublabel="Auto-mitigate"),
        DiagramNode("afd", "Front Door", "app_service", 350, 75, 120, 80, sublabel="CDN + WAF"),
    ])

    gen.groups.append(DiagramGroup("vnet_g", f"Online VNet ({cidr})",
                                   30, 200, 740, 110, AzureColor.GREEN, "vnet"))
    gen.nodes.extend([
        DiagramNode("web_sub", "Web Subnet", "subnet", 50, 225, 120, 65, sublabel="/24"),
        DiagramNode("app_sub", "App Subnet", "subnet", 200, 225, 120, 65, sublabel="/24"),
        DiagramNode("data_sub", "Data Subnet", "subnet", 350, 225, 120, 65, sublabel="/24"),
    ])

    gen.groups.append(DiagramGroup("gov", "Governance & Observability",
                                   30, 330, 740, 90, AzureColor.TEAL, "policy"))
    gen.nodes.extend([
        DiagramNode("pol", "Azure Policy", "policy", 50, 345, 120, 60, sublabel="Online baseline"),
        DiagramNode("def", "Defender", "defender", 200, 345, 120, 60, sublabel="5 plans"),
        DiagramNode("diag", "Diagnostics", "log_analytics", 350, 345, 120, 60,
                    sublabel="→ Central LAW"),
    ])

    gen.edges.extend([
        DiagramEdge("waf", "afd", "protects", color=AzureColor.RED),
        DiagramEdge("afd", "web_sub", "routes", color=AzureColor.GREEN),
    ])
    return gen.generate_svg()


def _generate_sap_diagram(gen, display_name, sub_name, location, cidr):
    gen.groups.append(DiagramGroup("sub", f"Subscription: {sub_name}",
                                   10, 10, 780, 460, AzureColor.BLUE, "subscription"))

    gen.groups.append(DiagramGroup("vnet_g", f"SAP VNet ({cidr})",
                                   30, 50, 740, 200, AzureColor.GREEN, "vnet"))
    gen.nodes.extend([
        DiagramNode("app_sub", "SAP App Subnet", "subnet", 50, 85, 120, 75,
                    sublabel="/24 · Accel Net"),
        DiagramNode("db_sub", "HANA DB Subnet", "subnet", 190, 85, 120, 75,
                    sublabel="/24 · Accel Net"),
        DiagramNode("anf_sub", "ANF Subnet", "subnet", 330, 85, 120, 75,
                    sublabel="/26 · Delegated"),
        DiagramNode("web_sub", "Web Dispatcher", "subnet", 470, 85, 120, 75,
                    sublabel="/26"),
        DiagramNode("mgmt_sub", "Management", "subnet", 610, 85, 120, 75,
                    sublabel="/26"),
    ])

    gen.groups.append(DiagramGroup("compute", "SAP Compute & Storage",
                                   30, 270, 740, 170, "#0FAAFF", "sap"))
    gen.nodes.extend([
        DiagramNode("ppg", "Proximity Group", "sap", 50, 305, 120, 75,
                    sublabel="Low latency"),
        DiagramNode("anf", "NetApp Files", "anf", 190, 305, 120, 75,
                    sublabel="Ultra tier"),
        DiagramNode("kv", "Key Vault", "key_vault", 330, 305, 120, 75,
                    sublabel="SAP creds"),
        DiagramNode("diag", "Diagnostics", "log_analytics", 470, 305, 120, 75,
                    sublabel="→ Central LAW"),
        DiagramNode("er", "ExpressRoute", "express_route", 610, 305, 120, 75,
                    sublabel="To on-prem"),
    ])

    gen.edges.extend([
        DiagramEdge("app_sub", "db_sub", "private", color=AzureColor.GREEN),
        DiagramEdge("db_sub", "anf_sub", "NFS mount", color=AzureColor.GREEN),
        DiagramEdge("ppg", "anf", "co-located", style="dashed", color="#0FAAFF"),
    ])
    return gen.generate_svg()


def _generate_sandbox_diagram(gen, display_name, sub_name, location, cidr):
    gen.groups.append(DiagramGroup("sub", f"Subscription: {sub_name}",
                                   10, 10, 640, 320, AzureColor.TEAL, "subscription"))

    gen.groups.append(DiagramGroup("vnet_g", f"Sandbox VNet ({cidr}) — Standalone",
                                   30, 50, 590, 120, AzureColor.GREEN, "vnet"))
    gen.nodes.extend([
        DiagramNode("dev_sub", "Dev Subnet", "subnet", 50, 75, 120, 70, sublabel="/24"),
        DiagramNode("test_sub", "Test Subnet", "subnet", 200, 75, 120, 70, sublabel="/24"),
    ])

    gen.groups.append(DiagramGroup("gov", "Guardrails (relaxed)",
                                   30, 190, 590, 110, AzureColor.TEAL, "policy"))
    gen.nodes.extend([
        DiagramNode("budget", "Budget Cap", "budget", 50, 210, 120, 70,
                    sublabel="$500/mo"),
        DiagramNode("pol", "Sandbox Policy", "policy", 200, 210, 120, 70,
                    sublabel="No public IPs"),
        DiagramNode("diag", "Diagnostics", "log_analytics", 350, 210, 120, 70,
                    sublabel="30-day retention"),
    ])

    return gen.generate_svg()


def generate_full_estate_diagram(mg_prefix: str, subscriptions_config: dict) -> str:
    """Generate a full-estate overview diagram showing all landing zones."""
    gen = AzureDiagramGenerator()
    gen.title = "Azure Landing Zone — Full Estate Overview"
    gen.subtitle = f"Management Group Prefix: {mg_prefix}  ·  {len(subscriptions_config.get('platform', {}))} Platform + {len([k for k in subscriptions_config.get('application', {}) if not k.startswith('_')])} Application LZs"

    # Root management group
    gen.groups.append(DiagramGroup("root", f"{mg_prefix} (Azure Landing Zones)",
                                   10, 10, 960, 530, AzureColor.DARK_BLUE, "management_group"))

    # Platform row
    gen.groups.append(DiagramGroup("plat", "Platform Landing Zones",
                                   30, 50, 920, 150, AzureColor.BLUE, "subscription"))

    x = 50
    platform_lzs = [
        ("mgmt", "Management", "log_analytics", "Sub 1"),
        ("conn", "Connectivity", "vnet", "Sub 2"),
        ("ident", "Identity", "active_directory", "Sub 3"),
        ("sec", "Security", "sentinel", "Sub 4"),
    ]
    for nid, label, icon, sub_label in platform_lzs:
        gen.nodes.append(DiagramNode(nid, label, icon, x, 85, 140, 90, sublabel=sub_label))
        x += 160

    # App LZ row
    gen.groups.append(DiagramGroup("apps", "Application Landing Zones (configurable)",
                                   30, 220, 920, 150, AzureColor.GREEN, "app_service"))

    app_section = subscriptions_config.get("application", {})
    x = 50
    for key, cfg in app_section.items():
        if key.startswith("_"):
            continue
        profile = cfg.get("profile", "")
        icon = {"corp": "vnet", "online": "waf", "sap": "sap", "sandbox": "budget"}.get(profile, "app_service")
        gen.nodes.append(DiagramNode(
            f"app_{key}", cfg.get("display_name", key), icon,
            x, 255, 130, 90,
            sublabel=f"Profile: {profile}"
        ))
        x += 150

    # Shared services row
    gen.groups.append(DiagramGroup("shared", "Cross-Cutting Services",
                                   30, 390, 920, 130, AzureColor.ORANGE, "policy"))
    gen.nodes.extend([
        DiagramNode("sh_policy", "Azure Policy", "policy", 50, 420, 120, 75,
                    sublabel="CAF baseline"),
        DiagramNode("sh_defender", "Defender for Cloud", "defender", 200, 420, 120, 75,
                    sublabel="All plans"),
        DiagramNode("sh_monitor", "Azure Monitor", "monitor", 350, 420, 120, 75,
                    sublabel="Central LAW"),
        DiagramNode("sh_cost", "Cost Management", "budget", 500, 420, 120, 75,
                    sublabel="Per-LZ budgets"),
        DiagramNode("sh_keyvault", "Key Vault", "key_vault", 650, 420, 120, 75,
                    sublabel="Per-LZ vaults"),
    ])

    # Data flow edges
    gen.edges.extend([
        DiagramEdge("mgmt", "conn", "depends", style="dashed", color=AzureColor.BLUE),
        DiagramEdge("conn", "ident", "depends", style="dashed", color=AzureColor.BLUE),
        DiagramEdge("ident", "sec", "depends", style="dashed", color=AzureColor.BLUE),
    ])

    return gen.generate_svg()


# ── Unified Diagram Facade ────────────────────────────────────────────────────
# Selectable engine: "python" (diagrams lib → PNG) | "svg" (custom SVG) | "drawio"


def generate_diagrams(
    engine: str = "python",
    output_dir: str = "docs/diagrams",
    mg_prefix: str = "alz",
    subscriptions_config: dict | None = None,
) -> list[str]:
    """Generate the standard set of ALZ architecture diagrams.

    Args:
        engine: "python" for PNG via diagrams library (default),
                "svg" for built-in custom SVG generator,
                "drawio" for Draw.io MCP (external — returns empty list).
        output_dir: Directory for output files.
        mg_prefix: Management group prefix.
        subscriptions_config: Optional subscriptions config for full-estate diagram.

    Returns:
        List of generated file paths.
    """
    if engine == "python":
        from src.tools.python_diagram_generator import DiagramEngine

        eng = DiagramEngine(output_dir=output_dir)
        outputs = [
            eng.generate_mg_hierarchy(mg_prefix=mg_prefix),
            eng.generate_hub_spoke(),
            eng.generate_security_governance(),
            eng.generate_alz_architecture(mg_prefix=mg_prefix),
        ]
        if subscriptions_config:
            outputs.append(eng.generate_full_estate(mg_prefix, subscriptions_config))
        return outputs

    elif engine == "svg":
        from pathlib import Path

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        outputs = []
        for name, gen_func in [
            ("management-group-hierarchy.svg", generate_management_subscription_diagram),
            ("hub-spoke-network.svg", lambda: generate_hub_spoke_diagram("hub_spoke")),
            ("full-estate.svg", lambda: generate_full_estate_diagram(
                mg_prefix, subscriptions_config or {})),
        ]:
            svg = gen_func()
            path = out / name
            path.write_text(svg)
            outputs.append(str(path))
        return outputs

    elif engine == "drawio":
        logger.info("Draw.io engine selected — diagrams generated via MCP server, not locally.")
        return []

    else:
        raise ValueError(f"Unknown diagram engine: {engine!r}. Use 'python', 'svg', or 'drawio'.")
