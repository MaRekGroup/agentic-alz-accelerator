---
name: "remote-rewind-with-lease"
description: "Safely rewind a remote branch to an older commit with explicit refspec and lease protection"
domain: "git-operations"
confidence: "high"
source: "danny-execution"
---

## Context

Use this pattern when a user explicitly wants a remote branch moved backward to an older commit and the operation must avoid touching other remotes.

## Pattern

1. Fetch the target remote branch.
2. Verify the requested commit exists as a commit object.
3. Confirm the requested commit is an ancestor of the current remote tip.
4. Capture the exact current remote SHA.
5. Push an explicit refspec with `--force-with-lease` scoped to that SHA.
6. Verify the remote ref resolves to the requested commit.

## Commands

```bash
git fetch origin main
git rev-parse --verify <target>^{commit}
git merge-base --is-ancestor <target> refs/remotes/origin/main
git ls-remote --heads origin main
git push --force-with-lease=refs/heads/main:<expected-old-sha> origin <target-sha>:refs/heads/main
git ls-remote --heads origin main
```

## Why it works

- `--force-with-lease` prevents overwriting unexpected remote movement.
- The explicit `<target-sha>:refs/heads/main` refspec rewinds only the intended remote branch.
- `git ls-remote` verifies the server-side ref instead of trusting local tracking state alone.

## Guardrails

- Do not use this unless the user clearly asked for a destructive rewind.
- Do not use `git push --force` without a lease.
- Do not rely on the current checked-out branch; push the commit SHA explicitly.
- If the target is not an ancestor of the remote tip, stop and escalate instead of rewriting divergent history silently.
