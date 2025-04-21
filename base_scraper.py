#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base scraper module for huizenzoeker application.
This module provides the base functionality for all website-specific scrapers.
"""

import logging
import requests
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("huizenzoeker.log"),
        logging.StreamHandler()
    ]
)

class BaseScraper(ABC):
    """Base class for all real estate website scrapers."""
    
    def __init__(self, name: str, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the base scraper.
        
        Args:
            name: Name of the website/scraper
            base_url: Base URL of the website
            headers: Optional HTTP headers for requests
        """
        self.name = name
        self.base_url = base_url
        self.logger = logging.getLogger(f"scraper.{name}")
        
        # Default headers if none provided
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a page and return a BeautifulSoup object.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if request failed
        """
        try:
            self.logger.info(f"Fetching page: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def clean_price(self, price_str: str) -> Optional[int]:
        """
        Clean price string and convert to integer.
        
        Args:
            price_str: Price string (e.g., "€ 250.000", "250.000 €", etc.)
            
        Returns:
            Price as integer or None if conversion failed
        """
        try:
            # Remove currency symbols, dots, spaces, and other non-numeric characters
            cleaned = ''.join(c for c in price_str if c.isdigit())
            return int(cleaned) if cleaned else None
        except (ValueError, TypeError):
            self.logger.warning(f"Could not parse price: {price_str}")
            return None
    
    def clean_area(self, area_str: str) -> Optional[int]:
        """
        Clean area string and convert to integer.
        
        Args:
            area_str: Area string (e.g., "120 m²", "120m2", etc.)
            
        Returns:
            Area as integer or None if conversion failed
        """
        try:
            # Extract digits from the string
            cleaned = ''.join(c for c in area_str if c.isdigit())
            return int(cleaned) if cleaned else None
        except (ValueError, TypeError):
            self.logger.warning(f"Could not parse area: {area_str}")
            return None
    
    @abstractmethod
    def get_listings(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get property listings from the website.
        
        Args:
            filters: Optional filters to apply (price range, location, etc.)
            
        Returns:
            List of property dictionaries with standardized keys
        """
        pass
    
    @abstractmethod
    def get_property_details(self, url: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific property.
        
        Args:
            url: URL of the property listing
            
        Returns:
            Dictionary with property details
        """
        pass
    
    def standardize_listing(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize a property listing to ensure consistent format across scrapers.
        
        Args:
            listing: Raw property listing data
            
        Returns:
            Standardized property listing
        """
        # Ensure all required fields are present
        standard_listing = {
            'id': listing.get('id', f"{self.name}_{datetime.now().timestamp()}"),
            'address': listing.get('address', 'Onbekend adres'),
            'city': listing.get('city', 'Onbekende plaats'),
            'price': listing.get('price', 0),
            'area': listing.get('area', 0),
            'rooms': listing.get('rooms', 0),
            'property_type': listing.get('property_type', 'Onbekend'),
            'url': listing.get('url', ''),
            'source': self.name,
            'scraped_at': datetime.now().isoformat(),
        }
        
        # Add any additional fields that might be present
        for key, value in listing.items():
            if key not in standard_listing:
                standard_listing[key] = value
                
        return standard_listing
