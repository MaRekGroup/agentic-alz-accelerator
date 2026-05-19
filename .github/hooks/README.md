# Copilot Agent Hooks

Runtime guards and telemetry that wrap GitHub Copilot CLI / Agent sessions in
this repo. Each subdirectory contains a `hooks.json` (event binding) and one
or more shell scripts (action). Hooks are auto-discovered by the Copilot
runtime — no separate registration step is required.

> **Self-protection**: `tool-guardian` blocks any tool call that attempts to
> edit files under `.github/hooks/` itself. To modify a hook, set
> `TOOL_GUARD_ALLOWLIST` for your session or commit through a human PR.

## Hook Inventory

| Hook | Event(s) | Purpose | Blocking? | Log path |
|------|----------|---------|-----------|----------|
| [`tool-guardian`](tool-guardian/) | `PreToolUse` | Deny destructive tool calls (`rm -rf`, `terraform destroy`, `git push --force`, pipe-to-shell, etc.) and protect `.github/hooks/` | `GUARD_MODE=block` only | `logs/copilot/tool-guardian/guard.log` |
| [`post-edit-format`](post-edit-format/) | `PostToolUse` | Lint/format edited files: `az bicep lint`, `terraform fmt`, `py_compile`, `markdownlint-cli2` | advisory | (stdout only) |
| [`secrets-scanner`](secrets-scanner/) | `Stop` | Regex-scan changed files for credentials/tokens; redact before logging | `SCAN_MODE=block` only | `logs/copilot/secrets/scan.log` |
| [`governance-audit`](governance-audit/) | `SessionStart`, `Stop`, `UserPromptSubmit` | Append audit metadata (session id, governance level, prompt length — not content) | non-blocking | `logs/copilot/governance/audit.log` |
| [`session-logger`](session-logger/) | `SessionStart`, `Stop`, `UserPromptSubmit` | Session telemetry: timestamp, session id, cwd, git branch | non-blocking | `logs/copilot/sessions/session.log` |
| [`subagent-validation`](subagent-validation/) | `SubagentStop` | Validate Challenger emits non-empty `findings[]`; warn on suspiciously short codegen/lint output | advisory | (stdout only) |

All log paths are under `logs/copilot/`, which is gitignored.

## Lifecycle Events

| Event | Fired when | Used by |
|-------|------------|---------|
| `SessionStart` | Copilot session begins | `governance-audit`, `session-logger` |
| `UserPromptSubmit` | User submits a prompt (before agent runs) | `governance-audit`, `session-logger` |
| `PreToolUse` | Before any tool call is executed | `tool-guardian` |
| `PostToolUse` | After a tool call completes (e.g. file edit) | `post-edit-format` |
| `SubagentStop` | A spawned subagent finishes | `subagent-validation` |
| `Stop` | Copilot session ends | `governance-audit`, `secrets-scanner`, `session-logger` |

Hook scripts receive a JSON payload on `stdin` and may emit a JSON response on
`stdout`. The runtime interprets non-zero exit codes per hook contract (see
each `hooks.json` for the `timeout` budget).

## Environment Variables

### Kill switches
| Variable | Hook | Effect |
|----------|------|--------|
| `SKIP_TOOL_GUARD` | tool-guardian | Bypass all dangerous-tool detection |
| `SKIP_SECRETS_SCAN` | secrets-scanner | Skip the end-of-session scan |
| `SKIP_GOVERNANCE_AUDIT` | governance-audit | Disable audit logging |
| `SKIP_SESSION_LOG` | session-logger | Disable session telemetry |

### Enforcement mode (warn vs block)

| Variable | Default | Set to `block` to |
|----------|---------|-------------------|
| `GUARD_MODE` | `warn` | Have `tool-guardian` deny dangerous tool calls (exit 1) |
| `SCAN_MODE` | `warn` | Have `secrets-scanner` fail the session on secret findings (exit 1) |

### Tuning

| Variable | Hook | Purpose |
|----------|------|---------|
| `TOOL_GUARD_ALLOWLIST` | tool-guardian | Regex allowlist for otherwise-blocked patterns |
| `TOOL_GUARD_LOG_DIR` | tool-guardian | Override default log directory |
| `SECRETS_LOG_DIR` | secrets-scanner | Override default log directory |
| `SECRETS_ALLOWLIST` | secrets-scanner | Regex allowlist for known-safe matches |
| `SCAN_SCOPE` | secrets-scanner | `diff` (default) or `staged` |
| `GOVERNANCE_LEVEL` | governance-audit | Free-form label included in audit entries |

## Adding a New Hook

1. Create `.github/hooks/<hook-name>/` with:
   - `hooks.json` — event binding (`hooks: [{ event, matcher?, command, timeout }]`)
   - `<hook-name>.sh` (or `.py`) — the action script
2. Read JSON from `stdin`, write JSON to `stdout` (use `jq` if available, with
   a `python3` fallback for portability).
3. Default to **non-blocking** (exit `0`). Only escalate to exit `1` when an
   explicit `*_MODE=block` env var is set.
4. Honor a `SKIP_<HOOK_NAME>` kill switch.
5. Write logs under `logs/copilot/<hook-name>/` (path is gitignored).
6. Add a row to the **Hook Inventory** table above.
7. Because `tool-guardian` blocks edits under `.github/hooks/`, additions must
   land via a human-reviewed PR.

## Relationship to Other Hook Surfaces

This directory is **not** the same as:

- **`lefthook.yml`** (repo root) — git pre-commit / pre-push hooks for local
  developers; runs `validate_security_baseline.py`, `validate_cost_governance.py`,
  `ruff`, `terraform fmt`, etc. Opt-in via `npx lefthook install` (the
  devcontainer runs this automatically).
- **`mcp/*/.githooks/`** and **`mcp/*/.pre-commit-config.yaml`** — vendored
  MCP subprojects with their own git hook configurations (Deno fmt, Python
  pre-commit framework). Scoped to those subdirs only.

CI workflow `.github/workflows/5-pr-validate.yml` re-runs the lefthook checks
on every PR, so PRs are protected even when contributors haven't installed
lefthook locally.
