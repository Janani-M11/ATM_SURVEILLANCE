#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script for ATM Surveillance System
Creates database, tables, and initial admin user
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'atm_surveillance')
}

def test_connection():
    """Test PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"ERROR: Connection failed: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL is installed and running")
        print("2. Database credentials are correct")
        print("3. Update .env file with correct credentials")
        return False

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (without specifying database)
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (DB_CONFIG['database'],)
        )
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DB_CONFIG['database'])
                )
            )
            print(f"SUCCESS: Database '{DB_CONFIG['database']}' created successfully")
        else:
            print(f"INFO: Database '{DB_CONFIG['database']}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"ERROR: Error creating database: {e}")
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
        
        # Create tables with PostgreSQL syntax
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
                date DATE DEFAULT CURRENT_DATE UNIQUE,
                people_count INTEGER DEFAULT 0,
                helmet_violations INTEGER DEFAULT 0,
                face_cover_violations INTEGER DEFAULT 0,
                loitering_events INTEGER DEFAULT 0,
                posture_violations INTEGER DEFAULT 0
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_event_log_timestamp ON event_log(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_event_log_type ON event_log(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_detection_stats_date ON detection_stats(date)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        print("SUCCESS: All tables and indexes created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"ERROR: Error creating tables: {e}")
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
            print("SUCCESS: Admin user created successfully")
            print("   Email: admin@atm.com")
            print("   Password: admin123")
        else:
            print("INFO: Admin user already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"ERROR: Error creating admin user: {e}")
        return False

def insert_sample_data():
    """Insert sample data for testing (optional)"""
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
        
        # Check if sample data already exists
        cursor.execute("SELECT COUNT(*) FROM event_log")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("INFO: Sample data already exists, skipping...")
            cursor.close()
            conn.close()
            return True
        
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
        
        # Insert sample detection stats for the last 7 days
        today = datetime.now().date()
        for i in range(7):
            date = today - timedelta(days=i)
            cursor.execute("""
                INSERT INTO detection_stats (date, people_count, helmet_violations, 
                          face_cover_violations, loitering_events, posture_violations)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (date) DO NOTHING
            """, (date, 25 + i*2, 3 + i, 5 + i, 2 + i//2, 4 + i))
        
        conn.commit()
        print("SUCCESS: Sample data inserted successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"ERROR: Error inserting sample data: {e}")
        return False

def main():
    """Main setup function"""
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("Setting up ATM Surveillance System Database (PostgreSQL)...")
    print("=" * 60)
    print(f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"User: {DB_CONFIG['user']}")
    print(f"Database: {DB_CONFIG['database']}")
    print("=" * 60)
    
    # Step 0: Test connection
    print("\n0. Testing PostgreSQL connection...")
    if not test_connection():
        print("\nERROR: Cannot connect to PostgreSQL. Please check your configuration.")
        print("\nCreate a .env file with:")
        print("DB_HOST=localhost")
        print("DB_PORT=5432")
        print("DB_USER=postgres")
        print("DB_PASSWORD=your_password")
        print("DB_NAME=atm_surveillance")
        sys.exit(1)
    
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
    
    # Step 4: Insert sample data (optional)
    print("\n4. Inserting sample data...")
    insert_sample_data()  # Don't fail if this doesn't work
    
    print("\n" + "=" * 60)
    print("SUCCESS: PostgreSQL database setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Make sure your .env file has the correct database configuration")
    print("2. Start the Flask backend: python backend/app.py")
    print("3. Start the React frontend: cd frontend && npm start")
    print("\nLogin credentials:")
    print("Email: admin@atm.com")
    print("Password: admin123")
    print("\nDatabase connection string:")
    print(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

if __name__ == "__main__":
    main()

