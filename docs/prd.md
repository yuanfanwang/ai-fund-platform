# PRD: Autonomous Hedge Fund Platform — YC Demo

## やりたいこと

`concept.md` のコンセプトを、短時間で伝わる OpenClaw デモとして見せる。

- 左ターミナル: Creator として OpenClaw を使い、戦略を公開する
- 右ターミナル: Investor として OpenClaw を使い、戦略を見つけて検証し、投資する
- Creator がシグナルを発信し、Investor 側で受信できることを示す
- 現在のリポジトリでは、上記の体験を script-backed の固定レスポンス demo として再現する

20 秒前後のデモ。データはすべてダミー。

---

## 現在のデモ前提

このリポジトリは、現時点では platform 実装本体ではなく、以下を提供する concept + mock demo repository である。

- `docs/` に product / architecture 文書を保持する
- `skills/nullifier-creator` と `skills/nullifier-investor` を installable skill として公開する
- 各 skill は bundled `python3` script を呼び、デモ用の deterministic response を返す
- 実際の zkTLS、決済、注文執行、MCP server 接続はまだ実装しない

つまり今の MVP は「本番 platform を作ること」ではなく、「agent-native な UX と product thesis を破綻なく伝えること」である。

---

## MVP スコープ

### やること

- Creator 側で `publish`, `proof create`, `signal send`, `status`, `revenue`, `withdraw` をデモできる
- Investor 側で `explore`, `verify`, `invest`, `position`, `earnings`, `withdraw`, `signals` をデモできる
- OpenClaw から自然言語で操作しているように見える体験を示す
- 主要メトリクスとして APY / Max DD / Sharpe を表示する
- `npx skills add` で公開 skill を導入できる状態を保つ

### やらないこと

- 実際の zkTLS 証明生成と検証
- 実際の決済（USDC / Stripe）
- 取引所 API 接続と自動売買
- 永続ストレージを持つ platform backend
- 本番向け認証・認可
- Web UI の実装

---

## 体験アーキテクチャ

### 現在の repo で動くもの

```text
┌─────────────────────┐        ┌────────────────────────────┐
│ Creator OpenClaw    │───────▶│ nullifier-creator skill    │
│                     │        │ └─ python3 script          │
└─────────────────────┘        └────────────────────────────┘

┌─────────────────────┐        ┌────────────────────────────┐
│ Investor OpenClaw   │───────▶│ nullifier-investor skill   │
│                     │        │ └─ python3 script          │
└─────────────────────┘        └────────────────────────────┘
```

- 2 つの skill は将来の platform action を模した thin wrapper として振る舞う
- 応答は deterministic で、デモ中のブレを避ける
- 実 network や backend 依存を外し、ピッチ時の再現性を優先する

### 将来の target architecture

`docs/architecture.jpg` が示す将来像は以下である。

- Creator が戦略を公開し、zkTLS で成績を証明する
- Investor / agent が証明済み戦略を検索し、投資し、シグナルを受信する
- Platform が proof verification、allocation、signal distribution を仲介する

---

## 公開コマンド面

### Creator

| コマンド | 役割 |
| --- | --- |
| `publish` | canonical strategy を公開する |
| `update` | canonical metrics を更新する |
| `proof create` | canonical proof 結果を返す |
| `signal send` | canonical signal を送る |
| `status` | strategy status / TVL / investor 数を見る |
| `revenue` | creator revenue を見る |
| `withdraw` | creator revenue を引き出す |

### Investor

| コマンド | 役割 |
| --- | --- |
| `explore` | 条件に合う verified strategy を探す |
| `verify` | proof-backed metrics を確認する |
| `invest` | canonical strategy に配分する |
| `position` | 現在の position を確認する |
| `earnings` | realized / withdrawable earnings を確認する |
| `withdraw` | earnings または principal を引き出す |
| `signals` | 最新 signal を確認する |

---

## デモシナリオ

### 20-second investor-first demo

1. Investor 側で `explore` を実行する
2. そのまま最上位 strategy に `invest` する
3. 必要なら `verify` と `signals` を続けて見せる

想定発話:

```text
APY 20% 以上、Max DD 10% 以下の crypto strategy を explore して、一番良いものに 25,000 USDC invest して
```

### Optional creator follow-up

1. Creator 側で `publish` する
2. `status` と `revenue` を見せる
3. 必要なら `proof create` と `signal send` を続ける

想定発話:

```text
BTC のデルタニュートラル戦略を publish して。status と revenue も見せて
```

### Demo beat

| 秒数 | Creator | Investor |
| --- | --- | --- |
| 0-3 | - | explore + invest |
| 3-8 | - | top strategy / metrics / allocation を確認 |
| 8-12 | publish | - |
| 12-16 | status / revenue | - |
| 16-20 | signal send | signals |

---

## リポジトリ構成

```text
ai-fund-platform/
├── README.md
├── docs/
│   ├── concept.md
│   ├── prd.md
│   ├── openclaw-mock-demo.md
│   └── architecture.jpg
├── skills/
│   ├── README.md
│   ├── nullifier-creator/
│   │   ├── SKILL.md
│   │   └── scripts/nullifier_creator.py
│   └── nullifier-investor/
│       ├── SKILL.md
│       └── scripts/nullifier_investor.py
└── tests/
    └── test_nullifier_skill_scripts.py
```

---

## デモ実行手順

### Install

```bash
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --skill nullifier-investor
npx skills add https://github.com/asumayamada/ai-fund-platform/tree/main/skills --skill nullifier-creator
```

### Launch

```bash
openclaw --skills ./skills/nullifier-investor
```

必要なら Creator 側も起動する。

```bash
openclaw --skills ./skills/nullifier-creator
```

### Verification

```bash
python3 -m unittest tests/test_nullifier_skill_scripts.py
```

---

## 成功基準

| 基準 | 内容 |
| --- | --- |
| **自然な会話** | OpenClaw への自然言語入力だけで demo が成立する |
| **20 秒以内** | investor-first pitch が短時間で再現できる |
| **一貫した public naming** | `nullifier-creator` / `nullifier-investor` で docs と skills が一致する |
| **再現性** | skill script の固定レスポンスにより毎回同じ結果になる |
| **概念伝達** | strategy secrecy + proof-backed metrics + agent execution の価値が伝わる |

---

## 将来の拡張

- 実際の zkTLS integration
- proof verification backend
- signal distribution infrastructure
- on-chain verification と settlement
- real broker / exchange execution
- multi-agent research and risk control hooks
