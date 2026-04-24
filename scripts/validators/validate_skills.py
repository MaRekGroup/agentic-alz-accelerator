#!/usr/bin/env python3
"""Validate skill definition files (SKILL.md).

Checks:
1. Every skill directory in .github/skills/ has a SKILL.md file
2. Every skill referenced in agent-registry.json has a SKILL.md
3. SKILL.md files are non-empty

Usage:
    python scripts/validators/validate_skills.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent
    skills_dir = repo_root / ".github" / "skills"
    registry_path = repo_root / ".github" / "agent-registry.json"

    errors: list[str] = []
    warnings: list[str] = []

    # Find skill directories on disk
    skill_dirs = sorted(
        p.name
        for p in skills_dir.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    ) if skills_dir.is_dir() else []

    # Check each skill directory has SKILL.md
    skills_with_file: set[str] = set()
    for skill_name in skill_dirs:
        skill_md = skills_dir / skill_name / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{skill_name}: missing SKILL.md")
        elif skill_md.stat().st_size == 0:
            errors.append(f"{skill_name}: SKILL.md is empty")
        else:
            skills_with_file.add(skill_name)
            print(f"  OK    {skill_name}/SKILL.md")

    # Cross-reference with agent registry
    if registry_path.is_file():
        with open(registry_path) as f:
            registry = json.load(f)

        # Collect all skill references
        referenced_skills: set[str] = set()
        for section in ("agents", "subagents"):
            for _key, entry in registry.get(section, {}).items():
                # Handle IaC-conditional entries
                if "bicep" in entry or "terraform" in entry:
                    for variant in ("bicep", "terraform"):
                        if variant in entry:
                            referenced_skills.update(entry[variant].get("skills", []))
                            referenced_skills.update(entry[variant].get("capability_skills", []))
                else:
                    referenced_skills.update(entry.get("skills", []))
                    referenced_skills.update(entry.get("capability_skills", []))

        # Check referenced skills exist
        for skill in sorted(referenced_skills):
            if skill not in skills_with_file:
                if skill in {d for d in skill_dirs}:
                    errors.append(f"{skill}: referenced in registry but SKILL.md is missing/empty")
                else:
                    errors.append(f"{skill}: referenced in registry but directory not found")

        # Check for unreferenced skills (warning only)
        unreferenced = skills_with_file - referenced_skills
        for skill in sorted(unreferenced):
            warnings.append(f"{skill}: exists but not referenced in agent-registry.json")

    # Print results
    print(f"\nChecked {len(skill_dirs)} skill directories")

    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  ⚠  {w}")

    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    print("All skill validations passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
