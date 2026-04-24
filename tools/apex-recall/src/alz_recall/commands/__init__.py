"""Command registry for alz-recall CLI."""

from __future__ import annotations

COMMANDS: dict[str, str] = {
    # Read commands
    "files":         "alz_recall.commands.files",
    "sessions":      "alz_recall.commands.sessions",
    "search":        "alz_recall.commands.search",
    "show":          "alz_recall.commands.show",
    "decisions":     "alz_recall.commands.decisions",
    "health":        "alz_recall.commands.health",
    "reindex":       "alz_recall.commands.reindex",
    # Write commands
    "init":          "alz_recall.commands.init",
    "start-step":    "alz_recall.commands.start_step",
    "complete-step": "alz_recall.commands.complete_step",
    "checkpoint":    "alz_recall.commands.checkpoint",
    "decide":        "alz_recall.commands.decide",
    "finding":       "alz_recall.commands.finding",
    "review-audit":  "alz_recall.commands.review_audit",
}
