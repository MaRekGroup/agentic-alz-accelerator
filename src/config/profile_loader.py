"""
Profile Loader — resolves Platform and Application Landing Zone profiles
with inheritance and environment override merging.

Resolution order (highest priority first):
  environment override  >  child profile  >  base-platform / base-application

Usage:
    loader = ProfileLoader()

    # Load a platform profile for production
    profile = loader.load("platform-connectivity", environment="prod")

    # Load an application profile
    profile = loader.load("corp", environment="prod")

    # List all available profiles
    profiles = loader.list_profiles()

    # Create a custom profile inheriting from an existing one
    loader.create_custom_profile(
        name="my-corp-variant",
        inherits="corp",
        overrides={"networking": {"hub_spoke": {"hub_vnet": {"address_space": "10.50.0.0/16"}}}}
    )
"""

import copy
import logging
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

PROFILES_DIR = Path(__file__).parent / "profiles"
CUSTOM_DIR = PROFILES_DIR / "custom"
OVERRIDES_DIR = PROFILES_DIR / "overrides"


class ProfileLoader:
    """Loads, merges, and validates Landing Zone profiles with inheritance."""

    def __init__(self, profiles_dir: Optional[Path] = None):
        self.profiles_dir = profiles_dir or PROFILES_DIR
        self._cache: dict[str, dict] = {}

    # ─────────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────────

    def load(self, profile_name: str, environment: str = "prod") -> dict:
        """
        Load a profile with full inheritance and environment override resolution.

        Args:
            profile_name : Profile name (e.g., "platform-connectivity", "corp")
            environment  : Target environment ("dev", "staging", "prod")

        Returns:
            Merged profile dict, ready for use by IaC generation agents.
        """
        cache_key = f"{profile_name}:{environment}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Step 1: Load the raw profile
        raw = self._read_profile(profile_name)

        # Step 2: Resolve inheritance chain
        merged = self._resolve_inheritance(raw)

        # Step 3: Apply environment override
        override = self._read_override(profile_name, environment)
        if override:
            merged = self._deep_merge(merged, override)
            logger.info(f"Applied {environment} override for '{profile_name}'")

        # Step 4: Validate
        self._validate(merged, profile_name, environment)

        self._cache[cache_key] = merged
        return merged

    def list_profiles(self) -> dict[str, list[str]]:
        """Return all available profiles grouped by type."""
        platform = []
        application = []
        custom = []

        for f in self.profiles_dir.glob("*.yaml"):
            if f.name.startswith("base-"):
                continue
            raw = self._safe_read(f)
            meta = raw.get("_meta", {})
            ptype = meta.get("profile_type", "application")
            if f.parent == CUSTOM_DIR:
                custom.append(f.stem)
            elif ptype == "platform":
                platform.append(f.stem)
            else:
                application.append(f.stem)

        for f in CUSTOM_DIR.glob("*.yaml"):
            custom.append(f.stem)

        return {
            "platform": sorted(platform),
            "application": sorted(application),
            "custom": sorted(custom),
        }

    def describe(self, profile_name: str) -> dict:
        """Return profile metadata without full resolution (fast)."""
        raw = self._read_profile(profile_name)
        meta = raw.get("_meta", {})
        return {
            "name": profile_name,
            "type": meta.get("profile_type", "application"),
            "inherits": meta.get("inherits"),
            "purpose": meta.get("subscription_purpose"),
            "description": meta.get("description", "").strip(),
            "caf_design_areas": meta.get("caf_design_areas", []),
        }

    def create_custom_profile(
        self,
        name: str,
        inherits: str,
        overrides: dict,
        description: str = "",
    ) -> Path:
        """
        Create a custom profile that inherits from an existing profile.

        Args:
            name      : Custom profile name (e.g., "finance-corp")
            inherits  : Base profile name to inherit from (e.g., "corp")
            overrides : Dict of fields to override (deep-merged over base)
            description: Human-readable description

        Returns:
            Path to the created custom profile file.
        """
        CUSTOM_DIR.mkdir(parents=True, exist_ok=True)
        output_path = CUSTOM_DIR / f"{name}.yaml"

        base_meta = self._read_profile(inherits).get("_meta", {})
        profile = {
            "_meta": {
                "profile_type": base_meta.get("profile_type", "application"),
                "inherits": inherits,
                "description": description or f"Custom profile inheriting from '{inherits}'",
                "version": "2.0",
            },
            **overrides,
        }

        with open(output_path, "w") as f:
            yaml.dump(profile, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Created custom profile: {output_path}")
        # Clear cache so the new profile is picked up
        self._cache = {}
        return output_path

    def get_iac_parameters(self, profile_name: str, environment: str = "prod") -> dict:
        """
        Convert a loaded profile to IaC parameter format for Bicep or Terraform.

        Returns a flat dict suitable for parameter files / tfvars.
        """
        profile = self.load(profile_name, environment)
        automation = profile.get("platform_automation", {})
        framework = automation.get("iac_framework", "bicep")

        params = {
            "location": "eastus2",            # Override via env var or CLI
            "prefix": profile.get("naming", {}).get("prefix", "alz"),
            "environment": environment,
            "iac_framework": framework,
            "hub_topology": profile.get("networking", {}).get("hub_topology", "hub-spoke"),
            "budget_amount_usd": (
                profile.get("governance", {}).get("budget", {}).get("amount_usd") or 0
            ),
            "log_retention_days": (
                profile.get("management", {}).get("log_analytics", {}).get("retention_days", 90)
            ),
            "enable_sentinel": profile.get("security", {}).get("sentinel", False),
            "enable_ddos": (
                profile.get("networking", {}).get("ddos_protection", {}).get("enabled", False)
                if isinstance(profile.get("networking", {}).get("ddos_protection"), dict)
                else profile.get("networking", {}).get("ddos_protection", False)
            ),
            "defender_plans": (
                profile.get("security", {}).get("defender_for_cloud", {}).get("plans", [])
            ),
        }

        # Add networking specifics
        networking = profile.get("networking", {})
        hub_topology = networking.get("hub_topology", "hub-spoke")
        if hub_topology == "hub-spoke":
            hub = networking.get("hub_spoke", {}).get("hub_vnet", {})
            params["hub_vnet_address_space"] = hub.get("address_space", "10.0.0.0/16")
            params["deploy_azure_firewall"] = (
                networking.get("hub_spoke", {}).get("azure_firewall", {}).get("enabled", False)
            )
            params["firewall_sku_tier"] = (
                networking.get("hub_spoke", {}).get("azure_firewall", {}).get("sku_tier", "Premium")
            )

        return params

    # ─────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _read_profile(self, name: str) -> dict:
        """Read a profile YAML file. Checks custom/ first, then profiles root."""
        for search_path in [CUSTOM_DIR / f"{name}.yaml", self.profiles_dir / f"{name}.yaml"]:
            if search_path.exists():
                return self._safe_read(search_path)
        raise FileNotFoundError(
            f"Profile '{name}' not found. Available: {list(self.profiles_dir.glob('*.yaml'))}"
        )

    def _safe_read(self, path: Path) -> dict:
        with open(path) as f:
            return yaml.safe_load(f) or {}

    def _resolve_inheritance(self, profile: dict) -> dict:
        """Walk the inheritance chain and deep-merge, base → child."""
        parent_name = profile.get("_meta", {}).get("inherits")
        if not parent_name:
            return copy.deepcopy(profile)

        parent_raw = self._read_profile(parent_name)
        parent_resolved = self._resolve_inheritance(parent_raw)
        return self._deep_merge(parent_resolved, profile)

    def _read_override(self, profile_name: str, environment: str) -> Optional[dict]:
        """Load an environment-specific override file if it exists."""
        override_path = OVERRIDES_DIR / environment / f"{profile_name}.yaml"
        if override_path.exists():
            return self._safe_read(override_path)
        return None

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """
        Recursively merge override into base.
        Lists are replaced (not extended) — use explicit list values in overrides.
        """
        result = copy.deepcopy(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        return result

    def _validate(self, profile: dict, name: str, environment: str) -> None:
        """Validate a resolved profile for required fields."""
        errors = []

        # Budget amount must be set
        budget = profile.get("governance", {}).get("budget", {})
        if budget.get("enabled") and not budget.get("amount_usd"):
            errors.append(
                f"governance.budget.amount_usd is required for profile '{name}' "
                f"in '{environment}' — set it in overrides/{environment}/{name}.yaml"
            )

        # Prefix must be set and short
        prefix = profile.get("naming", {}).get("prefix", "alz")
        if len(prefix) > 10:
            errors.append(f"naming.prefix '{prefix}' exceeds 10 characters")

        if errors:
            raise ValueError(
                f"Profile validation failed for '{name}':\n" + "\n".join(f"  - {e}" for e in errors)
            )
