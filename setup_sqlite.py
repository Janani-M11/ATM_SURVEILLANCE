#!/usr/bin/env python3
"""
Simple database setup script for ATM Surveillance System using SQLite
"""

import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Database file path
DB_PATH = 'atm_surveillance.db'

def create_database():
    """Create SQLite database and tables"""
    try:
        # Connect to SQLite database (creates if doesn't exist)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS event_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                confidence FLOAT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path VARCHAR(255)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS detection_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_admin_user():
    """Create the default admin user"""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM admin WHERE email = ?", ('admin@atm.com',))
        exists = cursor.fetchone()
        
        if not exists:
            # Create admin user
            password_hash = generate_password_hash('admin123')
            cursor.execute(
                "INSERT INTO admin (email, password_hash) VALUES (?, ?)",
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
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def insert_sample_data():
    """Insert sample data for testing"""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
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
                "INSERT INTO event_log (event_type, description, confidence) VALUES (?, ?, ?)",
                (event_type, description, confidence)
            )
        
        # Insert sample detection stats for the last 7 days
        today = datetime.now().date()
        
        for i in range(7):
            date = today - timedelta(days=i)
            cursor.execute("""
                INSERT OR IGNORE INTO detection_stats (date, people_count, helmet_violations, face_cover_violations, loitering_events, posture_violations)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date, 25 + i*2, 3 + i, 5 + i, 2 + i//2, 4 + i))
        
        conn.commit()
        print("✅ Sample data inserted successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up ATM Surveillance System Database (SQLite)...")
    print("=" * 60)
    
    # Step 1: Create database and tables
    print("\n1. Creating database and tables...")
    if not create_database():
        return False
    
    # Step 2: Create admin user
    print("\n2. Creating admin user...")
    if not create_admin_user():
        return False
    
    # Step 3: Insert sample data
    print("\n3. Inserting sample data...")
    if not insert_sample_data():
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Database setup completed successfully!")
    print(f"📁 Database file: {os.path.abspath(DB_PATH)}")
    print("\nNext steps:")
    print("1. Start the Flask backend: python backend/app.py")
    print("2. Install frontend dependencies: cd frontend && npm install")
    print("3. Start the React frontend: cd frontend && npm start")
    print("\nLogin credentials:")
    print("Email: admin@atm.com")
    print("Password: admin123")
    
    return True

if __name__ == "__main__":
    main()

