#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database schema update for custom realtors.
This script updates the database schema to support custom realtors.
"""

import sqlite3
import json
import os

def update_database_schema():
    """Update the database schema to support custom realtors."""
    
    # Database file path
    db_path = 'huizenzoeker.db'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Creating new database: {db_path}")
    else:
        print(f"Updating existing database: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create realtors table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS realtors (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        website TEXT NOT NULL,
        search_url TEXT NOT NULL,
        listing_selector TEXT NOT NULL,
        title_selector TEXT,
        price_selector TEXT,
        area_selector TEXT,
        rooms_selector TEXT,
        link_selector TEXT,
        city_selector TEXT,
        active INTEGER DEFAULT 1,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Add custom_realtor column to properties table if it doesn't exist
    cursor.execute("PRAGMA table_info(properties)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'properties' in [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
        if 'realtor_id' not in column_names:
            cursor.execute('ALTER TABLE properties ADD COLUMN realtor_id TEXT')
            print("Added realtor_id column to properties table")
    else:
        # Create properties table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id TEXT PRIMARY KEY,
            address TEXT,
            city TEXT,
            price INTEGER,
            area INTEGER,
            rooms INTEGER,
            property_type TEXT,
            url TEXT,
            source TEXT,
            realtor_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created properties table with realtor_id column")
    
    # Insert default realtors
    default_realtors = [
        {
            'id': 'klipenvw',
            'name': 'Klip & VW',
            'website': 'klipenvw.nl',
            'search_url': 'https://www.klipenvw.nl/aanbod/woningaanbod/',
            'listing_selector': '.property-item',
            'title_selector': '.property-title',
            'price_selector': '.property-price',
            'area_selector': '.property-area',
            'rooms_selector': '.property-rooms',
            'link_selector': '.property-link',
            'city_selector': '.property-city',
            'active': 1,
            'notes': 'Default realtor'
        },
        {
            'id': 'bijdevaate',
            'name': 'Bij de Vaate Makelaardij',
            'website': 'bijdevaatemakelaardij.nl',
            'search_url': 'https://www.bijdevaatemakelaardij.nl/aanbod',
            'listing_selector': '.property-item',
            'title_selector': '.property-title',
            'price_selector': '.property-price',
            'area_selector': '.property-area',
            'rooms_selector': '.property-rooms',
            'link_selector': '.property-link',
            'city_selector': '.property-city',
            'active': 1,
            'notes': 'Default realtor'
        },
        {
            'id': 'ooms',
            'name': 'Ooms Makelaars',
            'website': 'ooms.com',
            'search_url': 'https://www.ooms.com/woningaanbod',
            'listing_selector': '.property-item',
            'title_selector': '.property-title',
            'price_selector': '.property-price',
            'area_selector': '.property-area',
            'rooms_selector': '.property-rooms',
            'link_selector': '.property-link',
            'city_selector': '.property-city',
            'active': 1,
            'notes': 'Default realtor'
        },
        {
            'id': 'vbrmakelaars',
            'name': 'VBR Makelaars',
            'website': 'vbrmakelaars.nl',
            'search_url': 'https://www.vbrmakelaars.nl/aanbod',
            'listing_selector': '.property-item',
            'title_selector': '.property-title',
            'price_selector': '.property-price',
            'area_selector': '.property-area',
            'rooms_selector': '.property-rooms',
            'link_selector': '.property-link',
            'city_selector': '.property-city',
            'active': 1,
            'notes': 'Default realtor'
        },
        {
            'id': 'ruimzicht',
            'name': 'Ruimzicht Makelaardij',
            'website': 'ruimzicht.nl',
            'search_url': 'https://www.ruimzicht.nl/woningen',
            'listing_selector': '.property-item',
            'title_selector': '.property-title',
            'price_selector': '.property-price',
            'area_selector': '.property-area',
            'rooms_selector': '.property-rooms',
            'link_selector': '.property-link',
            'city_selector': '.property-city',
            'active': 1,
            'notes': 'Default realtor'
        }
    ]
    
    # Insert default realtors if they don't exist
    for realtor in default_realtors:
        cursor.execute('''
        INSERT OR IGNORE INTO realtors (
            id, name, website, search_url, listing_selector, 
            title_selector, price_selector, area_selector, 
            rooms_selector, link_selector, city_selector, 
            active, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            realtor['id'], realtor['name'], realtor['website'], 
            realtor['search_url'], realtor['listing_selector'],
            realtor['title_selector'], realtor['price_selector'], 
            realtor['area_selector'], realtor['rooms_selector'],
            realtor['link_selector'], realtor['city_selector'],
            realtor['active'], realtor['notes']
        ))
    
    # Create API endpoints for realtors
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_endpoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL,
        method TEXT NOT NULL,
        handler TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insert API endpoints for realtors
    api_endpoints = [
        {
            'path': '/api/realtors',
            'method': 'GET',
            'handler': 'get_realtors',
            'description': 'Get all realtors'
        },
        {
            'path': '/api/realtors',
            'method': 'POST',
            'handler': 'create_realtor',
            'description': 'Create a new realtor'
        },
        {
            'path': '/api/realtors/:id',
            'method': 'GET',
            'handler': 'get_realtor',
            'description': 'Get a realtor by ID'
        },
        {
            'path': '/api/realtors/:id',
            'method': 'PUT',
            'handler': 'update_realtor',
            'description': 'Update a realtor'
        },
        {
            'path': '/api/realtors/:id',
            'method': 'DELETE',
            'handler': 'delete_realtor',
            'description': 'Delete a realtor'
        }
    ]
    
    for endpoint in api_endpoints:
        cursor.execute('''
        INSERT OR IGNORE INTO api_endpoints (
            path, method, handler, description
        ) VALUES (?, ?, ?, ?)
        ''', (
            endpoint['path'], endpoint['method'], 
            endpoint['handler'], endpoint['description']
        ))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database schema updated successfully")

if __name__ == "__main__":
    update_database_schema()
