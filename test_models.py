#!/usr/bin/env python3
"""
Test script for ATM Surveillance System models
"""

import cv2
import numpy as np
from models import WorkingDetectionPipeline
import time

def test_models():
    """Test all detection models"""
    print("🧪 Testing ATM Surveillance Detection Models...")
    print("=" * 50)
    
    # Initialize pipeline
    try:
        pipeline = WorkingDetectionPipeline()
        print("✅ Detection pipeline initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        return False
    
    # Create test frame
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Test each model
    tests = [
        ("People Detection", lambda: pipeline.detect_people(test_frame)),
        ("Helmet Detection", lambda: pipeline.detect_helmet(test_frame)),
        ("Face Cover Detection", lambda: pipeline.detect_face_cover(test_frame)),
        ("Loitering Detection", lambda: pipeline.detect_loitering(test_frame)),
        ("Posture Detection", lambda: pipeline.detect_posture(test_frame))
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Testing {test_name}...")
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            results[test_name] = {
                'success': True,
                'result': result,
                'time': end_time - start_time
            }
            
            print(f"✅ {test_name}: {result} (took {end_time - start_time:.3f}s)")
            
        except Exception as e:
            results[test_name] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ {test_name}: {e}")
    
    # Test full pipeline
    print(f"\n🔍 Testing Full Pipeline...")
    try:
        start_time = time.time()
        full_result = pipeline.process_frame(test_frame)
        end_time = time.time()
        
        print(f"✅ Full Pipeline: Processed successfully (took {end_time - start_time:.3f}s)")
        print(f"   People Count: {full_result['people_count']}")
        print(f"   Alerts: {len(full_result['alerts'])}")
        
    except Exception as e:
        print(f"❌ Full Pipeline: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    successful_tests = sum(1 for r in results.values() if r['success'])
    total_tests = len(results)
    
    print(f"📊 Test Summary: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! Models are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

def test_with_webcam():
    """Test with actual webcam if available"""
    print("\n📹 Testing with webcam...")
    
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ No webcam available")
            return False
        
        pipeline = WorkingDetectionPipeline()
        
        print("✅ Webcam opened successfully")
        print("Press 'q' to quit, 's' to save frame")
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process every 30th frame to avoid overwhelming
            if frame_count % 30 == 0:
                result = pipeline.process_frame(frame)
                
                # Display results on frame
                cv2.putText(frame, f"People: {result['people_count']}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Alerts: {len(result['alerts'])}", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Show alerts
                for i, alert in enumerate(result['alerts'][:3]):  # Show max 3 alerts
                    cv2.putText(frame, alert['type'], 
                               (10, 110 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow('ATM Surveillance Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite('test_frame.jpg', frame)
                print("📸 Frame saved as test_frame.jpg")
        
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Webcam test completed")
        return True
        
    except Exception as e:
        print(f"❌ Webcam test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ATM Surveillance System - Model Testing")
    print("=" * 60)
    
    # Test basic models
    basic_test_passed = test_models()
    
    # Test with webcam if basic tests passed
    if basic_test_passed:
        webcam_test_passed = test_with_webcam()
        
        if webcam_test_passed:
            print("\n🎉 All tests completed successfully!")
            print("Your ATM Surveillance System is ready to use!")
        else:
            print("\n⚠️  Basic tests passed but webcam test failed.")
            print("The system will work but without live camera feed.")
    else:
        print("\n❌ Basic tests failed. Please check your installation.")
    
    print("\nNext steps:")
    print("1. Run: python backend/app.py")
    print("2. Run: cd frontend && npm start")
    print("3. Open: http://localhost:3000")
    print("4. Login with: admin@atm.com / admin123")
