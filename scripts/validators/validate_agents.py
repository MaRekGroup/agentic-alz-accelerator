#!/usr/bin/env python3
"""Validate agent definition files and the agent registry.

Checks:
1. Every agent in agent-registry.json with a non-null 'agent' path has a corresponding file
2. Every .md file in .github/agents/ is referenced in the registry
3. Every skill referenced in the registry exists in .github/skills/
4. Required fields are present in registry entries

Usage:
    python scripts/validators/validate_agents.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent
    registry_path = repo_root / ".github" / "agent-registry.json"
    agents_dir = repo_root / ".github" / "agents"
    skills_dir = repo_root / ".github" / "skills"

    errors: list[str] = []

    # Load registry
    if not registry_path.is_file():
        print(f"ERROR: {registry_path} not found")
        return 1

    with open(registry_path) as f:
        registry = json.load(f)

    agents = registry.get("agents", {})
    subagents = registry.get("subagents", {})

    # Collect all agent .md files on disk
    agent_files_on_disk = set()
    if agents_dir.is_dir():
        agent_files_on_disk = {
            f".github/agents/{p.name}"
            for p in agents_dir.glob("*.md")
        }

    # Collect all skill names on disk
    skills_on_disk = set()
    if skills_dir.is_dir():
        skills_on_disk = {
            p.parent.name
            for p in skills_dir.glob("*/SKILL.md")
        }

    referenced_files: set[str] = set()

    def check_entry(key: str, entry: dict, section: str) -> None:
        """Validate a single agent/subagent entry."""
        # Check required fields
        if "skills" not in entry:
            errors.append(f"{section}.{key}: missing 'skills' array")

        agent_path = entry.get("agent")
        if agent_path is not None:
            referenced_files.add(agent_path)
            full_path = repo_root / agent_path
            if not full_path.is_file():
                errors.append(f"{section}.{key}: agent file not found: {agent_path}")

        # Check skills exist
        for skill in entry.get("skills", []):
            if skill not in skills_on_disk:
                errors.append(f"{section}.{key}: skill not found: {skill}")

        for skill in entry.get("capability_skills", []):
            if skill not in skills_on_disk:
                errors.append(f"{section}.{key}: capability_skill not found: {skill}")

        # Check no overlap between skills and capability_skills
        skills_set = set(entry.get("skills", []))
        cap_set = set(entry.get("capability_skills", []))
        overlap = skills_set & cap_set
        if overlap:
            errors.append(f"{section}.{key}: overlap between skills and capability_skills: {overlap}")

    # Validate agents
    for key, entry in agents.items():
        # Handle IaC-conditional entries (bicep/terraform variants)
        if "bicep" in entry or "terraform" in entry:
            for variant in ("bicep", "terraform"):
                if variant in entry:
                    check_entry(f"{key}.{variant}", entry[variant], "agents")
        else:
            check_entry(key, entry, "agents")

    # Validate subagents
    for key, entry in subagents.items():
        check_entry(key, entry, "subagents")

    # Check for unreferenced agent files
    for agent_file in sorted(agent_files_on_disk):
        if agent_file not in referenced_files:
            # Warning, not error — some files may be in development
            print(f"  WARN  {agent_file} exists but not referenced in registry")

    # Print results
    print(f"Checked {len(agents)} agents, {len(subagents)} subagents")
    print(f"Skills on disk: {len(skills_on_disk)}")

    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    print("All agent validations passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
