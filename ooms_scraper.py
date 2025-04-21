#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper implementation for ooms.com website.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from .base_scraper import BaseScraper

class OomsScraper(BaseScraper):
    """Scraper for ooms.com website."""
    
    def __init__(self):
        """Initialize the Ooms scraper."""
        super().__init__(
            name="ooms",
            base_url="https://www.ooms.com"
        )
        self.logger = logging.getLogger("scraper.ooms")
    
    def get_listings(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get property listings from ooms.com.
        
        Args:
            filters: Optional filters to apply (price range, location, etc.)
            
        Returns:
            List of property dictionaries with standardized keys
        """
        filters = filters or {}
        min_price = filters.get('min_price', 0)
        max_price = filters.get('max_price', 10000000)
        
        # Start with the main real estate page
        url = f"{self.base_url}/woningaanbod"
        
        # Add price filter if specified
        if min_price > 0 or max_price < 10000000:
            url += f"?prijs-van={min_price}&prijs-tot={max_price}"
        
        soup = self.get_page(url)
        if not soup:
            self.logger.error(f"Failed to fetch listings from {url}")
            return []
        
        listings = []
        
        # Find all property cards/containers
        property_elements = soup.select('.property-item') or soup.select('.property') or soup.select('.object-item')
        
        for element in property_elements:
            try:
                # Extract property details
                property_url_element = element.select_one('a') or element.select_one('.property-link')
                if not property_url_element:
                    continue
                
                property_url = property_url_element.get('href')
                if not property_url.startswith('http'):
                    property_url = self.base_url + property_url
                
                # Extract address and city
                address_element = element.select_one('.address') or element.select_one('.street')
                city_element = element.select_one('.city') or element.select_one('.location')
                
                address = address_element.text.strip() if address_element else "Onbekend adres"
                city = city_element.text.strip() if city_element else "Onbekende plaats"
                
                # Extract price
                price_element = element.select_one('.price') or element.select_one('.object-price')
                price_text = price_element.text.strip() if price_element else "€ 0"
                price = self.clean_price(price_text)
                
                # Skip if price is outside filter range
                if price and (price < min_price or price > max_price):
                    continue
                
                # Extract area if available
                area_element = element.select_one('.surface') or element.select_one('.size') or element.select_one('.object-size')
                area_text = area_element.text.strip() if area_element else "0 m²"
                area = self.clean_area(area_text)
                
                # Extract property type if available
                type_element = element.select_one('.type') or element.select_one('.object-type')
                property_type = type_element.text.strip() if type_element else "Onbekend"
                
                # Create listing object
                listing = {
                    'id': f"ooms_{property_url.split('/')[-1]}",
                    'address': address,
                    'city': city,
                    'price': price,
                    'area': area,
                    'property_type': property_type,
                    'url': property_url,
                }
                
                # Standardize and add to results
                listings.append(self.standardize_listing(listing))
                
            except Exception as e:
                self.logger.error(f"Error parsing property element: {str(e)}")
                continue
        
        self.logger.info(f"Found {len(listings)} listings on ooms.com")
        return listings
    
    def get_property_details(self, url: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific property.
        
        Args:
            url: URL of the property listing
            
        Returns:
            Dictionary with property details
        """
        soup = self.get_page(url)
        if not soup:
            self.logger.error(f"Failed to fetch property details from {url}")
            return {}
        
        details = {}
        
        try:
            # Extract property ID from URL
            property_id = url.split('/')[-1]
            details['id'] = f"ooms_{property_id}"
            
            # Extract address and city
            address_element = soup.select_one('.address') or soup.select_one('.street') or soup.select_one('h1')
            city_element = soup.select_one('.city') or soup.select_one('.location')
            
            if address_element:
                details['address'] = address_element.text.strip()
            
            if city_element:
                details['city'] = city_element.text.strip()
            
            # Extract price
            price_element = soup.select_one('.price') or soup.select_one('.object-price')
            if price_element:
                price_text = price_element.text.strip()
                details['price'] = self.clean_price(price_text)
            
            # Extract area
            area_element = soup.select_one('.surface') or soup.select_one('.size') or soup.select_one('.object-size')
            if area_element:
                area_text = area_element.text.strip()
                details['area'] = self.clean_area(area_text)
            
            # Extract property type
            type_element = soup.select_one('.type') or soup.select_one('.object-type')
            if type_element:
                details['property_type'] = type_element.text.strip()
            
            # Extract number of rooms
            rooms_element = soup.select_one('.rooms') or soup.select_one('.object-rooms')
            if rooms_element:
                rooms_text = rooms_element.text.strip()
                rooms_match = re.search(r'(\d+)', rooms_text)
                details['rooms'] = int(rooms_match.group(1)) if rooms_match else 0
            
            # Extract description
            description_element = soup.select_one('.description') or soup.select_one('.object-description')
            if description_element:
                details['description'] = description_element.text.strip()
            
            # Add URL
            details['url'] = url
            
        except Exception as e:
            self.logger.error(f"Error parsing property details: {str(e)}")
        
        # Standardize and return
        return self.standardize_listing(details)
