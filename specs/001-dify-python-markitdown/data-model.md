# データモデル設計: Difyナレッジ自動登録・更新バッチプログラム

**Feature Branch**: `001-dify-python-markitdown`  
**Created**: 2025-09-05  
**Status**: Draft  
**Version**: 2.2.0

## 目的
本ドキュメントは、Difyナレッジ自動登録・更新バッチプログラムのデータモデルを定義し、システム内で扱うデータ構造とその関係性を明確化することを目的とします。

---

## エンティティ概要

### 1. Configuration（設定）
システム動作に必要な設定情報を管理するエンティティ。

### 2. InputFile（入力ファイル）
変換対象となるファイルを表現するエンティティ。

### 3. ConvertedDocument（変換済みドキュメント）
変換処理後のMarkdownドキュメントを表現するエンティティ。

### 4. DifyDocument（Difyドキュメント）
Difyナレッジベースに登録されるドキュメントを表現するエンティティ。

### 5. ProcessingLog（処理ログ）
バッチ処理の実行履歴と結果を記録するエンティティ。

### 6. FileMetadata（ファイルメタデータ）- v2.1.0新機能
ファイル更新検知のためのメタデータを管理するエンティティ。

### 7. BackupFile（バックアップファイル）- v2.1.0新機能
変換済みMarkdownのバックアップを管理するエンティティ。

### 8. ChunkSettings（チャンク設定）- v2.2.0新機能
Difyドキュメントのチャンク分割設定を管理するエンティティ。

### 9. DocumentMetadata（ドキュメントメタデータ）- v2.2.0新機能
ドキュメントに付与される組み込みメタデータを管理するエンティティ。

### 10. MetadataTemplate（メタデータテンプレート）- v2.2.0新機能
ドキュメントメタデータの自動生成テンプレートを管理するエンティティ。

### 11. ProcessSummary（処理サマリー）- v2.2.0新機能
バッチ処理全体の実行サマリーを管理するエンティティ。

---

## 詳細エンティティ定義

### Configuration
```yaml
Configuration:
  input_folder: string          # 入力ファイルフォルダパス
  dify_url: string             # Dify APIベースURL
  api_key: string              # Dify API認証キー
  dataset_id: string           # 対象データセットID
  log_dir: string              # ログ出力ディレクトリ
  file_extensions: string[]    # 対応ファイル拡張子リスト
  backup_folder: string        # バックアップフォルダパス（v2.1.0）
  chunk_settings: object       # チャンク分割設定（v2.2.0）
  metadata_template: object    # メタデータテンプレート（v2.2.0）
```

**制約:**
- input_folder: 存在するディレクトリパスであること
- dify_url: 有効なHTTP/HTTPSURLであること
- api_key: 非空文字列であること
- dataset_id: Dify APIで有効なデータセットIDであること
- file_extensions: サポートされる拡張子のリスト（.md, .txt, .docx, .xlsx, .pdf, .pptx, .ppt, .xls, .doc, .xlsm）

### InputFile
```yaml
InputFile:
  file_path: string            # ファイルの絶対パス
  relative_path: string        # input_folderからの相対パス
  file_name: string            # ファイル名
  extension: string            # ファイル拡張子
  file_size: integer           # ファイルサイズ（バイト）
  last_modified: datetime      # 最終更新日時
  encoding: string             # ファイルエンコーディング
  is_supported: boolean        # 対応フォーマットかどうか
```

**制約:**
- file_path: 存在するファイルパスであること
- extension: Configuration.file_extensionsに含まれること（is_supported=trueの場合）
- encoding: UTF-8が推奨されるが、自動検出可能

### ConvertedDocument
```yaml
ConvertedDocument:
  source_file: InputFile       # 変換元ファイル
  markdown_content: string     # 変換後Markdownテキスト
  extracted_title: string      # 抽出されたタイトル
  metadata: object             # フロントマターメタデータ
  conversion_method: string    # 変換手法（markitdown, native, etc.）
  converted_at: datetime       # 変換実行日時
  content_hash: string         # コンテンツハッシュ値
```

**制約:**
- markdown_content: 非空文字列であること
- extracted_title: ファイル名またはMarkdownから抽出されたタイトル
- conversion_method: 使用した変換ライブラリ/手法を記録

### DifyDocument
```yaml
DifyDocument:
  document_id: string          # Dify内でのドキュメントID
  name: string                 # Difyでのドキュメント名
  content: string              # Difyに送信されたコンテンツ
  dataset_id: string           # 所属データセットID
  created_at: datetime         # Dify登録日時
  updated_at: datetime         # Dify更新日時
  source_path: string          # 元ファイルパス
  processing_status: string    # 処理ステータス（success, error, pending）
  error_message: string        # エラー時のメッセージ
```

**制約:**
- document_id: Dify APIから返される一意ID
- processing_status: enum値（success, error, pending）
- source_path: 追跡可能性のための元ファイル情報

### ProcessingLog
```yaml
ProcessingLog:
  job_id: string               # バッチジョブ識別子
  timestamp: datetime          # ログ記録日時
  level: string                # ログレベル（info, warning, error）
  event: string                # イベント種別
  message: string              # ログメッセージ
  file_path: string            # 対象ファイルパス（該当する場合）
  execution_time: float        # 実行時間（秒）
  additional_data: object      # 追加データ（JSON形式）
```

**制約:**
- job_id: 実行セッション単位での一意識別子
- level: enum値（info, warning, error, debug）
- event: 定義されたイベント種別（uploaded, error, converted, etc.）

### FileMetadata（v2.1.0新機能）
```yaml
FileMetadata:
  file_path: string            # ファイルの絶対パス
  last_processed: datetime     # 最終処理日時
  file_size: integer           # 最終処理時のファイルサイズ
  last_modified: datetime      # 最終処理時の更新日時
  content_hash: string         # 最終処理時のコンテンツハッシュ
  processing_status: string    # 最終処理結果（success, error, skipped）
  dify_document_id: string     # 対応するDifyドキュメントID
```

**制約:**
- file_path: 主キーとしての一意性
- processing_status: enum値（success, error, skipped）
- content_hash: ファイル内容の変更検知に使用

### BackupFile（v2.1.0新機能）
```yaml
BackupFile:
  source_file_path: string     # 元ファイルの絶対パス
  backup_file_path: string     # バックアップファイルの絶対パス
  backup_folder: string        # バックアップ先フォルダ
  relative_structure: string   # 元ファイルのサブフォルダ構造
  timestamp: string            # バックアップ時刻（yyyymmddhhmiss形式）
  created_at: datetime         # バックアップ作成日時
  file_size: integer           # バックアップファイルサイズ
```

**制約:**
- backup_file_path: 一意性が保証されること
- timestamp: yyyymmddhhmiss形式（例：20250905143022）
- relative_structure: input_folderからの相対フォルダパス

### ChunkSettings（v2.2.0新機能）
```yaml
ChunkSettings:
  max_chunk_length: integer    # 最大チャンク長（トークン数）
  overlap_size: integer        # チャンク間のオーバーラップサイズ
  separator: string            # チャンク分割セパレータ
  segmentation_mode: string    # 分割モード（automatic, custom）
  enabled: boolean             # チャンク設定の有効/無効
```

**制約:**
- max_chunk_length: 1-8192の範囲（デフォルト: 500）
- overlap_size: 0以上max_chunk_length未満（デフォルト: 50）
- segmentation_mode: enum値（automatic, custom）
- separator: 有効な文字列（デフォルト: "\n\n"）

### DocumentMetadata（v2.2.0新機能）
```yaml
DocumentMetadata:
  document_name: string        # ドキュメント名
  uploader: string             # アップロード者名
  upload_date: datetime        # アップロード日時
  last_update_date: datetime   # 最終更新日時
  source: string               # ファイルの元パス
  file_size: integer           # ファイルサイズ
  file_extension: string       # ファイル拡張子
  processing_version: string   # 処理プログラムバージョン
```

**制約:**
- document_name: 非空文字列であること
- uploader: システム設定またはデフォルト値
- upload_date: ISO 8601形式
- source: 追跡可能な元ファイルパス

### MetadataTemplate（v2.2.0新機能）
```yaml
MetadataTemplate:
  document_name_template: string    # ドキュメント名生成テンプレート
  uploader_default: string          # デフォルトアップロード者名
  include_file_info: boolean        # ファイル情報を含めるか
  include_processing_info: boolean  # 処理情報を含めるか
  custom_fields: object             # カスタムフィールド定義
```

**制約:**
- document_name_template: 変数展開可能なテンプレート文字列
- uploader_default: 非空文字列（デフォルト: "DifyRagMnger"）
- custom_fields: キー・値ペアのオブジェクト

### ProcessSummary（v2.2.0新機能）
```yaml
ProcessSummary:
  job_id: string               # バッチジョブ識別子
  total_files: integer         # 処理対象ファイル総数
  processed_files: integer     # 正常処理ファイル数
  skipped_files: integer       # スキップファイル数
  error_files: integer         # エラーファイル数
  execution_time: float        # 総実行時間（秒）
  start_time: datetime         # 処理開始時刻
  end_time: datetime           # 処理終了時刻
  skipped_reasons: object      # スキップ理由別集計
  error_summary: object        # エラー種別別集計
```

**制約:**
- total_files = processed_files + skipped_files + error_files
- execution_time: end_time - start_time
- skipped_reasons: 理由文字列をキーとした件数オブジェクト
- error_summary: エラー種別をキーとした件数オブジェクト

---

## データ関係性

### 処理フロー関係
```
InputFile → ConvertedDocument → DifyDocument
    ↓              ↓                ↓
FileMetadata → BackupFile → ProcessingLog
    ↓              ↓                ↓
ChunkSettings → DocumentMetadata → ProcessSummary
```

### 主要な関係性
1. **InputFile ⟷ FileMetadata**: 1対1関係。ファイル更新検知のメタデータ管理
2. **ConvertedDocument ⟷ BackupFile**: 1対1関係。変換済みMarkdownのバックアップ
3. **ConvertedDocument ⟷ DifyDocument**: 1対1関係。DifyAPIへの登録
4. **DifyDocument ⟷ ChunkSettings**: 多対1関係。チャンク設定の適用
5. **DifyDocument ⟷ DocumentMetadata**: 1対1関係。メタデータの付与
6. **ProcessingLog ⟷ ProcessSummary**: 多対1関係。ログの集約サマリー
7. **全エンティティ ⟷ ProcessingLog**: 1対多関係。処理履歴の記録

### 永続化方式
- **Configuration**: YAML設定ファイル（config.yml）
- **ChunkSettings**: YAML設定ファイル内（config.yml）
- **MetadataTemplate**: YAML設定ファイル内（config.yml）
- **FileMetadata**: JSON形式（.file_metadata.json）
- **BackupFile**: ファイルシステム（markdown形式）
- **ProcessingLog**: JSON Lines形式（log/job-{timestamp}.log）
- **ProcessSummary**: JSON Lines形式（ログファイル末尾）
- **InputFile, ConvertedDocument, DifyDocument, DocumentMetadata**: 処理時の一時的なメモリ管理

---

## バージョン履歴

### v2.0.0
- 基本的なバッチ処理機能のデータモデル
- 10種類のファイルフォーマット対応

### v2.1.0（実装済み）
- FileMetadataエンティティ追加（ファイル更新検知）
- BackupFileエンティティ追加（Markdownバックアップ）
- サブフォルダ構造保持機能

### v2.2.0（計画中）
- ChunkSettingsエンティティ追加（チャンク分割設定）
- DocumentMetadataエンティティ追加（組み込みメタデータ）
- MetadataTemplateエンティティ追加（メタデータテンプレート）
- ProcessSummaryエンティティ追加（処理サマリー機能）
- 拡張ログ出力機能（スキップ理由、詳細サマリー）

---

## 注意事項
- 日本語ファイル名・コンテンツに対応するため、すべての文字列フィールドでUTF-8エンコーディングを使用
- ファイルパスは可能な限り絶対パスで管理し、相対パスは追跡可能性のために併記
- エラー時の復旧を考慮し、処理状態の追跡を重視した設計
- v2.1.0の新機能は既存機能への後方互換性を保持
- v2.2.0の新機能は設定ファイルでの有効/無効切り替えが可能
- チャンク設定は既存のDify APIパラメータと整合性を保つ
- メタデータ機能は既存ドキュメントへの影響を最小化する設計
