#!/usr/bin/env python3
"""
Simple test script for ATM Surveillance System with SQLite
Tests database functionality and basic model loading
"""

import sys
import os
import cv2
import numpy as np
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_database():
    """Test database functionality"""
    print("🗄️  Testing Database...")
    print("=" * 50)
    
    try:
        from backend.app import app, db, Admin, EventLog, DetectionStats
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # Create tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Test admin user creation
            admin = Admin.query.filter_by(email='admin@atm.com').first()
            if not admin:
                admin = Admin(
                    email='admin@atm.com',
                    password_hash=generate_password_hash('admin123')
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created successfully")
            else:
                print("✅ Admin user already exists")
            
            # Test event log creation
            event = EventLog(
                event_type='test',
                description='Test event for SQLite verification',
                confidence=0.95
            )
            db.session.add(event)
            db.session.commit()
            print("✅ Event log created successfully")
            
            # Test detection stats creation
            today = datetime.utcnow().date()
            stats = DetectionStats.query.filter_by(date=today).first()
            if not stats:
                stats = DetectionStats(
                    date=today,
                    people_count=10,
                    helmet_violations=2,
                    face_cover_violations=3,
                    loitering_events=1,
                    posture_violations=2
                )
                db.session.add(stats)
                db.session.commit()
                print("✅ Detection stats created successfully")
            else:
                print("✅ Detection stats already exist")
            
            # Test queries
            event_count = EventLog.query.count()
            admin_count = Admin.query.count()
            stats_count = DetectionStats.query.count()
            
            print(f"✅ Database queries working:")
            print(f"   - Event logs: {event_count}")
            print(f"   - Admin users: {admin_count}")
            print(f"   - Detection stats: {stats_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False

def test_detection_models():
    """Test detection models"""
    print("\n🧪 Testing Detection Models...")
    print("=" * 50)
    
    try:
        from backend.models import WorkingDetectionPipeline
        
        # Initialize detection pipeline
        pipeline = WorkingDetectionPipeline()
        print("✅ Detection pipeline initialized successfully")
        
        # Create a test frame (random image)
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test each detection method
        print("\n1. Testing People Detection...")
        people_count, conf = pipeline.detect_people(test_frame)
        print(f"   People detected: {people_count}, Confidence: {conf:.2f}")
        
        print("\n2. Testing Helmet Detection...")
        has_helmet, conf = pipeline.detect_helmet(test_frame)
        print(f"   Helmet detected: {has_helmet}, Confidence: {conf:.2f}")
        
        print("\n3. Testing Face Cover Detection...")
        has_face_cover, conf = pipeline.detect_face_cover(test_frame)
        print(f"   Face cover detected: {has_face_cover}, Confidence: {conf:.2f}")
        
        print("\n4. Testing Loitering Detection...")
        is_loitering, conf = pipeline.detect_loitering(test_frame)
        print(f"   Loitering detected: {is_loitering}, Confidence: {conf:.2f}")
        
        print("\n5. Testing Posture Detection...")
        bad_posture, conf = pipeline.detect_posture(test_frame)
        print(f"   Bad posture detected: {bad_posture}, Confidence: {conf:.2f}")
        
        print("\n6. Testing Complete Frame Processing...")
        results = pipeline.process_frame(test_frame)
        print(f"   Results: {results}")
        
        print("\n✅ All detection models working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing detection models: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints...")
    print("=" * 50)
    
    try:
        from backend.app import app
        
        with app.test_client() as client:
            # Test health check
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ Health check endpoint working")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
            
            # Test analytics endpoint
            response = client.get('/api/analytics')
            if response.status_code == 200:
                print("✅ Analytics endpoint working")
            else:
                print(f"❌ Analytics failed: {response.status_code}")
                return False
            
            # Test event logs endpoint
            response = client.get('/api/event-logs')
            if response.status_code == 200:
                print("✅ Event logs endpoint working")
            else:
                print(f"❌ Event logs failed: {response.status_code}")
                return False
            
            print("✅ All API endpoints working correctly!")
            return True
            
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 ATM Surveillance System - SQLite Test Suite")
    print("=" * 60)
    
    # Test database
    db_ok = test_database()
    
    # Test detection models
    models_ok = test_detection_models()
    
    # Test API endpoints
    api_ok = test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"   Detection Models: {'✅ PASS' if models_ok else '❌ FAIL'}")
    print(f"   API Endpoints: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if models_ok and db_ok and api_ok:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Run: python backend/app.py")
        print("2. Open: http://localhost:5000")
        print("3. Login with: admin@atm.com / admin123")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
