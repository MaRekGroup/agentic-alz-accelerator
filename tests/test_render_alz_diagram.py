"""Tests for scripts/diagrams/render_alz_diagram.py — icon registry and node resolution.

These tests lock the icon-mapping fixes that stopped diagrams from rendering the
wrong Azure glyphs (Defender as Key Vault, Automation as a certificate, Internet as
the Azure Monitor gauge). They are pure-logic tests and do not invoke Graphviz.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "diagrams" / "render_alz_diagram.py"
_spec = importlib.util.spec_from_file_location("render_alz_diagram", _MODULE_PATH)
assert _spec and _spec.loader
render_alz_diagram = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = render_alz_diagram
_spec.loader.exec_module(render_alz_diagram)


def test_defender_and_key_vault_map_to_distinct_icons() -> None:
    """Defender for Cloud and Key Vault must resolve to different icon classes."""
    defender = render_alz_diagram.ICON_MAP["Microsoft.Security/pricings"]
    key_vault = render_alz_diagram.ICON_MAP["Microsoft.KeyVault/vaults"]
    assert defender == ("diagrams.azure.security", "MicrosoftDefenderForCloud")
    assert key_vault == ("diagrams.azure.security", "KeyVaults")
    assert defender != key_vault


@pytest.mark.parametrize(
    ("resource_type", "expected"),
    [
        ("Microsoft.Automation/automationAccounts", ("diagrams.azure.managementgovernance", "AutomationAccounts")),
        ("Microsoft.Logic/workflows", ("diagrams.azure.integration", "LogicApps")),
        ("Microsoft.Insights/actionGroups", ("diagrams.azure.web", "NotificationHubNamespaces")),
        ("Microsoft.Consumption/budgets", ("diagrams.azure.general", "CostBudgets")),
    ],
)
def test_previously_wrong_types_map_correctly(resource_type: str, expected: tuple[str, str]) -> None:
    """Types that used to fall back to wrong glyphs now have explicit, correct icons."""
    assert render_alz_diagram.ICON_MAP[resource_type] == expected


def test_internet_resolves_to_internet_icon_not_monitor() -> None:
    """An external node must resolve to the internet icon, never the Azure Monitor gauge."""
    node = {"id": "external", "name": "Internet", "kind": "external"}
    assert render_alz_diagram._resolve_ref(node) == render_alz_diagram.EXTERNAL_ICON
    assert render_alz_diagram.EXTERNAL_ICON == ("diagrams.onprem.network", "Internet")


def test_onprem_resolves_to_datacenter_icon() -> None:
    """An on-prem node must resolve to the datacenter icon."""
    node = {"id": "onprem", "name": "On-Premises Datacenter", "kind": "onprem"}
    assert render_alz_diagram._resolve_ref(node) == render_alz_diagram.ONPREM_ICON


def test_unknown_type_falls_back_by_category() -> None:
    """Unknown resource types fall back to the category icon, not the generic icon."""
    node = {"id": "x", "name": "Mystery", "azureResourceType": "Microsoft.Foo/bar", "category": "networking"}
    assert render_alz_diagram._resolve_ref(node) == render_alz_diagram.CATEGORY_FALLBACK["networking"]


def test_inject_actor_nodes_turns_empty_external_zone_into_node() -> None:
    """Empty external/onprem zones are converted to icon actor nodes with blanked labels."""
    spec = {
        "zones": [
            {"id": "external", "label": "Internet", "kind": "external"},
            {"id": "mg", "label": "mrg", "kind": "mg"},
        ],
        "nodes": [{"id": "kv", "name": "kv", "azureResourceType": "Microsoft.KeyVault/vaults", "zone": "mg"}],
    }
    render_alz_diagram._inject_actor_nodes(spec)
    actor = [n for n in spec["nodes"] if n["id"] == "external__actor"]
    assert len(actor) == 1
    assert actor[0]["name"] == "Internet"
    external_zone = next(z for z in spec["zones"] if z["id"] == "external")
    assert external_zone["label"] == ""


def test_icon_map_classes_are_importable() -> None:
    """Every icon reference in the registry must import successfully."""
    refs = [
        *render_alz_diagram.ICON_MAP.values(),
        *render_alz_diagram.CATEGORY_FALLBACK.values(),
        render_alz_diagram.EXTERNAL_ICON,
        render_alz_diagram.ONPREM_ICON,
        render_alz_diagram.GENERIC_ICON,
    ]
    for module_path, class_name in refs:
        cls = render_alz_diagram._icon_class(module_path, class_name)
        assert isinstance(cls, type)
