# 内部モジュールインターフェース仕様

**Feature Branch**: `001-dify-python-markitdown`  
**Created**: 2025-09-05  
**Status**: Draft  
**Version**: 2.1.0

## 概要
本ドキュメントは、Difyナレッジ自動登録・更新バッチプログラムの内部モジュール間インターフェース仕様を定義します。

---

## モジュール構成

### src.lib.config
設定ファイルの読み込みと設定データの提供

### src.lib.converter
ファイル変換処理（各種フォーマット → Markdown）

### src.lib.dify_client
Dify Knowledge API クライアント

### src.lib.logging
構造化ログ機能

### src.lib.file_tracker（v2.1.0）
ファイル更新検知機能

### src.lib.backup_manager（v2.1.0）
Markdownバックアップ管理機能

---

## モジュール詳細仕様

### src.lib.config

#### クラス: Config
```python
@dataclass
class Config:
    input_folder: str
    dify_url: str
    api_key: str
    log_dir: str = "./log"
    file_extensions: Optional[List[str]] = None
    dataset_id: Optional[str] = None
    backup_folder: Optional[str] = None  # v2.1.0
```

#### 関数: load_config
```python
def load_config(config_path: str) -> Config:
    """設定ファイル（YAML/JSON）を読み込んでConfigオブジェクトを返す
    
    Args:
        config_path: 設定ファイルのパス
        
    Returns:
        Config: 設定データオブジェクト
        
    Raises:
        FileNotFoundError: 設定ファイルが存在しない
        ValueError: 必須フィールドが不足または形式エラー
        RuntimeError: YAML解析に必要なライブラリが不足
    """
```

#### 関数: as_dict
```python
def as_dict(self) -> Dict[str, Any]:
    """設定をdict形式で返す（デバッグ・ログ出力用）"""
```

### src.lib.converter

#### 関数: discover_files
```python
def discover_files(
    folder: str, 
    extensions: List[str]
) -> Generator[str, None, None]:
    """指定フォルダから対象拡張子のファイルを再帰的に発見
    
    Args:
        folder: 検索対象フォルダパス
        extensions: 対象拡張子リスト（例: ['.md', '.txt']）
        
    Yields:
        str: 発見したファイルの絶対パス
        
    Notes:
        - 隠しファイル（.で始まる）はスキップ
        - シンボリックリンクは辿らない
        - サブフォルダも再帰的に検索
    """
```

#### 関数: convert_file_to_markdown
```python
def convert_file_to_markdown(file_path: str) -> str:
    """ファイルをMarkdown形式に変換
    
    Args:
        file_path: 変換対象ファイルのパス
        
    Returns:
        str: 変換されたMarkdownテキスト
        
    Raises:
        FileNotFoundError: ファイルが存在しない
        ValueError: サポートされていないファイル形式
        UnicodeDecodeError: 文字エンコーディングエラー
        
    Supported Formats:
        - .md: Markdownファイル（そのまま返却）
        - .txt: テキストファイル
        - .docx: Word文書
        - .xlsx: Excel文書
        - .pdf: PDF文書
        - .pptx/.ppt: PowerPoint文書
        - .xls: Excel文書（旧形式）
        - .doc: Word文書（旧形式）
        - .xlsm: Excelマクロ有効文書
    """
```

#### 関数: extract_markdown_metadata
```python
def extract_markdown_metadata(markdown_text: str) -> Dict[str, Any]:
    """MarkdownテキストからFrontmatterメタデータを抽出
    
    Args:
        markdown_text: Markdownテキスト
        
    Returns:
        Dict[str, Any]: 抽出されたメタデータ
            - title: ドキュメントタイトル（Frontmatterまたは最初のh1から）
            - その他Frontmatterで定義されたフィールド
    """
```

### src.lib.dify_client

#### クラス: DifyClient
```python
class DifyClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 10):
        """Dify API クライアントを初期化
        
        Args:
            base_url: Dify APIのベースURL
            api_key: API認証キー
            timeout: リクエストタイムアウト（秒）
        """
```

#### メソッド: create_document_from_text
```python
def create_document_from_text(
    self,
    dataset_id: str,
    name: str,
    text: str,
    indexing_technique: Optional[str] = None,
    doc_form: Optional[str] = None,
    doc_language: Optional[str] = None,
    process_rule: Optional[Dict[str, Any]] = None,
    retrieval_model: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """テキストからDifyドキュメントを作成
    
    Args:
        dataset_id: 対象データセットID
        name: ドキュメント名
        text: ドキュメントテキスト
        indexing_technique: インデックス手法（デフォルト: "high_quality"）
        その他: APIパラメータ
        
    Returns:
        Dict[str, Any]: API レスポンス
        
    Raises:
        requests.HTTPError: API エラー
        requests.RequestException: ネットワークエラー
    """
```

#### メソッド: push_markdown
```python
def push_markdown(
    self,
    title: str,
    markdown: str,
    metadata: Optional[Dict] = None,
    max_retries: int = 3,
    endpoint: str = "/api/v1/knowledge",
) -> Any:
    """Markdownを Dify に送信（互換性ラッパー）
    
    Args:
        title: ドキュメントタイトル
        markdown: Markdownコンテンツ
        metadata: メタデータ（dataset_idを含む）
        max_retries: 最大リトライ回数
        endpoint: 旧エンドポイント（フォールバック用）
        
    Returns:
        APIレスポンス
    """
```

#### メソッド: verify_auth
```python
def verify_auth(self) -> bool:
    """API認証情報の有効性を確認
    
    Returns:
        bool: 認証が有効な場合True
    """
```

### src.lib.logging

#### 関数: get_logger
```python
def get_logger(
    name: str,
    job_id: str,
    log_dir: str = "./log"
) -> Logger:
    """構造化ログ用のLoggerを取得
    
    Args:
        name: ロガー名
        job_id: ジョブ識別子
        log_dir: ログ出力ディレクトリ
        
    Returns:
        Logger: 設定済みロガーインスタンス
        
    Notes:
        - JSON Lines形式でファイル出力
        - ファイル名: {log_dir}/job-{timestamp}.log
        - UTF-8エンコーディング
    """
```

### src.lib.file_tracker（v2.1.0）

#### クラス: FileMetadata
```python
@dataclass
class FileMetadata:
    file_path: str
    last_processed: datetime
    file_size: int
    last_modified: datetime
    content_hash: str
    processing_status: str
    dify_document_id: Optional[str] = None
```

#### クラス: FileTracker
```python
class FileTracker:
    def __init__(self, metadata_file: str = ".file_metadata.json"):
        """ファイル更新検知トラッカーを初期化"""
```

#### メソッド: is_file_changed
```python
def is_file_changed(self, file_path: str) -> bool:
    """ファイルが前回処理時から変更されているかチェック
    
    Args:
        file_path: チェック対象ファイルパス
        
    Returns:
        bool: 変更されている場合True
    """
```

#### メソッド: update_metadata
```python
def update_metadata(
    self, 
    file_path: str, 
    status: str, 
    dify_document_id: Optional[str] = None
) -> None:
    """ファイルメタデータを更新
    
    Args:
        file_path: 対象ファイルパス
        status: 処理ステータス（success, error, skipped）
        dify_document_id: 関連するDifyドキュメントID
    """
```

### src.lib.backup_manager（v2.1.0）

#### クラス: BackupFile
```python
@dataclass
class BackupFile:
    source_file_path: str
    backup_file_path: str
    backup_folder: str
    relative_structure: str
    timestamp: str
    created_at: datetime
    file_size: int
```

#### クラス: BackupManager
```python
class BackupManager:
    def __init__(self, backup_folder: str):
        """バックアップマネージャーを初期化"""
```

#### メソッド: create_backup
```python
def create_backup(
    self, 
    source_file_path: str, 
    markdown_content: str,
    input_folder: str
) -> BackupFile:
    """Markdownコンテンツをバックアップ
    
    Args:
        source_file_path: 元ファイルパス
        markdown_content: 変換されたMarkdownコンテンツ
        input_folder: 入力フォルダ（相対パス計算用）
        
    Returns:
        BackupFile: 作成されたバックアップ情報
        
    Notes:
        - ファイル名にタイムスタンプ追加（yyyymmddhhmiss）
        - サブフォルダ構造を保持
    """
```

---

## エラーハンドリング規約

### 例外の種類
- `FileNotFoundError`: ファイル・ディレクトリが存在しない
- `ValueError`: 不正な引数・設定値
- `UnicodeDecodeError`: 文字エンコーディングエラー
- `requests.HTTPError`: HTTP エラー
- `requests.RequestException`: ネットワークエラー
- `RuntimeError`: ランタイムエラー（ライブラリ不足等）

### ログ出力規約
- エラー情報は構造化ログで記録
- 機密情報（API キー等）はマスキング
- スタックトレースは ERROR レベルで出力

---

## テスト規約

### ユニットテスト
- 各公開関数・メソッドに対してテストケースを作成
- 正常系・異常系の両方をカバー
- モック使用でネットワーク依存を排除

### 統合テスト
- 実際のファイルとDify APIを使用した E2E テスト
- 設定ファイルバリエーションのテスト

### テストデータ
- 日本語ファイル名・コンテンツを含むテストケース
- 各サポートファイル形式のサンプルファイル

---

## バージョン履歴

### v2.0.0（現在）
- 基本的なモジュール構成
- 10種類のファイルフォーマット対応
- Dify API v1 対応

### v2.1.0（予定）
- file_tracker モジュール追加
- backup_manager モジュール追加
- 設定ファイル拡張
