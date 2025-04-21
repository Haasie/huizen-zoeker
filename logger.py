#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logger module for huizenzoeker application.
This module provides enhanced logging functionality.
"""

import os
import logging
import logging.handlers
from typing import Optional, Dict, Any

class LoggerSetup:
    """Class for setting up application logging."""
    
    def __init__(self, log_file: str = "huizenzoeker.log", log_level: int = logging.INFO):
        """
        Initialize the logger setup.
        
        Args:
            log_file: Path to log file
            log_level: Logging level (default: INFO)
        """
        self.log_file = log_file
        self.log_level = log_level
        self.loggers = {}
        
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(os.path.abspath(log_file))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure root logger
        self.setup_root_logger()
    
    def setup_root_logger(self) -> None:
        """Configure the root logger."""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create file handler
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(self.log_level)
        root_logger.addHandler(file_handler)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(self.log_level)
        root_logger.addHandler(console_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger with the specified name.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def set_level(self, level: int) -> None:
        """
        Set logging level for all handlers.
        
        Args:
            level: New logging level
        """
        self.log_level = level
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        for handler in root_logger.handlers:
            handler.setLevel(level)
    
    @staticmethod
    def get_log_levels() -> Dict[str, int]:
        """
        Get available logging levels.
        
        Returns:
            Dictionary mapping level names to values
        """
        return {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
