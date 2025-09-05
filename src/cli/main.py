"""CLI エントリポイント。

小さなラッパーとして以下を行います:
- 設定ファイルの読み込み
- ファイルの発見と変換
- ファイル更新検知による効率的な処理
- Dify への送信

使い方（簡易）:
    python -m src.cli.main path/to/config.yaml
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from src.lib.config import load_config
from src.lib.converter import convert_file_to_markdown, discover_files, extract_markdown_metadata
from src.lib.dify_client import DifyClient
from src.lib.file_tracker import FileTracker
from src.lib.backup_manager import BackupManager
from src.lib.logging import get_logger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dify batch uploader")
    parser.add_argument("config", help="Path to configuration file (YAML or JSON)")
    parser.add_argument("--force", "-f", action="store_true", 
                       help="Force processing all files (ignore change detection)")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)

    # 簡易ジョブID: timestamp
    job_id = f"job-{int(__import__('time').time())}"
    logger = get_logger("dify_batch", job_id=job_id, log_dir=cfg.log_dir)

    client = DifyClient(cfg.dify_url, cfg.api_key)

    # ファイル更新検知機能を初期化（メタデータファイルはinput_folderに配置）
    metadata_file = os.path.join(cfg.input_folder, ".file_metadata.json")
    file_tracker = FileTracker(metadata_file)
    
    # バックアップマネージャーを初期化
    backup_manager = BackupManager(cfg.backup_folder)

    # 探索対象拡張子
    exts = cfg.file_extensions or [".md", ".txt", ".docx"]

    if not os.path.isdir(cfg.input_folder):
        logger.info({"event": "error", "message": f"input_folder not found: {cfg.input_folder}"})
        return 2

    # すべてのファイルを発見
    all_files = list(discover_files(cfg.input_folder, exts))
    
    # 変更されたファイルのみに絞り込み（--forceフラグで無効化可能）
    if args.force:
        files_to_process = all_files
        logger.info({"event": "force_mode", "message": "Processing all files (force mode)", "total_files": len(all_files)})
    else:
        files_to_process = []
        for file_path in all_files:
            if file_tracker.is_file_changed(file_path):
                files_to_process.append(file_path)
        
        skipped_count = len(all_files) - len(files_to_process)
        logger.info({
            "event": "file_filtering", 
            "total_files": len(all_files),
            "files_to_process": len(files_to_process), 
            "skipped_unchanged": skipped_count
        })

    if not files_to_process:
        logger.info({"event": "no_changes", "message": "No files need processing"})
        # 処理するファイルがなくてもクリーンアップは実行する
    else:
        successes = 0
        failures = 0
        backups_created = 0
        for path in files_to_process:
            try:
                # 変換前にバックアップを作成
                backup_path = None
                try:
                    md = convert_file_to_markdown(path)
                    backup_path = backup_manager.backup_markdown(path, md, cfg.input_folder)
                    backups_created += 1
                    logger.info({"event": "backup_created", "source": path, "backup": backup_path})
                except Exception as backup_exc:
                    logger.info({"event": "backup_error", "path": path, "error": str(backup_exc)})
                    # バックアップ失敗でも処理は継続
                    md = convert_file_to_markdown(path)
                
                extracted = extract_markdown_metadata(md)
                title = extracted.get("title") or Path(path).stem
                
                # dataset_idが設定されている場合は新しいAPIエンドポイントを使用
                if cfg.dataset_id:
                    metadata = {"dataset_id": cfg.dataset_id, "source_path": path, "extracted_title": extracted.get("title")}
                else:
                    metadata = {"source_path": path, "extracted_title": extracted.get("title")}
                
                # v2.2.0新機能: チャンク設定をDifyClientに渡す
                resp = client.push_markdown(
                    title, 
                    md, 
                    metadata=metadata,
                    chunk_settings=cfg.chunk_settings
                )
                
                # 成功時：ファイルメタデータを更新
                file_tracker.update_metadata(path, "success", resp.get("document_id"))
                successes += 1
                logger.info({"event": "uploaded", "path": path, "response": resp})
                
            except Exception as exc:
                # 失敗時：エラー状態でメタデータを更新
                try:
                    file_tracker.update_metadata(path, "error")
                except Exception:
                    # メタデータ更新が失敗しても処理は継続
                    pass
                
                failures += 1
                logger.info({"event": "error", "path": path, "error": str(exc)})

        # summary
        logger.info({"event": "summary", "successes": successes, "failures": failures, "backups_created": backups_created})

    # 孤立したメタデータのクリーンアップ
    # メタデータに記録されている全ファイルをチェックして、実際に存在しないものを削除
    try:
        valid_files = set(all_files)
        # メタデータにあるファイルで実際に存在しないものも含めてチェック
        all_metadata = file_tracker.get_all_metadata()
        for metadata_file_path in all_metadata:
            if not os.path.exists(metadata_file_path):
                logger.info({"event": "file_deleted", "path": metadata_file_path})
        
        removed_count = file_tracker.cleanup_orphaned_metadata(valid_files)
        if removed_count > 0:
            logger.info({"event": "metadata_cleanup", "removed_orphaned_entries": removed_count})
    except Exception as exc:
        logger.info({"event": "cleanup_error", "error": str(exc)})

    # バックアップ統計情報とクリーンアップ
    try:
        backup_stats = backup_manager.get_backup_stats()
        logger.info({"event": "backup_stats", "stats": backup_stats})
        
        # 30日より古いバックアップをクリーンアップ
        cleaned_count = backup_manager.cleanup_old_backups(days_to_keep=30)
        if cleaned_count > 0:
            logger.info({"event": "backup_cleanup", "removed_old_backups": cleaned_count})
            
    except Exception as exc:
        logger.info({"event": "backup_cleanup_error", "error": str(exc)})

    # summary
    if 'successes' in locals() and 'failures' in locals():
        logger.info({"event": "summary", "successes": successes, "failures": failures, "backups_created": backups_created if 'backups_created' in locals() else 0})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
