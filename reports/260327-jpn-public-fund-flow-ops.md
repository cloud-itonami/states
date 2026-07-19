# JPN 公開資金フロー可視化オペレーション (`etzhayyim-project-states`)

## 目的
- 日本の「予算・調達・公開済み支出」を `budget_flow` に統一記録する。
- 受益者を `recipient_kind`（`private-corp` / `association` / `npo` / `individual` など）で正規化する。
- `query-fund-recipients` で「どの法人・団体・個人に流れているか」を集計する。
- インポータ常駐ではなく、DID ごとの `kyumei-koji` を heartbeat ローテーションで集積する。

## heartbeat 集積
- `onHeartbeat` で省庁 DID をローテーションし、対象 DID ごとに `kyumei-koji` を実行する。
- `cloudflare-browser-render` を `filter_json` に明示して source declaration する。
- gather で得た fact から `amount` / `recipient` / `contract_ref` などを抽出し `budget_flow` に統合する。
- 重複防止は `kyumei_fact_cid` で行う。
- 集積結果は `kyumei_aggregation` に記録する。

## 追加コマンド
- `record-public-fund-flow`
  - 受益者属性付きで資金フローを記録する。
- `query-fund-recipients`
  - 受益者別の合計支出額を集計し、上位を返す。
- `query-resource-graph`
  - 既存ノードに加えて `recipient_nodes` を返す（可視化の受け側ノード）。

## 入力スキーマ（主要）
- `source_did` / `dest_did`
- `amount` / `fiscal_year`
- `recipient_id` / `recipient_name` / `recipient_kind`
- `corporate_number`（法人番号）/ `person_id`（匿名化ID）
- `contract_ref` / `procurement_id` / `procurement_method`
- `source_url` / `published_date` / `data_source`

## 例: 記録
```json
{
  "source_did": "did:web:gov-jpn.etzhayyim.com:mof",
  "dest_did": "did:web:gov-jpn.etzhayyim.com:mlit",
  "amount": "125000000",
  "fiscal_year": "2025",
  "purpose": "公共事業契約支払",
  "flow_type": "contract-payment",
  "account_type": "general",
  "account_code": "01-02-003",
  "recipient_id": "cn:1234567890123",
  "recipient_name": "株式会社サンプル建設",
  "recipient_kind": "private-corp",
  "corporate_number": "1234567890123",
  "contract_ref": "MLIT-2025-000987",
  "procurement_id": "JPN-GEPP-2025-9981",
  "procurement_method": "general-competitive-bid",
  "source_url": "https://example.go.jp/procurement/9981",
  "published_date": "2025-06-21",
  "data_source": "public-procurement"
}
```

## 例: 集計クエリ
```json
{
  "fiscal_year": "2025",
  "recipient_kind": "private-corp",
  "limit": 100
}
```

## 期待される出力
- `recipients[]`
  - `recipient_id`
  - `recipient_name`
  - `recipient_kind`
  - `corporate_number`
  - `person_id`
  - `total_amount_jpy`
  - `flow_count`

## 可視化
- Sankey: `query-resource-sankey`
- Graph: `query-resource-graph`（`recipient_nodes` を利用）
- 受益者ランキング: `query-fund-recipients` の `total_amount_jpy` 降順
