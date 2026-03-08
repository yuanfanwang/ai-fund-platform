# PRD: Autonomous Hedge Fund Platform — YC Demo

## やりたいこと

- 左ターミナル: **Creator として OpenClaw とチャット**して戦略を提出する
- 右ターミナル: **Trader として OpenClaw とチャット**して戦略を見つけてトレードする
- 裏で **Platform（HTTP API サーバー）** が両者を仲介する

20 秒のデモ。データは全てダミー。

---

## アーキテクチャ

```
┌─────────────────────┐                     ┌─────────────────────┐
│ Creator の           │   curl / web_fetch  │ Trader の            │
│ OpenClaw TUI        │──────────┐  ┌───────│ OpenClaw TUI        │
│                     │          │  │       │                     │
│ Skill:              │          ▼  ▼       │ Skill:              │
│ - strategy-provider │    ┌───────────┐    │ - strategy-trader   │
└─────────────────────┘    │ Platform  │    └─────────────────────┘
                           │ (HTTP API)│
                           │ port 3456 │
                           │           │
                           │ data.json │
                           └───────────┘
```

- **Platform**: `node server.mjs` で起動する HTTP API。ポート 3456。
- **OpenClaw**: Gateway 1 つ起動し、TUI を 2 セッション開く。
- **Skills**: OpenClaw の Skill（SKILL.md）でエージェントの振る舞いを定義。エージェントは `exec` ツールで `curl` を叩いて Platform API を呼ぶ。

---

## Platform API

### エンドポイント

| Method | Path | 説明 |
|---|---|---|
| POST | `/strategies` | 戦略を登録する |
| POST | `/strategies/:id/proof` | zkTLS 証明を生成する |
| GET | `/strategies` | 戦略一覧を取得する（クエリパラメータでフィルタ） |
| GET | `/strategies/:id` | 戦略の詳細を取得する |
| GET | `/strategies/:id/proof` | 証明を検証する |
| POST | `/strategies/:id/subscribe` | 戦略をサブスクライブする |
| POST | `/strategies/:id/signals` | シグナルを発信する |
| GET | `/strategies/:id/signals/latest` | 最新シグナルを取得する |

### リクエスト/レスポンス例

**POST /strategies**
```bash
curl -X POST http://localhost:3456/strategies \
  -H "Content-Type: application/json" \
  -d '{"name":"BTC Momentum","asset_class":"crypto","apy":35.2,"max_drawdown":-12.1,"sharpe_ratio":1.83}'
```
```json
{"id":"strat_abc123","name":"BTC Momentum","asset_class":"crypto","apy":35.2,"max_drawdown":-12.1,"sharpe_ratio":1.83,"proof_status":"unverified"}
```

**POST /strategies/:id/proof**
```bash
curl -X POST http://localhost:3456/strategies/strat_abc123/proof
```
```json
{"strategy_id":"strat_abc123","proof_status":"verified","proof":{"type":"zktls_v1","data_source":"Binance API","claims":{"apy":35.2}}}
```

**GET /strategies**
```bash
curl http://localhost:3456/strategies?asset_class=crypto
```
```json
[{"id":"strat_abc123","name":"BTC Momentum","apy":35.2,"max_drawdown":-12.1,"sharpe_ratio":1.83,"proof_status":"verified"}, ...]
```

**GET /strategies/:id/proof**
```bash
curl http://localhost:3456/strategies/strat_abc123/proof
```
```json
{"valid":true,"proof":{"type":"zktls_v1","data_source":"Binance API","attested_at":"2026-03-08T12:00:00Z","claims":{"apy":35.2,"max_drawdown":-12.1,"sharpe_ratio":1.83}}}
```

**POST /strategies/:id/subscribe**
```bash
curl -X POST http://localhost:3456/strategies/strat_abc123/subscribe \
  -H "Content-Type: application/json" \
  -d '{"trader_id":"bob","allocation":10000}'
```
```json
{"subscription_id":"sub_001","strategy_name":"BTC Momentum","allocation":10000,"status":"active"}
```

**POST /strategies/:id/signals**
```bash
curl -X POST http://localhost:3456/strategies/strat_abc123/signals \
  -H "Content-Type: application/json" \
  -d '{"action":"BUY","asset":"BTC/USD","price":68500,"confidence":0.85,"reasoning":"RSI reversal below 30"}'
```
```json
{"signal_id":"sig_001","action":"BUY","asset":"BTC/USD","price":68500,"subscribers_notified":1}
```

**GET /strategies/:id/signals/latest**
```bash
curl http://localhost:3456/strategies/strat_abc123/signals/latest
```
```json
{"signal_id":"sig_001","action":"BUY","asset":"BTC/USD","price":68500,"confidence":0.85,"reasoning":"RSI reversal below 30"}
```

---

## Skills

### strategy-provider/SKILL.md

Creator 用。エージェントに「戦略を登録して証明を生成して、シグナルを出す」方法を教える。

```
allowed-tools: ["exec"]
```

SKILL.md の中で、上記の curl コマンドのパターンを文書化する。
エージェントは自然言語の指示を受けて、適切な curl を exec で実行する。

### strategy-trader/SKILL.md

Trader 用。エージェントに「戦略を検索して証明を検証して、サブスクして、シグナルを確認する」方法を教える。

```
allowed-tools: ["exec"]
```

---

## ディレクトリ構成

```
src/demo1/
├── platform/
│   ├── package.json
│   ├── server.mjs          ← HTTP API サーバー（1 ファイル）
│   └── data.json            ← 共有データ
├── skills/
│   ├── strategy-provider/
│   │   └── SKILL.md
│   └── strategy-trader/
│       └── SKILL.md
├── reset-data.sh
└── README.md
```

---

## デモ実行手順

```bash
# 0. セットアップ（初回のみ）
cd src/demo1/platform && npm install && cd ../../..

# 1. データリセット
./src/demo1/reset-data.sh

# 2. Platform 起動（バックグラウンド）
node src/demo1/platform/server.mjs &

# 3. OpenClaw Gateway 起動
openclaw gateway run --allow-unconfigured --auth none

# 4. 左ターミナル: Creator セッション
openclaw tui --session creator
# → "Register my BTC momentum strategy. APY 35%, Max DD -12%, Sharpe 1.8"

# 5. 右ターミナル: Trader セッション
openclaw tui --session trader
# → "Find the best verified crypto strategy and subscribe with $10k"

# 6. 左に戻って:
# → "Send a buy signal for BTC at $68,500"

# 7. 右で:
# → "Check for the latest signal"
```

---

## デモスクリプト（20秒）

| 秒数 | 左 (Creator) | 右 (Trader) |
|---|---|---|
| 0-2 | 1文入力 | — |
| 2-8 | 戦略登録 + 証明生成 | — |
| 8-10 | — | 1文入力 |
| 10-16 | — | 検索 → 検証 → サブスク |
| 16-18 | シグナル発信 | — |
| 18-20 | — | シグナル受信 |

---

## 成功基準

| 基準 | 内容 |
|---|---|
| **E2E** | Creator が登録した戦略を Trader が見つけてサブスクできる |
| **シグナル連動** | Creator のシグナルが Trader に届く |
| **20秒** | 全フローが 20 秒以内に完了 |
| **自然な会話** | OpenClaw とのチャットで全て完結（curl を直接打つ必要なし） |
