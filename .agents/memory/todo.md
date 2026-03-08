## Current Task

- [x] Find all public `npx skills add` references using the old GitHub owner
- [x] Update install examples to `yuanfanwang/ai-fund-platform`
- [x] Record the correction pattern in `.agents/memory/lessons.md`
- [x] Verify no stale install URLs remain

## Review

- Updated every public `npx skills add` example and direct skill-path example from `asumayamada/ai-fund-platform` to `yuanfanwang/ai-fund-platform`.
- Touched `README.md`, `docs/prd.md`, `docs/openclaw-mock-demo.md`, and `skills/README.md` so the install instructions stay consistent.
- Verified there are no stale owner references left in `README.md`, `docs/`, `skills/`, or `.agents/memory/`, and `git diff --check` is clean.

---

## Current Task

- [x] Load project docs, task memory, and relevant skill instructions
- [x] Inspect merge state and locate all `architecture.jpg` references
- [x] Resolve `docs/prd.md` merge conflict against the current repo direction
- [x] Update the broken `architecture.jpg` path
- [x] Verify no conflict markers remain and record results

## Review

- Replaced the conflicted `docs/prd.md` with a clean merged PRD aligned to the current repo: installable `nullifier-*` skills plus the script-backed OpenClaw mock demo.
- Fixed the broken image reference in `zkStrategy_Seed_Deck_Draft.md` to use `./docs/architecture.jpg`, which matches the actual file location.
- Verified `docs/prd.md` has no remaining merge markers, `git diff --check` is clean, and `python3 -m unittest tests/test_nullifier_skill_scripts.py` passes.

---

## Current Task

- [x] Load product and skill context
- [x] Audit current skill structure
- [x] Propose clearer skill design
- [x] Replace legacy skill names with `nullifier-creator` and `nullifier-investor`
- [x] Rewrite both skill specs to command-first wrappers
- [x] Remove `subscription` / `subscribe` interface language from primary docs
- [x] Update demo runbook and examples to the new skill names and commands
- [x] Make the repo consumable via `npx skills add <repo-or-url>`
- [x] Run verification checks and record results

## Review

- Replaced `skills/strategy-manager` and `skills/strategy-finder` with installable `nullifier-creator` and `nullifier-investor` skills.
- Updated README and primary docs to use creator/investor naming and `invest` / `withdraw` terminology instead of subscription flows.
- Verified `npx skills add ./skills --list` returns exactly the two public skills, and direct skill paths list one skill each.
- Verified formatting on touched files with `prettier --check` and whitespace safety with `git diff --check`.
- Refactored both public skills to bundled Python command runners so demo responses come from script stdout instead of free-form model narration.
- Verified the script contract with `python3 -m unittest tests/test_nullifier_skill_scripts.py` and confirmed `codex exec` in an isolated skill-only directory runs the bundled scripts for demo prompts.
