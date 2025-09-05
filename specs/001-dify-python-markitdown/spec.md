

# Feature Specification: Difyナレッジ自動登録・更新バッチプログラム

**Feature Branch**: `001-dify-python-markitdown`
**Created**: 2025-09-05
**Status**: Completed ✅
**Input**: User description: "Difyのナレッジを登録・更新するバッチ処理プログラムを開発します。Python、markitdown、Dify APIを使用します。指定したフォルダのファイルをmarkdown形式に変換して、Difyのナレッジをバッチで登録・更新します。ファイル名、ファイルの内容には日本語が含まれます。設定ファイルでフォルダ、Dify URL、APIキー等の必要な情報を定義します。"


## Execution Flow (main)
```
1. ユーザー説明文（Input）をパース
   → 空の場合: ERROR "No feature description provided"
2. 説明文から主要な要素を抽出
   → アクター: 管理者/運用担当
   → アクション: ナレッジ登録・更新（バッチ処理）、ファイル変換
   → データ: 指定フォルダ内のファイル（日本語含む）、DifyナレッジDB
   → 制約: 日本語対応、API認証、設定ファイル必須、バッチ処理であること
3. 不明点があれば [NEEDS CLARIFICATION: 具体的な質問] で明示
4. ユーザーシナリオ＆テストケースを記述
   → 明確なユーザーフローがなければ ERROR "Cannot determine user scenarios"
5. 機能要件を生成
   → 各要件はテスト可能であること
   → 曖昧な要件は明示
6. 主要エンティティを特定（データが関与する場合）
7. レビューチェックリストを実施
   → [NEEDS CLARIFICATION]があれば WARN "Spec has uncertainties"
   → 実装詳細が含まれていれば ERROR "Remove tech details"
8. 完了: SUCCESS（計画フェーズへ進行可能）
```

---


---

## ユーザーシナリオ & テストケース

### Primary User Story
管理者/運用担当者が指定フォルダ内の多様な形式のドキュメントファイルを、Difyナレッジベースに一括登録するバッチ処理を実行する。さらに、ファイルの更新を検知して既存ドキュメントを更新し、変換したMarkdownファイルをバックアップとして保存する。

### Acceptance Scenarios
1. **Given** config.ymlで対象フォルダ・Dify URL・APIキー・dataset_idを設定済み、**When** `python -m src.cli.main` を実行、**Then** 指定フォルダ内の全対応ファイルがDifyナレッジベースに正常登録される
2. **Given** 日本語ファイル名・内容のファイルが対象フォルダに存在、**When** バッチ処理実行、**Then** 日本語が文字化けせずに正常処理される
3. **Given** 無効なAPI認証情報でconfig.yml設定、**When** バッチ処理実行、**Then** 認証エラーが適切にログ出力される
4. **Given** 変換できないファイル形式が混在、**When** バッチ処理実行、**Then** 対応ファイルのみ処理され、未対応ファイルはスキップされる
5. **Given** 過去に処理済みのファイルが更新されている、**When** バッチ処理実行、**Then** ファイル更新を検知してDifyドキュメントが更新される
6. **Given** backup_folderが設定済み、**When** ファイル変換実行、**Then** 変換済みMarkdownがバックアップフォルダに保存される
7. **Given** サブフォルダ内のファイルを処理、**When** バックアップ実行、**Then** バックアップフォルダにも同じサブフォルダ構造が作成される
8. **Given** バックアップファイル名の重複、**When** 同一ファイルを複数回処理、**Then** yyyymmddhhmiss形式のタイムスタンプで区別される

### Edge Cases
- API接続エラー時のリトライ処理（最大3回、指数バックオフ）
- 大容量ファイルの処理制限
- 同一ファイル名の重複処理防止
- ログファイルのローテーション処理
- ファイル更新検知の判定基準（更新日時・ファイルサイズ・ハッシュ値）
- バックアップフォルダの容量制限・古いバックアップの自動削除
- サブフォルダ階層の深さ制限
- バックアップファイル名の文字数制限

## 機能要件

### Functional Requirements
- **FR-001**: システムはYAML形式の設定ファイル（config.yml）で、input_folder、dify_url、api_key、dataset_id、log_dir、file_extensionsを指定できること
- **FR-002**: システムは指定フォルダ配下を再帰的に探索し、以下の拡張子のファイルをMarkdown形式に変換できること：.md、.txt、.docx、.xlsx、.pdf、.pptx、.ppt、.xls、.doc、.xlsm
- **FR-003**: システムは変換後の内容をDify API v1のcreate_document_from_textエンドポイント経由で、指定dataset_idのナレッジベースに一括登録できること
- **FR-004**: システムはファイル名・内容に日本語が含まれても文字化けせずに正しく処理できること
- **FR-005**: システムはAPI認証エラー、ファイル変換失敗、ネットワークエラー時に適切なエラーハンドリングとリトライ処理（最大3回）を実行すること
- **FR-006**: システムはJSON形式の詳細ログを./logディレクトリに時系列で出力し、処理状況・エラー内容を記録できること
- **FR-007**: システムは認証確認機能（verify_auth）でDify APIキーの有効性を事前検証できること
- **FR-008**: システムは変換時にファイルのメタデータ（title等）を抽出し、Difyドキュメントに付与できること
- **FR-009**: システムはファイルの更新検知機能（更新日時・ファイルサイズ）により、変更されたファイルのみDifyドキュメントを更新できること
- **FR-010**: システムは変換したMarkdownファイルをconfig.ymlで指定されたbackup_folderにバックアップ保存できること
- **FR-011**: システムはバックアップ時に元ファイルのサブフォルダ構造を保持し、バックアップフォルダにも同じ階層を作成できること
- **FR-012**: システムはバックアップファイル名を「元ファイル名+yyyymmddhhmiss.md」形式で生成し、同一ファイルの複数バックアップを区別できること
- **FR-013**: システムはファイル更新状態を管理するメタデータ（最終処理日時、ファイルサイズ、ハッシュ値等）を保存・参照できること

### Key Entities
- **Config**: YAML設定ファイル（input_folder、dify_url、api_key、dataset_id、log_dir、file_extensions、backup_folder）
- **SourceFile**: 変換対象ファイル（日本語ファイル名・内容対応、10種類の拡張子サポート、更新検知メタデータ付き）
- **ConvertedDocument**: Markdown変換済みドキュメント（メタデータ付き）
- **DifyDocument**: Difyナレッジベース登録済みドキュメント（dataset_id指定）
- **ProcessLog**: JSON形式の処理ログ（時系列、成功/失敗状況記録）
- **FileMetadata**: ファイル更新検知用メタデータ（最終処理日時、ファイルサイズ、更新日時）
- **BackupFile**: バックアップ済みMarkdownファイル（タイムスタンプ付きファイル名、サブフォルダ構造保持）

## 解消済み要件詳細

### 変換対象ファイル形式（解決済み）
以下10種類の拡張子をサポート：
- テキスト系: .md（Markdown）、.txt（プレーンテキスト）
- Microsoft Office: .docx/.doc（Word）、.xlsx/.xlsm/.xls（Excel）、.pptx/.ppt（PowerPoint）
- その他: .pdf（PDF文書）

### Dify API仕様（解決済み）
- API バージョン: v1
- エンドポイント: POST /datasets/{dataset_id}/document/create_by_text
- エラー時リトライ: 最大3回、指数バックオフ（1秒、2秒、4秒）
- 必須パラメータ: indexing_technique="high_quality", process_rule={}

### 設定ファイル形式（解決済み）
YAML形式（config.yml）で以下の項目を設定：
```yaml
input_folder: ./data
dify_url: http://example.com/v1
api_key: dataset-xxxxxxxxxxxxx
dataset_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
log_dir: ./log
backup_folder: ./backup
file_extensions: [.md, .txt, .docx, .xlsx, .pdf, .pptx, .ppt, .xls, .doc, .xlsm]
```

## レビューチェックリスト
- [x] WHAT/WHY中心でHOW（実装詳細）は含まれていないか
- [x] 曖昧な要件は解消されているか（[NEEDS CLARIFICATION]なし）
- [x] 各要件はテスト可能か
- [x] テンプレートのセクション順を守っているか
- [x] 実装完了済み機能との整合性が取れているか

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted  
- [x] Ambiguities resolved（全解消済み）
- [x] User scenarios defined
- [x] Requirements generated（実装ベース）
- [x] Entities identified
- [x] Review checklist passed
- [x] **Implementation completed & verified**

---

この仕様書は実装完了済みプロジェクトの正式仕様として確定されています。
**実装検証済み項目:**
- Dify API v1連携（dataset_id指定でのドキュメント登録）
- 10種類ファイル形式変換（日本語対応確認済み）
- YAML設定ファイル運用
- JSON形式ログ出力
- エラーハンドリング・リトライ機能
- 実環境での動作確認（3ファイル登録成功）

**追加機能開発予定:**
- ファイル更新検知機能（FR-009）✅ 完了
- Markdownバックアップ機能（FR-010〜FR-012）✅ 完了
- ファイルメタデータ管理（FR-013）✅ 完了

**v2.2.0 新機能要件（開発中）:**
- チャンク設定機能（FR-014〜FR-016）
- ログ出力拡張機能（FR-017〜FR-018）
- 組み込みメタデータ管理機能（FR-019〜FR-021）

### v2.2.0追加機能要件

#### Functional Requirements (v2.2.0)
- **FR-014**: システムはconfig.ymlでmax_chunk_length（最大チャンク長）とoverlap_size（オーバーラップサイズ）を指定可能であること
- **FR-015**: システムは指定されたチャンク設定をDify APIのprocess_rule.rules.segmentationパラメータとして送信できること
- **FR-016**: システムはチャンク設定値の妥当性検証（最小/最大値、オーバーラップ<チャンク長等）を実行できること
- **FR-017**: システムは更新対象外となったドキュメント（変更なし、処理スキップ）をログに詳細出力できること
- **FR-018**: システムは処理サマリーでprocessed/skipped/errorsの内訳を詳細表示できること
- **FR-019**: システムは組み込みメタデータ（document_name、uploader、upload_date、last_update_date、source）を自動生成できること
- **FR-020**: システムはメタデータテンプレートをconfig.ymlで設定可能であること
- **FR-021**: システムは生成されたメタデータをDifyドキュメントに付与できること

#### New Acceptance Scenarios (v2.2.0)
1. **Given** config.ymlでmax_chunk_length=1000、overlap_size=100を設定、**When** ドキュメント登録実行、**Then** 指定されたチャンク設定でDifyに登録される
2. **Given** overlap_size > max_chunk_lengthの不正設定、**When** バッチ処理実行、**Then** 設定検証エラーが出力される
3. **Given** 処理対象ファイルに変更なしファイルが含まれる、**When** バッチ処理実行、**Then** スキップファイルがログに詳細出力される
4. **Given** metadata_templateでuploaderを設定、**When** ドキュメント登録実行、**Then** 指定されたuploaderがメタデータとして付与される
5. **Given** 自動メタデータ生成設定、**When** ファイル処理実行、**Then** upload_date、last_update_date、sourceが自動生成される

#### Additional Key Entities (v2.2.0)
- **ChunkSettings**: チャンク設定（max_chunk_length、overlap_size、妥当性検証）
- **ProcessSummary**: 処理サマリー拡張（詳細内訳、スキップファイル一覧）
- **DocumentMetadata**: 組み込みメタデータ（document_name、uploader、upload_date、last_update_date、source）
- **MetadataTemplate**: メタデータテンプレート設定（config.yml設定可能）
