#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for huizenzoeker application.
This script tests the functionality of the application components.
"""

import os
import sys
import logging
import unittest
from typing import Dict, List, Any, Optional

# Add parent directory to path to import application modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application modules
from huizenzoeker.config import ConfigManager
from huizenzoeker.database import PropertyDatabase
from huizenzoeker.utils import ChangeDetector, PropertyFilter
from huizenzoeker.notification import TelegramNotifier
from huizenzoeker.scrapers import BaseScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class TestConfigManager(unittest.TestCase):
    """Test ConfigManager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.config_path = "test_config.yaml"
        self.config = ConfigManager(self.config_path)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
    
    def test_default_config(self):
        """Test default configuration."""
        self.assertEqual(self.config.get('filter', 'min_price'), 100000)
        self.assertEqual(self.config.get('filter', 'max_price'), 225000)
        self.assertEqual(self.config.get('telegram', 'token'), "8169156824:AAG0Nz-OrByEWWjaCaDw6FaLVMCh3_lgnaA")
    
    def test_save_load_config(self):
        """Test saving and loading configuration."""
        # Modify configuration
        self.config.set('filter', 'min_price', 150000)
        self.config.set('filter', 'max_price', 200000)
        
        # Save configuration
        self.assertTrue(self.config.save())
        
        # Create new config manager to load from file
        new_config = ConfigManager(self.config_path)
        
        # Check loaded values
        self.assertEqual(new_config.get('filter', 'min_price'), 150000)
        self.assertEqual(new_config.get('filter', 'max_price'), 200000)

class TestPropertyFilter(unittest.TestCase):
    """Test PropertyFilter functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.filter = PropertyFilter(
            min_price=100000,
            max_price=225000,
            min_area=50,
            cities=["Rotterdam", "Amsterdam"],
            property_types=["Appartement", "Eengezinswoning"]
        )
    
    def test_filter_matches(self):
        """Test property filter matching."""
        # Property that matches all criteria
        property1 = {
            'price': 150000,
            'area': 75,
            'city': 'Rotterdam',
            'property_type': 'Appartement'
        }
        self.assertTrue(self.filter.matches(property1))
        
        # Property with price too low
        property2 = {
            'price': 90000,
            'area': 75,
            'city': 'Rotterdam',
            'property_type': 'Appartement'
        }
        self.assertFalse(self.filter.matches(property2))
        
        # Property with price too high
        property3 = {
            'price': 250000,
            'area': 75,
            'city': 'Rotterdam',
            'property_type': 'Appartement'
        }
        self.assertFalse(self.filter.matches(property3))
        
        # Property with area too small
        property4 = {
            'price': 150000,
            'area': 40,
            'city': 'Rotterdam',
            'property_type': 'Appartement'
        }
        self.assertFalse(self.filter.matches(property4))
        
        # Property with city not in list
        property5 = {
            'price': 150000,
            'area': 75,
            'city': 'Utrecht',
            'property_type': 'Appartement'
        }
        self.assertFalse(self.filter.matches(property5))
        
        # Property with type not in list
        property6 = {
            'price': 150000,
            'area': 75,
            'city': 'Rotterdam',
            'property_type': 'Vrijstaand'
        }
        self.assertFalse(self.filter.matches(property6))
    
    def test_filter_properties(self):
        """Test filtering a list of properties."""
        properties = [
            {
                'price': 150000,
                'area': 75,
                'city': 'Rotterdam',
                'property_type': 'Appartement'
            },
            {
                'price': 90000,
                'area': 75,
                'city': 'Rotterdam',
                'property_type': 'Appartement'
            },
            {
                'price': 250000,
                'area': 75,
                'city': 'Rotterdam',
                'property_type': 'Appartement'
            },
            {
                'price': 150000,
                'area': 40,
                'city': 'Rotterdam',
                'property_type': 'Appartement'
            },
            {
                'price': 150000,
                'area': 75,
                'city': 'Utrecht',
                'property_type': 'Appartement'
            },
            {
                'price': 150000,
                'area': 75,
                'city': 'Rotterdam',
                'property_type': 'Vrijstaand'
            }
        ]
        
        filtered = self.filter.filter_properties(properties)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['price'], 150000)
        self.assertEqual(filtered[0]['city'], 'Rotterdam')

class TestDatabase(unittest.TestCase):
    """Test PropertyDatabase functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.db_path = "test_database.db"
        self.db = PropertyDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_add_property(self):
        """Test adding a property to the database."""
        property_data = {
            'id': 'test_property_1',
            'address': 'Teststraat 123',
            'city': 'Rotterdam',
            'price': 150000,
            'area': 75,
            'rooms': 3,
            'property_type': 'Appartement',
            'url': 'https://example.com/property/1',
            'source': 'test_source'
        }
        
        status, changes = self.db.add_or_update_property(property_data)
        self.assertEqual(status, "new")
        self.assertEqual(len(changes), 0)
        
        # Retrieve property
        retrieved = self.db.get_property('test_property_1')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['address'], 'Teststraat 123')
        self.assertEqual(retrieved['price'], 150000)
    
    def test_update_property(self):
        """Test updating a property in the database."""
        # Add initial property
        property_data = {
            'id': 'test_property_2',
            'address': 'Teststraat 456',
            'city': 'Amsterdam',
            'price': 180000,
            'area': 85,
            'rooms': 4,
            'property_type': 'Eengezinswoning',
            'url': 'https://example.com/property/2',
            'source': 'test_source'
        }
        
        self.db.add_or_update_property(property_data)
        
        # Update property
        updated_data = property_data.copy()
        updated_data['price'] = 190000
        updated_data['rooms'] = 5
        
        status, changes = self.db.add_or_update_property(updated_data)
        self.assertEqual(status, "updated")
        self.assertEqual(len(changes), 2)
        
        # Retrieve updated property
        retrieved = self.db.get_property('test_property_2')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['price'], 190000)
        self.assertEqual(retrieved['rooms'], 5)
    
    def test_filter_properties(self):
        """Test filtering properties from the database."""
        # Add multiple properties
        properties = [
            {
                'id': 'test_property_3',
                'address': 'Teststraat 789',
                'city': 'Rotterdam',
                'price': 150000,
                'area': 75,
                'rooms': 3,
                'property_type': 'Appartement',
                'url': 'https://example.com/property/3',
                'source': 'test_source'
            },
            {
                'id': 'test_property_4',
                'address': 'Teststraat 101',
                'city': 'Amsterdam',
                'price': 200000,
                'area': 90,
                'rooms': 4,
                'property_type': 'Eengezinswoning',
                'url': 'https://example.com/property/4',
                'source': 'test_source'
            },
            {
                'id': 'test_property_5',
                'address': 'Teststraat 112',
                'city': 'Utrecht',
                'price': 250000,
                'area': 100,
                'rooms': 5,
                'property_type': 'Vrijstaand',
                'url': 'https://example.com/property/5',
                'source': 'test_source'
            }
        ]
        
        for prop in properties:
            self.db.add_or_update_property(prop)
        
        # Filter by price range
        filtered = self.db.get_properties({
            'min_price': 180000,
            'max_price': 220000
        })
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['id'], 'test_property_4')
        
        # Filter by city
        filtered = self.db.get_properties({
            'city': 'Rotterdam'
        })
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['id'], 'test_property_3')

def run_tests():
    """Run all tests."""
    unittest.main()

if __name__ == "__main__":
    run_tests()
