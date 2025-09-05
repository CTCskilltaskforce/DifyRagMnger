# Quickstart: Dify バッチ（テンプレート）

前提: Python 3.11 と仮想環境が用意されており、`requirements.txt` をインストール済みであること。
（注意）.xlsx を扱うには `openpyxl` が必要です。`requirements.txt` に既に追加済みなので、`pip install -r requirements.txt` を実行してください。

1. リポジトリルートに設定ファイルを作成します（`config.yml` を例にしています）。

```yaml
input_folder: ./data
dify_url: https://dify.example
api_key: REPLACE_WITH_KEY
log_dir: ./log
file_extensions:
  - .md
  - .txt
  - .docx
  - .xlsx
```

2. 入力フォルダにテスト用のファイルを配置します（例: `data/sample.md`）。

3. 仮想環境で CLI を実行します:

```bash
python -m src.cli.main config.yml
```

4. 実行後、`./log/YYYYMMDD/{job_id}.log` に結果が JSON Lines 形式で出力されます。

## E2E: 実際の Dify に登録して動作確認する手順

以下はローカル環境（Windows `cmd.exe`）での手順例です。`dify_url` と `api_key` は実際の値に置き換えてください。

1. 仮想環境をアクティブにし、依存をインストールする（まだの場合）:

```bat
:: Windows cmd の例
C:\> cd C:\Work\workspace\DifyRagMnger
C:\Work\workspace\DifyRagMnger> .venv\Scripts\activate
(.venv) C:\Work\workspace\DifyRagMnger> python -m pip install -r requirements.txt
```

2. `config.yml` を作成（`dify_url` と `api_key` を設定）:

```yaml
input_folder: ./data
dify_url: https://api.dify.ai/v1   # 例: 実際の API ベース URL
api_key: sk-xxxxxxx                # 実際の API キーを記入
log_dir: ./log
file_extensions:
  - .md
  - .txt
  - .docx
  - .xlsx
default_metadata:
  dataset_id: optional-dataset-id   # 省略可。未指定時は既存のエンドポイントに投げます
```

3. テスト用ファイルを `./data` に置く（日本語ファイル名や日本語本文を含めて OK）

4. CLI を実行して Dify に登録:

```bat
(.venv) C:\Work\workspace\DifyRagMnger> python -m src.cli.main --config config.yml
```

5. 実行結果の確認

- ログ: `./log/YYYYMMDD/{job_id}.log` を開き、各ドキュメントの登録結果（success/failure）を確認
- Dify 側: 管理画面や datasets API から登録されたドキュメントを確認

## 注意点とトラブルシュート

- 認証エラー: `401` や `403` が返る場合は `api_key` の値と `dify_url` が正しいか確認してください。Dify の OpenAPI では `Authorization: Bearer {API_KEY}` を要求する場合が多いです。
- ファイルエンコーディング: 日本語ファイルは UTF-8 (BOM なし) 推奨。文字化けがある場合はエンコードを確認してください。
- .xlsx が正しく変換されない: `openpyxl` がインストールされているか確認してください（requirements.txt に記載）。
- アップロード失敗（タイムアウト/接続エラー）: ネットワーク、プロキシ、または `dify_url` のベースが正しいかを確認してください。リトライが必要な場合は設定でバックオフを有効にしてください。
- 大量登録時の注意: バッチサイズを小さくして段階的に登録し、Dify 側のレート制限やインデックス時間を観察してください。

## 次のステップ（推奨）

- E2E を実行したら、`tests/integration/test_cli_e2e.py` の実機向けバージョン（実 API を呼ぶテスト）を別ファイルで作成することを推奨します。CI 上で APIキーを扱う場合はシークレット管理を必ず行ってください。
