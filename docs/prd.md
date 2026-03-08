# PRD: Autonomous Hedge Fund Platform — MVP Demo

## 目的

concept.md のコンセプトを動くデモとして実証する。
Creator が戦略を公開し、Investor が検索・検証・投資・シグナル受信するフローを、2つの OpenClaw インスタンスと1つの Platform を通じて End-to-End で動かす。

---

## MVP スコープ

### やること

- Creator 用 OpenClaw から戦略を登録・証明生成・シグナル発信
- Investor 用 OpenClaw から戦略を検索・検証・投資・シグナル受信
- Platform が MCP Server として両者を仲介
- zkTLS 証明は **モック**（デモ用にダミー証明を生成・検証）
- 戦略の成績指標（APY, PnL, Max DD）の表示

### やらないこと（MVP 外）

- 実際の zkTLS 証明（TLSNotary / Reclaim Protocol 統合）
- オンチェーン検証・スマートコントラクト
- 実際の決済（USDC / Stripe）
- 実際の取引所接続・自動売買
- 本番レベルの認証・認可
- UI（全て OpenClaw の会話 UI で操作）

---

## システム構成

```
┌─────────────────────┐  MCP (stdio)  ┌─────────────────────┐
│ Creator の            │◀────────────▶│                     │
│ OpenClaw             │               │                     │
│                      │               │   Platform          │
│ Skills:              │               │   (MCP Server)      │
│ - nullifier-creator  │               │                     │
└─────────────────────┘               │   - REST API        │
                                       │   - WebSocket       │
┌─────────────────────┐  MCP (stdio)  │   - SQLite DB       │
│ Investor の          │◀────────────▶│   - Mock zkTLS      │
│ OpenClaw             │               │                     │
│                      │               └─────────────────────┘
│ Skills:              │
│ - nullifier-investor │
└─────────────────────┘
```

---

## コンポーネント詳細

### 1. Platform（MCP Server）

プラットフォームのバックエンド。MCP Server として動作し、Creator と Investor 双方の OpenClaw に MCP ツールを提供する。

#### 技術スタック

| 項目           | 技術                             |
| -------------- | -------------------------------- |
| 言語           | TypeScript                       |
| MCP SDK        | `@modelcontextprotocol/sdk`      |
| トランスポート | stdio（ローカルデモ用）          |
| DB             | SQLite（`better-sqlite3`）       |
| シグナル配信   | インプロセス EventEmitter（MVP） |

#### データモデル

```sql
-- 戦略
CREATE TABLE strategies (
  id            TEXT PRIMARY KEY,
  provider_id   TEXT NOT NULL,
  name          TEXT NOT NULL,
  description   TEXT,
  asset_class   TEXT NOT NULL,  -- crypto, fx, us_equity, real_estate, prediction_market
  apy           REAL,
  pnl           REAL,
  max_drawdown  REAL,
  sharpe_ratio  REAL,
  status        TEXT DEFAULT 'active',  -- active, paused, archived
  proof_status  TEXT DEFAULT 'unverified',  -- unverified, verified, expired
  proof_data    TEXT,  -- JSON: mock zkTLS proof
  created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ポジション
CREATE TABLE positions (
  id            TEXT PRIMARY KEY,
  strategy_id   TEXT NOT NULL REFERENCES strategies(id),
  investor_id   TEXT NOT NULL,
  allocation    REAL NOT NULL,  -- USD
  current_value REAL,
  realized_pnl  REAL DEFAULT 0,
  status        TEXT DEFAULT 'active',  -- active, paused, withdrawn
  created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

-- シグナル
CREATE TABLE signals (
  id            TEXT PRIMARY KEY,
  strategy_id   TEXT NOT NULL REFERENCES strategies(id),
  action        TEXT NOT NULL,  -- buy, sell, hold
  asset         TEXT NOT NULL,  -- e.g. BTC/USD, EUR/USD
  price         REAL,
  quantity      REAL,
  confidence    REAL,  -- 0.0 - 1.0
  reasoning     TEXT,
  created_at    TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### MCP ツール一覧

**Creator 向け**

| ツール名       | 説明                                               |
| -------------- | -------------------------------------------------- |
| `publish`      | 新しい戦略を公開する                               |
| `update`       | 戦略の情報（成績指標等）を更新する                 |
| `proof_create` | 成績の zkTLS 証明を生成する（MVP ではモック）      |
| `signal_send`  | 売買シグナルを発信する                             |
| `status`       | 自分の戦略状態、TVL、investor 数を取得する         |
| `revenue`      | creator revenue と withdrawable balance を取得する |
| `withdraw`     | creator revenue を引き出す                         |

**Investor 向け**

| ツール名   | 説明                                                    |
| ---------- | ------------------------------------------------------- |
| `explore`  | 条件に合う戦略を検索する（APY, Max DD, asset_class 等） |
| `verify`   | 戦略の zkTLS 証明を検証する（MVP ではモック検証）       |
| `invest`   | 戦略に資金を投入する                                    |
| `position` | 現在の評価額や PnL を取得する                           |
| `earnings` | 確定利益と引き出し可能利益を取得する                    |
| `withdraw` | earnings または元本の一部を引き出す                     |
| `signals`  | 戦略のシグナル履歴または最新 signal を取得する          |

**共通**

| ツール名               | 説明                                 |
| ---------------------- | ------------------------------------ |
| `platform_status`      | プラットフォームの稼働状況を取得する |
| `strategy_leaderboard` | 成績上位の戦略ランキングを取得する   |

#### Mock zkTLS

MVP では zkTLS を以下のようにモックする：

```typescript
// 証明生成（Creator が呼ぶ）
function generateMockProof(
  strategyId: string,
  metrics: StrategyMetrics,
): Proof {
  return {
    id: crypto.randomUUID(),
    strategyId,
    type: "mock_zktls_v1",
    claims: {
      apy: metrics.apy,
      maxDrawdown: metrics.maxDrawdown,
      sharpeRatio: metrics.sharpeRatio,
      dataSource: "binance_api", // 模擬
      attestedAt: new Date().toISOString(),
    },
    // 実際の zkTLS ではここに暗号学的証明が入る
    signature: crypto.randomBytes(64).toString("hex"),
    verified: true,
  };
}

// 証明検証（Investor が呼ぶ）
function verifyMockProof(proof: Proof): VerificationResult {
  return {
    valid: true,
    message: "Mock proof verified successfully",
    attestedSource: proof.claims.dataSource,
    attestedAt: proof.claims.attestedAt,
  };
}
```

---

### 2. Creator 用 OpenClaw

Creator が使用する OpenClaw インスタンス。Platform の MCP Server に接続し、戦略の公開・証明生成・シグナル発信を行う。

#### MCP 設定

```json
{
  "mcpServers": {
    "zkstrategy": {
      "command": "node",
      "args": ["./platform/dist/mcp-server.js"],
      "env": {
        "USER_ROLE": "creator",
        "USER_ID": "creator_alice"
      }
    }
  }
}
```

#### Skill: `nullifier-creator`

```yaml
---
name: nullifier-creator
description: |
  Faithfully reproduce Nullifier creator commands such as publish, update,
  proof create, signal send, status, revenue, and withdraw.
---
```

Skill の指示内容：

- command-first で creator action を案内する
- `publish`, `update`, `proof create`, `signal send`, `status`, `revenue`, `withdraw` を公開する
- 不足パラメータだけを短くヒアリングする
- 固定レスポンス集ではなく、platform action の thin wrapper として振る舞う

#### デモシナリオ（Creator）

```
Creator: 「BTC のデルタニュートラル戦略を publish して。APY 24.8%、Max DD -6.9%、シャープ 2.3」

OpenClaw:
  → publish を呼び出し
  → 「BTC Delta Neutral Pool を publish しました」
  → 「proof create も実行しますか？」

Provider: 「はい」

OpenClaw:
  → proof_create を呼び出し
  → 「proof を作成しました。APY 24.8%、Max DD -6.9% を verified として更新しました。」

Creator: 「BTC/USD を 68,500 で buy signal を送って」

OpenClaw:
  → signal_send を呼び出し
  → 「signal を送信しました。active investor に配信されます。」
```

---

### 3. Investor 用 OpenClaw

Investor が使用する OpenClaw インスタンス。Platform の MCP Server に接続し、戦略の検索・検証・投資・シグナル受信を行う。

#### MCP 設定

```json
{
  "mcpServers": {
    "zkstrategy": {
      "command": "node",
      "args": ["./platform/dist/mcp-server.js"],
      "env": {
        "USER_ROLE": "investor",
        "USER_ID": "investor_bob"
      }
    }
  }
}
```

#### Skill: `nullifier-investor`

```yaml
---
name: nullifier-investor
description: |
  Faithfully reproduce Nullifier investor commands such as explore, verify,
  invest, position, earnings, withdraw, and signals.
---
```

Skill の指示内容：

- command-first で investor action を案内する
- `explore`, `verify`, `invest`, `position`, `earnings`, `withdraw`, `signals` を公開する
- ユーザーの投資条件（APY, Max DD, asset_class 等）だけをヒアリングする
- 投資操作は `invest` / `withdraw` モデルで統一する

#### デモシナリオ（Investor）

```
Investor: 「APY 20% 以上、DD 15% 以下の暗号通貨戦略を explore して」

OpenClaw:
  → explore を呼び出し
  → 検索結果を表示:
    1. BTC Momentum (APY: 35%, DD: -12%, Sharpe: 1.8) ✅ 証明済み
    2. ETH Mean Reversion (APY: 28%, DD: -14%, Sharpe: 1.5) ✅ 証明済み
    3. Crypto Multi-Factor (APY: 22%, DD: -10%, Sharpe: 2.1) ⏳ 未証明

Investor: 「1 番の proof を verify して」

OpenClaw:
  → verify を呼び出し
  → 「✅ 証明は有効です。Binance API データに基づき APY 35%、Max DD -12% が確認されています。」

Investor: 「25,000 USDC invest して」

OpenClaw:
  → invest を呼び出し
  → 「BTC Delta Neutral Pool に 25,000 USDC を投資しました。シグナル受信を開始します。」

--- （Creator がシグナルを発信した後） ---

OpenClaw:
  → signals を呼び出し
  → 「🔔 新しいシグナル: BTC Momentum が BTC/USD を $68,500 で買い推奨
      (confidence: 0.85, 理由: RSI が 30 を下回り反転シグナル)」
```

---

## ディレクトリ構成

```
ai-fund-platform/
├── docs/
│   ├── concept.md
│   ├── prd.md                          ← 本ドキュメント
│   └── ...
├── platform/                            ← Platform (MCP Server)
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── mcp-server.ts              ← MCP Server エントリポイント
│   │   ├── tools/
│   │   │   ├── creator-tools.ts      ← Creator 向けツール定義
│   │   │   ├── investor-tools.ts     ← Investor 向けツール定義
│   │   │   └── common-tools.ts        ← 共通ツール定義
│   │   ├── db/
│   │   │   ├── schema.ts             ← SQLite スキーマ定義
│   │   │   └── index.ts              ← DB 初期化・クエリ
│   │   ├── proof/
│   │   │   └── mock-zktls.ts         ← Mock zkTLS 証明生成・検証
│   │   └── signals/
│   │       └── emitter.ts            ← シグナル配信ロジック
│   └── dist/                          ← ビルド成果物
├── skills/
│   ├── nullifier-creator/             ← Creator 用 Skill
│   │   └── SKILL.md
│   └── nullifier-investor/            ← Investor 用 Skill
│       └── SKILL.md
├── configs/
│   ├── creator.mcp.json              ← Creator の MCP 設定
│   └── investor.mcp.json             ← Investor の MCP 設定
└── demo/
    ├── seed-data.ts                   ← デモ用の初期データ投入
    └── README.md                      ← デモ実行手順
```

---

## デモ実行フロー

### 前提条件

- Node.js 20+
- OpenClaw がインストール済み（`npm install -g openclaw@latest`）

### セットアップ

```bash
# 1. Platform をビルド
cd platform && npm install && npm run build

# 2. デモ用データを投入
npx tsx demo/seed-data.ts

# 3. Creator の OpenClaw を起動（ターミナル A）
openclaw --mcp-config configs/creator.mcp.json --skills ./skills/nullifier-creator

# 4. Investor の OpenClaw を起動（ターミナル B）
openclaw --mcp-config configs/investor.mcp.json --skills ./skills/nullifier-investor

# Optional: inspect or install public skills
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --list
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --skill nullifier-investor
```

### デモストーリー

| ステップ | 誰が     | 操作                                  | 使う MCP ツール |
| -------- | -------- | ------------------------------------- | --------------- |
| 1        | Creator  | 「FX 戦略を publish して」            | `publish`       |
| 2        | Creator  | 「proof を作って」                    | `proof_create`  |
| 3        | Investor | 「APY 20% 以上の戦略を explore して」 | `explore`       |
| 4        | Investor | 「proof を verify して」              | `verify`        |
| 5        | Investor | 「25,000 USDC invest して」           | `invest`        |
| 6        | Creator  | 「EUR/USD の buy signal を送って」    | `signal_send`   |
| 7        | Investor | （自動受信）                          | `signals`       |

---

## 成功基準

| 基準               | 内容                                                                                |
| ------------------ | ----------------------------------------------------------------------------------- |
| **E2E フロー**     | Creator → 戦略公開 → 証明生成 → 投資 → シグナル発信 → Investor が受信、が一連で動く |
| **MCP 接続**       | 2 つの OpenClaw インスタンスが同一 Platform の MCP Server に接続して動作する        |
| **検索・フィルタ** | Investor が APY, Max DD, asset_class 等で戦略を検索できる                           |
| **Mock 証明**      | 証明の生成・検証フローがデモとして成立する                                          |
| **シグナル配信**   | Creator のシグナルが Investor にリアルタイムで届く                                  |

---

## 将来の拡張（MVP 後）

| フェーズ    | 内容                                              |
| ----------- | ------------------------------------------------- |
| **Phase 2** | 実際の zkTLS 統合（TLSNotary / Reclaim Protocol） |
| **Phase 2** | オンチェーン証明検証（Base / Arbitrum）           |
| **Phase 3** | USDC / Stripe による実決済                        |
| **Phase 3** | 取引所 API 接続による自動売買                     |
| **Phase 4** | マルチエージェント分析（RFS のエージェント群）    |
| **Phase 4** | リスク管理 Hook                                   |
