#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration module for huizenzoeker application.
This module provides functionality for loading and saving application configuration.
"""

import os
import yaml
import json
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("huizenzoeker.log"),
        logging.StreamHandler()
    ]
)

class ConfigManager:
    """Class for managing application configuration."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
        """
        self.config_path = config_path
        self.logger = logging.getLogger("config_manager")
        self.config = self._get_default_config()
        
        # Create config directory if it doesn't exist
        config_dir = os.path.dirname(os.path.abspath(config_path))
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Load configuration if it exists
        if os.path.exists(config_path):
            self.load()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            # General settings
            "general": {
                "scan_interval": 30,  # minutes
                "log_level": "INFO",
                "database_path": "huizenzoeker.db"
            },
            
            # Filter settings
            "filter": {
                "min_price": 100000,
                "max_price": 225000,
                "min_area": 0,
                "cities": [],
                "property_types": []
            },
            
            # Telegram settings
            "telegram": {
                "token": "8169156824:AAG0Nz-OrByEWWjaCaDw6FaLVMCh3_lgnaA",
                "chat_id": "",
                "notify_new": True,
                "notify_updated": True,
                "notify_removed": True,
                "send_summary": True
            },
            
            # Website settings
            "websites": {
                "klipenvw": True,
                "bijdevaate": True,
                "ooms": True,
                "vbrmakelaars": True,
                "ruimzicht": True,
                "visiemakelaardij": True,
                "voornemakelaars": True,
                "marquis": True,
                "rozenburgmakelaardij": True,
                "deltamakelaardij": True,
                "dehuizenbemiddelaar": True,
                "kolpavanderhoek": True,
                "rijnmondmakelaars": True,
                "woonvoorn": True,
                "boogerman": True
            },
            
            # GUI settings
            "gui": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False
            }
        }
    
    def load(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if configuration was loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"Configuration file {self.config_path} does not exist, using defaults")
                return False
            
            file_ext = os.path.splitext(self.config_path)[1].lower()
            
            if file_ext == '.yaml' or file_ext == '.yml':
                with open(self.config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
            elif file_ext == '.json':
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
            else:
                self.logger.error(f"Unsupported configuration file format: {file_ext}")
                return False
            
            # Merge with default config to ensure all keys exist
            self._merge_config(loaded_config)
            self.logger.info(f"Configuration loaded from {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return False
    
    def save(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if configuration was saved successfully, False otherwise
        """
        try:
            file_ext = os.path.splitext(self.config_path)[1].lower()
            
            if file_ext == '.yaml' or file_ext == '.yml':
                with open(self.config_path, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            elif file_ext == '.json':
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
            else:
                self.logger.error(f"Unsupported configuration file format: {file_ext}")
                return False
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def _merge_config(self, loaded_config: Dict[str, Any]) -> None:
        """
        Merge loaded configuration with default configuration.
        
        Args:
            loaded_config: Loaded configuration dictionary
        """
        def merge_dicts(default_dict, loaded_dict):
            for key, value in loaded_dict.items():
                if key in default_dict and isinstance(default_dict[key], dict) and isinstance(value, dict):
                    merge_dicts(default_dict[key], value)
                else:
                    default_dict[key] = value
        
        merge_dicts(self.config, loaded_config)
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key (if None, returns entire section)
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value
        """
        if section not in self.config:
            return default
        
        if key is None:
            return self.config[section]
        
        return self.config[section].get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Configuration value
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def get_enabled_websites(self) -> List[str]:
        """
        Get list of enabled websites.
        
        Returns:
            List of enabled website names
        """
        enabled = []
        for website, enabled_flag in self.config['websites'].items():
            if enabled_flag:
                enabled.append(website)
        return enabled
    
    def get_filter_settings(self) -> Dict[str, Any]:
        """
        Get filter settings.
        
        Returns:
            Filter settings dictionary
        """
        return self.config['filter']
    
    def get_telegram_settings(self) -> Dict[str, Any]:
        """
        Get Telegram settings.
        
        Returns:
            Telegram settings dictionary
        """
        return self.config['telegram']
    
    def get_gui_settings(self) -> Dict[str, Any]:
        """
        Get GUI settings.
        
        Returns:
            GUI settings dictionary
        """
        return self.config['gui']
    
    def get_general_settings(self) -> Dict[str, Any]:
        """
        Get general settings.
        
        Returns:
            General settings dictionary
        """
        return self.config['general']
