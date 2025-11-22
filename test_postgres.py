#!/usr/bin/env python3
"""
Test PostgreSQL connection for ATM Surveillance System
"""

import psycopg2
import sys

def test_connection():
    """Test PostgreSQL connection with different configurations"""
    
    # Try different connection strings
    connection_strings = [
        'postgresql://postgres:S%40dh5518%21@localhost:5432/postgres',
        'postgresql://postgres:S%40dh5518%21@localhost:5432/atmsurvelliance',
        'postgresql://postgres@localhost:5432/postgres',
        'postgresql://postgres@localhost:5432/atmsurvelliance'
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\nTesting connection {i}: {conn_str}")
        try:
            conn = psycopg2.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"SUCCESS: Connection successful!")
            print(f"PostgreSQL version: {version[0]}")
            cursor.close()
            conn.close()
            return conn_str
        except psycopg2.Error as e:
            print(f"FAILED: {e}")
    
    return None

def create_database_if_needed(conn_str):
    """Create the database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect('postgresql://postgres:S%40dh5518%21@localhost:5432/postgres')
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'atmsurvelliance'")
        exists = cursor.fetchone()
        
        if not exists:
            print("\nCreating database 'atmsurvelliance'...")
            cursor.execute("CREATE DATABASE atmsurvelliance")
            print("SUCCESS: Database created successfully")
        else:
            print("INFO: Database 'atmsurvelliance' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing PostgreSQL Connection for ATM Surveillance System")
    print("=" * 60)
    
    # Test connection
    working_conn = test_connection()
    
    if working_conn:
        print(f"\nSUCCESS: Found working connection: {working_conn}")
        
        # Create database if needed
        if create_database_if_needed(working_conn):
            print("\nPostgreSQL setup completed successfully!")
            print("\nNext steps:")
            print("1. Update your config.py with the working connection string")
            print("2. Run: python backend/setup_database.py")
            print("3. Run: python backend/app.py")
        else:
            print("\nDatabase creation failed")
    else:
        print("\nNo working PostgreSQL connection found")
        print("\nTroubleshooting steps:")
        print("1. Make sure PostgreSQL service is running")
        print("2. Check if password 'S@dh5518!' is correct")
        print("3. Try connecting with pgAdmin or psql command line")
        print("4. Check PostgreSQL configuration files")