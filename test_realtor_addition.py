#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for manual realtor addition functionality.
This script tests the custom scraper template with a sample realtor configuration.
"""

import os
import sys
import json
import logging
import sqlite3
from custom_scraper_template import CustomScraper, create_scraper_from_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test_realtor_addition")

def test_database_schema():
    """Test the database schema for custom realtors."""
    logger.info("Testing database schema...")
    
    # Create database connection
    conn = sqlite3.connect('huizenzoeker.db')
    cursor = conn.cursor()
    
    # Check if realtors table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='realtors'")
    if not cursor.fetchone():
        logger.error("Realtors table does not exist")
        return False
    
    # Check if properties table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='properties'")
    if not cursor.fetchone():
        logger.error("Properties table does not exist")
        return False
    
    # Check if realtor_id column exists in properties table
    cursor.execute("PRAGMA table_info(properties)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    if 'realtor_id' not in column_names:
        logger.error("realtor_id column does not exist in properties table")
        return False
    
    # Check if default realtors were inserted
    cursor.execute("SELECT COUNT(*) FROM realtors")
    count = cursor.fetchone()[0]
    if count < 5:
        logger.error(f"Expected at least 5 default realtors, but found {count}")
        return False
    
    logger.info("Database schema test passed")
    return True

def test_custom_scraper():
    """Test the custom scraper template with a sample realtor configuration."""
    logger.info("Testing custom scraper template...")
    
    # Sample realtor configuration for a real estate website
    # Using funda.nl as an example (a popular Dutch real estate website)
    sample_config = {
        'id': 'funda_test',
        'name': 'Funda Test',
        'website': 'funda.nl',
        'search_url': 'https://www.funda.nl/koop/heel-nederland/',
        'listing_selector': '.search-result',
        'title_selector': '.search-result__header-title',
        'price_selector': '.search-result-price',
        'area_selector': '.search-result-kenmerken span:nth-child(1)',
        'rooms_selector': '.search-result-kenmerken span:nth-child(2)',
        'link_selector': '.search-result__header-title-col a',
        'city_selector': '.search-result__header-subtitle',
        'active': True,
        'notes': 'Test realtor for funda.nl'
    }
    
    try:
        # Create scraper
        scraper = create_scraper_from_config(sample_config)
        
        # Test scraper attributes
        assert scraper.id == 'funda_test', f"Expected id 'funda_test', got '{scraper.id}'"
        assert scraper.name == 'Funda Test', f"Expected name 'Funda Test', got '{scraper.name}'"
        assert scraper.website == 'funda.nl', f"Expected website 'funda.nl', got '{scraper.website}'"
        assert scraper.listing_selector == '.search-result', f"Expected listing_selector '.search-result', got '{scraper.listing_selector}'"
        
        logger.info("Custom scraper template test passed")
        return True
    except Exception as e:
        logger.error(f"Error testing custom scraper template: {str(e)}")
        return False

def test_realtor_api_endpoints():
    """Test the API endpoints for realtor management."""
    logger.info("Testing realtor API endpoints...")
    
    # Create database connection
    conn = sqlite3.connect('huizenzoeker.db')
    cursor = conn.cursor()
    
    # Check if api_endpoints table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_endpoints'")
    if not cursor.fetchone():
        logger.error("api_endpoints table does not exist")
        return False
    
    # Check if realtor API endpoints were inserted
    cursor.execute("SELECT COUNT(*) FROM api_endpoints WHERE path LIKE '/api/realtors%'")
    count = cursor.fetchone()[0]
    if count < 5:
        logger.error(f"Expected at least 5 realtor API endpoints, but found {count}")
        return False
    
    logger.info("Realtor API endpoints test passed")
    return True

def test_realtor_addition():
    """Test adding a new realtor to the database."""
    logger.info("Testing realtor addition...")
    
    # Create database connection
    conn = sqlite3.connect('huizenzoeker.db')
    cursor = conn.cursor()
    
    # Sample realtor data
    new_realtor = {
        'id': 'test_realtor',
        'name': 'Test Realtor',
        'website': 'testrealtor.nl',
        'search_url': 'https://www.testrealtor.nl/aanbod',
        'listing_selector': '.property-item',
        'title_selector': '.property-title',
        'price_selector': '.property-price',
        'area_selector': '.property-area',
        'rooms_selector': '.property-rooms',
        'link_selector': '.property-link',
        'city_selector': '.property-city',
        'active': 1,
        'notes': 'Test realtor for testing'
    }
    
    try:
        # Insert new realtor
        cursor.execute('''
        INSERT OR REPLACE INTO realtors (
            id, name, website, search_url, listing_selector, 
            title_selector, price_selector, area_selector, 
            rooms_selector, link_selector, city_selector, 
            active, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            new_realtor['id'], new_realtor['name'], new_realtor['website'], 
            new_realtor['search_url'], new_realtor['listing_selector'],
            new_realtor['title_selector'], new_realtor['price_selector'], 
            new_realtor['area_selector'], new_realtor['rooms_selector'],
            new_realtor['link_selector'], new_realtor['city_selector'],
            new_realtor['active'], new_realtor['notes']
        ))
        
        # Commit changes
        conn.commit()
        
        # Verify realtor was added
        cursor.execute("SELECT * FROM realtors WHERE id = ?", (new_realtor['id'],))
        result = cursor.fetchone()
        if not result:
            logger.error("Failed to add new realtor to database")
            return False
        
        # Clean up - delete test realtor
        cursor.execute("DELETE FROM realtors WHERE id = ?", (new_realtor['id'],))
        conn.commit()
        
        logger.info("Realtor addition test passed")
        return True
    except Exception as e:
        logger.error(f"Error testing realtor addition: {str(e)}")
        return False
    finally:
        conn.close()

def run_all_tests():
    """Run all tests for manual realtor addition functionality."""
    logger.info("Starting tests for manual realtor addition functionality...")
    
    # Run database schema update if needed
    if not os.path.exists('huizenzoeker.db'):
        logger.info("Database does not exist, running schema update...")
        os.system('python update_database_schema.py')
    
    # Run tests
    tests = [
        test_database_schema,
        test_custom_scraper,
        test_realtor_api_endpoints,
        test_realtor_addition
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Print summary
    logger.info("Test results:")
    for i, test in enumerate(tests):
        logger.info(f"  {test.__name__}: {'PASSED' if results[i] else 'FAILED'}")
    
    # Overall result
    if all(results):
        logger.info("All tests PASSED")
        return True
    else:
        logger.error("Some tests FAILED")
        return False

if __name__ == "__main__":
    run_all_tests()
