---
name: sync-agent-symlinks
description: Sync `.agents/commands`, `.agents/rules`, and `.agents/skills` into `.claude`, `.cursor`, and `.codex` as symlinks, and sync `CLAUDE.md` to `AGENTS.md`. Use when setting up or re-syncing local agent configuration directories and Claude/Codex instruction files, or when links are broken after cloning/moving the repository.
---

# Sync Agent Symlinks

## Overview

Create and maintain symlinks from `.claude`, `.cursor`, and `.codex` to shared directories under `.agents`.
Use the bundled script so the setup can be rerun safely at any time.

## Workflow

1. Run the script:

```bash
bash .agents/skills/sync-agent-symlinks/scripts/sync_agent_symlinks.sh
```

2. The script ensures these links exist:
- `.claude/commands` -> `../.agents/commands`
- `.claude/rules` -> `../.agents/rules`
- `.claude/skills` -> `../.agents/skills`
- `.cursor/commands` -> `../.agents/commands`
- `.cursor/rules` -> `../.agents/rules`
- `.cursor/skills` -> `../.agents/skills`
- `.codex/commands` -> `../.agents/commands`
- `.codex/rules` -> `../.agents/rules`
- `.codex/skills` -> `../.agents/skills`
- `CLAUDE.md` -> `AGENTS.md`

3. If a destination exists as a non-symlink, the script stops with an error by default.

4. To replace existing non-symlink paths intentionally, run with `--force`:

```bash
bash .agents/skills/sync-agent-symlinks/scripts/sync_agent_symlinks.sh --force
```

## Notes

- Run this script from anywhere; it resolves the repository root from its own location.
- Keep link targets relative (`../.agents/...`) so the repo stays portable across machines and paths.

### scripts/
- `scripts/sync_agent_symlinks.sh`: create or refresh the symlinks.
