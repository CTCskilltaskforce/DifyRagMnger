# DifyRagMnger

Difyナレッジベースの自動登録・更新バッチ処理プログラム

## 概要

DifyRagMngerは、指定したフォルダ内のファイルを自動的にDifyナレッジベースに登録・更新するPythonバッチプログラムです。様々なファイル形式をMarkdown形式に変換し、Dify APIを通じてナレッジベースに一括登録することができます。

### 主な機能

- 📁 **多様なファイル形式のサポート**: .md、.txt、.docx、.xlsx、.pdf、.pptx、.ppt、.xls、.doc、.xlsm形式のファイルを自動変換
- 🌏 **日本語完全対応**: ファイル名・内容に日本語が含まれても正しく処理
- 🔄 **バッチ処理**: 指定フォルダ内のファイルを一括処理
- 📊 **詳細なログ出力**: 処理状況を時系列でログファイルに出力
- ⚙️ **設定ファイル**: YAML形式の設定ファイルで柔軟な設定が可能
- 🔐 **認証対応**: Dify API認証をサポート
- 🧩 **チャンク設定**: カスタマイズ可能な文書分割設定（文字数・オーバーラップサイズ）
- 🔍 **ファイル更新検知**: SHA256ハッシュベースの変更検知で効率的な処理
- 💾 **自動バックアップ**: 変換前ファイルの安全な保存

## 必要環境

- Python 3.11以上
- Difyサーバー（API Key必須）

## インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd DifyRagMnger
```

### 2. 仮想環境の作成（推奨）

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# または
.venv\\Scripts\\activate  # Windows
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 設定ファイルの準備

`config.yml` ファイルを作成し、以下の設定を行います：

```yaml
# 入力フォルダ（処理対象ファイルが含まれるフォルダ）
input_folder: ./data

# Dify APIの設定
dify_url: http://your-dify-server/v1
api_key: your-api-key-here
dataset_id: your-dataset-id  # 対象のナレッジベースID

# ログ出力先
log_dir: ./log

# バックアップ設定
backup_folder: ./backup

# チャンク設定（オプション）
chunk_settings:
  max_chunk_length: 4000  # 最大チャンク文字数（1-8192）
  overlap_size: 200       # オーバーラップサイズ（0-max_chunk_length）

# 処理対象のファイル拡張子
file_extensions:
  - .md
  - .txt
  - .docx
  - .xlsx
  - .pdf
  - .pptx
```

### 2. バッチ処理の実行

```bash
# 基本実行
python -m src.cli.main config.yml

# 強制実行（ファイル変更検知をスキップ）
python -m src.cli.main config.yml --force
```

### 3. 処理結果の確認

- 処理結果は `./log/YYYYMMDD/job-<timestamp>.log` に出力されます
- バックアップファイルは `./backup/` に保存されます
- 成功・失敗件数がサマリとして表示されます
- ファイルメタデータは `.file_metadata.json` で管理されます

## 設定項目詳細

| 項目 | 必須 | 説明 |
|------|------|------|
| `input_folder` | ✓ | 処理対象ファイルが含まれるフォルダパス |
| `dify_url` | ✓ | DifyサーバーのベースURL |
| `api_key` | ✓ | Dify API認証キー |
| `dataset_id` | ✓ | 対象のDifyナレッジベースID |
| `log_dir` | | ログ出力先ディレクトリ（デフォルト: ./log） |
| `backup_folder` | | バックアップ保存先ディレクトリ（デフォルト: ./backup） |
| `chunk_settings.max_chunk_length` | | 最大チャンク文字数（1-8192、デフォルト: 自動） |
| `chunk_settings.overlap_size` | | チャンクオーバーラップサイズ（0-max_chunk_length、デフォルト: 0） |
| `file_extensions` | | 処理対象ファイル拡張子リスト |

## サポートファイル形式

| 拡張子 | 形式 | 説明 |
|--------|------|------|
| `.md` | Markdown | そのまま処理 |
| `.txt` | プレーンテキスト | テキストとして処理 |
| `.docx` | Word文書 | markitdownで変換 |
| `.doc` | Word文書 (旧形式) | python-docxで変換 |
| `.xlsx` | Excel | openpyxlで変換 |
| `.xlsm` | Excel (マクロ付き) | openpyxlで変換 |
| `.xls` | Excel (旧形式) | xlrdで変換 |
| `.pdf` | PDF文書 | pdfplumberで変換 |
| `.pptx` | PowerPoint | python-pptxで変換 |
| `.ppt` | PowerPoint (旧形式) | python-pptxで変換 |

## ログ形式

処理ログはJSON形式で出力され、以下の情報が含まれます：

```json
{
  "ts": "2025-09-05T09:26:31.257761Z",
  "level": "INFO", 
  "logger": "dify_batch",
  "event": "uploaded",
  "path": "c:\\path\\to\\file.md",
  "response": {...}
}
```

## エラーハンドリング

- **認証エラー**: API Key、URL設定を確認してください
- **ファイル変換エラー**: サポートされていないファイル形式の場合はスキップされます
- **API通信エラー**: リトライ機能により自動的に再試行されます

## 開発者向け情報

### アーキテクチャ

```
src/
├── cli/           # CLIエントリポイント
│   └── main.py
├── lib/           # ライブラリ
│   ├── backup_manager.py  # バックアップ管理
│   ├── config.py          # 設定ファイル読み込み（チャンク設定含む）
│   ├── converter.py       # ファイル変換処理（10+フォーマット対応）
│   ├── dify_client.py     # Dify API クライアント（チャンク対応）
│   ├── file_tracker.py    # ファイル更新検知・メタデータ管理
│   └── logging.py         # ログ処理
└── tests/         # テストコード（82テスト）
    ├── unit/              # ユニットテスト
    └── integration/       # 統合テスト
```

### テスト実行

```bash
python -m pytest tests/ -v
```

### コードスタイル

プロジェクトでは以下のツールを使用しています：
- **pytest**: テストフレームワーク
- **型ヒント**: Python 3.11+ 対応

## ライセンス

本プロジェクトのライセンスについては、LICENSE ファイルを参照してください。

## 貢献

プルリクエストやイシューの報告を歓迎します。

## トラブルシューティング

### よくある問題

**Q: 認証エラーが発生する**
A: `config.yml` の `api_key` と `dify_url` が正しく設定されているか確認してください。

**Q: ファイルが処理されない**
A: `file_extensions` 設定と実際のファイル拡張子が一致しているか確認してください。

**Q: 日本語ファイル名でエラーが発生する**
A: システムの文字エンコーディング設定を UTF-8 に設定してください。

詳細なトラブルシューティング情報は、生成されたログファイルを確認してください。
