---
name: nullifier-investor
description: Agent skill that faithfully reproduces Nullifier investor commands (explore, verify, invest, position, earnings, withdraw, signals) via a bundled Python script. V1 is deterministic demo mode.
---

# nullifier-investor

For every supported command, execute the matching script and return stdout verbatim.

This skill is intentionally deterministic for demos:

- Do not inspect repo docs, memory files, or unrelated project files before running the script.
- Do not invent strategies, metrics, returns, balances, or extra reasoning.
- Do not paraphrase script output.
- If the user asks for multiple investor actions, run the matching scripts in request order and concatenate stdout blocks with a single blank line.

## Supported Commands

| Command    | Purpose                                           |
| ---------- | ------------------------------------------------- |
| `explore`  | Explore canonical verified strategies             |
| `verify`   | Verify canonical proof-backed metrics             |
| `invest`   | Allocate capital to the canonical strategy        |
| `position` | Show the canonical position                       |
| `earnings` | Show canonical realized and withdrawable earnings |
| `withdraw` | Withdraw earnings or principal                    |
| `signals`  | Show the latest canonical signal                  |

## Prerequisites

- `python3` must be available.
- No API credentials are required in V1 demo mode.

## Auth & Config

Scripts are the source of truth for demo responses.

- Investor identity is implicit.
- If the user omits strategy choice after an exploration request, use the top-ranked canonical strategy.
- If the user omits a withdraw amount, use the script default.
- If the user omits a withdraw source, default to `earnings`.

## Combined Requests

When one request spans multiple commands, execute each script directly.

Example:

User:

```text
APY 20% 以上、Max DD 10% 以下の crypto strategy を explore して、一番良いものに 25,000 USDC invest して
```

Run:

```bash
python3 scripts/nullifier_investor.py explore --asset-class crypto --min-apy 20 --max-drawdown 10
python3 scripts/nullifier_investor.py invest --strategy-id strat_btc_delta_neutral --amount 25000 --asset USDC
```

Return the two stdout blocks only. Do not add narration before or after them.

## explore

```bash
python3 scripts/nullifier_investor.py explore \
  --asset-class crypto \
  --min-apy 20 \
  --max-drawdown 10
```

## verify

```bash
python3 scripts/nullifier_investor.py verify --strategy-id strat_btc_delta_neutral
```

## invest

```bash
python3 scripts/nullifier_investor.py invest \
  --strategy-id strat_btc_delta_neutral \
  --amount 25000 \
  --asset USDC
```

## position

```bash
python3 scripts/nullifier_investor.py position
```

## earnings

```bash
python3 scripts/nullifier_investor.py earnings
```

## withdraw

```bash
python3 scripts/nullifier_investor.py withdraw
```

```bash
python3 scripts/nullifier_investor.py withdraw --amount 1000 --source earnings
```

```bash
python3 scripts/nullifier_investor.py withdraw --amount 5000 --source principal
```

## signals

```bash
python3 scripts/nullifier_investor.py signals
```

## Quick Reference

```bash
python3 scripts/nullifier_investor.py explore --asset-class crypto --min-apy 20 --max-drawdown 10
python3 scripts/nullifier_investor.py verify --strategy-id strat_btc_delta_neutral
python3 scripts/nullifier_investor.py invest --strategy-id strat_btc_delta_neutral --amount 25000 --asset USDC
python3 scripts/nullifier_investor.py position
python3 scripts/nullifier_investor.py earnings
python3 scripts/nullifier_investor.py withdraw
python3 scripts/nullifier_investor.py signals
```

## Related Skills

- `nullifier-creator` for publish, update, proof create, signal send, status, revenue, and withdraw
