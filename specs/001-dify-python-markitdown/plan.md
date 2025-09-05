

# Implementation Plan: Difyナレッジ自動登録・更新バッチプログラム

**Branch**: `001-dify-python-markitdown` | **Date**: 2025-09-05 | **Spec**: [spec.md](spec.md)
**Status**: Implementation Completed ✅
**Input**: Feature specification from `/specs/001-dify-python-markitdown/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)


## Summary
Difyのナレッジを登録・更新するバッチ処理Pythonプログラムを開発する。指定フォルダ内の日本語ファイルを含む全ファイルをmarkdown形式に変換し、Dify API経由でナレッジとして一括登録・更新する。設定ファイルで対象フォルダ、Dify URL、APIキー等を指定可能。さらに、ファイル更新検知機能とMarkdownバックアップ機能を追加し、効率的な差分更新と履歴管理を実現する。


## Technical Context
**Language/Version**: Python 3.11  
**Primary Dependencies**: markitdown, requests, PyYAML, python-docx, openpyxl, pdfplumber, python-pptx, xlrd, python-frontmatter  
**Storage**: ファイルシステム（ローカル）、DifyナレッジDB（API経由、dataset_id指定）、バックアップストレージ（ローカル）  
**Testing**: pytest（unit/integration/E2Eテスト完備）  
**Target Platform**: Linux/WSL, Windows  
**Project Type**: single（CLIバッチ処理）  
**Performance Goals**: 10種類ファイル形式サポート、日本語ファイル処理、エラー時3回リトライ、差分更新による高速化  
**Constraints**: 日本語ファイル対応、API認証必須、YAML設定ファイル必須、バッチ処理であること  
**Log Destination**: 固定 `./log` ディレクトリ（JSON形式、時系列ログ）
**Backup Destination**: 設定可能 `backup_folder` ディレクトリ（Markdown形式、タイムスタンプ付き）
**Scale/Scope**: dataset_id単位でのバッチ処理、実運用検証済み（3ファイル登録成功）、追加機能開発中


## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**: ✅ **PASS**
- Projects: 1（cli+lib統合、テスト別、バッチ処理専用）
- フレームワーク直利用（requests, PyYAML, markitdown等を直接利用）
- データモデルは単一（config.yml、file entities、log entities）
- 不要なパターン禁止（Repository等は不使用、直接API呼び出し）

**Architecture**: ✅ **PASS**
- すべてライブラリ化（src/lib/配下にdify_client.py, converter.py, config.py, logging.py）
- CLI: src/cli/main.py（バッチエントリーポイント明確化）
- ドキュメント: README.md, OPERATION_GUIDE.md完備

**Testing (NON-NEGOTIABLE)**: ✅ **PASS**
- RED-GREEN-Refactorサイクル遵守済み
- Contract→Integration→E2E→Unit順実装済み
- 実Dify API利用テスト（モック不使用）
- バッチ処理の正常・異常系テスト完備

**Observability**: ✅ **PASS（拡張予定）**
- JSON構造化ログ（./logディレクトリ、時系列、進捗・エラー記録）
- エラー文脈十分（API エラー詳細、ファイル変換エラー詳細）
- ファイル更新検知ログ（変更検知、スキップ理由）
- バックアップ操作ログ（保存先、ファイルサイズ）

**Versioning**: ✅ **PASS（更新予定）**
- MAJOR.MINOR.BUILD形式（2.0.0 → 2.1.0）
- 新機能追加によるMINORバージョン増分
- 後方互換性維持（既存config.ymlも動作）

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

tests/
ios/ or android/
### Source Code (repository root) - **実装済み** ✅ **拡張予定**
```
src/
├── __init__.py
├── cli/
│   └── main.py              # バッチエントリーポイント
└── lib/
    ├── config.py            # YAML設定ファイル管理
    ├── converter.py         # 10種類ファイル形式変換
    ├── dify_client.py       # Dify API v1クライアント
    ├── logging.py           # JSON構造化ログ
    ├── file_tracker.py      # ファイル更新検知（新規）
    └── backup_manager.py    # バックアップ機能（新規）

tests/
├── integration/
│   └── test_cli_e2e.py      # E2Eテスト（実Dify API）
└── unit/
    ├── test_config.py       # 設定ファイルテスト
    ├── test_converter_*.py  # 変換機能テスト
    ├── test_dify_client.py  # API クライアントテスト
    ├── test_logging.py      # ログ機能テスト
    ├── test_file_tracker.py # ファイル更新検知テスト（新規）
    └── test_backup_manager.py # バックアップ機能テスト（新規）

# 設定・データ
config.yml                   # YAML設定ファイル（backup_folder追加）
data/                        # 変換対象ファイル
log/                         # JSON ログ出力先
backup/                      # Markdownバックアップ先（新規）
.file_metadata.json          # ファイル更新検知用メタデータ（新規）
```
config.yml                   # YAML設定ファイル
data/                        # 変換対象ファイル
log/                         # JSON ログ出力先
```

**Structure Decision**: ✅ **実装完了** - バッチ処理専用の単一プロジェクト構成（src/配下にcli, lib、tests/配下に各種テスト、バッチmainを明示）

## Phase 0: Outline & Research - **完了** ✅
1. ✅ Technical Context・spec.mdの[NEEDS CLARIFICATION]を抽出し、research.mdで調査完了
2. ✅ 依存技術・API・日本語ファイル対応・テスト方針・パフォーマンス目標等のベストプラクティス調査完了
3. ✅ research.mdに「決定事項・理由・代替案」を記載し、全不明点を解消済み

**Output**: ✅ research.md（全NEEDS CLARIFICATION解消済み）


## Phase 1: Design & Contracts - **完了** ✅ **拡張予定**
*Prerequisites: research.md complete*

1. ✅ spec.mdから主要エンティティ（Config, SourceFile, ConvertedDocument, DifyDocument, ProcessLog）を抽出し、実装で反映
2. ✅ 機能要件ごとにDify API v1利用、CLIインターフェース設計完了、実装済み
3. ✅ 各契約ごとにテスト（pytest形式）を作成完了（unit/integration/E2E）
4. ✅ ユーザーストーリーからintegrationテストシナリオ・quickstart.md作成済み
5. ✅ AI支援ファイル(.github/copilot-instructions.md)更新済み

**新機能拡張設計**:
6. 🔄 FileMetadata・BackupFileエンティティの追加設計
7. 🔄 file_tracker.py・backup_manager.pyの契約設計
8. 🔄 ファイル更新検知・バックアップのテストケース設計
9. 🔄 config.yml拡張（backup_folder設定）

**Output**: ✅ 実装反映済み、包括的テスト完備、README.md/OPERATION_GUIDE.md完備 + 🔄 新機能設計


## Phase 2: Task Planning Approach - **完了** ✅
*実装により代替完了*

**実装されたタスク**:
- ✅ Config管理（config.py）→YAMLパーサー実装
- ✅ ファイル変換（converter.py）→10種類ファイル形式対応
- ✅ Dify API連携（dify_client.py）→dataset_id指定でのドキュメント登録
- ✅ ログ機能（logging.py）→JSON構造化ログ
- ✅ CLIエントリーポイント（main.py）→バッチ処理実装
- ✅ 包括的テスト（tests/）→unit/integration/E2E完備

**実装順序**: TDD順（テスト→実装）、依存順（lib→cli）で完了


## Phase 3+: Implementation Status - **完了** ✅ **拡張実装中** 🔄

**Phase 3**: ✅ タスク実行完了（実装により代替）
**Phase 4**: ✅ 実装完了（憲法原則順守、全機能実装）
**Phase 5**: ✅ 検証完了（テスト・quickstart.md・実環境検証）
**Additional**: ✅ 追加フォーマット対応（.pdf, .pptx, .ppt, .xls, .doc, .xlsm）

**新機能実装フェーズ**:
**Phase 4.1**: ✅ ファイル更新検知機能実装完了
- file_tracker.py作成（ファイル更新検知ロジック）
- .file_metadata.json管理機能
- 差分更新ロジック

**Phase 4.2**: ✅ バックアップ機能実装完了
- backup_manager.py作成（Markdownバックアップ）
- サブフォルダ構造保持機能
- タイムスタンプ付きファイル名生成

**Phase 4.3**: ✅ 統合・テスト完了
- main.py統合（新機能組み込み）
- config.yml拡張（backup_folder追加）
- 包括的テスト実行

**v2.2.0新機能実装フェーズ**:
**Phase 5.1**: 🔄 チャンク設定機能実装
- config.yml拡張（chunk_settings設定）
- DifyClient拡張（process_rule.segmentationパラメータ）
- 設定値検証機能

**Phase 5.2**: 🔄 ログ出力拡張機能実装
- ログイベント拡張（file_skipped、processing_summary）
- スキップ理由詳細化機能
- 処理サマリー拡張

**Phase 5.3**: 🔄 組み込みメタデータ管理機能実装
- DocumentMetadataクラス作成
- config.yml拡張（metadata_template設定）
- メタデータ自動生成・Dify連携

**Phase 5.4**: 🔄 統合・検証・v2.2.0リリース
- 全機能統合テスト
- パフォーマンス検証
- ドキュメント更新・リリース準備


## Complexity Tracking
*憲法チェックで逸脱があれば理由を記載*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|




## Progress Tracking
*このチェックリストは進捗に応じて更新*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) ✅
- [x] Phase 1: Design complete (/plan command) ✅
- [x] Phase 2: Task planning complete (実装により代替) ✅
- [x] Phase 3: Tasks generated (実装により代替) ✅
- [x] Phase 4: Implementation complete ✅
- [x] Phase 5: Validation passed ✅
- [x] **Additional**: 追加ファイルフォーマット対応完了 ✅

**新機能開発フェーズ**:
- [x] **Phase 0.2**: 新機能仕様策定完了 ✅
- [x] **Phase 1.2**: 新機能設計完了 ✅
- [x] **Phase 4.1**: ファイル更新検知機能実装完了 ✅
- [x] **Phase 4.2**: バックアップ機能実装完了 ✅
- [x] **Phase 4.3**: 統合・テスト実行完了 ✅
- [x] **Phase 5.2**: 新機能検証・v2.1.0リリース完了 ✅

**v2.2.0開発フェーズ**:
- [x] **Phase 0.3**: v2.2.0仕様策定完了 ✅
- [x] **Phase 1.3**: v2.2.0設計開始 ✅
- [ ] **Phase 5.1**: チャンク設定機能実装
- [ ] **Phase 5.2**: ログ出力拡張機能実装
- [ ] **Phase 5.3**: 組み込みメタデータ管理機能実装
- [ ] **Phase 5.4**: 統合・検証・v2.2.0リリース

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved ✅
- [x] Complexity deviations documented (なし) ✅
- [x] **New Feature Specification**: PASS ✅

**実装検証済み機能**:
- [x] Dify API v1連携（dataset_id指定ドキュメント登録）
- [x] 10種類ファイル形式変換（日本語対応）
- [x] YAML設定ファイル運用
- [x] JSON構造化ログ出力
- [x] エラーハンドリング・リトライ機能
- [x] 実環境動作確認（3ファイル登録成功）

**新機能開発計画**:
- [x] ファイル更新検知機能（FR-009）✅ v2.1.0完了
- [x] Markdownバックアップ機能（FR-010〜FR-012）✅ v2.1.0完了
- [x] ファイルメタデータ管理（FR-013）✅ v2.1.0完了

**v2.2.0新機能開発計画**:
- [ ] チャンク設定機能（FR-014〜FR-016）
- [ ] ログ出力拡張機能（FR-017〜FR-018）
- [ ] 組み込みメタデータ管理機能（FR-019〜FR-021）

## v2.2.0 Implementation Phases

### Phase 5.1: チャンク設定機能実装
**技術要件**:
- config.yml拡張: `chunk_settings`セクション追加（max_chunk_length、overlap_size）
- DifyClient拡張: process_rule.rules.segmentationパラメータ対応
- 設定値検証: 範囲チェック、相互制約検証（overlap < chunk_length等）
- 後方互換性: 既存config.ymlも動作（デフォルト値設定）

**実装順序**:
1. config.py拡張（ChunkSettingsクラス追加）
2. DifyClient.create_document_from_text拡張（チャンク設定パラメータ）
3. 設定値検証ロジック実装
4. ユニットテスト作成（設定値検証、API連携）
5. 統合テスト作成（実際のチャンク分割確認）

### Phase 5.2: ログ出力拡張機能実装
**技術要件**:
- ログイベント拡張: file_skipped、processing_summary_detailedイベント追加
- スキップ理由詳細化: no_change、validation_error、processing_error等
- 処理サマリー拡張: processed/skipped/errorsの詳細内訳
- ログ構造化: 既存JSON形式との互換性維持

**実装順序**:
1. logging.py拡張（新ログイベント追加）
2. main.py拡張（スキップファイル記録、詳細サマリー）
3. file_tracker.py拡張（スキップ理由の詳細化）
4. ユニットテスト作成（ログ出力確認）
5. 統合テスト作成（スキップシナリオ確認）

### Phase 5.3: 組み込みメタデータ管理機能実装
**技術要件**:
- DocumentMetadataクラス設計: document_name、uploader、upload_date、last_update_date、source
- config.yml拡張: metadata_templateセクション追加
- メタデータ自動生成: ファイル情報・システム情報から動的生成
- DifyClient統合: メタデータ付きドキュメント登録

**実装順序**:
1. DocumentMetadataクラス実装（メタデータ生成ロジック）
2. config.py拡張（metadata_template設定読込）
3. DifyClient拡張（メタデータパラメータ対応）
4. main.py統合（メタデータ生成・付与）
5. ユニットテスト作成（メタデータ生成確認）
6. 統合テスト作成（Difyメタデータ連携確認）

### Phase 5.4: 統合・検証・リリース
**技術要件**:
- 全機能統合テスト: チャンク設定とメタデータの組み合わせ
- パフォーマンス検証: 大容量ファイルでのチャンク分割性能
- 後方互換性確認: 既存設定ファイルでの動作
- ドキュメント更新: README.md、OPERATION_GUIDE.md、config.ymlテンプレート

**実装順序**:
1. 全機能統合（config.yml最終形、main.py完全統合）
2. 包括的テスト実行（unit/integration/E2E）
3. 実環境検証（実際のDify環境でのテスト）
4. パフォーマンス測定（処理時間、メモリ使用量）
5. ドキュメント更新（ユーザーガイド、設定例）
6. v2.2.0リリース準備

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*