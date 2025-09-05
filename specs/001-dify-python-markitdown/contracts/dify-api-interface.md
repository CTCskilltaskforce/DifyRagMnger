# Dify API インターフェース仕様

**Feature Branch**: `001-dify-python-markitdown`  
**Created**: 2025-09-05  
**Status**: Draft  
**Version**: 2.2.0

## 概要
本ドキュメントは、Difyナレッジ自動登録・更新バッチプログラムが使用するDify Knowledge APIのインターフェース仕様を定義します。

---

## API エンドポイント

### 基本情報
- **ベースURL**: `{dify_url}` (設定ファイルで指定)
- **認証方式**: Bearer Token (API Key)
- **データ形式**: JSON
- **文字エンコーディング**: UTF-8

### 認証ヘッダー
```http
Authorization: Bearer {api_key}
Content-Type: application/json
Accept: application/json
```

---

## エンドポイント仕様

### 1. ドキュメント作成（テキストから）

**エンドポイント**: `POST /datasets/{dataset_id}/document/create-by-text`

**目的**: テキストコンテンツからDifyナレッジベースにドキュメントを作成

#### リクエスト
```http
POST /datasets/{dataset_id}/document/create-by-text
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "name": "string",                    # ドキュメント名（必須）
  "text": "string",                    # ドキュメントテキスト（必須）
  "indexing_technique": "string",      # インデックス手法（デフォルト: "high_quality"）
  "process_rule": {                    # 処理ルール（デフォルト: {"mode": "automatic"}）
    "mode": "automatic"
  },
  "doc_form": "string",               # ドキュメント形式（オプション）
  "doc_language": "string",           # ドキュメント言語（オプション）
  "retrieval_model": {                # 検索モデル設定（オプション）
    "search_method": "string",
    "reranking_enable": boolean,
    "reranking_model": "string",
    "top_k": integer,
    "score_threshold": number
  }
}
```

#### パラメータ詳細
- `dataset_id` (path): 対象データセットID
- `name`: ドキュメント名（日本語対応）
- `text`: ドキュメントのテキストコンテンツ（Markdown形式）
- `indexing_technique`: インデックス手法
  - `"high_quality"`: 高品質（デフォルト）
  - `"economy"`: エコノミー
- `process_rule.mode`: 処理モード
  - `"automatic"`: 自動（デフォルト）
  - `"custom"`: カスタム
- `process_rule.rules`: カスタムモード時の詳細設定（v2.2.0対応）
  - `segmentation`: チャンク分割設定
    - `separator`: 分割セパレータ
    - `max_tokens`: 最大トークン数（チャンク長）
    - `chunk_overlap`: オーバーラップサイズ

#### レスポンス（成功）
```json
{
  "document": {
    "id": "string",                   # ドキュメントID
    "name": "string",                 # ドキュメント名
    "character_count": integer,       # 文字数
    "tokens": integer,                # トークン数
    "indexing_latency": number,       # インデックス処理時間
    "completed_at": "string",         # 完了時刻（ISO 8601）
    "error": null,                    # エラー情報（正常時はnull）
    "enabled": boolean,               # 有効/無効状態
    "disabled_at": null,              # 無効化時刻
    "disabled_by": null,              # 無効化実行者
    "archived": boolean,              # アーカイブ状態
    "display_status": "string",       # 表示ステータス
    "word_count": integer,            # 単語数
    "hit_count": integer,             # ヒット回数
    "doc_form": "string"              # ドキュメント形式
  },
  "batch": "string"                   # バッチID
}
```

#### レスポンス（エラー）
```json
{
  "code": "string",                   # エラーコード
  "message": "string",                # エラーメッセージ
  "status": integer                   # HTTPステータスコード
}
```

### 2. 認証確認

**エンドポイント**: `GET /datasets/tags`

**目的**: API認証情報の有効性確認

#### リクエスト
```http
GET /datasets/tags
Authorization: Bearer {api_key}
```

#### レスポンス（成功）
```json
{
  "tags": [
    {
      "id": "string",
      "name": "string",
      "binding_count": integer
    }
  ]
}
```

### 3. データセット作成（オプション）

**エンドポイント**: `POST /datasets`

**目的**: 新しいデータセットの作成

#### リクエスト
```json
{
  "name": "string",                   # データセット名（必須）
  "description": "string"             # 説明（オプション）
}
```

#### レスポンス
```json
{
  "id": "string",                     # データセットID
  "name": "string",                   # データセット名
  "description": "string",            # 説明
  "permission": "string",             # 権限
  "data_source_type": "string",       # データソース種別
  "indexing_technique": "string",     # インデックス手法
  "app_count": integer,               # 関連アプリ数
  "document_count": integer,          # ドキュメント数
  "word_count": integer,              # 単語数
  "created_by": "string",             # 作成者
  "created_at": "string",             # 作成時刻
  "updated_by": "string",             # 更新者
  "updated_at": "string"              # 更新時刻
}
```

---

## v2.2.0 チャンク設定対応

### チャンク設定付きドキュメント作成
```http
POST /datasets/{dataset_id}/document/create-by-text
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "name": "ドキュメント名",
  "text": "ドキュメントのテキストコンテンツ...",
  "indexing_technique": "high_quality",
  "process_rule": {
    "mode": "custom",
    "rules": {
      "segmentation": {
        "separator": "\n\n",
        "max_tokens": 800,
        "chunk_overlap": 100
      }
    }
  },
  "doc_form": "text_model",
  "doc_language": "japanese"
}
```

### チャンク設定パラメータ
- `separator`: チャンク分割に使用するセパレータ文字列
  - デフォルト: `"\n\n"`
  - 有効値: `"\n"`, `"\n\n"`, `"."`, `"。"`, カスタム文字列
- `max_tokens`: 各チャンクの最大トークン数
  - デフォルト: `500`
  - 範囲: `50-8192`
- `chunk_overlap`: チャンク間のオーバーラップサイズ
  - デフォルト: `50`
  - 範囲: `0-max_tokens未満`

---

## エラーハンドリング

### HTTPステータスコード
- `200`: 成功
- `400`: 不正なリクエスト（パラメータエラー）
- `401`: 認証失敗（無効なAPI キー）
- `403`: 権限不足
- `404`: リソースが見つからない（無効なdataset_id）
- `429`: レート制限超過
- `500`: サーバー内部エラー

### リトライ戦略
- **対象ステータス**: 429, 500, 502, 503, 504
- **リトライ回数**: 最大3回
- **待機時間**: 指数バックオフ（2^試行回数 秒）
- **最大待機時間**: 8秒

### タイムアウト設定
- **接続タイムアウト**: 10秒
- **読み取りタイムアウト**: 10秒

---

## データ制限

### リクエスト制限
- **最大ファイルサイズ**: 50MB/ドキュメント
- **最大文字数**: 100万文字/ドキュメント
- **リクエスト頻度**: 10リクエスト/分（推奨）

### 文字エンコーディング
- **サポート**: UTF-8
- **日本語対応**: フル対応
- **特殊文字**: 絵文字、記号を含むUnicode文字をサポート

---

## 使用例

### 基本的なドキュメント作成
```python
client = DifyClient(base_url="https://api.dify.example.com/v1", 
                   api_key="dataset-xxxxxxxxxxxxxxxxxxxxx")

response = client.create_document_from_text(
    dataset_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    name="サンプルドキュメント",
    text="# タイトル\n\nこれはサンプルドキュメントです。",
    indexing_technique="high_quality"
)

print(f"ドキュメントID: {response['document']['id']}")
```

### 認証確認
```python
is_valid = client.verify_auth()
if not is_valid:
    raise Exception("API認証に失敗しました")
```

### エラーハンドリング付きの作成
```python
try:
    response = client.push_markdown(
        title="ドキュメントタイトル",
        markdown="# 見出し\n\n本文です。",
        metadata={"dataset_id": dataset_id},
        max_retries=3
    )
except requests.HTTPError as e:
    if e.response.status_code == 401:
        print("認証エラー: API キーを確認してください")
    elif e.response.status_code == 404:
        print("データセットが見つかりません")
    else:
        print(f"API エラー: {e.response.status_code}")
```

---

## セキュリティ考慮事項

### API キー管理
- 設定ファイルでの保存
- 環境変数での上書き対応
- ログへの出力禁止

### データ保護
- HTTPS通信必須
- リクエスト・レスポンスログでの機密情報マスキング
- タイムアウト設定による接続管理

### レート制限対応
- 適切な間隔でのリクエスト実行
- 429エラー時の自動待機
- 並行処理の制限

---

## バージョン履歴

### v2.0.0（現在）
- create_document_from_text エンドポイント対応
- 認証確認機能
- エラーハンドリングとリトライ機能

### v2.1.0（予定）
- ドキュメント更新API対応
- バッチ処理API対応
- メタデータ拡張対応
