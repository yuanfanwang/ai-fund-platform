# OpenClaw Mock Demo

This is the shortest runbook for showing the `ai-fund-platform` agent-native UX in under 20 seconds.

This is not a live platform integration. It is a script-backed fixed-response demo powered by the skills under `skills/`.

## Install

```bash
npx skills add https://github.com/yuanfanwang/ai-fund-platform/tree/main/skills --skill nullifier-investor
npx skills add https://github.com/yuanfanwang/ai-fund-platform/tree/main/skills --skill nullifier-creator
```

## Launch

```bash
openclaw --skills ./skills/nullifier-investor
```

If needed, you can also launch the creator-side companion demo.

```bash
openclaw --skills ./skills/nullifier-creator
```

## 20-Second Pitch Script

User:

```text
Explore crypto strategies with APY above 20% and Max DD below 10%, then invest 25,000 USDC in the best one.
```

Expected response:

```text
Found 3 matching strategies. The top result is BTC Delta Neutral Pool.
Verified metrics: APY 24.8%, Max DD -6.9%, Sharpe 2.3.

Invested 25,000 USDC into BTC Delta Neutral Pool.
Current value is 26,420 USDC, unrealized PnL is +1,120 USDC, and realized earnings are 300 USDC.
```

## 10-Second Variant

User:

```text
Invest 25,000 USDC in the best verified crypto strategy.
```

Expected response:

```text
The top result is BTC Delta Neutral Pool.

Invested 25,000 USDC into BTC Delta Neutral Pool.
Current value is 26,420 USDC, unrealized PnL is +1,120 USDC, and realized earnings are 300 USDC.
```

## Optional Creator Follow-Up

User:

```text
Publish the BTC delta-neutral strategy. Also show status and revenue.
```

Expected response:

```text
Published BTC Delta Neutral Pool with proof-backed performance.
Public metrics: APY 24.8%, Max DD -6.9%, Sharpe 2.3.

BTC Delta Neutral Pool is active. Proof status is verified.
Current TVL is 1.84M USDC with 128 investors.

Total creator revenue is 42,380 USDC.
Withdrawable revenue is 18,240 USDC.
```
