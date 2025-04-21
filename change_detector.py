#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Change detection module for huizenzoeker application.
This module provides functionality for detecting changes in property listings.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from ..database.property_db import PropertyDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("huizenzoeker.log"),
        logging.StreamHandler()
    ]
)

class ChangeDetector:
    """Class for detecting changes in property listings."""
    
    def __init__(self, db: PropertyDatabase):
        """
        Initialize the change detector.
        
        Args:
            db: PropertyDatabase instance
        """
        self.db = db
        self.logger = logging.getLogger("change_detector")
    
    def process_listings(self, listings: List[Dict[str, Any]], source: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process a batch of listings to detect changes.
        
        Args:
            listings: List of property listings
            source: Source website name
            
        Returns:
            Dictionary with lists of new, updated, and removed properties
        """
        self.logger.info(f"Processing {len(listings)} listings from {source}")
        
        new_properties = []
        updated_properties = []
        active_ids = []
        
        # Process each listing
        for listing in listings:
            # Ensure source is set
            listing['source'] = source
            
            # Add or update property in database
            status, changes = self.db.add_or_update_property(listing)
            
            # Track active IDs
            active_ids.append(listing['id'])
            
            # Collect new and updated properties
            if status == "new":
                new_properties.append(listing)
            elif status == "updated" and changes:
                # Add changes to the listing for notification purposes
                listing['changes'] = changes
                updated_properties.append(listing)
        
        # Find removed properties (those that were active but are no longer in the listings)
        removed_ids = self.db.mark_inactive_properties(active_ids, source)
        removed_properties = []
        
        for property_id in removed_ids:
            property_data = self.db.get_property(property_id)
            if property_data:
                removed_properties.append(property_data)
        
        self.logger.info(f"Detected {len(new_properties)} new, {len(updated_properties)} updated, and {len(removed_properties)} removed properties from {source}")
        
        return {
            "new": new_properties,
            "updated": updated_properties,
            "removed": removed_properties
        }
    
    def filter_properties(self, properties: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter properties based on criteria.
        
        Args:
            properties: List of property dictionaries
            filters: Filter criteria
                - min_price: Minimum price
                - max_price: Maximum price
                - city: City name
                - min_area: Minimum area
                - property_type: Property type
                
        Returns:
            Filtered list of properties
        """
        filtered_properties = []
        
        for prop in properties:
            # Apply price filter
            if 'min_price' in filters and prop['price'] < filters['min_price']:
                continue
            if 'max_price' in filters and prop['price'] > filters['max_price']:
                continue
            
            # Apply city filter
            if 'city' in filters and filters['city'].lower() not in prop['city'].lower():
                continue
            
            # Apply area filter
            if 'min_area' in filters and prop.get('area', 0) < filters['min_area']:
                continue
            
            # Apply property type filter
            if 'property_type' in filters and filters['property_type'] != prop.get('property_type', ''):
                continue
            
            filtered_properties.append(prop)
        
        return filtered_properties
    
    def get_recent_changes(self, limit: int = 100, filters: Dict[str, Any] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get recent property changes with optional filtering.
        
        Args:
            limit: Maximum number of changes to return per category
            filters: Optional filters to apply
                
        Returns:
            Dictionary with lists of new, updated, and removed properties
        """
        # Get recent changes from database
        all_changes = self.db.get_recent_changes(limit * 3)  # Get more than needed for filtering
        
        # Categorize changes
        new_properties = []
        updated_properties = []
        removed_properties = []
        
        for change in all_changes:
            property_id = change['property_id']
            property_data = self.db.get_property(property_id)
            
            if not property_data:
                continue
                
            # Add change information to property data
            property_data['change_type'] = change['change_type']
            property_data['change_date'] = change['change_date']
            
            if change['change_type'] == 'new_property':
                new_properties.append(property_data)
            elif change['change_type'].startswith('changed_'):
                # Add specific change details
                if 'changes' not in property_data:
                    property_data['changes'] = []
                
                property_data['changes'].append({
                    'field': change['change_type'].replace('changed_', ''),
                    'old_value': change['old_value'],
                    'new_value': change['new_value']
                })
                
                updated_properties.append(property_data)
            elif change['change_type'] == 'property_inactive':
                removed_properties.append(property_data)
        
        # Apply filters if provided
        if filters:
            new_properties = self.filter_properties(new_properties, filters)
            updated_properties = self.filter_properties(updated_properties, filters)
            removed_properties = self.filter_properties(removed_properties, filters)
        
        # Limit results
        new_properties = new_properties[:limit]
        updated_properties = updated_properties[:limit]
        removed_properties = removed_properties[:limit]
        
        return {
            "new": new_properties,
            "updated": updated_properties,
            "removed": removed_properties
        }
