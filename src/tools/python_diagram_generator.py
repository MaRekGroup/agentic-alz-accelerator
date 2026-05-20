"""
Python Diagram Generator — uses the `diagrams` library (mingrammer/diagrams)
to produce architecture diagrams with official Azure icons and auto-layout.

Provides the same profile-based generation functions as azure_diagram_generator.py
but outputs PNG via Graphviz instead of custom SVG.

Usage:
    engine = DiagramEngine()
    engine.generate_alz_diagram(profile_name, config, output_path)
"""

import logging
from pathlib import Path
from typing import Any

from diagrams import Cluster, Diagram, Edge

# ── Azure icon imports ────────────────────────────────────────────────────
from diagrams.azure.compute import VM, ContainerApps, FunctionApps
from diagrams.azure.database import CosmosDb, DatabaseForMysqlServers
from diagrams.azure.general import (
    CostManagement,
    ManagementGroups,
    ResourceGroups,
    Subscriptions,
)
from diagrams.azure.identity import (
    ActiveDirectory,
    EntraConnect,
    EntraDomainServices,
    ManagedIdentities,
)
from diagrams.azure.integration import EventGridDomains
from diagrams.azure.managementgovernance import (
    AutomationAccounts,
    Blueprints,
    Compliance,
    Policy,
)
from diagrams.azure.monitor import (
    ApplicationInsights,
    LogAnalyticsWorkspaces,
    Monitor,
)
from diagrams.azure.network import (
    ApplicationGateway,
    DNSZones,
    ExpressrouteCircuits,
    Firewall,
    FrontDoors,
    LoadBalancers,
    PrivateEndpoint,
    RouteTables,
    Subnets,
    VirtualNetworkGateways,
    VirtualNetworks,
    VirtualWans,
)
from diagrams.azure.networking import Bastions, NetworkSecurityGroups
from diagrams.azure.security import (
    KeyVaults,
    MicrosoftDefenderForCloud,
    Sentinel,
)
from diagrams.azure.storage import BlobStorage, StorageAccounts

logger = logging.getLogger(__name__)

# ── Icon registry (string → class) ───────────────────────────────────────

ICON_MAP: dict[str, type] = {
    # General
    "management_group": ManagementGroups,
    "subscription": Subscriptions,
    "resource_group": ResourceGroups,
    "cost_management": CostManagement,
    # Networking
    "vnet": VirtualNetworks,
    "subnet": Subnets,
    "firewall": Firewall,
    "application_gateway": ApplicationGateway,
    "front_door": FrontDoors,
    "load_balancer": LoadBalancers,
    "vpn_gateway": VirtualNetworkGateways,
    "expressroute": ExpressrouteCircuits,
    "vwan": VirtualWans,
    "dns": DNSZones,
    "private_endpoint": PrivateEndpoint,
    "bastion": Bastions,
    "nsg": NetworkSecurityGroups,
    "route_table": RouteTables,
    # Compute
    "vm": VM,
    "container_app": ContainerApps,
    "function_app": FunctionApps,
    # Identity
    "active_directory": ActiveDirectory,
    "entra_ds": EntraDomainServices,
    "entra_connect": EntraConnect,
    "managed_identity": ManagedIdentities,
    # Security
    "key_vault": KeyVaults,
    "defender": MicrosoftDefenderForCloud,
    "sentinel": Sentinel,
    # Governance
    "policy": Policy,
    "compliance": Compliance,
    "automation": AutomationAccounts,
    "blueprints": Blueprints,
    # Monitor
    "monitor": Monitor,
    "log_analytics": LogAnalyticsWorkspaces,
    "app_insights": ApplicationInsights,
    # Data
    "cosmos_db": CosmosDb,
    "mysql": DatabaseForMysqlServers,
    "storage": StorageAccounts,
    "blob": BlobStorage,
    # Integration
    "event_grid": EventGridDomains,
}


def _icon(icon_type: str, label: str):
    """Instantiate a diagram node from a string icon type."""
    cls = ICON_MAP.get(icon_type, ResourceGroups)
    return cls(label)


# ── Diagram Engine ────────────────────────────────────────────────────────


class DiagramEngine:
    """Generates ALZ architecture diagrams using the `diagrams` library.

    Each generate_* method produces a PNG file at the given output path.
    Graphviz handles layout automatically — no manual x/y needed.
    """

    def __init__(self, output_dir: str = "agent-output/diagrams") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ── Management Group Hierarchy ────────────────────────────────────

    def generate_mg_hierarchy(
        self,
        mg_prefix: str = "mrg",
        filename: str = "01-management-group-hierarchy",
    ) -> str:
        """Generate management group hierarchy diagram."""
        outpath = str(self.output_dir / filename)
        with Diagram(
            f"{mg_prefix} — Management Group Hierarchy",
            filename=outpath,
            show=False,
            direction="TB",
            graph_attr={"bgcolor": "white", "pad": "0.5", "ranksep": "0.8", "dpi": "200"},
        ):
            root = ManagementGroups(f"{mg_prefix}\n(Root)")

            with Cluster("Platform"):
                mgmt = ManagementGroups("Management")
                mgmt_sub = Subscriptions("Management\nSubscription")
                mgmt_policy = Policy("Diagnostics\n& Monitoring")
                conn = ManagementGroups("Connectivity")
                conn_sub = Subscriptions("Connectivity\nSubscription")
                conn_policy = Policy("Network\nPolicies")
                ident = ManagementGroups("Identity")
                ident_sub = Subscriptions("Identity\nSubscription")
                ident_policy = Policy("Identity\nPolicies")
                sec = ManagementGroups("Security")
                sec_sub = Subscriptions("Security\nSubscription")
                sec_policy = Policy("Security\nBaseline")

            with Cluster("Landing Zones"):
                corp = ManagementGroups("Corp")
                corp_sub = Subscriptions("Corp LZ\nSubscription(s)")
                corp_policy = Policy("Corp Deny\nPublic IP")
                online = ManagementGroups("Online")
                online_sub = Subscriptions("Online LZ\nSubscription(s)")
                online_policy = Policy("Online\nAllow Public")

            with Cluster("Sandbox / Decom"):
                sandbox = ManagementGroups("Sandbox")
                sandbox_sub = Subscriptions("Sandbox\nSubscription(s)")
                decom = ManagementGroups("Decommissioned")
                decom_sub = Subscriptions("Decommissioned\nSubscription(s)")

            root >> Edge(color="purple") >> [mgmt, conn, ident, sec]
            root >> Edge(color="purple") >> [corp, online]
            root >> Edge(color="purple", style="dashed") >> [sandbox, decom]

            mgmt >> Edge(color="purple", style="dashed") >> mgmt_sub
            mgmt >> Edge(color="purple", style="dotted") >> mgmt_policy
            conn >> Edge(color="purple", style="dashed") >> conn_sub
            conn >> Edge(color="purple", style="dotted") >> conn_policy
            ident >> Edge(color="purple", style="dashed") >> ident_sub
            ident >> Edge(color="purple", style="dotted") >> ident_policy
            sec >> Edge(color="purple", style="dashed") >> sec_sub
            sec >> Edge(color="purple", style="dotted") >> sec_policy
            corp >> Edge(color="purple", style="dashed") >> corp_sub
            corp >> Edge(color="purple", style="dotted") >> corp_policy
            online >> Edge(color="purple", style="dashed") >> online_sub
            online >> Edge(color="purple", style="dotted") >> online_policy
            sandbox >> Edge(color="purple", style="dashed") >> sandbox_sub
            decom >> Edge(color="purple", style="dashed") >> decom_sub

        return outpath + ".png"

    # ── Hub-Spoke Network Topology ────────────────────────────────────

    def generate_hub_spoke(
        self,
        config: dict[str, Any] | None = None,
        filename: str = "02-hub-spoke-network-topology",
    ) -> str:
        """Generate hub-spoke network topology diagram."""
        outpath = str(self.output_dir / filename)
        with Diagram(
            "Hub-Spoke Network Topology",
            filename=outpath,
            show=False,
            direction="TB",
            graph_attr={
                "bgcolor": "white",
                "pad": "0.5",
                "ranksep": "0.8",
                "nodesep": "0.4",
                "dpi": "200",
            },
        ):
            with Cluster("On-Premises"):
                onprem = VirtualNetworkGateways("VPN / ER\nGateway")

            with Cluster("Hub VNet — 10.0.0.0/16 (Connectivity)"):
                with Cluster("GatewaySubnet\n10.0.1.0/24"):
                    hub_gw = VirtualNetworkGateways("VPN Gateway")
                with Cluster("AzureFirewallSubnet\n10.0.2.0/24"):
                    fw = Firewall("Azure Firewall\n(Premium)")
                with Cluster("AzureBastionSubnet\n10.0.3.0/24"):
                    bastion = Bastions("Bastion")
                hub_rt = RouteTables("Hub UDR\n0.0.0.0/0 → FW")

            with Cluster("Spoke — Management — 10.1.0.0/16"):
                mgmt_nsg = NetworkSecurityGroups("NSG")
                law = LogAnalyticsWorkspaces("Log Analytics")
                auto = AutomationAccounts("Automation")

            with Cluster("Spoke — Identity — 10.2.0.0/16"):
                id_nsg = NetworkSecurityGroups("NSG")
                dc = ActiveDirectory("Domain\nControllers")

            with Cluster("Spoke — Corp LZ — 10.3.0.0/16"):
                with Cluster("app-snet\n10.3.1.0/24"):
                    corp_nsg = NetworkSecurityGroups("NSG")
                    app = ContainerApps("Workload")
                with Cluster("data-snet\n10.3.2.0/24"):
                    pe = PrivateEndpoint("Private\nEndpoint")
                    db = CosmosDb("Database")
                corp_rt = RouteTables("Spoke UDR\n0.0.0.0/0 → FW")

            with Cluster("Private DNS Zones"):
                dns = DNSZones("privatelink.*\n.database.cosmos\n.vaultcore.net")

            # On-prem to hub
            onprem >> Edge(label="S2S / ER", color="darkblue") >> hub_gw
            hub_gw >> Edge(color="darkblue") >> fw

            # Hub to spokes (peering)
            fw >> Edge(label="Peering", color="orange") >> law
            fw >> Edge(label="Peering", color="orange") >> dc
            fw >> Edge(label="Peering", color="green") >> app

            # App data flow
            app >> Edge(color="steelblue") >> pe
            pe >> Edge(color="steelblue") >> db

            # DNS resolution
            pe >> Edge(style="dashed", color="gray", label="DNS resolution") >> dns

        return outpath + ".png"

    # ── Security / Governance / Monitoring ─────────────────────────────

    def generate_security_governance(
        self,
        filename: str = "03-security-governance-monitoring",
    ) -> str:
        """Generate security, governance, and monitoring diagram."""
        outpath = str(self.output_dir / filename)
        with Diagram(
            "Security, Governance & Monitoring",
            filename=outpath,
            show=False,
            direction="TB",
            graph_attr={
                "bgcolor": "white",
                "pad": "0.5",
                "ranksep": "0.8",
                "nodesep": "0.4",
                "dpi": "200",
            },
        ):
            with Cluster("Governance & Compliance"):
                mg = ManagementGroups("Mgmt Groups")
                policy = Policy("Azure Policy\n(CAF Baseline)")
                compliance_node = Compliance("Compliance\nDashboard")
                cost = CostManagement("Cost Mgmt\n& Budgets")

            with Cluster("Identity & Access"):
                entra = ActiveDirectory("Entra ID")
                pim = ManagedIdentities("PIM / RBAC\nRoles")
                cond_access = EntraDomainServices("Conditional\nAccess")

            with Cluster("Security"):
                defender = MicrosoftDefenderForCloud("Defender\nfor Cloud")
                sentinel_node = Sentinel("Sentinel\n(SIEM/SOAR)")
                kv = KeyVaults("Key Vault\n(CMK / Secrets)")

            with Cluster("Monitoring & Observability"):
                mon = Monitor("Azure Monitor")
                law = LogAnalyticsWorkspaces("Central LAW")
                ai = ApplicationInsights("App Insights")
                ag = EventGridDomains("Action Groups\n& Alerts")

            # Governance flow
            mg >> Edge(color="darkblue") >> policy
            policy >> Edge(label="evaluate", color="steelblue") >> compliance_node
            policy >> Edge(label="enforce", color="steelblue") >> defender
            defender >> Edge(label="alerts", color="red", style="dashed") >> sentinel_node
            cost >> Edge(label="budget alerts", color="orange", style="dashed") >> ag

            # Monitoring flow
            mon >> Edge(color="steelblue") >> law
            law >> Edge(color="steelblue") >> ai
            law >> Edge(label="security logs", style="dashed", color="red") >> sentinel_node
            law >> Edge(label="alert rules", color="orange") >> ag

            # Identity flow
            entra >> Edge(color="steelblue") >> pim
            entra >> Edge(color="steelblue") >> cond_access
            kv >> Edge(style="dashed", color="gray", label="RBAC") >> entra

            # Diagnostic settings
            defender >> Edge(style="dashed", color="orange", label="diagnostics") >> law

        return outpath + ".png"

    # ── Full ALZ Architecture ─────────────────────────────────────────

    def generate_alz_architecture(
        self,
        mg_prefix: str = "mrg",
        filename: str = "alz-architecture",
    ) -> str:
        """Generate the comprehensive ALZ architecture overview.

        Follows the Microsoft Enterprise-Scale reference architecture layout:
        - Management group hierarchy as the structural backbone (LR flow)
        - Subscriptions nested under their parent MGs
        - Resources shown inside subscription clusters
        - Network topology (peering) as cross-cutting connections
        - All hierarchy edges purple, uniform weight
        """
        outpath = str(self.output_dir / filename)
        sub_icon = self._get_subscription_icon()
        mg_icon = self._get_mg_icon()

        def sub_lbl(name: str) -> str:
            return (
                f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR>'
                f'<TD FIXEDSIZE="TRUE" WIDTH="16" HEIGHT="16">'
                f'<IMG SRC="{sub_icon}" SCALE="TRUE"/></TD>'
                f'<TD> <FONT POINT-SIZE="10">{name}</FONT></TD></TR></TABLE>>'
            )

        def mg_lbl(name: str) -> str:
            return (
                f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR>'
                f'<TD FIXEDSIZE="TRUE" WIDTH="16" HEIGHT="16">'
                f'<IMG SRC="{mg_icon}" SCALE="TRUE"/></TD>'
                f'<TD> <FONT POINT-SIZE="12"><B>{name}</B></FONT></TD></TR></TABLE>>'
            )

        with Diagram(
            f"{mg_prefix} — Azure Landing Zone Architecture",
            filename=outpath,
            show=False,
            direction="TB",
            graph_attr={
                "bgcolor": "white",
                "pad": "0.5",
                "ranksep": "0.7",
                "nodesep": "0.4",
                "compound": "true",
                "dpi": "200",
            },
            node_attr={
                "fontsize": "9",
            },
        ):
            # ── Root Management Group ─────────────────────────────────
            root = ManagementGroups(f"{mg_prefix}\n(Root MG)")

            # ── Platform MG ──────────────────────────────────────────
            with Cluster(
                f"{mg_prefix}-platform",
                graph_attr={
                    "style": "rounded",
                    "bgcolor": "#e8f4fd",
                    "penwidth": "2",
                    "label": mg_lbl(f"{mg_prefix}-platform"),
                    "labeljust": "l",
                },
            ):
                with Cluster(
                    "Management Sub",
                    graph_attr={"label": sub_lbl("Management"), "labeljust": "l"},
                ):
                    law = LogAnalyticsWorkspaces("mrg-law")
                    auto = AutomationAccounts("mrg-automation")

                with Cluster(
                    "Connectivity Sub",
                    graph_attr={"label": sub_lbl("Connectivity"), "labeljust": "l"},
                ):
                    hub = VirtualNetworks("mrg-hub-vnet\n10.0.0.0/16")
                    bastion = Bastions("mrg-bastion")
                    pdns = DNSZones("Private DNS\n(9 zones)")

                with Cluster(
                    "Identity Sub",
                    graph_attr={"label": sub_lbl("Identity"), "labeljust": "l"},
                ):
                    id_vnet = VirtualNetworks("mrg-identity-\nspoke-vnet\n10.1.0.0/24")

                with Cluster(
                    "Security Sub",
                    graph_attr={"label": sub_lbl("Security"), "labeljust": "l"},
                ):
                    sentinel_node = Sentinel("Sentinel")
                    defender = MicrosoftDefenderForCloud("Defender\n(11 plans)")
                    kv = KeyVaults("mrg-sec-kv")

            # ── Landing Zones MG ─────────────────────────────────────
            with Cluster(
                f"{mg_prefix}-landingzones",
                graph_attr={
                    "style": "rounded,dashed",
                    "bgcolor": "#e8fde8",
                    "penwidth": "2",
                    "label": mg_lbl(f"{mg_prefix}-landingzones"),
                    "labeljust": "l",
                },
            ):
                with Cluster(
                    "Corp",
                    graph_attr={
                        "style": "dashed",
                        "label": sub_lbl("Corp"),
                        "labeljust": "l",
                    },
                ):
                    corp_spoke = VirtualNetworks("Corp Spoke\n(planned)")

                with Cluster(
                    "Online",
                    graph_attr={
                        "style": "dashed",
                        "label": sub_lbl("Online"),
                        "labeljust": "l",
                    },
                ):
                    online_spoke = VirtualNetworks("Online Spoke\n(planned)")

                with Cluster(
                    "SAP",
                    graph_attr={
                        "style": "dashed",
                        "label": sub_lbl("SAP"),
                        "labeljust": "l",
                    },
                ):
                    sap_spoke = VirtualNetworks("SAP Spoke\n(planned)")

            # ── Sandbox & Decommissioned ─────────────────────────────
            with Cluster(
                "Sandbox / Decommissioned",
                graph_attr={
                    "style": "rounded,dotted",
                    "bgcolor": "#f5f5f5",
                    "penwidth": "1",
                    "label": mg_lbl(f"{mg_prefix}-sandbox / {mg_prefix}-decommissioned"),
                    "labeljust": "l",
                },
            ):
                sandbox_sub = Subscriptions("Sandbox\nSubscription(s)")

            # ── Hierarchy edges (all purple, terminate at cluster border) ──
            # Platform edge targets hub (center of platform cluster)
            root >> Edge(
                color="purple", penwidth="2",
                lhead=f"cluster_{mg_prefix}-platform",
            ) >> hub

            # Landing zones edge
            root >> Edge(
                color="purple", penwidth="2",
                lhead=f"cluster_{mg_prefix}-landingzones",
            ) >> corp_spoke

            # Sandbox edge
            root >> Edge(
                color="purple", penwidth="2",
                lhead="cluster_Sandbox / Decommissioned",
            ) >> sandbox_sub

            # Invisible edges to balance layout:
            # Pull root left toward leftmost Platform node to center it
            root - Edge(style="invis") - kv
            root - Edge(style="invis") - defender
            # Keep sandbox next to landingzones
            corp_spoke - Edge(style="invis") - sandbox_sub

        return outpath + ".png"

    def _get_subscription_icon(self) -> str:
        """Return the absolute path to a 32×32 subscription icon for cluster labels."""
        return self._get_resized_icon("subscriptions.png", "sub-icon-sm.png")

    def _get_mg_icon(self) -> str:
        """Return the absolute path to a 32×32 management group icon for cluster labels."""
        return self._get_resized_icon("management-groups.png", "mg-icon-sm.png")

    def _get_resized_icon(self, source_name: str, cache_name: str) -> str:
        """Resolve an Azure icon from the diagrams package, resize to 32×32, and cache it."""
        small_icon = self.output_dir / cache_name
        if not small_icon.exists():
            import importlib.util

            from PIL import Image

            spec = importlib.util.find_spec("diagrams")
            if spec and spec.origin:
                pkg_root = Path(spec.origin).parent.parent
            else:
                pkg_root = Path(Subscriptions._icon_dir).parents[3]
            original = pkg_root / "resources" / "azure" / "general" / source_name
            img = Image.open(original)
            img = img.resize((32, 32), Image.LANCZOS)
            img.save(small_icon)
        return str(small_icon.resolve())

    def _get_resource_icon(self, icon_class: type, size: int = 128) -> str:
        """Return the absolute path to a resized resource icon for smaller diagram nodes.

        Resolves the icon from the diagrams package, resizes it, and caches
        in the output directory.
        """
        cache_name = f"res-{icon_class.__name__.lower()}-{size}.png"
        small_icon = self.output_dir / cache_name
        if not small_icon.exists():
            import importlib.util

            from PIL import Image

            spec = importlib.util.find_spec("diagrams")
            if spec and spec.origin:
                pkg_root = Path(spec.origin).parent.parent
            else:
                pkg_root = Path(icon_class._icon_dir).parents[3]
            original = pkg_root / icon_class._icon_dir / icon_class._icon
            img = Image.open(original)
            img = img.resize((size, size), Image.LANCZOS)
            img.save(small_icon)
        return str(small_icon.resolve())

    # ── TDD Profile Diagrams (for Technical Design Documents) ─────────

    def generate_tdd_diagram(
        self,
        profile: str,
        project_name: str,
        subscription_name: str,
        location: str,
        output_dir: str | None = None,
        filename: str | None = None,
    ) -> str:
        """Generate a TDD architecture diagram for a specific LZ profile.

        Returns the PNG file path.
        """
        out = Path(output_dir) if output_dir else self.output_dir
        out.mkdir(parents=True, exist_ok=True)
        fname = filename or f"TDD_{project_name}_architecture"
        outpath = str(out / fname)

        dispatch = {
            "platform-management": self._tdd_management,
            "platform-connectivity": self._tdd_connectivity,
            "platform-identity": self._tdd_identity,
            "platform-security": self._tdd_security,
        }
        gen_fn = dispatch.get(profile, self._tdd_app_lz)

        if profile in dispatch:
            gen_fn(outpath, subscription_name, location)
        else:
            display_name = project_name.replace("-", " ").title()
            self._tdd_app_lz(outpath, subscription_name, location, profile, display_name)

        return outpath + ".png"

    def _tdd_management(self, outpath: str, sub: str, loc: str) -> None:
        with Diagram(
            f"Platform Management — {sub}",
            filename=outpath, show=False, direction="LR",
            graph_attr={"bgcolor": "white", "pad": "0.8", "ranksep": "1.0", "nodesep": "0.6"},
        ):
            with Cluster(f"Subscription: {sub}\n({loc})"):
                with Cluster("Monitoring & Analytics"):
                    law = LogAnalyticsWorkspaces("Log Analytics\n365d retention")
                    sentinel_node = Sentinel("Microsoft\nSentinel")
                    mon = Monitor("Azure Monitor")
                    ai = ApplicationInsights("App Insights")
                with Cluster("Operations & Continuity"):
                    auto = AutomationAccounts("Automation\nAccount")
                    rsv = StorageAccounts("Recovery\nServices Vault")
                    ag = EventGridDomains("Action Groups")
                with Cluster("Governance"):
                    policy = Policy("Azure Policy\nCAF Baseline")
                    cost = CostManagement("Budget Alerts\n80/100/120%")

            law >> Edge(style="dashed", color="orange") >> sentinel_node
            mon >> Edge(style="dashed", color="orange") >> law
            auto >> Edge(style="dashed", color="gray") >> law
            policy >> Edge(style="dashed", color="purple") >> law

    def _tdd_connectivity(self, outpath: str, sub: str, loc: str) -> None:
        with Diagram(
            f"Platform Connectivity — {sub}",
            filename=outpath, show=False, direction="LR",
            graph_attr={"bgcolor": "white", "pad": "0.8", "ranksep": "1.0", "nodesep": "0.6"},
        ):
            with Cluster(f"Subscription: {sub}\n({loc})"):
                with Cluster("Hub VNet — 10.0.0.0/16"):
                    with Cluster("GatewaySubnet"):
                        gw = VirtualNetworkGateways("VPN/ER\nGateway")
                    with Cluster("AzureFirewallSubnet"):
                        fw = Firewall("Azure Firewall\n(Premium)")
                    with Cluster("AzureBastionSubnet"):
                        bastion = Bastions("Bastion")
                    rt = RouteTables("Hub UDR")
                with Cluster("DNS & Protection"):
                    dns = DNSZones("Private DNS\nZones")
                    ddos = NetworkSecurityGroups("DDoS\nProtection")
                with Cluster("Governance"):
                    policy = Policy("Network\nPolicies")
                    cost = CostManagement("Budget")

            gw >> fw >> Edge(label="spoke\npeering") >> bastion
            fw >> Edge(style="dashed", color="purple") >> dns

    def _tdd_identity(self, outpath: str, sub: str, loc: str) -> None:
        with Diagram(
            f"Platform Identity — {sub}",
            filename=outpath, show=False, direction="LR",
            graph_attr={"bgcolor": "white", "pad": "0.8", "ranksep": "1.0", "nodesep": "0.6"},
        ):
            with Cluster(f"Subscription: {sub}\n({loc})"):
                with Cluster("Identity Services"):
                    entra = ActiveDirectory("Entra ID")
                    ds = EntraDomainServices("Entra DS")
                    connect = EntraConnect("Entra\nConnect")
                    mi = ManagedIdentities("Managed\nIdentities")
                with Cluster("Access Control"):
                    pim = ManagedIdentities("PIM / RBAC")
                    kv = KeyVaults("Key Vault\n(Credentials)")
                with Cluster("Governance"):
                    policy = Policy("Identity\nPolicies")
                    cost = CostManagement("Budget")

            entra >> Edge(color="steelblue") >> [ds, connect, mi]
            entra >> Edge(color="purple", style="dashed") >> pim
            kv >> Edge(style="dashed", color="gray") >> entra

    def _tdd_security(self, outpath: str, sub: str, loc: str) -> None:
        with Diagram(
            f"Platform Security — {sub}",
            filename=outpath, show=False, direction="LR",
            graph_attr={"bgcolor": "white", "pad": "0.8", "ranksep": "1.0", "nodesep": "0.6"},
        ):
            with Cluster(f"Subscription: {sub}\n({loc})"):
                with Cluster("Security Operations Center"):
                    sentinel_node = Sentinel("Sentinel\nSIEM/SOAR")
                    defender = MicrosoftDefenderForCloud("Defender\nfor Cloud")
                with Cluster("Secrets & Keys"):
                    kv = KeyVaults("Key Vault")
                    kv2 = KeyVaults("CMK Vault")
                with Cluster("Posture & Compliance"):
                    compliance_node = Compliance("Secure Score")
                    policy = Policy("Security\nBaseline")
                with Cluster("Governance"):
                    cost = CostManagement("Budget")

            defender >> Edge(color="red", label="alerts") >> sentinel_node
            policy >> Edge(style="dashed", color="purple") >> defender
            kv >> Edge(style="dashed", color="gray") >> sentinel_node

    def _tdd_app_lz(
        self, outpath: str, sub: str, loc: str,
        profile: str = "corp", display_name: str = "Application",
    ) -> None:
        with Diagram(
            f"{display_name} Landing Zone — {sub}",
            filename=outpath, show=False, direction="LR",
            graph_attr={"bgcolor": "white", "pad": "0.8", "ranksep": "1.0", "nodesep": "0.6"},
        ):
            with Cluster(f"Subscription: {sub}\n({loc}) — {profile}"):
                with Cluster("Networking"):
                    spoke = VirtualNetworks("Spoke VNet")
                    nsg = NetworkSecurityGroups("NSG")
                    rt = RouteTables("UDR → FW")
                with Cluster("Workload"):
                    if profile == "online":
                        app = FrontDoors("Public\nEndpoint")
                        waf = ApplicationGateway("App GW\n+ WAF")
                    elif profile == "sap":
                        app = VM("SAP\nWorkload")
                        waf = LoadBalancers("Internal LB")
                    else:
                        app = ContainerApps("Workload")
                        waf = PrivateEndpoint("Private\nEndpoints")
                with Cluster("Data"):
                    if profile == "sap":
                        db = DatabaseForMysqlServers("SAP HANA DB")
                    else:
                        db = CosmosDb("Database")
                    storage = StorageAccounts("Storage")
                with Cluster("Governance"):
                    policy = Policy("LZ Policies")
                    cost = CostManagement("Budget\n80/100/120%")

            spoke >> nsg >> app
            app >> waf >> db
            app >> Edge(style="dashed", color="gray") >> storage

    # ── Profile-Based Generation ──────────────────────────────────────

    def generate_for_profile(
        self,
        profile_name: str,
        config: dict[str, Any],
        output_prefix: str = "",
    ) -> list[str]:
        """Generate all diagrams for a landing zone profile.

        Returns list of output file paths (PNGs).
        """
        prefix = output_prefix or profile_name
        mg_prefix = config.get("management_group_prefix", "mrg")

        outputs = []
        outputs.append(self.generate_mg_hierarchy(
            mg_prefix=mg_prefix,
            filename=f"{prefix}-01-mg-hierarchy",
        ))
        outputs.append(self.generate_hub_spoke(
            config=config,
            filename=f"{prefix}-02-hub-spoke",
        ))
        outputs.append(self.generate_security_governance(
            filename=f"{prefix}-03-security-governance",
        ))
        outputs.append(self.generate_alz_architecture(
            mg_prefix=mg_prefix,
            filename=f"{prefix}-04-alz-architecture",
        ))

        logger.info("Generated %d diagrams for profile '%s': %s", len(outputs), profile_name, outputs)
        return outputs

    # ── Full Estate ───────────────────────────────────────────────────

    def generate_full_estate(
        self,
        mg_prefix: str,
        subscriptions_config: dict[str, Any],
        filename: str = "full-estate-overview",
    ) -> str:
        """Generate full-estate overview showing all landing zones."""
        outpath = str(self.output_dir / filename)
        app_lzs = {
            k: v for k, v in subscriptions_config.get("application", {}).items()
            if not k.startswith("_")
        }

        # Group app LZs by profile for balanced layout
        app_by_profile: dict[str, list[tuple[str, str]]] = {}
        for key, cfg in app_lzs.items():
            profile = cfg.get("profile", "corp")
            display = cfg.get("display_name", key)
            app_by_profile.setdefault(profile, []).append((key, display))

        with Diagram(
            f"{mg_prefix} — Full Estate Overview",
            filename=outpath,
            show=False,
            direction="TB",
            graph_attr={"bgcolor": "white", "pad": "0.8", "ranksep": "1.0", "nodesep": "0.5"},
        ):
            root = ManagementGroups(f"{mg_prefix}\n(Root)")

            with Cluster("Platform Landing Zones"):
                mgmt = Subscriptions("Management")
                conn = Subscriptions("Connectivity")
                ident = Subscriptions("Identity")
                sec = Subscriptions("Security")
                plat_nodes = [mgmt, conn, ident, sec]

            with Cluster("Application Landing Zones"):
                app_nodes = []
                for profile_name, entries in app_by_profile.items():
                    icon_type = {
                        "corp": "vnet", "online": "front_door",
                        "sap": "vm", "sandbox": "cost_management",
                    }.get(profile_name, "resource_group")
                    with Cluster(profile_name.title()):
                        for _key, display in entries:
                            app_nodes.append(_icon(icon_type, f"{display}"))

            with Cluster("Cross-Cutting Services"):
                policy = Policy("Azure Policy")
                defender = MicrosoftDefenderForCloud("Defender")
                monitor = Monitor("Monitor")
                cost = CostManagement("Cost Mgmt")
                kv = KeyVaults("Key Vault")

            root >> Edge(color="darkblue") >> plat_nodes
            if app_nodes:
                root >> Edge(color="green") >> app_nodes

        return outpath + ".png"


# ── Convenience entry point ───────────────────────────────────────────────


def generate_all_diagrams(
    output_dir: str = "agent-output/diagrams",
    mg_prefix: str = "mrg",
) -> list[str]:
    """Generate the standard set of ALZ diagrams. Returns list of PNG paths."""
    engine = DiagramEngine(output_dir=output_dir)
    return [
        engine.generate_mg_hierarchy(mg_prefix=mg_prefix),
        engine.generate_hub_spoke(),
        engine.generate_security_governance(),
        engine.generate_alz_architecture(mg_prefix=mg_prefix),
    ]
