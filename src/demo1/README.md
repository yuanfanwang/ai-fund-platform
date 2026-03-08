# Demo 1: Autonomous Hedge Fund Platform

2つの OpenClaw エージェント（Strategy Provider + Trader）が MCP Server を介して連携するデモ。

## 前提条件

- Node.js 20+
- OpenClaw がビルド済み（`../yc-hackathon/openclaw` から `npm link` で使用）

```bash
# OpenClaw のセットアップ（初回のみ）
cd ../yc-hackathon/openclaw && pnpm install && pnpm build && npm link && cd -

# MCP Server の依存インストール
cd src/demo1/platform && npm install && cd ../../..

# データを初期状態にリセット
./src/demo1/reset-data.sh
```

## デモ実行（ターミナル左右 split）

### 左ターミナル: Strategy Provider

```bash
openclaw --mcp-config src/demo1/configs/provider.mcp.json
```

起動したら以下を入力:

```
@strategy-provider Register my BTC momentum strategy. APY 35%, Max DD -12%, Sharpe 1.8
```

→ エージェントが戦略を登録し、自動で zkTLS 証明を生成する。

### 右ターミナル: Trader

```bash
openclaw --mcp-config src/demo1/configs/trader.mcp.json
```

起動したら以下を入力:

```
@strategy-trader Find the best verified crypto strategy and subscribe with $10k
```

→ エージェントが検索 → 証明検証 → サブスクまで自律的に実行する。

### クライマックス: シグナル連動

左ターミナル (Provider) に入力:

```
Send a buy signal for BTC at $68,500. Confidence 0.85, reason: RSI reversal below 30
```

→ 右ターミナル (Trader) で:

```
Check for the latest signal from the strategy I subscribed to
```

→ Provider が出したシグナルが Trader に届く。

## デモタイムライン（20秒）

| 秒数 | 左 (Provider) | 右 (Trader) |
|---|---|---|
| 0-2 | 1文入力（コピペ） | — |
| 2-8 | 戦略登録 + zkTLS 証明生成 | — |
| 8-10 | — | 1文入力（コピペ） |
| 10-16 | — | 検索 → 検証 → サブスク |
| 16-18 | シグナル発信入力 | — |
| 18-20 | シグナル送信 | シグナル確認 |

## ファイル構成

```
src/demo1/
├── README.md               ← 本ドキュメント
├── reset-data.sh           ← data.json リセット
├── platform/
│   ├── package.json
│   ├── index.mjs           ← MCP Server（全ツール定義 + データ読み書き）
│   └── data.json           ← 共有データ（戦略・サブスク・シグナル）
├── skills/
│   ├── strategy-provider/
│   │   └── SKILL.md        ← Provider のエージェント振る舞い定義
│   └── strategy-trader/
│       └── SKILL.md        ← Trader のエージェント振る舞い定義
└── configs/
    ├── provider.mcp.json   ← Provider の MCP 接続設定
    └── trader.mcp.json     ← Trader の MCP 接続設定
```

## リセット

デモをやり直す場合:

```bash
./src/demo1/reset-data.sh
```
