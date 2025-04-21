#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper implementation for rozenburgmakelaardij.nl website.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from .base_scraper import BaseScraper

class RozenburgMakelaarScraper(BaseScraper):
    """Scraper for rozenburgmakelaardij.nl website."""
    
    def __init__(self):
        """Initialize the Rozenburg Makelaar scraper."""
        super().__init__(
            name="rozenburgmakelaardij",
            base_url="https://www.rozenburgmakelaardij.nl"
        )
        self.logger = logging.getLogger("scraper.rozenburgmakelaardij")
    
    def get_listings(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get property listings from rozenburgmakelaardij.nl.
        
        Args:
            filters: Optional filters to apply (price range, location, etc.)
            
        Returns:
            List of property dictionaries with standardized keys
        """
        filters = filters or {}
        min_price = filters.get('min_price', 0)
        max_price = filters.get('max_price', 10000000)
        
        # Start with the main real estate page
        url = f"{self.base_url}/aanbod"
        
        soup = self.get_page(url)
        if not soup:
            self.logger.error(f"Failed to fetch listings from {url}")
            return []
        
        listings = []
        
        # Find all property cards/containers
        property_elements = soup.select('.property-item') or soup.select('.object') or soup.select('.woning')
        
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
                
                address_text = address_element.text.strip() if address_element else "Onbekend adres"
                
                # If city element exists, use it; otherwise try to extract from address
                if city_element:
                    city = city_element.text.strip()
                else:
                    # Try to extract city from address (common format: "Street, City")
                    address_parts = address_text.split(',')
                    if len(address_parts) > 1:
                        address = address_parts[0].strip()
                        city = address_parts[1].strip()
                    else:
                        address = address_text
                        city = "Onbekende plaats"
                
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
                    'id': f"rozenburgmakelaardij_{property_url.split('/')[-1]}",
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
        
        self.logger.info(f"Found {len(listings)} listings on rozenburgmakelaardij.nl")
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
            details['id'] = f"rozenburgmakelaardij_{property_id}"
            
            # Extract address and city
            address_element = soup.select_one('.address') or soup.select_one('.street') or soup.select_one('h1')
            city_element = soup.select_one('.city') or soup.select_one('.location')
            
            if address_element:
                address_text = address_element.text.strip()
                # Check if address contains city information
                address_parts = address_text.split(',')
                if len(address_parts) > 1 and not city_element:
                    details['address'] = address_parts[0].strip()
                    details['city'] = address_parts[1].strip()
                else:
                    details['address'] = address_text
            
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
