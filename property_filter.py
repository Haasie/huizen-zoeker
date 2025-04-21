#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filter module for huizenzoeker application.
This module provides functionality for filtering property listings.
"""

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

class PropertyFilter:
    """Class for filtering property listings."""
    
    def __init__(self, min_price: int = 0, max_price: int = 10000000, 
                 min_area: int = 0, cities: List[str] = None,
                 property_types: List[str] = None):
        """
        Initialize the property filter.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            min_area: Minimum area in square meters
            cities: List of cities to include
            property_types: List of property types to include
        """
        self.min_price = min_price
        self.max_price = max_price
        self.min_area = min_area
        self.cities = cities or []
        self.property_types = property_types or []
        self.logger = logging.getLogger("property_filter")
    
    def matches(self, property_data: Dict[str, Any]) -> bool:
        """
        Check if a property matches the filter criteria.
        
        Args:
            property_data: Property data dictionary
            
        Returns:
            True if property matches all criteria, False otherwise
        """
        # Check price range
        price = property_data.get('price', 0)
        if price < self.min_price or price > self.max_price:
            return False
        
        # Check minimum area
        area = property_data.get('area', 0)
        if area < self.min_area:
            return False
        
        # Check city if cities are specified
        if self.cities:
            city = property_data.get('city', '')
            if not any(c.lower() in city.lower() for c in self.cities):
                return False
        
        # Check property type if types are specified
        if self.property_types:
            property_type = property_data.get('property_type', '')
            if property_type not in self.property_types:
                return False
        
        return True
    
    def filter_properties(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a list of properties.
        
        Args:
            properties: List of property dictionaries
            
        Returns:
            Filtered list of properties
        """
        filtered = [p for p in properties if self.matches(p)]
        self.logger.info(f"Filtered {len(properties)} properties to {len(filtered)} matches")
        return filtered
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert filter to dictionary.
        
        Returns:
            Dictionary representation of filter
        """
        return {
            'min_price': self.min_price,
            'max_price': self.max_price,
            'min_area': self.min_area,
            'cities': self.cities,
            'property_types': self.property_types
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyFilter':
        """
        Create filter from dictionary.
        
        Args:
            data: Dictionary with filter parameters
            
        Returns:
            PropertyFilter instance
        """
        return cls(
            min_price=data.get('min_price', 0),
            max_price=data.get('max_price', 10000000),
            min_area=data.get('min_area', 0),
            cities=data.get('cities', []),
            property_types=data.get('property_types', [])
        )
