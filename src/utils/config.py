"""
Configuration Manager
Handles loading and managing application configuration from JSON files
"""

import json, os
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration loaded from JSON files"""

    def __init__(self):
        self.config_dir = Path(os.path.join(os.getcwd(), "config"))
        self._app_config = None
        self._theme_config = None

    @property
    def app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        if self._app_config is None:
            self._app_config = self._load_config("app_config.json")
        return self._app_config

    @property
    def theme_config(self) -> Dict[str, Any]:
        """Get theme configuration"""
        if self._theme_config is None:
            self._theme_config = self._load_config("theme_config.json")
        return self._theme_config

    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        config_path = self.config_dir / filename
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Configuration file {filename} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing {filename}: {e}")
            return {}

    def get_app_setting(self, key_path: str, default: Any = None) -> Any:
        """Get application setting using dot notation (e.g., 'window.default_width')"""
        return self._get_nested_value(self.app_config, key_path, default)

    def get_theme_setting(self, key_path: str, default: Any = None) -> Any:
        """Get theme setting using dot notation (e.g., 'colors.primary')"""
        return self._get_nested_value(self.theme_config, key_path, default)

    def _get_nested_value(
        self, config: Dict[str, Any], key_path: str, default: Any = None
    ) -> Any:
        """Get nested dictionary value using dot notation"""
        keys = key_path.split(".")
        value = config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
