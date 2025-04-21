#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Custom scraper template for user-added realtors.
This module provides a template for scraping custom realtor websites.
"""

import re
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

class CustomScraper:
    """Class for scraping custom realtor websites."""
    
    def __init__(self, realtor_config: Dict[str, Any]):
        """
        Initialize the custom scraper.
        
        Args:
            realtor_config: Dictionary with realtor configuration
        """
        self.logger = logging.getLogger(f"custom_scraper_{realtor_config['id']}")
        self.config = realtor_config
        self.name = realtor_config['name']
        self.id = realtor_config['id']
        self.website = realtor_config['website']
        self.search_url = realtor_config['search_url']
        
        # CSS selectors
        self.listing_selector = realtor_config['listing_selector']
        self.title_selector = realtor_config.get('title_selector', '')
        self.price_selector = realtor_config.get('price_selector', '')
        self.area_selector = realtor_config.get('area_selector', '')
        self.rooms_selector = realtor_config.get('rooms_selector', '')
        self.link_selector = realtor_config.get('link_selector', '')
        self.city_selector = realtor_config.get('city_selector', '')
        
        # Active status
        self.active = realtor_config.get('active', True)
    
    def get_listings(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get property listings from the realtor website.
        
        Args:
            filters: Optional dictionary with filters
            
        Returns:
            List of property dictionaries
        """
        if not self.active:
            self.logger.info(f"Scraper for {self.name} is inactive, skipping")
            return []
        
        self.logger.info(f"Scraping {self.name} ({self.website})")
        
        try:
            # Apply filters to search URL if provided
            url = self._apply_filters_to_url(self.search_url, filters)
            
            # Fetch the search page
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all property listings
            listings = soup.select(self.listing_selector)
            self.logger.info(f"Found {len(listings)} listings on {self.name}")
            
            # Process each listing
            properties = []
            for listing in listings:
                try:
                    property_data = self._extract_property_data(listing)
                    if property_data:
                        properties.append(property_data)
                except Exception as e:
                    self.logger.error(f"Error processing listing: {str(e)}")
            
            self.logger.info(f"Successfully extracted {len(properties)} properties from {self.name}")
            return properties
            
        except Exception as e:
            self.logger.error(f"Error scraping {self.name}: {str(e)}")
            return []
    
    def _apply_filters_to_url(self, url: str, filters: Optional[Dict[str, Any]]) -> str:
        """
        Apply filters to the search URL.
        
        Args:
            url: Base search URL
            filters: Dictionary with filters
            
        Returns:
            URL with filters applied
        """
        if not filters:
            return url
        
        # This is a simple implementation that works for some websites
        # In a real implementation, this would need to be customized for each website
        
        # Check if URL already has query parameters
        if '?' in url:
            base_url, query_string = url.split('?', 1)
            params = {}
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
        else:
            base_url = url
            params = {}
        
        # Apply price filters
        if 'min_price' in filters:
            params['min_price'] = str(filters['min_price'])
        if 'max_price' in filters:
            params['max_price'] = str(filters['max_price'])
        
        # Apply other filters
        if 'min_area' in filters and filters['min_area'] > 0:
            params['min_area'] = str(filters['min_area'])
        if 'max_area' in filters:
            params['max_area'] = str(filters['max_area'])
        if 'min_rooms' in filters and filters['min_rooms'] > 0:
            params['min_rooms'] = str(filters['min_rooms'])
        if 'max_rooms' in filters:
            params['max_rooms'] = str(filters['max_rooms'])
        if 'city' in filters and filters['city']:
            params['city'] = filters['city']
        
        # Reconstruct URL with filters
        if params:
            query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
            return f"{base_url}?{query_string}"
        else:
            return url
    
    def _extract_property_data(self, listing: Any) -> Optional[Dict[str, Any]]:
        """
        Extract property data from a listing element.
        
        Args:
            listing: BeautifulSoup element representing a property listing
            
        Returns:
            Dictionary with property data or None if extraction failed
        """
        try:
            # Extract property details using the provided selectors
            
            # Title/Address
            title = ""
            if self.title_selector:
                title_element = listing.select_one(self.title_selector)
                if title_element:
                    title = title_element.get_text(strip=True)
            
            # Price
            price = 0
            if self.price_selector:
                price_element = listing.select_one(self.price_selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    # Extract numbers from price text
                    price_numbers = re.findall(r'\d+', price_text.replace('.', '').replace(',', ''))
                    if price_numbers:
                        price = int(''.join(price_numbers))
            
            # Area
            area = 0
            if self.area_selector:
                area_element = listing.select_one(self.area_selector)
                if area_element:
                    area_text = area_element.get_text(strip=True)
                    # Extract numbers from area text
                    area_numbers = re.findall(r'\d+', area_text)
                    if area_numbers:
                        area = int(area_numbers[0])
            
            # Rooms
            rooms = 0
            if self.rooms_selector:
                rooms_element = listing.select_one(self.rooms_selector)
                if rooms_element:
                    rooms_text = rooms_element.get_text(strip=True)
                    # Extract numbers from rooms text
                    rooms_numbers = re.findall(r'\d+', rooms_text)
                    if rooms_numbers:
                        rooms = int(rooms_numbers[0])
            
            # City
            city = ""
            if self.city_selector:
                city_element = listing.select_one(self.city_selector)
                if city_element:
                    city = city_element.get_text(strip=True)
            
            # URL
            url = ""
            if self.link_selector:
                link_element = listing.select_one(self.link_selector)
                if link_element and link_element.has_attr('href'):
                    url = link_element['href']
                    # Make sure URL is absolute
                    if not url.startswith(('http://', 'https://')):
                        url = urljoin(self.search_url, url)
            
            # Generate a unique ID for the property
            property_id = f"{self.id}_{re.sub(r'[^a-z0-9]', '', url.lower())}"
            
            # Create property data dictionary
            property_data = {
                'id': property_id,
                'address': title,
                'city': city,
                'price': price,
                'area': area,
                'rooms': rooms,
                'property_type': 'Unknown',  # This would need custom extraction logic
                'url': url,
                'source': self.website,
                'realtor_id': self.id
            }
            
            return property_data
            
        except Exception as e:
            self.logger.error(f"Error extracting property data: {str(e)}")
            return None

def create_scraper_from_config(realtor_config: Dict[str, Any]) -> CustomScraper:
    """
    Create a custom scraper from realtor configuration.
    
    Args:
        realtor_config: Dictionary with realtor configuration
        
    Returns:
        CustomScraper instance
    """
    return CustomScraper(realtor_config)

def get_all_custom_scrapers(db_connection) -> List[CustomScraper]:
    """
    Get all custom scrapers from the database.
    
    Args:
        db_connection: Database connection
        
    Returns:
        List of CustomScraper instances
    """
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM realtors WHERE active = 1")
    realtors = cursor.fetchall()
    
    scrapers = []
    for realtor in realtors:
        # Convert SQLite row to dictionary
        realtor_config = {
            'id': realtor[0],
            'name': realtor[1],
            'website': realtor[2],
            'search_url': realtor[3],
            'listing_selector': realtor[4],
            'title_selector': realtor[5],
            'price_selector': realtor[6],
            'area_selector': realtor[7],
            'rooms_selector': realtor[8],
            'link_selector': realtor[9],
            'city_selector': realtor[10],
            'active': bool(realtor[11]),
            'notes': realtor[12]
        }
        
        scrapers.append(CustomScraper(realtor_config))
    
    return scrapers

# Example usage
if __name__ == "__main__":
    # Example realtor configuration
    example_config = {
        'id': 'example',
        'name': 'Example Realtor',
        'website': 'example.com',
        'search_url': 'https://www.example.com/properties',
        'listing_selector': '.property-item',
        'title_selector': '.property-title',
        'price_selector': '.property-price',
        'area_selector': '.property-area',
        'rooms_selector': '.property-rooms',
        'link_selector': '.property-link',
        'city_selector': '.property-city',
        'active': True,
        'notes': 'Example realtor for testing'
    }
    
    # Create scraper
    scraper = create_scraper_from_config(example_config)
    
    # Get listings
    listings = scraper.get_listings({'min_price': 100000, 'max_price': 225000})
    
    # Print results
    print(f"Found {len(listings)} listings")
    for listing in listings:
        print(f"{listing['address']} - {listing['price']} - {listing['url']}")
