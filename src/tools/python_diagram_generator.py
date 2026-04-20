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
import os
from pathlib import Path
from typing import Any

from diagrams import Cluster, Diagram, Edge

# ── Azure icon imports ────────────────────────────────────────────────────
from diagrams.azure.compute import ContainerApps, FunctionApps, VM
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

    def __init__(self, output_dir: str = "docs/diagrams") -> None:
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
            graph_attr={"bgcolor": "white", "pad": "0.5", "ranksep": "0.8"},
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

            root >> Edge(color="darkblue") >> [mgmt, conn, ident, sec]
            root >> Edge(color="green") >> [corp, online]
            root >> Edge(color="gray", style="dashed") >> [sandbox, decom]

            mgmt >> Edge(color="darkblue", style="dashed") >> mgmt_sub
            mgmt >> Edge(color="purple", style="dotted") >> mgmt_policy
            conn >> Edge(color="darkblue", style="dashed") >> conn_sub
            conn >> Edge(color="purple", style="dotted") >> conn_policy
            ident >> Edge(color="darkblue", style="dashed") >> ident_sub
            ident >> Edge(color="purple", style="dotted") >> ident_policy
            sec >> Edge(color="darkblue", style="dashed") >> sec_sub
            sec >> Edge(color="purple", style="dotted") >> sec_policy
            corp >> Edge(color="green", style="dashed") >> corp_sub
            corp >> Edge(color="purple", style="dotted") >> corp_policy
            online >> Edge(color="green", style="dashed") >> online_sub
            online >> Edge(color="purple", style="dotted") >> online_policy
            sandbox >> Edge(color="gray", style="dashed") >> sandbox_sub
            decom >> Edge(color="gray", style="dashed") >> decom_sub

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
            direction="LR",
            graph_attr={"bgcolor": "white", "pad": "0.5", "ranksep": "1.0"},
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
                hub_ddos = NetworkSecurityGroups("DDoS\nProtection")

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

            # Connections
            onprem >> Edge(label="S2S / ER", color="darkblue") >> hub_gw
            hub_gw >> fw
            fw >> Edge(label="VNet Peering", color="orange") >> law
            fw >> Edge(label="VNet Peering", color="orange") >> dc
            fw >> Edge(label="VNet Peering", color="green") >> app
            app >> pe >> db
            pe >> Edge(style="dashed", color="purple", label="DNS\nresolution") >> dns

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
            graph_attr={"bgcolor": "white", "pad": "0.5", "ranksep": "1.0"},
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
            policy >> Edge(label="evaluate", color="purple") >> compliance_node
            policy >> Edge(label="enforce", color="purple") >> defender
            defender >> Edge(label="security alerts", color="red") >> sentinel_node
            cost >> Edge(label="budget\nalerts", color="orange", style="dashed") >> ag

            # Monitoring flow
            mon >> law
            law >> ai
            law >> Edge(label="security logs", style="dashed", color="purple") >> sentinel_node
            law >> Edge(label="alert rules", color="orange") >> ag

            # Identity flow
            entra >> Edge(color="steelblue") >> pim
            entra >> Edge(color="steelblue") >> cond_access
            kv >> Edge(style="dashed", color="gray", label="RBAC") >> entra

            # Diagnostic settings
            defender >> Edge(style="dashed", color="orange", label="diag\nsettings") >> law

        return outpath + ".png"

    # ── Full ALZ Architecture ─────────────────────────────────────────

    def generate_alz_architecture(
        self,
        mg_prefix: str = "mrg",
        filename: str = "alz-architecture",
    ) -> str:
        """Generate the comprehensive ALZ architecture overview."""
        outpath = str(self.output_dir / filename)
        with Diagram(
            f"{mg_prefix} — Azure Landing Zone Architecture",
            filename=outpath,
            show=False,
            direction="TB",
            graph_attr={"bgcolor": "white", "pad": "0.5", "ranksep": "1.2"},
        ):
            root = ManagementGroups(f"{mg_prefix}\nRoot MG")

            with Cluster("Platform Subscriptions"):
                with Cluster("Management"):
                    law = LogAnalyticsWorkspaces("Log Analytics")
                    auto = AutomationAccounts("Automation")
                    mon = Monitor("Azure Monitor")
                with Cluster("Connectivity"):
                    fw = Firewall("Azure Firewall\n(Premium)")
                    hub = VirtualNetworks("Hub VNet\n10.0.0.0/16")
                    gw = VirtualNetworkGateways("VPN/ER GW")
                    bastion = Bastions("Bastion")
                    pdns = DNSZones("Private DNS\nZones")
                with Cluster("Identity"):
                    dc = ActiveDirectory("Domain\nControllers")
                    pim = ManagedIdentities("PIM / RBAC")
                with Cluster("Security"):
                    defender = MicrosoftDefenderForCloud("Defender")
                    sentinel_node = Sentinel("Sentinel")

            with Cluster("Landing Zone Subscriptions"):
                with Cluster("Corp LZ"):
                    corp_spoke = VirtualNetworks("Corp Spoke\n10.3.0.0/16")
                    corp_nsg = NetworkSecurityGroups("NSG")
                    corp_app = ContainerApps("Workloads")
                    corp_pe = PrivateEndpoint("Private\nEndpoints")
                with Cluster("Online LZ"):
                    online_app = FrontDoors("Public\nEndpoints")
                    online_waf = ApplicationGateway("App GW\n+ WAF")

            with Cluster("Cross-Cutting Services"):
                policy = Policy("Azure Policy\n(CAF Baseline)")
                compliance_node = Compliance("Compliance")
                cost = CostManagement("Cost Mgmt\n& Budgets")
                kv = KeyVaults("Key Vault")
                rt = RouteTables("Route Tables\n(UDR → FW)")

            # Hierarchy
            root >> Edge(color="darkblue", style="bold") >> [law, fw, dc, defender]

            # Network flow
            gw >> hub >> fw
            fw >> Edge(color="green", label="VNet\nPeering") >> corp_spoke
            corp_spoke >> corp_nsg >> corp_app
            corp_app >> corp_pe
            fw >> Edge(color="green", style="dashed") >> online_app
            online_app >> online_waf

            # Monitoring
            law >> Edge(style="dashed", color="orange") >> sentinel_node
            mon >> Edge(style="dashed", color="orange") >> law

            # DNS
            corp_pe >> Edge(style="dashed", color="purple") >> pdns

            # Cross-cutting
            policy >> Edge(style="dashed", color="gray") >> compliance_node
            policy >> Edge(style="dashed", color="gray") >> defender

        return outpath + ".png"

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
            filename=outpath, show=False, direction="TB",
            graph_attr={"bgcolor": "white", "pad": "0.5", "ranksep": "0.8"},
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
            graph_attr={"bgcolor": "white", "pad": "0.5", "ranksep": "1.0"},
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
            filename=outpath, show=False, direction="TB",
            graph_attr={"bgcolor": "white", "pad": "0.5", "ranksep": "0.8"},
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
            filename=outpath, show=False, direction="TB",
            graph_attr={"bgcolor": "white", "pad": "0.5", "ranksep": "0.8"},
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
            filename=outpath, show=False, direction="TB",
            graph_attr={"bgcolor": "white", "pad": "0.5", "ranksep": "0.8"},
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
        platform_lzs = subscriptions_config.get("platform", {})
        app_lzs = {
            k: v for k, v in subscriptions_config.get("application", {}).items()
            if not k.startswith("_")
        }

        with Diagram(
            f"{mg_prefix} — Full Estate Overview",
            filename=outpath,
            show=False,
            direction="TB",
            graph_attr={"bgcolor": "white", "pad": "0.5", "ranksep": "1.0"},
        ):
            root = ManagementGroups(f"{mg_prefix}\n(Root)")

            with Cluster("Platform Landing Zones"):
                plat_nodes = []
                for name in ["Management", "Connectivity", "Identity", "Security"]:
                    plat_nodes.append(Subscriptions(name))

            with Cluster("Application Landing Zones"):
                app_nodes = []
                for key, cfg in app_lzs.items():
                    display = cfg.get("display_name", key)
                    profile = cfg.get("profile", "corp")
                    icon_type = {
                        "corp": "vnet", "online": "front_door",
                        "sap": "vm", "sandbox": "cost_management",
                    }.get(profile, "resource_group")
                    app_nodes.append(_icon(icon_type, f"{display}\n({profile})"))

            with Cluster("Cross-Cutting"):
                cross = [
                    Policy("Azure Policy"),
                    MicrosoftDefenderForCloud("Defender"),
                    Monitor("Monitor"),
                    CostManagement("Cost Mgmt"),
                    KeyVaults("Key Vault"),
                ]

            root >> Edge(color="darkblue") >> plat_nodes
            if app_nodes:
                root >> Edge(color="green") >> app_nodes

        return outpath + ".png"


# ── Convenience entry point ───────────────────────────────────────────────


def generate_all_diagrams(
    output_dir: str = "docs/diagrams",
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
