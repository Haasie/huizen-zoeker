#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web deployment version of the Huizenzoeker application.
This file serves as the entry point for the web application.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from huizenzoeker.config import ConfigManager
from huizenzoeker.database import PropertyDatabase
from huizenzoeker.utils import ChangeDetector, PropertyFilter, LoggerSetup
from huizenzoeker.notification import TelegramNotifier
from huizenzoeker.gui import WebGUI

# Configure logging
logger_setup = LoggerSetup(log_file="huizenzoeker.log", log_level=logging.INFO)
logger = logger_setup.get_logger("web_app")

# Initialize configuration
config = ConfigManager("config.yaml")

# Initialize database
db_path = config.get('general', 'database_path', 'huizenzoeker.db')
db = PropertyDatabase(db_path)

# Initialize change detector
change_detector = ChangeDetector(db)

# Initialize Telegram notifier if configured
telegram_settings = config.get_telegram_settings()
notifier = None
if telegram_settings.get('token') and telegram_settings.get('chat_id'):
    notifier = TelegramNotifier(
        token=telegram_settings['token'],
        chat_id=telegram_settings['chat_id']
    )
    logger.info("Telegram notifier initialized")
else:
    logger.warning("Telegram notifier not configured (missing token or chat_id)")

# Initialize web GUI
gui_settings = config.get_gui_settings()
app = Flask(__name__, 
            template_folder=os.path.abspath("templates"),
            static_folder=os.path.abspath("static"))

# Create WebGUI instance
web_gui = WebGUI(
    config_path="config.yaml",
    template_dir="templates",
    static_dir="static",
    host=gui_settings.get('host', '0.0.0.0'),
    port=gui_settings.get('port', 5000)
)

# Create template files if they don't exist
web_gui.create_template_files()

# Register routes from WebGUI
app.register_blueprint(web_gui.app)

if __name__ == "__main__":
    # This is for local development only
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # For production deployment
    # The app variable is used by the WSGI server
    pass
