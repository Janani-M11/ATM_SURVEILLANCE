#!/usr/bin/env python3
"""
Database setup script for ATM Surveillance System
Creates the database and initializes with admin user
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from werkzeug.security import generate_password_hash

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'S@dh5518!',  # Updated password
    'database': 'atmsurvelliance'
}

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_CONFIG['database'],))
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"✅ Database '{DB_CONFIG['database']}' created successfully")
        else:
            print(f"ℹ️  Database '{DB_CONFIG['database']}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables():
    """Create all required tables"""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        # Create tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS admin (
                id SERIAL PRIMARY KEY,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS event_log (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                confidence FLOAT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path VARCHAR(255)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS detection_stats (
                id SERIAL PRIMARY KEY,
                date DATE DEFAULT CURRENT_DATE,
                people_count INTEGER DEFAULT 0,
                helmet_violations INTEGER DEFAULT 0,
                face_cover_violations INTEGER DEFAULT 0,
                loitering_events INTEGER DEFAULT 0,
                posture_violations INTEGER DEFAULT 0,
                UNIQUE(date)
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        conn.commit()
        print("✅ All tables created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_admin_user():
    """Create the default admin user"""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM admin WHERE email = %s", ('admin@atm.com',))
        exists = cursor.fetchone()
        
        if not exists:
            # Create admin user
            password_hash = generate_password_hash('admin123')
            cursor.execute(
                "INSERT INTO admin (email, password_hash) VALUES (%s, %s)",
                ('admin@atm.com', password_hash)
            )
            conn.commit()
            print("✅ Admin user created successfully")
            print("   Email: admin@atm.com")
            print("   Password: admin123")
        else:
            print("ℹ️  Admin user already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def insert_sample_data():
    """Insert sample data for testing"""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        # Insert sample event logs
        sample_events = [
            ('people_count', 'Multiple people detected: 4', 0.85),
            ('helmet', 'Helmet detected - Please remove helmet', 0.92),
            ('face_cover', 'Face covering detected - Please remove mask', 0.88),
            ('loitering', 'Loitering detected - Please move away', 0.76),
            ('posture', 'Improper posture detected - Please stand straight', 0.81),
            ('people_count', 'Multiple people detected: 3', 0.78),
            ('helmet', 'Helmet detected - Please remove helmet', 0.89),
            ('face_cover', 'Face covering detected - Please remove scarf', 0.91)
        ]
        
        for event_type, description, confidence in sample_events:
            cursor.execute(
                "INSERT INTO event_log (event_type, description, confidence) VALUES (%s, %s, %s)",
                (event_type, description, confidence)
            )
        
        # Insert sample detection stats
        cursor.execute("""
            INSERT INTO detection_stats (date, people_count, helmet_violations, face_cover_violations, loitering_events, posture_violations)
            VALUES (CURRENT_DATE, 25, 3, 5, 2, 4)
            ON CONFLICT (date) DO NOTHING
        """)
        
        conn.commit()
        print("✅ Sample data inserted successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error inserting sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up ATM Surveillance System Database...")
    print("=" * 50)
    
    # Step 1: Create database
    print("\n1. Creating database...")
    if not create_database():
        sys.exit(1)
    
    # Step 2: Create tables
    print("\n2. Creating tables...")
    if not create_tables():
        sys.exit(1)
    
    # Step 3: Create admin user
    print("\n3. Creating admin user...")
    if not create_admin_user():
        sys.exit(1)
    
    # Step 4: Insert sample data
    print("\n4. Inserting sample data...")
    if not insert_sample_data():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Install Python dependencies: pip install -r requirements.txt")
    print("2. Start the Flask backend: python backend/app.py")
    print("3. Install frontend dependencies: cd frontend && npm install")
    print("4. Start the React frontend: cd frontend && npm start")
    print("\nLogin credentials:")
    print("Email: admin@atm.com")
    print("Password: admin123")

if __name__ == "__main__":
    main()
