"""Draw.io as-built diagram generator.

Emits production-quality Draw.io XML (`.drawio`) using the official Azure
public service icon library, and renders the same composition to SVG for
inline embedding in the TDD Word document.

Why this exists:
  - The `diagrams` (Graphviz) library produces functional but utilitarian
    PNGs that don't match the Microsoft ALZ reference visual style.
  - The Draw.io MCP server produces beautiful diagrams interactively but
    can't run in a headless CI/CD pipeline.
  - This module replicates the MCP server's output programmatically so
    the same quality is available in the deployment pipeline.

Output artifacts per call:
  1. `<name>.drawio` — editable source diagram (CAF-aligned visual style)
  2. `<name>.svg`    — composed SVG with real Azure icons (embeds in Word)

Both files use the same Azure icon SVGs from the library, so they look
identical.
"""

from __future__ import annotations

import html
import json
import logging
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# ─── Azure icon library ───────────────────────────────────────────────────────

ICON_LIBRARY_PATH = (
    Path(__file__).resolve().parents[2]
    / "mcp" / "drawio-mcp-server" / "assets"
    / "azure-public-service-icons"
    / "000 all azure public service icons.xml"
)


@dataclass(frozen=True)
class IconEntry:
    """One resolved icon from the library."""

    name: str  # e.g. "Virtual Networks"
    style: str  # full Draw.io style string (with embedded base64 SVG)
    svg_b64: str  # base64-encoded raw SVG payload, for SVG rendering
    width: int
    height: int


class IconLibrary:
    """Lazy loader for the Azure icon catalog."""

    _instance: IconLibrary | None = None

    def __init__(self, path: Path = ICON_LIBRARY_PATH):
        self.path = path
        self._by_key: dict[str, IconEntry] = {}
        self._loaded = False

    @classmethod
    def shared(cls) -> IconLibrary:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def _normalize(name: str) -> str:
        """Reduce a name to a fuzzy-match key: 'Virtual Networks' → 'virtualnetworks'."""
        n = unicodedata.normalize("NFKD", name)
        n = n.lower()
        n = re.sub(r"[^a-z0-9]+", "", n)
        return n

    def _load(self) -> None:
        if self._loaded:
            return
        if not self.path.exists():
            raise FileNotFoundError(f"Azure icon library not found: {self.path}")
        raw = self.path.read_text()
        inner = re.sub(r"</?mxlibrary[^>]*>", "", raw).strip()
        entries = json.loads(inner)
        style_re = re.compile(r'style="([^"]+)"')
        image_re = re.compile(r"image=data:image/svg\+xml,([A-Za-z0-9+/=]+)")
        for e in entries:
            title = e.get("title", "")
            if not title:
                continue
            # Title format: "10061-icon-service-Virtual-Networks" → "Virtual Networks"
            m = re.match(r"^\d+-icon-service-(.+)$", title)
            if not m:
                continue
            display = m.group(1).replace("-", " ")
            decoded = html.unescape(e["xml"])
            style_match = style_re.search(decoded)
            if not style_match:
                continue
            style = style_match.group(1)
            img_match = image_re.search(style)
            svg_b64 = img_match.group(1) if img_match else ""
            entry = IconEntry(
                name=display,
                style=style,
                svg_b64=svg_b64,
                width=int(e.get("w", 48)),
                height=int(e.get("h", 48)),
            )
            self._by_key[self._normalize(display)] = entry
        self._loaded = True
        logger.debug("Loaded %d Azure icons from %s", len(self._by_key), self.path)

    def get(self, name: str) -> IconEntry:
        """Look up an icon by display name (fuzzy)."""
        self._load()
        key = self._normalize(name)
        if key in self._by_key:
            return self._by_key[key]
        # Try common aliases / suffix tolerance
        for suffix in ("s", "es"):
            if self._normalize(name + suffix) in self._by_key:
                return self._by_key[self._normalize(name + suffix)]
            stripped = re.sub(rf"{suffix}$", "", key)
            if stripped in self._by_key:
                return self._by_key[stripped]
        raise KeyError(f"Azure icon not found: {name!r}")

    def has(self, name: str) -> bool:
        try:
            self.get(name)
            return True
        except KeyError:
            return False


# ─── Diagram builder ──────────────────────────────────────────────────────────


@dataclass
class _Cell:
    cid: str
    kind: str  # 'vertex' | 'edge' | 'container' | 'text' | 'icon'
    x: float = 0
    y: float = 0
    w: float = 0
    h: float = 0
    label: str = ""
    style: str = ""
    source: str = ""
    target: str = ""
    icon: IconEntry | None = None


class DrawioBuilder:
    """Composes a Draw.io page and renders to .drawio XML or SVG."""

    PAGE_W = 850
    PAGE_H = 1100

    def __init__(self, library: IconLibrary | None = None):
        self.lib = library or IconLibrary.shared()
        self._cells: list[_Cell] = []
        self._counter = 0

    # ── primitives ────────────────────────────────────────────────────────

    def _next_id(self, prefix: str = "c") -> str:
        self._counter += 1
        return f"{prefix}-{self._counter}"

    def container(
        self,
        x: float, y: float, w: float, h: float,
        *, fill: str = "#F2F7FB", stroke: str = "#0078D4",
        dashed: bool = False, stroke_width: float = 1.0,
    ) -> str:
        dash = "dashed=1;dashPattern=8 4;" if dashed else ""
        style = (
            f"rounded=1;whiteSpace=wrap;fillColor={fill};strokeColor={stroke};"
            f"arcSize=2;strokeWidth={stroke_width};{dash}"
        )
        cid = self._next_id("box")
        self._cells.append(_Cell(cid=cid, kind="container", x=x, y=y, w=w, h=h, style=style))
        return cid

    def text(
        self,
        x: float, y: float, w: float, h: float, label: str,
        *, font_size: int = 11, bold: bool = False, italic: bool = False,
        color: str = "#333333", align: str = "left",
    ) -> str:
        weight = 1 if bold else 0
        if italic:
            weight |= 2
        style = (
            f"text;fontSize={font_size};fontStyle={weight};fontColor={color};"
            f"align={align};verticalAlign=middle;"
        )
        cid = self._next_id("txt")
        self._cells.append(
            _Cell(cid=cid, kind="text", x=x, y=y, w=w, h=h, label=label, style=style)
        )
        return cid

    def icon(
        self, shape_name: str, x: float, y: float, label: str,
        *, size: int = 48,
    ) -> str:
        icon = self.lib.get(shape_name)
        cid = self._next_id("ic")
        self._cells.append(
            _Cell(cid=cid, kind="icon", x=x, y=y, w=size, h=size,
                  label=label, style=icon.style, icon=icon)
        )
        return cid

    def edge(
        self,
        source: str, target: str,
        *, color: str = "#0078D4", dashed: bool = False,
        width: float = 2.0, label: str = "",
        around: bool = False, route_y: float | None = None,
    ) -> str:
        """Create an edge between two cells.

        When `around=True`, the edge exits the bottom of the source, drops to
        ``route_y``, traverses horizontally, and enters the bottom of the
        target. Use this for connections that would otherwise cut through
        intervening container boundaries. The caller is responsible for
        choosing a ``route_y`` that lies in unused whitespace below both
        containers.
        """
        dash = "dashed=1;" if dashed else ""
        if around:  # noqa: SIM108
            # Anchors are direction-aware: top vs bottom is decided in the
            # SVG renderer; for Draw.io we always use bottom-to-bottom (a
            # no-op approximation — Draw.io's auto-router will pick a
            # reasonable path). Real visual fidelity comes from the SVG.
            anchors = "exitX=0.5;exitY=1;entryX=0.5;entryY=1;"
        else:
            anchors = "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
        style = (
            f"edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor={color};"
            f"strokeWidth={width};endArrow=blockThin;endFill=1;{dash}"
            f"{anchors}"
        )
        cid = self._next_id("edge")
        cell = _Cell(
            cid=cid, kind="edge", source=source, target=target,
            label=label, style=style,
        )
        # Stash route metadata on the cell for the SVG renderer
        cell.x = float(route_y) if (around and route_y is not None) else 0
        cell.y = 1.0 if around else 0.0  # flag in y-slot
        self._cells.append(cell)
        return cid

    # ── output ────────────────────────────────────────────────────────────

    def to_drawio_xml(self) -> str:
        """Emit a complete .drawio XML document."""
        parts = [
            '<mxfile host="agentic-alz-accelerator">',
            '<diagram id="page-1" name="Page-1">',
            f'<mxGraphModel dx="800" dy="600" grid="1" gridSize="10" '
            f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
            f'page="1" pageScale="1" pageWidth="{self.PAGE_W}" '
            f'pageHeight="{self.PAGE_H}" math="0" shadow="0" background="#FFFFFF">',
            "<root>",
            '<mxCell id="0"/>',
            '<mxCell id="1" parent="0"/>',
        ]
        for c in self._cells:
            label_attr = html.escape(c.label, quote=True)
            if c.kind == "edge":
                parts.append(
                    f'<mxCell id="{c.cid}" value="{label_attr}" style="{c.style}" '
                    f'edge="1" parent="1" source="{c.source}" target="{c.target}">'
                    f'<mxGeometry relative="1" as="geometry"/></mxCell>'
                )
            else:
                parts.append(
                    f'<mxCell id="{c.cid}" value="{label_attr}" style="{c.style}" '
                    f'vertex="1" parent="1">'
                    f'<mxGeometry x="{c.x}" y="{c.y}" width="{c.w}" '
                    f'height="{c.h}" as="geometry"/></mxCell>'
                )
        parts.extend(["</root>", "</mxGraphModel>", "</diagram>", "</mxfile>"])
        return "".join(parts)

    def to_svg(self, *, width: int | None = None, height: int | None = None) -> str:
        """Compose all cells into a single standalone SVG.

        Used for inline embedding in the TDD Word document. Renders Azure
        icons by inlining their decoded SVG payloads, draws boxes and text
        with native SVG primitives, and routes orthogonal edges with
        right-angle joins.
        """
        w = width or self.PAGE_W
        h = height or self.PAGE_H
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="Segoe UI, Arial, sans-serif">',
            f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>',
        ]

        by_id: dict[str, _Cell] = {c.cid: c for c in self._cells}

        # Defs for arrow marker
        parts.append(
            '<defs>'
            '<marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="#0078D4"/></marker>'
            '<marker id="arrow-gray" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="#999999"/></marker>'
            '</defs>'
        )

        # Containers first (background)
        for c in self._cells:
            if c.kind == "container":
                fill = self._style_value(c.style, "fillColor", "#F2F7FB")
                stroke = self._style_value(c.style, "strokeColor", "#0078D4")
                sw = self._style_value(c.style, "strokeWidth", "1")
                dash = "8 4" if "dashed=1" in c.style else "none"
                parts.append(
                    f'<rect x="{c.x}" y="{c.y}" width="{c.w}" height="{c.h}" '
                    f'rx="6" ry="6" fill="{fill}" stroke="{stroke}" '
                    f'stroke-width="{sw}" stroke-dasharray="{dash}"/>'
                )

        # Edges
        for c in self._cells:
            if c.kind == "edge":
                src, tgt = by_id.get(c.source), by_id.get(c.target)
                if not src or not tgt:
                    continue
                color = self._style_value(c.style, "strokeColor", "#0078D4")
                sw = self._style_value(c.style, "strokeWidth", "2")
                dasharray = "6 4" if "dashed=1" in c.style else "none"
                marker = "arrow-blue" if color.upper() == "#0078D4" else "arrow-gray"
                around = c.y == 1.0
                if around:
                    # Detour vertically through `route_y`. Exit the side of
                    # src (top or bottom) closer to route_y; enter tgt the
                    # same way. Works whether route_y is above or below.
                    route_y = c.x or max(src.y + src.h, tgt.y + tgt.h) + 60
                    src_cx = src.x + src.w / 2
                    tgt_cx = tgt.x + tgt.w / 2
                    src_anchor = (
                        src.y + src.h if route_y >= src.y + src.h / 2 else src.y
                    )
                    tgt_anchor = (
                        tgt.y + tgt.h if route_y >= tgt.y + tgt.h / 2 else tgt.y
                    )
                    d = (
                        f"M {src_cx} {src_anchor} "
                        f"L {src_cx} {route_y} "
                        f"L {tgt_cx} {route_y} "
                        f"L {tgt_cx} {tgt_anchor}"
                    )
                else:
                    x1 = src.x + src.w
                    y1 = src.y + src.h / 2
                    x2 = tgt.x
                    y2 = tgt.y + tgt.h / 2
                    if abs(y1 - y2) < 0.5:
                        d = f"M {x1} {y1} L {x2 - 6} {y2}"
                    else:
                        mid_x = (x1 + x2) / 2
                        d = (
                            f"M {x1} {y1} L {mid_x} {y1} "
                            f"L {mid_x} {y2} L {x2 - 6} {y2}"
                        )
                parts.append(
                    f'<path d="{d}" fill="none" stroke="{color}" '
                    f'stroke-width="{sw}" stroke-dasharray="{dasharray}" '
                    f'marker-end="url(#{marker})"/>'
                )

        # Icons + text (foreground)
        for c in self._cells:
            if c.kind == "icon" and c.icon and c.icon.svg_b64:
                # Inline the icon SVG via an <image> with data URI
                parts.append(
                    f'<image x="{c.x}" y="{c.y}" width="{c.w}" height="{c.h}" '
                    f'xlink:href="data:image/svg+xml;base64,{c.icon.svg_b64}"/>'
                )
                if c.label:
                    label = html.escape(c.label)
                    parts.append(
                        f'<text x="{c.x + c.w/2}" y="{c.y + c.h + 12}" '
                        f'font-size="10" fill="#333333" text-anchor="middle">'
                        f'{label}</text>'
                    )
            elif c.kind == "text":
                fs = self._style_value(c.style, "fontSize", "11")
                weight_val = int(self._style_value(c.style, "fontStyle", "0"))
                fw = "bold" if weight_val & 1 else "normal"
                fst = "italic" if weight_val & 2 else "normal"
                color = self._style_value(c.style, "fontColor", "#333333")
                align = self._style_value(c.style, "align", "left")
                tx = c.x + (c.w / 2 if align == "center" else 0)
                anchor = "middle" if align == "center" else "start"
                label = html.escape(c.label)
                parts.append(
                    f'<text x="{tx}" y="{c.y + c.h - 4}" font-size="{fs}" '
                    f'fill="{color}" font-weight="{fw}" font-style="{fst}" '
                    f'text-anchor="{anchor}">{label}</text>'
                )

        parts.append("</svg>")
        return "".join(parts)

    @staticmethod
    def _style_value(style: str, key: str, default: str) -> str:
        m = re.search(rf"{re.escape(key)}=([^;]+)", style)
        return m.group(1) if m else default


# ─── Profile-based engine ─────────────────────────────────────────────────────


class DrawioEngine:
    """Generates Draw.io and SVG TDD diagrams per landing-zone profile."""

    def __init__(self, output_dir: str | Path = "agent-output/tdd"):
        self.output_dir = Path(output_dir)
        self.lib = IconLibrary.shared()

    def generate_tdd_diagram(
        self,
        profile: str,
        project_name: str,
        subscription_name: str,
        location: str,
        output_dir: str | Path | None = None,
        filename: str | None = None,
    ) -> tuple[str, str]:
        """Generate a Draw.io + SVG diagram pair.

        Returns (drawio_path, svg_path).
        """
        out = Path(output_dir) if output_dir else self.output_dir
        out.mkdir(parents=True, exist_ok=True)
        fname = filename or f"TDD_{project_name}_architecture"

        dispatch = {
            "platform-management": self._management,
            "platform-connectivity": self._connectivity,
            "platform-identity": self._identity,
            "platform-security": self._security,
        }
        builder = DrawioBuilder(self.lib)
        if profile in dispatch:
            dispatch[profile](builder, subscription_name, location)
        else:
            display_name = project_name.replace("-", " ").title()
            self._app_lz(builder, subscription_name, location, profile, display_name)

        drawio_path = out / f"{fname}.drawio"
        svg_path = out / f"{fname}.svg"
        drawio_path.write_text(builder.to_drawio_xml())
        svg_path.write_text(builder.to_svg())
        return str(drawio_path), str(svg_path)

    # ── Layout helpers ────────────────────────────────────────────────────

    def _header(
        self, b: DrawioBuilder, title: str, sub: str, loc: str,
    ) -> None:
        """Outer subscription envelope + identity icon + title."""
        b.container(40, 40, 770, 820, fill="#E6F2FA", stroke="#0078D4",
                    dashed=True, stroke_width=1.5)
        # Subscription icon (top-left, no inline label so we control text)
        b.icon("Subscriptions", 50, 50, "")
        b.text(110, 50, 280, 22, f"{title} subscription",
               font_size=14, bold=True, color="#0078D4")
        b.text(110, 74, 280, 18, f"{sub}  ·  {loc}",
               font_size=10, italic=True, color="#666666")

    def _governance_row(self, b: DrawioBuilder, y: int = 670) -> None:
        """Bottom-of-page cross-cutting governance icons."""
        items = [
            ("Alerts", "Action Groups"),
            ("Cost Management", "Cost Management"),
            ("Managed Identities", "Role Assignment"),
            ("Policy", "Policy Assignment"),
            ("Network Watcher", "Network Watcher"),
            ("Microsoft Defender for Cloud", "Defender for Cloud"),
            ("Update Management Center", "Update Manager"),
        ]
        x = 80
        for shape, label in items:
            b.icon(shape, x, y, label)
            x += 100

    # ── Profile generators ────────────────────────────────────────────────

    def _identity(self, b: DrawioBuilder, sub: str, loc: str) -> None:
        self._header(b, "Identity", sub, loc)

        # Region 1
        b.container(55, 135, 370, 210, fill="#F2F7FB", stroke="#0078D4")
        b.container(440, 135, 355, 210, fill="#FFFFFF", stroke="#BBBBBB")
        b.text(60, 110, 200, 18, "Virtual network", font_size=11, bold=True)
        b.text(445, 110, 200, 18, "Resource group", font_size=11, bold=True)
        vnet1 = b.icon("Virtual Networks", 80, 160, "VNet")
        b.icon("DNS Zones", 170, 160, "DNS")
        b.icon("Route Tables", 260, 160, "UDRs")
        b.icon("Network Security Groups", 345, 160, "NSGs / ASGs")
        dc1_r1 = b.icon("Virtual Machine", 460, 160, "DC1")
        b.icon("Virtual Machine", 545, 160, "DC2")
        b.icon("Virtual Machine", 630, 160, "DC3")
        rsv_r1 = b.icon("Recovery Services Vaults", 720, 160, "Recovery Services Vault")
        b.text(460, 245, 35, 18, "OR", font_size=10, bold=True,
               color="#666666", align="center")
        b.icon("Entra Domain Services", 510, 238, "Entra Domain Services")

        # Region N
        b.container(55, 405, 370, 210, fill="#F2F7FB", stroke="#0078D4")
        b.container(440, 405, 355, 210, fill="#FFFFFF", stroke="#BBBBBB")
        b.text(60, 380, 140, 18, "Virtual network", font_size=11, bold=True)
        b.text(200, 380, 80, 18, "region N", font_size=10, italic=True, color="#888888")
        b.text(445, 380, 200, 18, "Resource group", font_size=11, bold=True)
        vnet2 = b.icon("Virtual Networks", 80, 430, "VNet")
        b.icon("DNS Zones", 170, 430, "DNS")
        b.icon("Route Tables", 260, 430, "UDRs")
        b.icon("Network Security Groups", 345, 430, "NSGs / ASGs")
        dc1_rn = b.icon("Virtual Machine", 460, 430, "DC1")
        b.icon("Virtual Machine", 545, 430, "DC2")
        b.icon("Virtual Machine", 630, 430, "DC3")
        rsv_rn = b.icon("Recovery Services Vaults", 720, 430, "Recovery Services Vault")
        b.text(460, 515, 35, 18, "OR", font_size=10, bold=True,
               color="#666666", align="center")
        b.icon("Entra Domain Services", 510, 508, "Entra Domain Services")

        # Edges: VNet → DC1 routes around (under region container);
        # DC1 → RSV stays inline (same container).
        b.edge(vnet1, dc1_r1, color="#0078D4", width=2,
               around=True, route_y=370)
        b.edge(dc1_r1, rsv_r1, color="#999999", width=1.5, dashed=True)
        b.edge(vnet2, dc1_rn, color="#0078D4", width=2,
               around=True, route_y=640)
        b.edge(dc1_rn, rsv_rn, color="#999999", width=1.5, dashed=True)

        self._governance_row(b, y=720)

    def _management(self, b: DrawioBuilder, sub: str, loc: str) -> None:
        self._header(b, "Management", sub, loc)

        # Resource group: monitoring & analytics
        b.container(55, 135, 370, 210, fill="#FFFFFF", stroke="#BBBBBB")
        b.text(60, 110, 250, 18, "Monitoring & Analytics", font_size=11, bold=True)
        law = b.icon("Log Analytics Workspaces", 75, 160, "Log Analytics")
        sentinel = b.icon("Azure Sentinel", 170, 160, "Sentinel")
        b.icon("Monitor", 260, 160, "Monitor")
        b.icon("Application Insights", 345, 160, "App Insights")
        # Row 2 shifted right so column x~99 (above Log Analytics) stays
        # clear for the policy->law cross-container edge.
        b.icon("Azure Workbooks", 260, 250, "Workbooks")
        b.icon("Azure Monitor Dashboard", 345, 250, "Dashboards")

        # Resource group: operations & continuity
        b.container(440, 135, 355, 210, fill="#FFFFFF", stroke="#BBBBBB")
        b.text(445, 110, 250, 18, "Operations & Continuity", font_size=11, bold=True)
        auto = b.icon("Automation Accounts", 460, 160, "Automation")
        rsv = b.icon("Recovery Services Vaults", 545, 160, "Recovery Vault")
        b.icon("Alerts", 630, 160, "Action Groups")

        # Resource group: governance
        b.container(55, 405, 740, 210, fill="#F2F7FB", stroke="#0078D4")
        b.text(60, 380, 200, 18, "Governance", font_size=11, bold=True)
        policy = b.icon("Policy", 100, 460, "Azure Policy")
        b.icon("Cost Management", 220, 460, "Budget Alerts")
        b.icon("Microsoft Defender for Cloud", 340, 460, "Defender")
        b.icon("Compliance", 460, 460, "Compliance")
        b.icon("Update Management Center", 580, 460, "Update Manager")

        # Edges
        b.edge(law, sentinel, color="#0078D4", width=2)
        b.edge(auto, rsv, color="#999999", width=1.5, dashed=True)
        # policy (in governance container, below) → law (in monitoring, above)
        b.edge(policy, law, color="#999999", width=1.5, dashed=True,
               around=True, route_y=375)

        self._governance_row(b, y=720)

    def _connectivity(self, b: DrawioBuilder, sub: str, loc: str) -> None:
        self._header(b, "Connectivity", sub, loc)

        # Hub VNet container
        b.container(55, 135, 740, 280, fill="#F2F7FB", stroke="#0078D4")
        b.text(60, 110, 200, 18, "Hub virtual network", font_size=11, bold=True)
        gw = b.icon("Virtual Network Gateways", 80, 175, "VPN/ER GW")
        fw = b.icon("Firewall", 200, 175, "Azure Firewall")
        bastion = b.icon("Bastions", 320, 175, "Bastion")
        b.icon("Route Tables", 440, 175, "Hub UDR")
        b.icon("DNS Zones", 560, 175, "Private DNS")
        b.icon("Public IP Addresses", 680, 175, "Public IPs")
        # Row 2 shifted past the Firewall column (x~200) so the
        # spokes->firewall cross-container edges drop into a clear channel.
        b.icon("DDOS Protection Plans", 80, 290, "DDoS Standard")
        b.icon("Network Security Groups", 260, 290, "NSGs")
        b.icon("Application Security Groups", 380, 290, "ASGs")
        b.icon("Network Watcher", 500, 290, "Network Watcher")

        # Spoke peering hint
        b.container(55, 470, 740, 145, fill="#FFFFFF", stroke="#BBBBBB")
        b.text(60, 445, 200, 18, "Peered spokes (illustrative)", font_size=11, bold=True)
        spoke1 = b.icon("Virtual Networks", 100, 510, "Corp spoke")
        spoke2 = b.icon("Virtual Networks", 280, 510, "Online spoke")
        b.icon("Virtual Networks", 460, 510, "Sandbox spoke")

        b.edge(gw, fw, color="#0078D4", width=2)
        b.edge(fw, bastion, color="#0078D4", width=2)
        # Spokes (lower container) → firewall (upper container) — route via gap
        b.edge(spoke1, fw, color="#999999", width=1.5, dashed=True,
               around=True, route_y=440)
        b.edge(spoke2, fw, color="#999999", width=1.5, dashed=True,
               around=True, route_y=440)

        self._governance_row(b, y=720)

    def _security(self, b: DrawioBuilder, sub: str, loc: str) -> None:
        self._header(b, "Security", sub, loc)

        # SOC
        b.container(55, 135, 370, 210, fill="#FFFFFF", stroke="#BBBBBB")
        b.text(60, 110, 280, 18, "Security Operations Center", font_size=11, bold=True)
        sentinel = b.icon("Azure Sentinel", 80, 160, "Sentinel SIEM/SOAR")
        defender = b.icon("Microsoft Defender for Cloud", 200, 160, "Defender for Cloud")
        b.icon("Compliance", 320, 160, "Secure Score")

        # Secrets
        b.container(440, 135, 355, 210, fill="#F2F7FB", stroke="#0078D4")
        b.text(445, 110, 200, 18, "Secrets & Keys", font_size=11, bold=True)
        kv1 = b.icon("Key Vaults", 460, 160, "Key Vault")
        b.icon("Key Vaults", 545, 160, "CMK Vault")
        b.icon("Dedicated HSM", 630, 160, "Managed HSM")

        # Posture
        b.container(55, 405, 740, 210, fill="#F2F7FB", stroke="#0078D4")
        b.text(60, 380, 280, 18, "Posture & Compliance", font_size=11, bold=True)
        policy = b.icon("Policy", 100, 460, "Security Baseline")
        b.icon("Microsoft Defender EASM", 220, 460, "EASM")
        b.icon("Microsoft Defender for IoT", 340, 460, "Defender for IoT")
        b.icon("Azure Sentinel", 460, 460, "Sentinel Workbooks")
        b.icon("Log Analytics Workspaces", 580, 460, "Log Analytics")

        b.edge(defender, sentinel, color="#0078D4", width=2, label="alerts")
        # KV (right container) → Sentinel (left container) — same row,
        # route via narrow band above containers' icon row.
        b.edge(kv1, sentinel, color="#999999", width=1.5, dashed=True,
               around=True, route_y=128)
        # Policy (lower container) → Defender (upper container)
        b.edge(policy, defender, color="#999999", width=1.5, dashed=True,
               around=True, route_y=375)

        self._governance_row(b, y=720)

    def _app_lz(
        self, b: DrawioBuilder, sub: str, loc: str,
        profile: str, display_name: str,
    ) -> None:
        self._header(b, display_name, sub, loc)

        # Networking
        b.container(55, 135, 370, 210, fill="#F2F7FB", stroke="#0078D4")
        b.text(60, 110, 200, 18, "Spoke virtual network", font_size=11, bold=True)
        spoke = b.icon("Virtual Networks", 80, 160, "Spoke VNet")
        b.icon("Network Security Groups", 170, 160, "NSGs")
        b.icon("Route Tables", 260, 160, "UDR → FW")
        b.icon("Private Endpoint", 345, 160, "Private Endpoints")

        # Workload
        b.container(440, 135, 355, 210, fill="#FFFFFF", stroke="#BBBBBB")
        b.text(445, 110, 200, 18, "Workload", font_size=11, bold=True)
        if profile == "online":
            front = b.icon("Front Door And CDN Profiles", 460, 160, "Front Door")
            app = b.icon("Application Gateways", 545, 160, "App GW + WAF")
            b.icon("App Services", 630, 160, "App Service")
        elif profile == "sap":
            front = b.icon("Virtual Machine", 460, 160, "SAP App")
            app = b.icon("Load Balancers", 545, 160, "Internal LB")
            b.icon("Virtual Machine", 630, 160, "SAP HANA")
        else:
            front = b.icon("Container Apps Environments", 460, 160, "Workload")
            app = b.icon("App Services", 545, 160, "API")
            b.icon("Function Apps", 630, 160, "Functions")

        # Data
        b.container(55, 405, 740, 210, fill="#F2F7FB", stroke="#0078D4")
        b.text(60, 380, 200, 18, "Data", font_size=11, bold=True)
        if profile == "sap":
            db = b.icon("Database Instance For SAP", 100, 460, "SAP HANA DB")
        else:
            db = b.icon("Azure Cosmos DB", 100, 460, "Cosmos DB")
        b.icon("Storage Accounts", 220, 460, "Storage")
        b.icon("SQL Database", 340, 460, "SQL DB")
        b.icon("Key Vaults", 460, 460, "Key Vault")

        b.edge(spoke, front, color="#0078D4", width=2,
               around=True, route_y=370)
        b.edge(front, app, color="#0078D4", width=2)
        # Workload (upper container) → DB (lower container)
        b.edge(app, db, color="#999999", width=1.5, dashed=True,
               around=True, route_y=380)

        self._governance_row(b, y=720)
