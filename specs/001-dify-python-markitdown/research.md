# research.md — ログ仕様調査（バッチ処理向け）- v2.2.0対応

## 目的
本調査は、Difyナレッジ自動登録・更新バッチプログラムにおけるログ出力の粒度・形式・運用要件を定義し、v2.2.0新機能（拡張ログ、処理サマリー）の仕様を含めた包括的なログ仕様を策定するためのものです。

**調査ステータス**: ✅ **v2.1.0完了・実装済み** | 🚧 **v2.2.0計画中** 

## 要件（設計前提）- ✅ **実装済み**
- ✅ バッチ処理であるため、プロセス単位での進捗と各ファイルの処理結果（成功/失敗）を記録する。
- ✅ 日本語を含むファイル名・内容がログに含まれても文字化けしないこと（ensure_ascii=False対応）。
- ✅ 運用時に検索しやすい構造（JSON Lines）での出力をサポートする。
- ✅ 長期間の運用を想定し、ログローテーション（日次サブディレクトリ）を実装済み。
- ✅ エラー発生時に容易に原因追跡できるようにトレーシング情報（ファイルパス、エラーコード、スタックトレース）を出力する。

## 実装済みログ出力フォーマット ✅
- **フォーマット**: JSON Lines（1行=1イベント）- `JsonLinesFormatter`実装済み
- **文字エンコーディング**: UTF-8（ensure_ascii=False）
- **ログレベル**: INFO, WARN, ERROR, DEBUG
- **各イベント共通フィールド**:
  - `ts` (ISO8601 UTC形式: "2025-09-05T12:00:00.123456Z")
  - `level` (INFO/WARN/ERROR/DEBUG)
  - `logger` (ロガー名: e.g., "main", "converter", "dify_client")
  - `message` (human-readable, 日本語対応)
  - その他の構造化データ（辞書として直接マージ）

**実装例** (`src/lib/logging.py`):
```json
{"ts":"2025-09-05T09:26:31.257761Z","level":"INFO","logger":"main","event":"file_converted","file_path":"./data/sample.md","file_name":"sample.md","job_id":"job-1757050778"}
```

## 実装済み出力先 ✅
- **出力先**: ワークスペースルートの `./log` ディレクトリ（相対パス）
- **ファイル形式**: `./log/{YYYYMMDD}/{job_id}.log` （JSON Lines）
- **ローテーション**: 日次ローテーション（サブディレクトリで自動管理）- `_ensure_log_path()`実装済み
- **文字エンコーディング**: UTF-8対応（FileHandler encoding指定済み）

**実装詳細** (`src/lib/logging.py`):
- `get_logger(name, job_id, log_dir="./log")` 関数で自動セットアップ
- 日付ディレクトリ自動作成（例: `./log/20250905/`）
- 重複ハンドラー防止機能付き
- job_id基準でファイル分割

**実際の出力例**:
```
./log/20250905/job-1757050778.log
./log/20250905/job-1757063003.log
```

## 実装済み進捗表示 ✅
- **進捗イベント**: 各ファイル処理でINFOレベルログ出力（file_converted, file_uploaded等）
- **バッチ完了**: summaryイベントを出力（processed_count, success_count, fail_count, duration等）
- **リアルタイム表示**: 標準出力にも進捗表示

**実装済みサマリー例**:
```json
{"ts":"2025-09-05T09:30:45.123456Z","level":"INFO","logger":"main","event":"batch_summary","total_files":3,"success_count":3,"duration_seconds":45.67,"job_id":"job-1757050778"}
```

## 実装済みエラー/リトライ方針 ✅
- **リトライ処理**: Dify APIクライアントで最大3回リトライ（指数バックオフ）実装済み
- **エラーログ**: WARNレベル（リトライ時）、ERRORレベル（最終失敗時）
- **例外情報**: スタックトレース自動付与（JsonLinesFormatter.format()でexc_info処理）
- **エラー詳細**: API応答内容、ファイルパス等の文脈情報を構造化ログで記録

**実装済みエラーログ例**:
```json
{"ts":"2025-09-05T09:27:15.123456Z","level":"ERROR","logger":"dify_client","event":"api_error","message":"Failed to upload document","api_response":"400 Bad Request","file_path":"./data/test.txt","retry_count":3,"exc_info":"Traceback..."}
```

## 実装済みコード例 ✅

**実装ファイル**: `src/lib/logging.py`

```python
class JsonLinesFormatter(logging.Formatter):
    """ログレコードを compact な JSON オブジェクトとして整形します。"""
    
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
        }
        
        # If the message is a structured dict, merge it
        msg = record.msg
        if isinstance(msg, dict):
            payload.update(msg)
        else:
            payload["message"] = str(msg)
            
        # Include exception info if present
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
            
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

def get_logger(name: str, job_id: str, log_dir: str = "./log") -> logging.Logger:
    """指定された job_id に対応する JSON Lines ファイルハンドラを持つ Logger を返す。"""
    # 実装済み - 日付ディレクトリ自動作成、重複防止機能付き
```

**使用例** (`src/cli/main.py`):
```python
from src.lib.logging import get_logger

logger = get_logger("main", job_id)
logger.info({"event": "file_converted", "file_path": file_path, "file_name": file_name})
```

## 実装検証済み運用チェックリスト ✅
- [x] JSON Linesでの出力確認済み（JsonLinesFormatterで実装）
- [x] 日本語文字化けなし確認済み（ensure_ascii=False + UTF-8エンコーディング）
- [x] ログローテーション実装済み（日次サブディレクトリ自動作成）
- [x] summaryイベントが正しく出力される（batch_summary実装済み）
- [x] エラー発生時にexc_infoが含まれる（JsonLinesFormatter対応済み）
- [x] 実運用での動作確認済み（3ファイル処理ログ出力成功）

## 実装完了済み追加要件解決 ✅

### 1. ファイル形式対応（解決済み）
**当初の不明点**: 変換対象ファイルの拡張子制限
**実装された解決策**: 10種類のファイル形式サポート
- テキスト系: .md, .txt  
- Microsoft Office: .docx, .doc, .xlsx, .xlsm, .xls, .pptx, .ppt
- その他: .pdf

### 2. Dify API仕様（解決済み）
**当初の不明点**: Dify APIのエラー時リトライ要件
**実装された解決策**:
- API バージョン: v1対応
- エラー時リトライ: 最大3回、指数バックオフ（1秒、2秒、4秒）
- 必須パラメータ: indexing_technique="high_quality", process_rule={}自動設定

### 3. 設定ファイル形式（解決済み）
**当初の不明点**: 設定ファイルの形式（YAML/JSON/その他）
**実装された解決策**: YAML形式（config.yml）で統一
```yaml
input_folder: ./data
dify_url: http://example.com/v1  
api_key: dataset-xxxxxxxxxxxxx
dataset_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
log_dir: ./log
file_extensions: [.md, .txt, .docx, .xlsx, .pdf, .pptx, .ppt, .xls, .doc, .xlsm]
```

## 次のアクション（完了済み）
1. ✅ このログ仕様（出力先 `./log` 固定）を `spec.md` / `plan.md` に反映済み
2. ✅ 実装: `src/lib/logging.py` に JsonLinesFormatter と `./log` 出力の設定完了
3. ✅ テスト: ログ出力のユニットテスト作成済み（pytest）
4. ✅ 実運用検証: Dify API連携含む動作確認完了

---

## v2.2.0 拡張ログ仕様（計画中） 🚧

### 新機能要件
1. **スキップファイル詳細ログ**: ファイルがスキップされた詳細理由の出力
2. **処理サマリーログ**: バッチ処理全体の統計情報自動生成
3. **エラー分類ログ**: エラー種別の自動分類と集計

### 追加イベント種別
```json
// スキップ詳細ログ
{
  "ts": "2025-09-05T12:00:00Z",
  "level": "INFO",
  "logger": "main",
  "event": "file_skipped",
  "file_path": "./data/sample.md",
  "skip_reason": "no_changes_detected",
  "last_processed": "2025-09-04T10:30:00Z",
  "current_hash": "abc123",
  "previous_hash": "abc123"
}

// 処理サマリーログ（バッチ終了時）
{
  "ts": "2025-09-05T12:05:00Z",
  "level": "INFO", 
  "logger": "main",
  "event": "process_summary",
  "job_id": "job-1757050778",
  "total_files": 25,
  "processed_files": 20,
  "skipped_files": 3,
  "error_files": 2,
  "execution_time": 45.2,
  "start_time": "2025-09-05T12:00:00Z",
  "end_time": "2025-09-05T12:05:00Z",
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

### CLIオプション対応
- `--show-skipped`: スキップファイル詳細をコンソール出力
- `--skip-summary`: サマリーログの生成を無効化
- 既存の `--verbose` でスキップ理由も詳細表示

### 実装計画
- Phase 5.2: ログ拡張機能（スキップ理由詳細、処理サマリー）
- `src/lib/logging.py` に新イベント種別追加
- `src/cli/main.py` にサマリー生成ロジック追加
- 既存ログ仕様との後方互換性保持


