# OpenClaw Mock Demo

20 秒以内で `ai-fund-platform` の agent-native UX を見せるための最短 runbook です。

これは実 platform 接続ではなく、`skills/` 配下の script-backed 固定レスポンス demo です。

## Install

```bash
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --skill nullifier-investor
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --skill nullifier-creator
```

## Launch

```bash
openclaw --skills ./skills/nullifier-investor
```

必要なら creator 側の補助デモも起動できます。

```bash
openclaw --skills ./skills/nullifier-creator
```

## 20-Second Pitch Script

User:

```text
APY 20% 以上、Max DD 10% 以下の crypto strategy を explore して、一番良いものに 25,000 USDC invest して
```

Expected response:

```text
3件見つかりました。最上位は BTC Delta Neutral Pool です。
zk proof 済み成績は APY 24.8%、Max DD -6.9%、Sharpe 2.3 です。
25,000 USDC を投資しました。現在評価額は 26,420 USDC です。
```

## 10-Second Variant

User:

```text
一番良い証明済み crypto strategy に 25,000 USDC invest して
```

Expected response:

```text
最上位は BTC Delta Neutral Pool です。
25,000 USDC を投資しました。現在評価額は 26,420 USDC です。
```

## Optional Creator Follow-Up

User:

```text
BTC のデルタニュートラル戦略を publish して。status と revenue も見せて
```

Expected response:

```text
BTC Delta Neutral Pool を publish しました。zk proof 付き成績を公開済みです。
現在の TVL は 1.84M USDC、investor 数は 128 です。
累計 revenue は 42,380 USDC、withdraw 可能額は 18,240 USDC です。
```
