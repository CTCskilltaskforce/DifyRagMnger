"""設定管理モジュール

アプリケーションの設定ファイル読み込みと設定管理を行います。
v2.3.1で空白行処理設定機能を追加しました。
"""

import json
import logging
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Union

try:
    import yaml
    _has_yaml = True
except ImportError:
    _has_yaml = False

logger = logging.getLogger(__name__)


@dataclass
class ChunkSettings:
    """チャンク設定を管理するデータクラス。
    
    Attributes:
        max_chunk_length: 最大チャンク長（1-8192文字）
        overlap_size: オーバーラップサイズ（0-max_chunk_length文字）
    """
    max_chunk_length: int = 4000
    overlap_size: int = 200
    
    def __post_init__(self):
        """初期化後の検証処理。"""
        self.validate()
    
    def validate(self):
        """設定値の妥当性を検証する。
        
        Raises:
            ValueError: 設定値が不正な場合
        """
        if not isinstance(self.max_chunk_length, int):
            raise ValueError(f"max_chunk_length must be int, got {type(self.max_chunk_length)}")
        if not isinstance(self.overlap_size, int):
            raise ValueError(f"overlap_size must be int, got {type(self.overlap_size)}")
        
        if not (1 <= self.max_chunk_length <= 8192):
            raise ValueError(f"max_chunk_length must be between 1 and 8192, got {self.max_chunk_length}")
        if not (0 <= self.overlap_size <= self.max_chunk_length):
            raise ValueError(f"overlap_size must be between 0 and {self.max_chunk_length}, got {self.overlap_size}")
    
    def as_dict(self) -> Dict[str, Any]:
        """辞書形式で設定を返す。
        
        Returns:
            設定の辞書
        """
        return asdict(self)


@dataclass 
class EmptyLineConfig:
    """空白行処理設定を管理するデータクラス。
    
    Attributes:
        enabled: 空白行処理を有効にするかどうか
        remove_consecutive: 連続する空白行を単一改行に集約するかどうか
        remove_trailing: テーブル末尾の空白行を削除するかどうか
        preserve_single_empty: 単一の空白行は保持するかどうか
    """
    enabled: bool = True
    remove_consecutive: bool = True
    remove_trailing: bool = True
    preserve_single_empty: bool = True
    
    def __post_init__(self):
        """初期化後の検証処理。"""
        self.validate()
    
    def validate(self):
        """設定値の妥当性を検証する。
        
        Raises:
            ValueError: 設定値が不正な場合
        """
        if not isinstance(self.enabled, bool):
            raise ValueError(f"enabled must be bool, got {type(self.enabled)} ({self.enabled})")
        if not isinstance(self.remove_consecutive, bool):
            raise ValueError(f"remove_consecutive must be bool, got {type(self.remove_consecutive)} ({self.remove_consecutive})")
        if not isinstance(self.remove_trailing, bool):
            raise ValueError(f"remove_trailing must be bool, got {type(self.remove_trailing)} ({self.remove_trailing})")
        if not isinstance(self.preserve_single_empty, bool):
            raise ValueError(f"preserve_single_empty must be bool, got {type(self.preserve_single_empty)} ({self.preserve_single_empty})")
    
    def as_dict(self) -> Dict[str, Any]:
        """辞書形式で設定を返す。
        
        Returns:
            設定の辞書
        """
        return asdict(self)


class Config:
    """アプリケーション設定を管理するクラス。
    
    Attributes:
        input_folder: 入力フォルダのパス
        dify_url: DifyのAPI URL
        api_key: DifyのAPIキー
        dataset_id: DifyのデータセットID
        log_dir: ログディレクトリのパス
        backup_folder: バックアップフォルダのパス
        chunk_settings: チャンク設定
        empty_line_handling: 空白行処理設定
        file_extensions: 対応ファイル拡張子のリスト
    """
    
    def __init__(self, data: Dict[str, Any]):
        """設定オブジェクトを初期化する。
        
        Args:
            data: 設定データの辞書
        """
        self.input_folder = data.get("input_folder", "./data")
        self.dify_url = data.get("dify_url", "")
        self.api_key = data.get("api_key", "")
        self.dataset_id = data.get("dataset_id", "")
        self.log_dir = data.get("log_dir", "./log")
        self.backup_folder = data.get("backup_folder", "./backup")
        
        # チャンク設定の処理
        chunk_data = data.get("chunk_settings", {})
        if chunk_data:
            try:
                self.chunk_settings = ChunkSettings(**chunk_data)
            except (TypeError, ValueError) as e:
                logger.warning(f"Invalid chunk_settings, using defaults: {e}")
                self.chunk_settings = ChunkSettings()
        else:
            self.chunk_settings = None
        
        # 空白行処理設定の処理
        empty_line_data = data.get("empty_line_handling", {})
        if empty_line_data:
            try:
                self.empty_line_handling = EmptyLineConfig(**empty_line_data)
            except (TypeError, ValueError) as e:
                logger.warning(f"Invalid empty_line_handling settings, using defaults: {e}")
                self.empty_line_handling = EmptyLineConfig()
        else:
            self.empty_line_handling = EmptyLineConfig()
        
        # ファイル拡張子の設定
        self.file_extensions = data.get("file_extensions", [
            ".md", ".txt", ".docx", ".xlsx", ".pdf", ".pptx", ".ppt", ".xls", ".doc", ".xlsm"
        ])
    
    def as_dict(self) -> Dict[str, Any]:
        """設定を辞書形式で返す。
        
        Returns:
            設定の辞書
        """
        result = {
            "input_folder": self.input_folder,
            "dify_url": self.dify_url,
            "api_key": self.api_key,
            "dataset_id": self.dataset_id,
            "log_dir": self.log_dir,
            "backup_folder": self.backup_folder,
            "file_extensions": self.file_extensions,
            "empty_line_handling": self.empty_line_handling.as_dict()
        }
        
        if self.chunk_settings:
            result["chunk_settings"] = self.chunk_settings.as_dict()
        
        return result


def load_config(config_path: str) -> Config:
    """設定ファイルを読み込んでConfigオブジェクトを返す。
    
    Args:
        config_path: 設定ファイルのパス
        
    Returns:
        設定オブジェクト
        
    Raises:
        FileNotFoundError: 設定ファイルが見つからない場合
        ValueError: 設定ファイルの形式が不正な場合
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    # ファイル拡張子から形式を判定
    ext = os.path.splitext(config_path)[1].lower()
    
    with open(config_path, "r", encoding="utf-8") as f:
        if ext == ".json":
            data = json.load(f)
        elif ext in [".yml", ".yaml"]:
            if not _has_yaml:
                raise ValueError("PyYAML is required to load YAML config files")
            data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config file format: {ext}")
    
    logger.info(f"設定ファイル読み込み完了: {config_path}")
    return Config(data)


def get_empty_line_config(config: Optional[Config] = None) -> EmptyLineConfig:
    """空白行処理設定を取得する。
    
    Args:
        config: 設定オブジェクト（Noneの場合はデフォルト設定を返す）
        
    Returns:
        空白行処理設定
    """
    try:
        if config is None:
            # 設定オブジェクトが提供されていない場合はデフォルト設定を返す
            return EmptyLineConfig()
        
        if hasattr(config, 'empty_line_handling') and config.empty_line_handling is not None:
            return config.empty_line_handling
        else:
            # empty_line_handling属性がない場合はデフォルト設定を返す
            return EmptyLineConfig()
            
    except Exception as e:
        # 何らかのエラーが発生した場合はデフォルト設定を返す
        logger.warning(f"Failed to get empty line config, using defaults: {e}")
        return EmptyLineConfig()
