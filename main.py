#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main application file for huizenzoeker.
This file is the entry point for the application.
"""

import os
import sys
import logging
import argparse
from typing import Dict, List, Any, Optional

# Import application modules
from huizenzoeker.config import ConfigManager
from huizenzoeker.database import PropertyDatabase
from huizenzoeker.utils import ChangeDetector, PropertyFilter, TaskScheduler, LoggerSetup
from huizenzoeker.notification import TelegramNotifier
from huizenzoeker.gui import WebGUI

# Import scrapers
from huizenzoeker.scrapers import (
    BaseScraper,
    KlipEnVWScraper,
    BijDeVaateScraper,
    OomsScraper,
    VBRMakelaarsScraper,
    RuimzichtScraper,
    VisieMakelaardijScraper,
    VoorneMakelaarsScraper,
    MarquisScraper,
    RozenburgMakelaardijScraper,
    DeltaMakelaardijScraper,
    DeHuizenBemiddelaarScraper,
    KolpaVanDerHoekScraper,
    RijnmondMakelaarsScraper,
    WoonVoornScraper,
    BoogermanScraper
)

def setup_logger(config: ConfigManager) -> LoggerSetup:
    """
    Set up application logging.
    
    Args:
        config: Configuration manager
        
    Returns:
        Logger setup instance
    """
    log_level_str = config.get('general', 'log_level', 'INFO')
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    log_level = log_levels.get(log_level_str, logging.INFO)
    
    return LoggerSetup(log_file="huizenzoeker.log", log_level=log_level)

def get_scrapers(config: ConfigManager) -> List[BaseScraper]:
    """
    Get list of enabled scrapers.
    
    Args:
        config: Configuration manager
        
    Returns:
        List of scraper instances
    """
    # Map of website names to scraper classes
    scraper_map = {
        'klipenvw': KlipEnVWScraper,
        'bijdevaate': BijDeVaateScraper,
        'ooms': OomsScraper,
        'vbrmakelaars': VBRMakelaarsScraper,
        'ruimzicht': RuimzichtScraper,
        'visiemakelaardij': VisieMakelaardijScraper,
        'voornemakelaars': VoorneMakelaarsScraper,
        'marquis': MarquisScraper,
        'rozenburgmakelaardij': RozenburgMakelaardijScraper,
        'deltamakelaardij': DeltaMakelaardijScraper,
        'dehuizenbemiddelaar': DeHuizenBemiddelaarScraper,
        'kolpavanderhoek': KolpaVanDerHoekScraper,
        'rijnmondmakelaars': RijnmondMakelaarsScraper,
        'woonvoorn': WoonVoornScraper,
        'boogerman': BoogermanScraper
    }
    
    # Get enabled websites
    enabled_websites = config.get_enabled_websites()
    
    # Create scraper instances
    scrapers = []
    for website in enabled_websites:
        if website in scraper_map:
            scrapers.append(scraper_map[website]())
    
    return scrapers

def run_scraper_job(config: ConfigManager, db: PropertyDatabase, 
                   change_detector: ChangeDetector, notifier: Optional[TelegramNotifier] = None) -> Dict[str, Any]:
    """
    Run scraper job to fetch and process property listings.
    
    Args:
        config: Configuration manager
        db: Property database
        change_detector: Change detector
        notifier: Optional Telegram notifier
        
    Returns:
        Dictionary with counts of new, updated, and removed properties
    """
    logger = logging.getLogger("scraper_job")
    logger.info("Starting scraper job")
    
    # Get scrapers
    scrapers = get_scrapers(config)
    
    # Get filter settings
    filter_settings = config.get_filter_settings()
    property_filter = PropertyFilter(
        min_price=filter_settings.get('min_price', 100000),
        max_price=filter_settings.get('max_price', 225000),
        min_area=filter_settings.get('min_area', 0),
        cities=filter_settings.get('cities', []),
        property_types=filter_settings.get('property_types', [])
    )
    
    # Initialize counters
    total_new = 0
    total_updated = 0
    total_removed = 0
    
    # Process each scraper
    for scraper in scrapers:
        try:
            logger.info(f"Running scraper for {scraper.name}")
            
            # Get listings with filter
            listings = scraper.get_listings({
                'min_price': property_filter.min_price,
                'max_price': property_filter.max_price
            })
            
            # Apply additional filtering
            filtered_listings = property_filter.filter_properties(listings)
            
            # Process listings
            changes = change_detector.process_listings(filtered_listings, scraper.name)
            
            # Count changes
            new_count = len(changes['new'])
            updated_count = len(changes['updated'])
            removed_count = len(changes['removed'])
            
            logger.info(f"Scraper {scraper.name} found {new_count} new, {updated_count} updated, and {removed_count} removed properties")
            
            # Send notifications if notifier is available
            if notifier and (new_count > 0 or updated_count > 0 or removed_count > 0):
                notifier.notify_property_changes(changes)
            
            # Update counters
            total_new += new_count
            total_updated += updated_count
            total_removed += removed_count
            
        except Exception as e:
            logger.error(f"Error running scraper {scraper.name}: {str(e)}")
    
    # Send summary notification if notifier is available
    if notifier:
        summary = {
            'new': total_new,
            'updated': total_updated,
            'removed': total_removed
        }
        notifier.send_summary(summary)
    
    logger.info(f"Scraper job completed. Found {total_new} new, {total_updated} updated, and {total_removed} removed properties")
    
    return {
        'new': total_new,
        'updated': total_updated,
        'removed': total_removed
    }

def main():
    """Main application entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Huizenzoeker - Dutch Real Estate Scraper')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to configuration file')
    parser.add_argument('--run-once', action='store_true', help='Run scraper once and exit')
    parser.add_argument('--no-gui', action='store_true', help='Disable web GUI')
    args = parser.parse_args()
    
    # Load configuration
    config = ConfigManager(args.config)
    
    # Set up logging
    logger_setup = setup_logger(config)
    logger = logger_setup.get_logger("main")
    
    logger.info("Starting Huizenzoeker application")
    
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
    
    # Run once if requested
    if args.run_once:
        logger.info("Running scraper once and exiting")
        run_scraper_job(config, db, change_detector, notifier)
        return
    
    # Initialize scheduler
    scheduler = TaskScheduler()
    
    # Schedule scraper job
    scan_interval = config.get('general', 'scan_interval', 30)
    scheduler.add_job(
        lambda: run_scraper_job(config, db, change_detector, notifier),
        interval_minutes=scan_interval,
        job_name="scraper_job"
    )
    
    # Start scheduler
    scheduler.start()
    logger.info(f"Scheduler started with scan interval of {scan_interval} minutes")
    
    # Start web GUI if enabled and not disabled by command line
    if config.get('gui', 'enabled', True) and not args.no_gui:
        gui_settings = config.get_gui_settings()
        gui = WebGUI(
            config_path=args.config,
            template_dir="templates",
            static_dir="static",
            host=gui_settings.get('host', '0.0.0.0'),
            port=gui_settings.get('port', 5000)
        )
        
        # Create template files if they don't exist
        gui.create_template_files()
        
        # Run GUI (this will block until the application is terminated)
        logger.info(f"Starting web GUI on {gui_settings.get('host', '0.0.0.0')}:{gui_settings.get('port', 5000)}")
        gui.run(debug=gui_settings.get('debug', False))
    else:
        # If GUI is disabled, keep the application running
        logger.info("Web GUI is disabled, running in background mode")
        try:
            # Keep the main thread alive
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down")
            scheduler.stop()

if __name__ == "__main__":
    main()
