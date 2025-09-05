# クイックスタートガイド

**Feature Branch**: `001-dify-python-markitdown`  
**Created**: 2025-09-05  
**Status**: Draft  
**Version**: 2.2.0

## 🚀 5分で始めるDifyナレッジ自動登録

このガイドに従って、DifyRagMngerを素早くセットアップし、最初のバッチ処理を実行できます。

---

## 📋 前提条件

### 必要な環境
- **Python**: 3.11以上
- **Dify**: アクセス可能なDifyサーバー
- **OS**: Windows, macOS, Linux

### 必要な情報
- Dify APIベースURL（例: `https://api.dify.example.com/v1`）
- Dify API キー（例: `dataset-xxxxxxxxxxxxxxxxxxxxx`）
- Dataset ID（例: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`）

---

## ⚡ クイックスタート（5ステップ）

### ステップ 1: プロジェクトのセットアップ

```bash
# プロジェクトディレクトリに移動
cd DifyRagMnger

# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# Windows
venv\\Scripts\\activate
# macOS/Linux
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### ステップ 2: テストファイルの準備

```bash
# データフォルダの作成
mkdir data

# サンプルファイルの作成
echo "# テストドキュメント\n\nこれはテスト用のMarkdownドキュメントです。" > data/test.md
echo "これはテスト用のテキストファイルです。" > data/test.txt
```

### ステップ 3: 設定ファイルの作成

`config.yml` ファイルを作成して、以下の内容を記入します：

```yaml
# config.yml（基本設定）
input_folder: ./data
dify_url: https://api.dify.example.com/v1  # あなたのDify URL
api_key: dataset-xxxxxxxxxxxxxxxxxxxxx     # あなたのAPI キー
dataset_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  # あなたのDataset ID
log_dir: ./log
file_extensions:
  - .md
  - .txt
  - .docx
  - .xlsx
  - .pdf
  - .pptx
  - .ppt
  - .xls
  - .doc
  - .xlsm

# v2.2.0新機能（オプション）
chunk_settings:
  enabled: true                    # チャンク設定の有効化
  max_chunk_length: 800           # 最大チャンク長
  overlap_size: 100               # オーバーラップサイズ
  separator: "\n\n"               # 分割セパレータ
  segmentation_mode: "custom"     # 分割モード

metadata_template:
  enabled: true                    # メタデータ機能の有効化
  document_name_template: "{file_name}_知識ベース"
  uploader_default: "DifyRagMnger"
  include_file_info: true
  include_processing_info: true
  custom_fields:
    category: "knowledge_base"
    language: "ja"
```

**⚠️ 重要**: `dify_url`、`api_key`、`dataset_id`を実際の値に置き換えてください。

### ステップ 4: 認証テストの実行

設定が正しいかテストします：

```bash
# 認証テスト用のシンプルなスクリプト
python test_auth.py
```

### ステップ 5: バッチ処理の実行

```bash
# バッチ処理を実行
python -m src.cli.main config.yml
```

成功すると以下のようなメッセージが表示されます：

```
✅ 処理完了: 2ファイル成功, 0ファイル失敗
📁 ログファイル: ./log/job-1725514222.log
```

---

## 📊 実行結果の確認

### ログファイルの確認
```bash
# 最新のログファイルを表示
cat log/job-*.log | tail -10
```

### Difyナレッジベースの確認
1. Dify Webインターフェースにアクセス
2. 指定したDatasetを開く
3. アップロードされたドキュメントを確認

---

## 🔧 基本的な設定カスタマイズ

### 対象ファイル形式の変更
```yaml
file_extensions:
  - .md    # Markdownのみ処理したい場合
  - .txt
```

### 異なるフォルダの指定
```yaml
input_folder: /path/to/your/documents
log_dir: /path/to/your/logs
```

### バックアップ機能の有効化（v2.1.0）
```yaml
backup_folder: ./backup  # 変換済みMarkdownのバックアップ先
```

---

## 🛠️ よくある問題と解決方法

### 問題 1: 認証エラー
```
ERROR: API 認証に失敗しました
```

**解決方法:**
1. `api_key` が正しいか確認
2. `dify_url` がDifyサーバーのURLと一致するか確認
3. ネットワーク接続を確認

### 問題 2: Dataset ID エラー
```
ERROR: Dataset not found
```

**解決方法:**
1. `dataset_id` が正しいか確認
2. 指定したDatasetへのアクセス権限があるか確認

### 問題 3: ファイル変換エラー
```
WARNING: ファイル変換に失敗しました: sample.pdf
```

**解決方法:**
1. ファイルが破損していないか確認
2. 必要なライブラリがインストールされているか確認
3. ファイルがロックされていないか確認

### 問題 4: 文字化け
```
WARNING: 文字エンコーディングエラー
```

**解決方法:**
1. ファイルがUTF-8エンコーディングか確認
2. 日本語Windows環境では `chcp 65001` を実行

---

## 📈 本格運用への移行

### 大量ファイル処理の準備
```yaml
# 大量ファイル向けの設定例
input_folder: /documents/knowledge_base
log_dir: /logs/dify_batch
file_extensions:
  - .md
  - .docx
  - .pdf
```

### 定期実行の設定
```bash
# Cronでの定期実行例（毎日午前2時）
0 2 * * * cd /path/to/DifyRagMnger && python -m src.cli.main config.yml
```

### 処理結果の監視
```bash
# ログファイルの監視
tail -f log/job-*.log

# 成功/失敗の統計
grep '"event": "summary"' log/job-*.log | tail -5
```

---

## 🔄 バージョン2.1.0の新機能（実装済み）

### ファイル更新検知
- 前回処理時からファイルが変更されていない場合は自動スキップ
- ハッシュ値による変更検知
- メタデータファイル（`.file_metadata.json`）による履歴管理

### Markdownバックアップ機能
- 変換済みMarkdownの自動バックアップ
- サブフォルダ構造の保持
- タイムスタンプ付きファイル名

---

## 🆕 バージョン2.2.0の新機能（計画中）

### チャンク設定機能
**目的**: Difyでのドキュメント分割を細かく制御

**使用方法**:
```yaml
chunk_settings:
  enabled: true
  max_chunk_length: 800       # 長いドキュメント向け
  overlap_size: 100           # 前後の文脈保持
  separator: "\n\n"           # 段落単位での分割
  segmentation_mode: "custom" # カスタム分割設定
```

**効果**:
- 検索精度の向上
- 大容量ドキュメントの効率的処理
- 用途に応じた柔軟な分割設定

### メタデータ自動付与機能
**目的**: ドキュメントの追跡性と管理性向上

**使用方法**:
```yaml
metadata_template:
  enabled: true
  document_name_template: "{file_name}_v{timestamp}"
  uploader_default: "knowledge_manager"
  include_file_info: true     # ファイルサイズ、拡張子等
  include_processing_info: true # 処理日時、バージョン等
  custom_fields:
    department: "research"
    classification: "public"
```

**自動生成されるメタデータ**:
- `document_name`: カスタマイズ可能なドキュメント名
- `uploader`: アップロード者名
- `upload_date`: アップロード日時
- `last_update_date`: 最終更新日時  
- `source`: 元ファイルパス
- `file_size`: ファイルサイズ
- `file_extension`: ファイル拡張子
- `processing_version`: 処理プログラムバージョン

### 拡張ログ機能
**目的**: より詳細な処理状況の把握

**新機能**:
- スキップファイルの理由詳細出力
- 処理サマリーの自動生成
- エラー種別の分類と集計

**実行例**:
```bash
# スキップファイル詳細表示
python -m src.cli.main config.yml --show-skipped

# 処理サマリーのみ表示
python -m src.cli.main config.yml --verbose | grep summary
```

**サマリー出力例**:
```json
{
  "event": "process_summary",
  "total_files": 25,
  "processed_files": 20,
  "skipped_files": 3,
  "error_files": 2,
  "execution_time": 45.2,
  "skipped_reasons": {
    "no_changes_detected": 2,
    "unsupported_format": 1
  },
  "error_summary": {
    "conversion_error": 1,
    "upload_error": 1
  }
}
```
```bash
# 変更されたファイルのみ処理
python -m src.cli.main config.yml  # 自動的に変更検知
```

### ドライラン実行
```bash
# 実際の処理をせずに対象ファイルを確認
python -m src.cli.main config.yml --dry-run
```

### バックアップ機能
```bash
# 変換済みMarkdownのバックアップ
python -m src.cli.main config.yml --backup-only
```

---

## 📚 さらに詳しく

### ドキュメント
- [仕様書](./spec.md) - 詳細な機能仕様
- [設計書](./plan.md) - 技術設計とアーキテクチャ
- [データモデル](./data-model.md) - データ構造の詳細
- [API仕様](./contracts/) - インターフェース定義

### 高度な使用方法
- [運用ガイド](../../OPERATION_GUIDE.md) - 本格運用のベストプラクティス
- [トラブルシューティング](../../README.md#troubleshooting) - 詳細な問題解決方法

### 開発者向け
- [コントリビューションガイド](../../README.md#contributing) - 開発への参加方法
- [テスト実行方法](../../README.md#testing) - テストスイートの実行

---

## 🎯 次のステップ

1. **基本動作確認**: このガイドでバッチ処理を実行
2. **実際のデータでテスト**: 小規模なファイルセットで試用
3. **設定の最適化**: 環境に合わせた設定調整
4. **定期実行の設定**: 自動化のためのスケジュール設定
5. **監視体制の構築**: ログ監視とアラート設定

---

**🚀 準備完了！Difyナレッジベースの自動化を始めましょう！**
