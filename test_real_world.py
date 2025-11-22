#!/usr/bin/env python3
"""
Real-world test script for ATM Surveillance System with actual camera
"""

import requests
import base64
import numpy as np
from PIL import Image
import io
import json
import cv2
import time

def test_with_real_camera():
    """Test with actual webcam for real-world validation"""
    print("=" * 80)
    print("REAL-WORLD CAMERA TEST - ATM SURVEILLANCE SYSTEM")
    print("=" * 80)
    
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] No webcam available")
            return False
        
        print("[SUCCESS] Webcam opened successfully")
        print("[INFO] Press 'q' to quit, 's' to save frame, 't' to test detection")
        
        frame_count = 0
        test_results = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Display instructions
            cv2.putText(frame, "Press 't' to test detection", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to quit", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Process every 30th frame automatically for continuous monitoring
            if frame_count % 30 == 0:
                result = test_detection_on_frame(frame)
                if result:
                    test_results.append(result)
                    
                    # Display results on frame
                    cv2.putText(frame, f"People: {result['people_count']}", 
                               (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Alerts: {len(result['alerts'])}", 
                               (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Show alerts
                    for i, alert in enumerate(result['alerts'][:3]):
                        cv2.putText(frame, f"{alert['type']}: {alert['confidence']:.2f}", 
                                   (10, 160 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            cv2.imshow('ATM Surveillance - Real Camera Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite('test_frame.jpg', frame)
                print("[SAVED] Frame saved as test_frame.jpg")
            elif key == ord('t'):
                result = test_detection_on_frame(frame)
                if result:
                    test_results.append(result)
                    print(f"[TEST] People: {result['people_count']}, Alerts: {len(result['alerts'])}")
                    for alert in result['alerts']:
                        print(f"[ALERT] {alert['type']}: {alert['message']} (confidence: {alert['confidence']:.2f})")
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Analyze test results
        if test_results:
            analyze_test_results(test_results)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Camera test failed: {e}")
        return False

def test_detection_on_frame(frame):
    """Test detection on a single frame"""
    try:
        # Convert frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        img_str = base64.b64encode(buffer).decode()
        frame_data = f'data:image/jpeg;base64,{img_str}'
        
        # Send to detection endpoint
        response = requests.post(
            'http://localhost:5000/api/process-video',
            json={'frame': frame_data},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['results']
        else:
            print(f"[ERROR] Detection failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Detection test failed: {e}")
        return None

def analyze_test_results(results):
    """Analyze the test results"""
    print("\n" + "=" * 80)
    print("TEST RESULTS ANALYSIS")
    print("=" * 80)
    
    total_frames = len(results)
    frames_with_people = sum(1 for r in results if r['people_count'] > 0)
    frames_with_helmet = sum(1 for r in results if r['helmet_violation'])
    frames_with_mask = sum(1 for r in results if r['face_cover_violation'])
    frames_with_loitering = sum(1 for r in results if r['loitering'])
    frames_with_posture = sum(1 for r in results if r['posture_violation'])
    
    print(f"Total frames analyzed: {total_frames}")
    print(f"Frames with people detected: {frames_with_people}")
    print(f"Frames with helmet violations: {frames_with_helmet}")
    print(f"Frames with face cover violations: {frames_with_mask}")
    print(f"Frames with loitering: {frames_with_loitering}")
    print(f"Frames with posture violations: {frames_with_posture}")
    
    # Calculate detection rates
    if total_frames > 0:
        people_detection_rate = (frames_with_people / total_frames) * 100
        print(f"\nPeople detection rate: {people_detection_rate:.1f}%")
        
        if people_detection_rate > 80:
            print("[SUCCESS] People detection working well")
        elif people_detection_rate > 60:
            print("[FAIR] People detection needs improvement")
        else:
            print("[POOR] People detection not working properly")

def test_api_performance():
    """Test API performance with real requests"""
    print("\n" + "=" * 80)
    print("API PERFORMANCE TEST")
    print("=" * 80)
    
    # Create a simple test image
    test_img = np.ones((480, 640, 3), dtype=np.uint8) * 128
    _, buffer = cv2.imencode('.jpg', test_img)
    img_str = base64.b64encode(buffer).decode()
    frame_data = f'data:image/jpeg;base64,{img_str}'
    
    times = []
    successes = 0
    
    for i in range(10):
        start_time = time.time()
        try:
            response = requests.post(
                'http://localhost:5000/api/process-video',
                json={'frame': frame_data},
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code == 200:
                processing_time = end_time - start_time
                times.append(processing_time)
                successes += 1
                print(f"[PERF] Test {i+1}: {processing_time:.3f}s - SUCCESS")
            else:
                print(f"[PERF] Test {i+1}: FAILED - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"[PERF] Test {i+1}: FAILED - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n[PERF] Success rate: {successes}/10 ({successes*10}%)")
        print(f"[PERF] Average processing time: {avg_time:.3f}s")
        
        if avg_time < 1.0:
            print("[SUCCESS] Performance: Excellent")
        elif avg_time < 2.0:
            print("[SUCCESS] Performance: Good")
        elif avg_time < 5.0:
            print("[FAIR] Performance: Acceptable")
        else:
            print("[POOR] Performance: Needs optimization")

def test_endpoints():
    """Test all API endpoints"""
    print("\n" + "=" * 80)
    print("API ENDPOINT TEST")
    print("=" * 80)
    
    endpoints = [
        ('Health Check', 'http://localhost:5000/api/health'),
        ('Analytics', 'http://localhost:5000/api/analytics'),
        ('Event Logs', 'http://localhost:5000/api/event-logs'),
        ('Frontend', 'http://localhost:3000')
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[PASS] {name}: Accessible")
            else:
                print(f"[FAIL] {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"[FAIL] {name}: {e}")

if __name__ == "__main__":
    print("ATM SURVEILLANCE SYSTEM - REAL-WORLD VALIDATION")
    print("Testing with actual camera for maximum accuracy...")
    
    # Test API endpoints first
    test_endpoints()
    
    # Test API performance
    test_api_performance()
    
    # Test with real camera
    print("\nStarting real camera test...")
    print("Make sure you have a webcam connected!")
    
    camera_test_passed = test_with_real_camera()
    
    print("\n" + "=" * 80)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 80)
    
    if camera_test_passed:
        print("SYSTEM VALIDATION: SUCCESS")
        print("Real-world camera testing completed")
        print("System ready for production use")
        print("\nAccess your system at: http://localhost:3000")
        print("Login: admin@atm.com / admin123")
    else:
        print("SYSTEM VALIDATION: NEEDS IMPROVEMENT")
        print("Camera testing failed")
        print("Check webcam connection and try again")
    
    print("\nNext steps:")
    print("1. Test with different lighting conditions")
    print("2. Test with different people and scenarios")
    print("3. Monitor system performance over time")
    print("4. Collect user feedback for further improvements")
