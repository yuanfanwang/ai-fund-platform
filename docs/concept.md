# Autonomous Hedge Fund Platform for Agents

## 一言で言うと

> **トレーディング戦略を秘匿したまま、zkTLS で成績を暗号学的に証明し、AI エージェントが Skills / MCP 経由で自律的に検索・購入・実行できるヘッジファンド・プラットフォーム。**

---

## 解決する課題

### Creator（戦略提供者）の問題

| 課題 | 現状 |
|---|---|
| **公開したら終わり** | 優秀な戦略を公開した瞬間にコピーされ、アルファが消滅する |
| **成績を証明できない** | 「年利 40%」と主張してもスクショは改竄可能。誰も信じない |
| **マネタイズ手段がない** | ファンドに所属しないと個人では収益化できない |

### Investor（投資家）の問題

| 課題 | 現状 |
|---|---|
| **信頼できない** | 戦略の実績が本物かどうか検証する手段がない |
| **黒箱への不安** | ブラックボックスに資金を預けることへの抵抗 |
| **手動オペレーション** | 戦略を見つけても、自分で実装・運用する必要がある |

### AI エージェント時代の問題

| 課題 | 現状 |
|---|---|
| **エージェントが戦略を探せない** | エージェントが使える「戦略 API」が存在しない |
| **決済の壁** | エージェントが自律的に戦略を購入・サブスクする仕組みがない |
| **品質の担保** | エージェントがどの戦略を信頼すべきか判断できない |

---

## プラットフォームの全体フロー

```
Creator                         Platform                          Investor
  │                                │                                 │
  │ 1. encrypt their strategy      │                                 │
  │    (zkTLS で戦略を秘匿)         │                                 │
  │                                │                                 │
  │ 2. publish to the platform     │                                 │
  ├──── skills / MCP ─────────────→│                                 │
  │    (APY, PnL, Max DD を公開)    │                                 │
  │                                │                                 │
  │                                │←──── skills / MCP ──────────────┤
  │                                │  1. invest according to APY     │
  │                                │                                 │
  │                                │──── signals ───────────────────→│
  │                                │                 2. take profit  │
  │                                │                                 │
  │←──── fund and profit ──────────│                                 │
  │ 3. get fund and profit         │                                 │
```

---

## 戦略カテゴリ

プラットフォーム上で以下のアセットクラスの戦略を扱う：

| カテゴリ | 例 |
|---|---|
| **Crypto** | BTC、ETH 等の暗号通貨戦略 |
| **FX** | 為替（USD/JPY、EUR/USD 等） |
| **US Equity** | 米国株式 |
| **Real Estate** | 不動産関連 |
| **Prediction Markets** | Polymarket 等の予測市場 |

各戦略は以下の指標を zkTLS で証明付きで公開する：
- **APY**（年間利回り）
- **PnL**（損益）
- **Max DD**（最大ドローダウン）

---

## コア技術：zkTLS による「ゼロ知識ストラテジー証明」

### zkTLS とは

TLS（HTTPS 通信）のレスポンスを**ゼロ知識証明**で検証可能にする技術。

```
通常の流れ：
  Creator → Binance API → 「あなたの年間リターンは +42%」

zkTLS の流れ：
  Creator → Binance API → 「あなたの年間リターンは +42%」
       ↓
  この TLS レスポンスから ZK 証明を生成
       ↓
  「Binance が返した本物のデータで +42% であること」を
  戦略の中身を明かさずに証明できる
```

### 何が証明できるか

| 証明対象 | データソース | 証明内容 |
|---|---|---|
| 取引成績 | 取引所 API（Binance, Coinbase 等） | 過去 1 年で +42% のリターン |
| シャープレシオ | 取引所 API | リスク調整後リターンが 2.1 以上 |
| 最大ドローダウン | 取引所 API | 最大 DD が -15% 以内 |
| 取引頻度 | 取引所 API | 月平均 50 回以上（アクティブ） |
| SNS 実績 | Twitter/X API | フォロワー 10k 以上 |
| 本人確認 | 各種 API | 実在する人物で取引所アカウントを所有 |

**戦略のロジック（どの銘柄を、いつ、なぜ買うか）は一切公開されない。**

---

## エージェント統合：Skills / MCP

AI エージェントは **Skills** および **MCP（Model Context Protocol）** を通じてプラットフォームにアクセスする。

### ユーザー体験

```
ユーザー: 「月利 5% 以上、DD 10% 以下の暗号通貨戦略を探して」

Agent:
  → Platform API を Skills/MCP 経由で呼び出し
  → zkTLS 証明済みの戦略を検索
  → 上位 3 件を提示（APY, PnL, Max DD の証明付き）

ユーザー: 「2 番目の戦略をサブスクして」

Agent:
  → 決済実行（ステーブルコイン / Stripe）
  → シグナルフィードを購読開始
  → 以降、シグナル受信 → 自動売買実行
```

### MCP Tool 設計

```typescript
// 戦略検索
{
  name: "zk_strategy_search",
  description: "zkTLS で成績が証明された戦略を検索する",
  parameters: {
    min_return: { type: "number", description: "最低リターン (%)" },
    max_drawdown: { type: "number", description: "最大DD上限 (%)" },
    asset_class: { enum: ["crypto", "us_equity", "fx", "real_estate", "prediction_market"] },
    min_sharpe: { type: "number" }
  }
}

// 戦略サブスクライブ
{
  name: "zk_strategy_subscribe",
  description: "戦略をサブスクライブし、シグナルを受信開始する",
  parameters: {
    strategy_id: { type: "string" },
    allocation: { type: "number", description: "配分額 (USD)" }
  }
}

// zkTLS 証明検証
{
  name: "zk_strategy_verify",
  description: "戦略の zkTLS 証明を検証する",
  parameters: {
    strategy_id: { type: "string" },
    proof_type: { enum: ["return", "sharpe", "drawdown", "identity"] }
  }
}

// シグナルリスナー（常駐サービス）
{
  name: "zk_signal_listener",
  description: "シグナルフィードを購読し、自動売買を実行する"
}
```

---

## プラットフォーム構造

```
┌──────────────────────────────────────────────────────────────────┐
│            Autonomous Hedge Fund Platform for Agents              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐                   ┌──────────────────────┐    │
│  │ Creator       │                   │ Investor / Agent     │    │
│  │              │                   │                      │    │
│  │ ・戦略を暗号化  │     zkTLS        │  ・成績証明を検証      │    │
│  │ ・プラットフォーム│     証明         │  ・戦略をサブスク      │    │
│  │   に公開       │────────────────→│  ・シグナルを受信      │    │
│  │ ・シグナル配信   │                  │  ・自動売買を実行      │    │
│  │ ・報酬を受取    │←────決済─────────│                      │    │
│  └──────────────┘                   └──────────────────────┘    │
│        ↑ skills/MCP                        skills/MCP ↑         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐      │
│  │               zkTLS Verification Layer                  │      │
│  │                                                        │      │
│  │  取引所 API ──→ TLS 証明生成 ──→ オンチェーン検証         │      │
│  │  Twitter API ──→ TLS 証明生成 ──→ オンチェーン検証        │      │
│  │  任意の API ──→ TLS 証明生成 ──→ オンチェーン検証          │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐      │
│  │               Strategy Marketplace                      │      │
│  │                                                        │      │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────────┐  │      │
│  │  │ Crypto   │ │ FX      │ │ Real    │ │ Prediction │  │      │
│  │  │ APY/PnL  │ │ APY/PnL │ │ Estate  │ │ Markets    │  │      │
│  │  │ Max DD   │ │ Max DD  │ │ APY/PnL │ │ APY/PnL    │  │      │
│  │  └─────────┘ └─────────┘ │ Max DD  │ │ Max DD     │  │      │
│  │                          └─────────┘ └────────────┘  │      │
│  └────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────┘
```

---

## ビジネスモデル

```
Creator ──シグナル──→ Platform ──シグナル──→ Investor/Agent
                          │
                   手数料（成果報酬 or 月額）
                          │
              ┌───────────┼───────────┐
              │           │           │
          Creator: 70%  Platform: 20%  Protocol: 10%
```

| 収益源 | モデル |
|---|---|
| サブスクリプション | 月額 $XX〜で戦略シグナルを購読 |
| 成果報酬 | 利益の X% を Creator と Platform で分配 |
| 証明手数料 | zkTLS 証明生成ごとに少額手数料 |
| API アクセス | エージェント向け Skills/MCP コール課金 |

---

## 競合との差別化

| 既存サービス | 問題 | 本プラットフォームの優位性 |
|---|---|---|
| QuantConnect / Numerai | 戦略コードの提出が必要（秘匿不可） | **戦略ロジック完全秘匿** |
| コピートレード（eToro 等） | 成績改竄リスク、戦略が丸見え | **zkTLS で暗号学的に成績を証明** |
| Hive5（GKTLS） | 汎用 zkTLS | **Agent ネイティブ**、Skills/MCP で直接接続 |
| Signal プロバイダー（Telegram） | 信頼性ゼロ、手動コピー | **証明付き + 自動執行** |

**最大の差別化：「Agent First」**
- 人間が UI で操作するのではなく、**AI エージェントが自律的に戦略を評価・購入・実行**
- Skills / MCP 対応 → あらゆる AI エージェントフレームワークから接続可能

---

## 技術スタック（想定）

| レイヤー | 技術 |
|---|---|
| zkTLS 証明 | TLSNotary / Reclaim Protocol / Opacity Network |
| オンチェーン検証 | Ethereum L2（Base / Arbitrum）+ スマートコントラクト |
| 決済 | ステーブルコイン（USDC）+ Stripe（法定通貨） |
| シグナル配信 | WebSocket + Redis Pub/Sub |
| エージェント統合 | Skills / MCP（Model Context Protocol） |
| バックエンド | TypeScript / Node.js |
| 戦略実行 | サンドボックス環境（Firecracker / Wasm） |

---

## まとめ

```
従来：  戦略を公開 → コピーされる → アルファ消滅
        成績を主張 → 証明できない → 信頼されない
        戦略を発見 → 手動で実装 → 運用が大変

本プラットフォーム：
        戦略を秘匿 → zkTLS で成績だけ証明 → 信頼を獲得
        Agent が Skills/MCP で検索 → 自動サブスク → 自動実行
        Creator は報酬を得る → 持続的なエコシステム
```

> **「優秀な戦略を持つ個人が、秘密を守りながら収益を得られ、AI エージェントがその戦略に自律的にアクセスできる世界を作る。」**
