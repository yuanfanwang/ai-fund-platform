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
