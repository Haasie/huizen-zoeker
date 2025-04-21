#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database module for huizenzoeker application.
This module provides functionality for storing and retrieving property listings.
"""

import os
import sqlite3
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("huizenzoeker.log"),
        logging.StreamHandler()
    ]
)

class PropertyDatabase:
    """Database class for property listings."""
    
    def __init__(self, db_path: str = "properties.db"):
        """
        Initialize the property database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger("database")
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create properties table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id TEXT PRIMARY KEY,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                price INTEGER NOT NULL,
                area INTEGER,
                rooms INTEGER,
                property_type TEXT,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                extra_data TEXT,
                active INTEGER DEFAULT 1
            )
            ''')
            
            # Create property_history table for tracking changes
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS property_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id TEXT NOT NULL,
                change_type TEXT NOT NULL,
                change_date TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
            ''')
            
            conn.commit()
            self.logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def add_or_update_property(self, property_data: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Add a new property or update an existing one.
        
        Args:
            property_data: Property data dictionary
            
        Returns:
            Tuple containing:
                - Status string ("new", "updated", or "unchanged")
                - List of changes (for "updated" status)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if property already exists
            cursor.execute("SELECT * FROM properties WHERE id = ?", (property_data['id'],))
            existing_property = cursor.fetchone()
            
            current_time = datetime.now().isoformat()
            changes = []
            
            if existing_property:
                # Property exists, check for changes
                columns = [desc[0] for desc in cursor.description]
                existing_data = dict(zip(columns, existing_property))
                
                # Extract extra_data as JSON
                if existing_data['extra_data']:
                    try:
                        extra_data = json.loads(existing_data['extra_data'])
                        for key, value in extra_data.items():
                            existing_data[key] = value
                    except json.JSONDecodeError:
                        self.logger.warning(f"Failed to parse extra_data for property {property_data['id']}")
                
                # Check for changes in core fields
                core_fields = ['price', 'area', 'rooms', 'property_type', 'address', 'city']
                has_changes = False
                
                for field in core_fields:
                    if field in property_data and field in existing_data:
                        old_value = existing_data[field]
                        new_value = property_data[field]
                        
                        if old_value != new_value:
                            has_changes = True
                            changes.append({
                                'field': field,
                                'old_value': old_value,
                                'new_value': new_value
                            })
                            
                            # Record change in history
                            cursor.execute('''
                            INSERT INTO property_history 
                            (property_id, change_type, change_date, old_value, new_value)
                            VALUES (?, ?, ?, ?, ?)
                            ''', (
                                property_data['id'],
                                f"changed_{field}",
                                current_time,
                                str(old_value),
                                str(new_value)
                            ))
                
                if has_changes:
                    # Prepare extra data (fields not in core table)
                    extra_data = {k: v for k, v in property_data.items() 
                                 if k not in ['id', 'address', 'city', 'price', 'area', 
                                             'rooms', 'property_type', 'url', 'source', 
                                             'first_seen', 'last_seen', 'last_updated', 'active']}
                    
                    # Update property
                    cursor.execute('''
                    UPDATE properties SET 
                        address = ?,
                        city = ?,
                        price = ?,
                        area = ?,
                        rooms = ?,
                        property_type = ?,
                        url = ?,
                        last_seen = ?,
                        last_updated = ?,
                        extra_data = ?,
                        active = 1
                    WHERE id = ?
                    ''', (
                        property_data['address'],
                        property_data['city'],
                        property_data['price'],
                        property_data.get('area', 0),
                        property_data.get('rooms', 0),
                        property_data.get('property_type', 'Onbekend'),
                        property_data['url'],
                        current_time,
                        current_time,
                        json.dumps(extra_data),
                        property_data['id']
                    ))
                    
                    conn.commit()
                    self.logger.info(f"Updated property: {property_data['id']} with {len(changes)} changes")
                    return "updated", changes
                else:
                    # Just update last_seen timestamp
                    cursor.execute('''
                    UPDATE properties SET 
                        last_seen = ?,
                        active = 1
                    WHERE id = ?
                    ''', (current_time, property_data['id']))
                    
                    conn.commit()
                    self.logger.debug(f"Property unchanged: {property_data['id']}")
                    return "unchanged", []
            else:
                # New property
                # Prepare extra data (fields not in core table)
                extra_data = {k: v for k, v in property_data.items() 
                             if k not in ['id', 'address', 'city', 'price', 'area', 
                                         'rooms', 'property_type', 'url', 'source', 
                                         'first_seen', 'last_seen', 'last_updated', 'active']}
                
                # Insert new property
                cursor.execute('''
                INSERT INTO properties 
                (id, address, city, price, area, rooms, property_type, url, source, 
                 first_seen, last_seen, last_updated, extra_data, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    property_data['id'],
                    property_data['address'],
                    property_data['city'],
                    property_data['price'],
                    property_data.get('area', 0),
                    property_data.get('rooms', 0),
                    property_data.get('property_type', 'Onbekend'),
                    property_data['url'],
                    property_data['source'],
                    current_time,
                    current_time,
                    current_time,
                    json.dumps(extra_data)
                ))
                
                # Record new property in history
                cursor.execute('''
                INSERT INTO property_history 
                (property_id, change_type, change_date, new_value)
                VALUES (?, ?, ?, ?)
                ''', (
                    property_data['id'],
                    "new_property",
                    current_time,
                    f"New property: {property_data['address']}, {property_data['city']}"
                ))
                
                conn.commit()
                self.logger.info(f"Added new property: {property_data['id']}")
                return "new", []
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error in add_or_update_property: {str(e)}")
            return "error", []
        finally:
            if conn:
                conn.close()
    
    def mark_inactive_properties(self, active_ids: List[str], source: str) -> List[str]:
        """
        Mark properties as inactive if they're not in the active_ids list.
        
        Args:
            active_ids: List of active property IDs
            source: Source website name
            
        Returns:
            List of IDs that were marked as inactive
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find properties from this source that are currently active but not in active_ids
            placeholders = ','.join(['?'] * len(active_ids)) if active_ids else "''"
            query = f'''
            SELECT id FROM properties 
            WHERE source = ? AND active = 1 
            AND id NOT IN ({placeholders})
            '''
            
            params = [source] + active_ids
            cursor.execute(query, params)
            inactive_ids = [row[0] for row in cursor.fetchall()]
            
            if inactive_ids:
                # Mark these properties as inactive
                current_time = datetime.now().isoformat()
                
                for inactive_id in inactive_ids:
                    # Update property
                    cursor.execute('''
                    UPDATE properties SET 
                        active = 0,
                        last_updated = ?
                    WHERE id = ?
                    ''', (current_time, inactive_id))
                    
                    # Record in history
                    cursor.execute('''
                    INSERT INTO property_history 
                    (property_id, change_type, change_date, new_value)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        inactive_id,
                        "property_inactive",
                        current_time,
                        "Property no longer available"
                    ))
                
                conn.commit()
                self.logger.info(f"Marked {len(inactive_ids)} properties as inactive from source: {source}")
            
            return inactive_ids
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error in mark_inactive_properties: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_property(self, property_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a property by ID.
        
        Args:
            property_id: Property ID
            
        Returns:
            Property data dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
            property_data = cursor.fetchone()
            
            if property_data:
                columns = [desc[0] for desc in cursor.description]
                result = dict(zip(columns, property_data))
                
                # Parse extra_data
                if result['extra_data']:
                    try:
                        extra_data = json.loads(result['extra_data'])
                        result.update(extra_data)
                    except json.JSONDecodeError:
                        self.logger.warning(f"Failed to parse extra_data for property {property_id}")
                
                return result
            else:
                return None
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error in get_property: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_properties(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get properties with optional filtering.
        
        Args:
            filters: Optional filters to apply
                - min_price: Minimum price
                - max_price: Maximum price
                - city: City name
                - min_area: Minimum area
                - property_type: Property type
                - active_only: Only active properties (default True)
                
        Returns:
            List of property dictionaries
        """
        filters = filters or {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            cursor = conn.cursor()
            
            query = "SELECT * FROM properties WHERE 1=1"
            params = []
            
            # Apply filters
            if 'min_price' in filters:
                query += " AND price >= ?"
                params.append(filters['min_price'])
            
            if 'max_price' in filters:
                query += " AND price <= ?"
                params.append(filters['max_price'])
            
            if 'city' in filters:
                query += " AND city LIKE ?"
                params.append(f"%{filters['city']}%")
            
            if 'min_area' in filters:
                query += " AND area >= ?"
                params.append(filters['min_area'])
            
            if 'property_type' in filters:
                query += " AND property_type = ?"
                params.append(filters['property_type'])
            
            # By default, only return
(Content truncated due to size limit. Use line ranges to read in chunks)