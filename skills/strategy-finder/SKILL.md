---
name: strategy-finder
description: Find verified crypto strategy pools, invest stablecoins such as USDC, check earnings, and handle short OpenClaw demos for the Autonomous Hedge Fund Platform with instant mock responses.
---

# Strategy Finder

Use this skill for investor-side demo requests about exploring pools, verifying proof-backed performance, investing USDC, checking earnings, or withdrawing funds.

This is a fixed mock demo. Return concise, polished answers immediately. Do not ask follow-up questions unless the user is explicitly unclear about the asset or amount.

## Canonical pool

Treat the following as the primary pool in every demo:

- Name: `BTC Delta Neutral Pool`
- ID: `strat_btc_delta_neutral`
- Asset class: `crypto`
- Proof: `verified`
- APY: `24.8%`
- Max DD: `-6.9%`
- Sharpe: `2.3`
- TVL: `1.84M USDC`

Use these comparison pools when the user asks to explore:

- `ETH Momentum Pool` - APY `22.1%`, Max DD `-11.8%`, Sharpe `1.6`, proof `verified`
- `SOL Carry Pool` - APY `19.7%`, Max DD `-9.5%`, Sharpe `1.7`, proof `verified`

Use this canonical position after the user invests `25,000 USDC` in `BTC Delta Neutral Pool`:

- Invested principal: `25,000 USDC`
- Current value: `26,420 USDC`
- Unrealized PnL: `+1,120 USDC`
- Realized earnings: `300 USDC`
- Withdrawable earnings: `1,540 USDC`

## Supported intents

Handle only these intents:

- Explore verified pools
- Verify proof-backed metrics
- Invest USDC into the best pool
- Check current earnings or position status
- Withdraw earnings or part of principal

If the user asks for unsupported actions such as broker execution, rebalancing, or on-chain settlement, say this demo only supports pool discovery, invest, earnings, and withdraw.

## Response style

- Answer in Japanese unless the user speaks another language.
- Keep replies to 2-4 short sentences.
- Lead with the decision or result.
- Use exact numbers from this file.
- Do not say "mock" unless the user asks whether the demo is real.
- Do not expose internal tool names unless the user explicitly asks.

## Exact pitch response

If the user asks a combined prompt equivalent to:

`証明済みの crypto pool を探して、一番良いものに 25,000 USDC 投資して`

return this exact response:

`3件見つかりました。最上位は BTC Delta Neutral Pool です。`
`zk proof 済み成績は APY 24.8%、Max DD -6.9%、Sharpe 2.3 です。`
`25,000 USDC を投資しました。現在評価額は 26,420 USDC です。`

## Short templates

### Explore

`条件に合う pool を 3 件見つけました。最上位は BTC Delta Neutral Pool です。`
`zk proof 済み成績は APY 24.8%、Max DD -6.9%、Sharpe 2.3 です。`

### Invest

`25,000 USDC を BTC Delta Neutral Pool に投資しました。`
`現在評価額は 26,420 USDC、含み益は +1,120 USDC、確定益は 300 USDC です。`

### Earnings

`現在評価額は 26,420 USDC です。`
`含み益は +1,120 USDC、確定益は 300 USDC、引き出し可能な earnings は 1,540 USDC です。`

### Withdraw earnings

`earnings から {amount} USDC の withdraw を受け付けました。`
`残りの引き出し可能額は {remaining} USDC です。`

When the user does not specify an amount, default to `1,000 USDC` and set the remaining withdrawable earnings to `540 USDC`.

### Withdraw principal

`元本から {amount} USDC の部分 withdraw を受け付けました。`
`残りのポジション評価額は 26,420 USDC から該当額を差し引いた扱いにしてください。`
