# DifyRagMnger 運用ガイド

## セットアップ手順

### 1. Difyサーバーの準備

#### Dify APIキーの取得
1. Difyサーバーにログイン
2. 「設定」→「API」メニューを開く
3. 新しいAPIキーを生成
4. 生成されたAPIキーをコピー（後で設定ファイルに記述）

#### ナレッジベース（Dataset）の作成
1. Difyサーバーで「ナレッジベース」メニューを開く
2. 「作成」ボタンをクリック
3. 名前と説明を設定
4. 作成後、URLに表示される Dataset ID をコピー

### 2. DifyRagMngerの設定

#### 設定ファイルの作成
`config.yml` をプロジェクトルートに作成し、以下を設定：

```yaml
# 基本設定
input_folder: ./data
dify_url: http://your-dify-server/v1
api_key: dataset-xxxxxxxxx  # DifyのAPIキー
dataset_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  # Dataset ID
log_dir: ./log

# ファイル処理設定
file_extensions:
  - .md
  - .txt
  - .docx
  - .xlsx
```

#### 入力フォルダの準備
```bash
mkdir data
# 処理したいファイルを data フォルダに配置
```

### 3. 動作確認

#### 認証テスト
```bash
python -c "
from src.lib.config import load_config
from src.lib.dify_client import DifyClient
cfg = load_config('config.yml')
client = DifyClient(cfg.dify_url, cfg.api_key)
print('認証OK' if client.verify_auth() else '認証NG')
"
```

#### テスト実行
```bash
# テストファイルを作成
echo "# テスト文書\nこれはテストです。" > data/test.md

# バッチ実行
python -m src.cli.main config.yml

# ログ確認
ls -la log/$(date +%Y%m%d)/
```

## 定期実行の設定

### Linuxでのcron設定

```bash
# crontabを編集
crontab -e

# 毎日深夜2時に実行
0 2 * * * cd /path/to/DifyRagMnger && /path/to/python -m src.cli.main config.yml
```

### Windowsでのタスクスケジューラ設定

1. 「タスクスケジューラ」を開く
2. 「基本タスクの作成」を選択
3. 名前: "DifyRagMnger"
4. トリガー: 「毎日」
5. 操作: 「プログラムの開始」
   - プログラム: `C:\path\to\python.exe`
   - 引数: `-m src.cli.main config.yml`
   - 開始場所: `C:\path\to\DifyRagMnger`

## ログ監視とメンテナンス

### ログファイルの構造
```
log/
├── 20250905/           # 日付別フォルダ
│   ├── job-1757064391.log
│   └── job-1757064392.log
└── 20250906/
    └── job-1757150234.log
```

### ログの確認方法

#### 最新のログ確認
```bash
# 最新のログファイルを表示
ls -t log/$(date +%Y%m%d)/*.log | head -1 | xargs cat
```

#### エラーログの検索
```bash
# エラーが含まれるログを検索
grep -r "error\|ERROR" log/
```

#### 成功・失敗件数の確認
```bash
# サマリ情報を抽出
grep "summary" log/$(date +%Y%m%d)/*.log
```

### ログファイルのローテーション

#### 自動クリーンアップスクリプト例
```bash
#!/bin/bash
# 30日より古いログを削除
find log/ -type f -name "*.log" -mtime +30 -delete
find log/ -type d -empty -delete
```

## パフォーマンス調整

### 処理速度の最適化

#### ファイル数が多い場合
- `file_extensions` を必要最小限に絞る
- 大きなファイルは事前に分割する

#### API呼び出し頻度の調整
`src/lib/dify_client.py` の `timeout` 値を調整：
```python
def __init__(self, base_url: str, api_key: str, timeout: int = 30):
```

### リソース使用量の監視

#### メモリ使用量
```bash
# 実行中のメモリ使用量確認
ps aux | grep python | grep dify
```

#### ディスク使用量
```bash
# ログディスクの使用量確認
du -sh log/
```

## セキュリティ考慮事項

### APIキーの管理
- APIキーはファイルの権限を適切に設定（600等）
- 本番環境では環境変数での管理を推奨
- 定期的なAPIキーのローテーション

### ファイルアクセス権限
```bash
# 設定ファイルの権限設定
chmod 600 config.yml

# ログディレクトリの権限設定
chmod 755 log/
```

## 障害対応

### よくある障害と対処法

#### 1. API認証エラー
**症状**: `Authentication test: False`
**対処法**:
1. APIキーの有効性確認
2. Difyサーバーのアクセス可能性確認
3. ネットワーク接続確認

#### 2. ファイル変換エラー
**症状**: `FileNotFoundError` or `UnicodeDecodeError`
**対処法**:
1. ファイル権限確認
2. ファイル形式確認
3. 文字エンコーディング確認

#### 3. Dify API呼び出しエラー
**症状**: `400 Client Error: BAD REQUEST`
**対処法**:
1. Dataset ID の正確性確認
2. Difyサーバーのバージョン確認
3. APIエンドポイントの確認

### エラーログの読み方

#### 正常ログの例
```json
{
  "event": "uploaded",
  "path": "/path/to/file.md",
  "response": {"document": {"id": "xxx"}}
}
```

#### エラーログの例
```json
{
  "event": "error", 
  "path": "/path/to/file.md",
  "error": "400 Client Error: BAD REQUEST"
}
```

## バックアップとリストア

### 設定のバックアップ
```bash
# 設定ファイルのバックアップ
cp config.yml config.yml.backup.$(date +%Y%m%d)
```

### Difyナレッジベースのバックアップ
Difyサーバー側で提供されるエクスポート機能を使用

## 監視とアラート

### ヘルスチェックスクリプト例
```bash
#!/bin/bash
# health_check.sh

CONFIG_FILE="config.yml"
LOG_DIR="log/$(date +%Y%m%d)"

# 設定ファイル存在確認
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found"
    exit 1
fi

# 最新ログのエラーチェック
if grep -q "failures.*[1-9]" "$LOG_DIR"/*.log 2>/dev/null; then
    echo "WARNING: Processing failures detected"
    exit 2
fi

echo "OK: Health check passed"
exit 0
```

### アラート通知の設定
```bash
# メール通知例（要sendmail設定）
if ! ./health_check.sh; then
    echo "DifyRagMnger エラーが発生しました" | mail -s "DifyRagMnger Alert" admin@example.com
fi
```

## 更新とメンテナンス

### アプリケーションの更新
```bash
# コードの更新
git pull origin main

# 依存関係の更新
pip install -r requirements.txt --upgrade

# テスト実行
python -m pytest tests/ -v
```

### 設定の移行
新しいバージョンで設定項目が追加された場合：
```bash
# 現在の設定をバックアップ
cp config.yml config.yml.old

# 新しい設定項目を追加
# （README.md の設定例を参考に手動で追記）
```
