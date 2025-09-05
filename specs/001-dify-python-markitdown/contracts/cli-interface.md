# CLI インターフェース仕様

**Feature Branch**: `001-dify-python-markitdown`  
**Created**: 2025-09-05  
**Status**: Draft  
**Version**: 2.2.0

## 概要
本ドキュメントは、Difyナレッジ自動登録・更新バッチプログラムのコマンドラインインターフェース（CLI）仕様を定義します。

---

## コマンドライン引数

### 基本構文
```bash
python -m src.cli.main <config_file> [options]
```

### 必須引数
- `config_file`: 設定ファイルのパス（YAML または JSON 形式）

### オプション引数（v2.1.0予定）
- `--dry-run`: 実際の処理を実行せず、処理対象ファイルの一覧のみ表示
- `--force-update`: ファイル更新検知を無視してすべてのファイルを強制処理
- `--backup-only`: Dify登録を行わず、Markdownバックアップのみ実行
- `--verbose, -v`: 詳細ログ出力
- `--help, -h`: ヘルプメッセージ表示

### オプション引数（v2.2.0予定）
- `--chunk-settings`: チャンク設定を一時的にオーバーライド
- `--skip-summary`: 処理サマリーログの出力をスキップ
- `--metadata-only`: メタデータ生成のみ実行（Dify登録なし）
- `--show-skipped`: スキップしたファイルの詳細情報を表示

---

## 設定ファイル仕様

### 必須フィールド
```yaml
input_folder: string          # 入力ファイルフォルダパス
dify_url: string             # Dify APIベースURL  
api_key: string              # Dify API認証キー
dataset_id: string           # 対象データセットID
```

### オプションフィールド
```yaml
log_dir: string              # ログ出力ディレクトリ（デフォルト: "./log"）
file_extensions: string[]    # 対応ファイル拡張子リスト
backup_folder: string        # バックアップフォルダパス（v2.1.0）
chunk_settings: object      # チャンク分割設定（v2.2.0）
metadata_template: object   # メタデータテンプレート（v2.2.0）
```

### v2.2.0新機能フィールド
```yaml
# チャンク設定（v2.2.0）
chunk_settings:
  enabled: boolean           # チャンク設定の有効/無効
  max_chunk_length: integer  # 最大チャンク長（デフォルト: 500）
  overlap_size: integer      # オーバーラップサイズ（デフォルト: 50）
  separator: string          # 分割セパレータ（デフォルト: "\n\n"）
  segmentation_mode: string  # 分割モード（automatic/custom）

# メタデータテンプレート（v2.2.0）
metadata_template:
  enabled: boolean                    # メタデータ機能の有効/無効
  document_name_template: string      # ドキュメント名テンプレート
  uploader_default: string            # デフォルトアップロード者
  include_file_info: boolean          # ファイル情報含む
  include_processing_info: boolean    # 処理情報含む
  custom_fields: object               # カスタムフィールド
```

### サポートされるファイル拡張子（デフォルト）
```yaml
file_extensions:
  - .md      # Markdown
  - .txt     # テキスト
  - .docx    # Word文書
  - .xlsx    # Excel文書
  - .pdf     # PDF文書
  - .pptx    # PowerPoint文書
  - .ppt     # PowerPoint文書（旧形式）
  - .xls     # Excel文書（旧形式）
  - .doc     # Word文書（旧形式）
  - .xlsm    # Excelマクロ有効文書
```

### 設定ファイル例
```yaml
# config.yml
input_folder: ./data
dify_url: https://api.dify.example.com/v1
api_key: dataset-xxxxxxxxxxxxxxxxxxxxx
dataset_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
log_dir: ./log
backup_folder: ./backup  # v2.1.0
file_extensions:
  - .md
  - .txt
  - .docx
  - .xlsx
  - .pdf

# v2.2.0新機能設定例
chunk_settings:
  enabled: true
  max_chunk_length: 800
  overlap_size: 100
  separator: "\n\n"
  segmentation_mode: "custom"

metadata_template:
  enabled: true
  document_name_template: "{file_name}_v{version}"
  uploader_default: "DifyRagMnger"
  include_file_info: true
  include_processing_info: true
  custom_fields:
    category: "knowledge_base"
    language: "ja"
```

---

## 実行例

### 基本的な実行
```bash
python -m src.cli.main config.yml
```

### 詳細ログ付き実行（v2.1.0予定）
```bash
python -m src.cli.main config.yml --verbose
```

### v2.2.0新機能の実行例
```bash
# チャンク設定オーバーライド
python -m src.cli.main config.yml --chunk-settings "max_chunk_length=1000,overlap_size=100"

# スキップファイル詳細表示
python -m src.cli.main config.yml --show-skipped

# メタデータ生成のみ
python -m src.cli.main config.yml --metadata-only

# 処理サマリーなし
python -m src.cli.main config.yml --skip-summary
```

### ドライラン実行（v2.1.0予定）
```bash
python -m src.cli.main config.yml --dry-run
```

### バックアップのみ実行（v2.1.0予定）
```bash
python -m src.cli.main config.yml --backup-only
```

---

## 終了コード

| コード | 意味 | 説明 |
|--------|------|------|
| 0 | 成功 | すべてのファイルが正常に処理された |
| 1 | 部分的失敗 | 一部のファイル処理でエラーが発生したが、処理は継続された |
| 2 | 設定エラー | 設定ファイルまたは引数に問題がある |
| 3 | 認証エラー | Dify API認証に失敗した |
| 4 | システムエラー | ファイルアクセスやその他のシステムレベルエラー |

---

## ログ出力

### ログファイル形式
- **ファイル名**: `log/job-{timestamp}.log`
- **形式**: JSON Lines（1行1JSON）
- **エンコーディング**: UTF-8

### ログレベル
- `INFO`: 正常な処理の進行状況
- `WARNING`: 警告（処理は継続）
- `ERROR`: エラー（個別ファイルの処理失敗）
- `DEBUG`: デバッグ情報（--verboseオプション時のみ）

### ログエントリ例
```json
{"timestamp": "2025-09-05T14:30:22.123456", "level": "INFO", "job_id": "job-1725514222", "event": "started", "message": "Batch processing started", "config_file": "config.yml"}
{"timestamp": "2025-09-05T14:30:22.234567", "level": "INFO", "job_id": "job-1725514222", "event": "file_discovered", "path": "./data/sample.md", "size": 1024}
{"timestamp": "2025-09-05T14:30:22.345678", "level": "INFO", "job_id": "job-1725514222", "event": "converted", "path": "./data/sample.md", "title": "Sample Document"}
{"timestamp": "2025-09-05T14:30:22.456789", "level": "INFO", "job_id": "job-1725514222", "event": "uploaded", "path": "./data/sample.md", "dify_document_id": "doc-xxxxx"}
{"timestamp": "2025-09-05T14:30:25.567890", "level": "INFO", "job_id": "job-1725514222", "event": "summary", "successes": 5, "failures": 1, "total_files": 6}
```

---

## エラーハンドリング

### 設定ファイルエラー
- ファイルが存在しない場合: 終了コード 2
- YAML/JSON構文エラー: 終了コード 2
- 必須フィールド不足: 終了コード 2

### 認証エラー
- 無効なAPI キー: 終了コード 3
- ネットワークエラー: 終了コード 3
- dataset_id が無効: 終了コード 3

### ファイル処理エラー
- 読み取り不可ファイル: 警告ログ、処理継続
- 変換失敗: 警告ログ、処理継続
- Dify登録失敗: エラーログ、処理継続

### システムエラー
- input_folder が存在しない: 終了コード 4
- ログディレクトリ作成失敗: 終了コード 4
- メモリ不足: 終了コード 4

---

## パフォーマンス仕様

### 処理能力
- **ファイル数**: 最大 1,000 ファイル/実行
- **ファイルサイズ**: 最大 50MB/ファイル
- **同時処理**: シーケンシャル処理（APIレート制限考慮）
- **メモリ使用量**: 最大 500MB

### タイムアウト設定
- **Dify API**: 10秒/リクエスト
- **ファイル読み込み**: 30秒/ファイル
- **変換処理**: 60秒/ファイル

---

## セキュリティ考慮事項

### 認証情報
- API キーは設定ファイルで管理
- 環境変数での上書き対応（v2.1.0予定）
- ログにAPI キーが出力されないよう配慮

### ファイルアクセス
- input_folder 配下のファイルのみアクセス
- シンボリックリンクは辿らない
- 隠しファイル（.で始まるファイル）はスキップ

---

## バージョン履歴

### v2.0.0（現在）
- 基本的なCLIインターフェース
- YAML/JSON設定ファイル対応
- 10種類のファイルフォーマット対応

### v2.1.0（予定）
- オプション引数追加（--dry-run, --force-update, --backup-only, --verbose）
- 環境変数対応
- ファイル更新検知機能
- Markdownバックアップ機能
