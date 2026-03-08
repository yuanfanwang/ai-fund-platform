# Installable Nullifier Skills

This directory is the public source for `npx skills add`.

Each skill is self-contained and ships with bundled `python3` scripts for deterministic demo responses.

## List available skills

```bash
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --list
```

## Install a specific skill

```bash
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --skill nullifier-creator
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --skill nullifier-investor
```

## Install directly from a skill path

```bash
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills/nullifier-creator
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills/nullifier-investor
```
