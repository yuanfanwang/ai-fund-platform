---
name: nullifier-creator
description: Agent skill that faithfully reproduces Nullifier creator commands (publish, update, proof create, signal send, status, revenue, withdraw) via a bundled Python script. V1 is deterministic demo mode.
---

# nullifier-creator

For every supported command, execute the matching script and return stdout verbatim.

This skill is intentionally deterministic for demos:

- Do not inspect repo docs, memory files, or unrelated project files before running the script.
- Do not invent metrics, IDs, balances, fees, or extra explanation.
- Do not paraphrase script output.
- Always return English output.
- If the user asks for multiple creator actions, run the matching scripts in request order and concatenate stdout blocks with a single blank line.

## Supported Commands

| Command        | Purpose                             |
| -------------- | ----------------------------------- |
| `publish`      | Publish the canonical strategy      |
| `update`       | Refresh canonical metrics           |
| `proof create` | Generate the canonical proof result |
| `signal send`  | Send the canonical signal           |
| `status`       | Show canonical strategy status      |
| `revenue`      | Show canonical creator revenue      |
| `withdraw`     | Withdraw creator revenue            |

## Prerequisites

- `python3` must be available.
- No API credentials are required in V1 demo mode.

## Auth & Config

Scripts are the source of truth for demo responses.

- Creator identity is implicit.
- If the user omits the strategy name, use the canonical strategy.
- If the user omits a withdraw amount, use the script default.

## Combined Requests

When one request spans multiple commands, execute each script directly.

Example:

User:

```text
Publish the BTC delta-neutral strategy. Also show status and revenue.
```

Run:

```bash
python3 scripts/nullifier_creator.py publish
python3 scripts/nullifier_creator.py status
python3 scripts/nullifier_creator.py revenue
```

Return the three stdout blocks only. Do not add narration before or after them.

## publish

```bash
python3 scripts/nullifier_creator.py publish
```

## update

```bash
python3 scripts/nullifier_creator.py update
```

## proof create

```bash
python3 scripts/nullifier_creator.py proof-create
```

## signal send

```bash
python3 scripts/nullifier_creator.py signal-send \
  --asset BTC/USD \
  --action buy \
  --price 68,500 \
  --confidence 0.85
```

Use user-specified signal fields when they are provided. Otherwise rely on script defaults.

## status

```bash
python3 scripts/nullifier_creator.py status
```

## revenue

```bash
python3 scripts/nullifier_creator.py revenue
```

## withdraw

```bash
python3 scripts/nullifier_creator.py withdraw
```

```bash
python3 scripts/nullifier_creator.py withdraw --amount 10000
```

## Quick Reference

```bash
python3 scripts/nullifier_creator.py publish
python3 scripts/nullifier_creator.py proof-create
python3 scripts/nullifier_creator.py signal-send --asset BTC/USD --action buy
python3 scripts/nullifier_creator.py status
python3 scripts/nullifier_creator.py revenue
python3 scripts/nullifier_creator.py withdraw
```

## Related Skills

- `nullifier-investor` for explore, verify, invest, position, earnings, withdraw, and signals
