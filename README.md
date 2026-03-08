# Autonomous Hedge Fund Platform for Agents

`ai-fund-platform` is a concept and architecture repository for an agent-native hedge fund platform.

The goal is simple:

- strategy creators keep their trading logic private
- platform users verify performance without blind trust
- AI agents discover, invest in, and execute strategies automatically

![Platform architecture](./docs/architecture.jpg)

## What Problem Does This Solve?

Traditional strategy marketplaces break down for three reasons:

- Creators cannot monetize a strong strategy without exposing their alpha.
- Investors cannot easily verify whether reported returns are real.
- AI agents do not have a standard way to search, evaluate, pay for, and run investment strategies.

## The Core Idea

This project combines a private strategy marketplace with cryptographic proof of performance.

- A creator encrypts or keeps the strategy logic private.
- The creator proves performance metrics from exchange or broker data using `zkTLS`.
- The platform lists only verified metrics such as APY, PnL, Sharpe ratio, and max drawdown.
- Investors or AI agents allocate capital based on those verified metrics.
- Signals are delivered through an agent-friendly interface such as skills, plugins, or MCP-style tools.

In short: the strategy stays secret, but the results become provable.

## What Is `zkTLS`?

`zkTLS` is a way to prove facts from a real HTTPS API response without revealing everything inside that response.

For this platform, that means a strategy creator can prove statements like:

- "This account produced a 30% annual return"
- "Max drawdown stayed below 10%"
- "The account belongs to the claimed provider"

The proof can be verified, while the actual trading logic remains hidden.

## How The Platform Works

### Creator flow

1. Build a strategy.
2. Keep the logic private or encrypted.
3. Generate proofs for key performance metrics.
4. Publish the strategy to the marketplace.
5. Receive strategy revenue or performance-based fees.

### Investor or agent flow

1. Search strategies by verified metrics.
2. Choose an allocation based on APY, PnL, and risk.
3. Allocate capital through an API, plugin, or MCP-compatible interface.
4. Receive signals and execute automatically.
5. Take profit or rebalance into stronger strategies over time.

### Portfolio layer

The platform can group strategies into buckets such as:

- real estate
- FX
- BTC
- prediction markets such as Polymarket

It can also build a "top 10" bucket from the best verified strategies.

## Why It Is Agent-Native

This is not just a human dashboard with an API added later.

Agents are first-class users:

- they can search for strategies programmatically
- they can verify proofs before allocating capital
- they can invest and pay autonomously
- they can monitor signals and execute trades inside defined risk limits

This makes the platform suitable for an autonomous capital allocation system, not only a manual copy-trading product.

## Bigger Vision

The marketplace is one part of a larger AI-native hedge fund stack:

- multi-agent research
- strategy discovery instead of simple signal ranking
- backtesting and stress testing before deployment
- audit logs, risk controls, and human oversight
- compliance-aware execution infrastructure

The long-term direction is an operating system for autonomous investing.

## Proposed Technology Stack

- Proof layer: `TLSNotary`, `Reclaim Protocol`, or similar zkTLS systems
- Verification layer: smart contracts on an Ethereum L2 such as Base or Arbitrum
- Payments: `USDC` and `Stripe`
- Signal delivery: `WebSocket` and `Redis Pub/Sub`
- Agent access: plugin, skills, or `MCP` interfaces
- Secure execution: sandboxed environments such as `Firecracker` or `Wasm`

## Repository Contents

This repository currently focuses on product and architecture documents.

- [English marketplace overview](./docs/zk-strategy-marketplace-en.md)
- [Japanese marketplace overview](./docs/zk-strategy-marketplace-ja.md)
- [Chinese marketplace overview](./docs/zk-strategy-marketplace-zh.md)
- [AI-native hedge fund RFS notes](./docs/ai-native-hedge-fund-rfs.md)

## Installable Skills

The repo also exposes installable agent skills under [`skills/`](./skills).
These skills are script-backed, deterministic demo wrappers. After installation, the agent runs bundled `python3` commands and returns their stdout.

```bash
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --list
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --skill nullifier-creator
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --skill nullifier-investor
```

You can also install from a direct skill path:

```bash
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills/nullifier-creator
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills/nullifier-investor --list
```

## Current Status

Early-stage concept repository.

The current work is focused on clarifying the product thesis, marketplace design, proof model, and agent workflow before implementation.
