"""CLI entry point for alz-recall."""

from __future__ import annotations

import argparse
import importlib
import sys

from . import __version__
from .commands import COMMANDS


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alz-recall",
        description="Progressive session recall CLI for ALZ accelerator artifacts",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # Dynamically register every command module
    for name, module_path in COMMANDS.items():
        mod = importlib.import_module(module_path)
        mod.register(sub)  # type: ignore[attr-defined]

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    # Resolve the hyphenated command name to its module
    module_path = COMMANDS.get(args.command)
    if module_path is None:
        parser.print_help()
        return 1

    mod = importlib.import_module(module_path)
    return mod.run(args)  # type: ignore[attr-defined]


if __name__ == "__main__":
    sys.exit(main())
