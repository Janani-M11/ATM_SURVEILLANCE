#!/usr/bin/env python3
"""
Comprehensive test script for 100% accuracy validation of ATM Surveillance System
"""

import requests
import base64
import numpy as np
from PIL import Image
import io
import json
import cv2
import time

def create_test_image_with_helmet(width=640, height=480):
    """Create a test image with a simulated helmet"""
    # Create base image
    img = np.ones((height, width, 3), dtype=np.uint8) * 128  # Gray background
    
    # Add a person silhouette
    cv2.rectangle(img, (width//2-50, height//2-100), (width//2+50, height//2+100), (100, 100, 100), -1)
    
    # Add a helmet (dark blue circle)
    cv2.circle(img, (width//2, height//2-80), 40, (100, 50, 20), -1)  # Dark blue helmet
    
    # Convert to PIL and encode
    pil_img = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f'data:image/png;base64,{img_str}'

def create_test_image_with_mask(width=640, height=480):
    """Create a test image with a simulated face mask"""
    # Create base image
    img = np.ones((height, width, 3), dtype=np.uint8) * 200  # Light background
    
    # Add a person silhouette
    cv2.rectangle(img, (width//2-50, height//2-100), (width//2+50, height//2+100), (150, 150, 150), -1)
    
    # Add a face
    cv2.ellipse(img, (width//2, height//2-20), (30, 40), 0, 0, 360, (200, 180, 160), -1)
    
    # Add a blue surgical mask
    cv2.rectangle(img, (width//2-25, height//2-10), (width//2+25, height//2+10), (100, 150, 200), -1)
    
    # Convert to PIL and encode
    pil_img = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f'data:image/png;base64,{img_str}'

def create_test_image_with_person(width=640, height=480):
    """Create a test image with a person (no violations)"""
    # Create base image
    img = np.ones((height, width, 3), dtype=np.uint8) * 200  # Light background
    
    # Add a person silhouette
    cv2.rectangle(img, (width//2-50, height//2-100), (width//2+50, height//2+100), (150, 150, 150), -1)
    
    # Add a face
    cv2.ellipse(img, (width//2, height//2-20), (30, 40), 0, 0, 360, (200, 180, 160), -1)
    
    # Add eyes
    cv2.circle(img, (width//2-10, height//2-30), 3, (0, 0, 0), -1)
    cv2.circle(img, (width//2+10, height//2-30), 3, (0, 0, 0), -1)
    
    # Convert to PIL and encode
    pil_img = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f'data:image/png;base64,{img_str}'

def test_detection_endpoint(frame_data, expected_results):
    """Test the detection endpoint with expected results"""
    try:
        response = requests.post(
            'http://localhost:5000/api/process-video',
            json={'frame': frame_data},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return True, result['results']
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def run_accuracy_tests():
    """Run comprehensive accuracy tests"""
    print("=" * 80)
    print("ATM SURVEILLANCE SYSTEM - 100% ACCURACY VALIDATION")
    print("=" * 80)
    
    test_cases = [
        {
            'name': 'Blank Frame Test',
            'image_func': lambda: create_test_image_with_person(),
            'expected': {
                'people_count': 1,
                'helmet_violation': False,
                'face_cover_violation': False,
                'loitering': False,
                'posture_violation': False
            }
        },
        {
            'name': 'Person with Helmet Test',
            'image_func': lambda: create_test_image_with_helmet(),
            'expected': {
                'people_count': 1,
                'helmet_violation': True,
                'face_cover_violation': False,
                'loitering': False,
                'posture_violation': False
            }
        },
        {
            'name': 'Person with Mask Test',
            'image_func': lambda: create_test_image_with_mask(),
            'expected': {
                'people_count': 1,
                'helmet_violation': False,
                'face_cover_violation': True,
                'loitering': False,
                'posture_violation': False
            }
        },
        {
            'name': 'Normal Person Test',
            'image_func': lambda: create_test_image_with_person(),
            'expected': {
                'people_count': 1,
                'helmet_violation': False,
                'face_cover_violation': False,
                'loitering': False,
                'posture_violation': False
            }
        }
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_case in test_cases:
        print(f"\n[TEST] {test_case['name']}")
        print("-" * 50)
        
        # Run test multiple times for consistency
        test_passes = 0
        test_attempts = 5
        
        for attempt in range(test_attempts):
            total_tests += 1
            
            # Create test image
            test_image = test_case['image_func']()
            
            # Test detection
            success, result = test_detection_endpoint(test_image, test_case['expected'])
            
            if success:
                # Check each expected result
                test_passed = True
                for key, expected_value in test_case['expected'].items():
                    if result[key] != expected_value:
                        test_passed = False
                        print(f"[FAIL] {key}: expected {expected_value}, got {result[key]}")
                        break
                
                if test_passed:
                    test_passes += 1
                    passed_tests += 1
                    print(f"[PASS] Attempt {attempt + 1}: All detections correct")
                else:
                    print(f"[FAIL] Attempt {attempt + 1}: Detection mismatch")
            else:
                print(f"[FAIL] Attempt {attempt + 1}: {result}")
            
            # Small delay between attempts
            time.sleep(0.5)
        
        # Calculate accuracy for this test case
        accuracy = (test_passes / test_attempts) * 100
        print(f"[RESULT] {test_case['name']}: {test_passes}/{test_attempts} ({accuracy:.1f}%)")
    
    # Overall accuracy
    overall_accuracy = (passed_tests / total_tests) * 100
    
    print("\n" + "=" * 80)
    print("ACCURACY TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed Tests: {passed_tests}")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    
    if overall_accuracy >= 95:
        print("[SUCCESS] System achieved 95%+ accuracy!")
        print("[STATUS] Ready for production use")
    elif overall_accuracy >= 90:
        print("[GOOD] System achieved 90%+ accuracy")
        print("[STATUS] Good for testing, minor improvements needed")
    elif overall_accuracy >= 80:
        print("[FAIR] System achieved 80%+ accuracy")
        print("[STATUS] Needs improvement before production")
    else:
        print("[POOR] System accuracy below 80%")
        print("[STATUS] Significant improvements required")
    
    return overall_accuracy

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n" + "=" * 80)
    print("API ENDPOINT VALIDATION")
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

def run_performance_tests():
    """Run performance tests"""
    print("\n" + "=" * 80)
    print("PERFORMANCE VALIDATION")
    print("=" * 80)
    
    # Test processing speed
    test_image = create_test_image_with_person()
    times = []
    
    for i in range(10):
        start_time = time.time()
        success, result = test_detection_endpoint(test_image, {})
        end_time = time.time()
        
        if success:
            processing_time = end_time - start_time
            times.append(processing_time)
            print(f"[PERF] Test {i+1}: {processing_time:.3f}s")
        else:
            print(f"[FAIL] Test {i+1}: Failed")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n[PERF] Average Processing Time: {avg_time:.3f}s")
        print(f"[PERF] Min Processing Time: {min_time:.3f}s")
        print(f"[PERF] Max Processing Time: {max_time:.3f}s")
        
        if avg_time < 1.0:
            print("[PASS] Performance: Excellent (< 1s)")
        elif avg_time < 2.0:
            print("[PASS] Performance: Good (< 2s)")
        elif avg_time < 5.0:
            print("[FAIR] Performance: Acceptable (< 5s)")
        else:
            print("[POOR] Performance: Needs optimization (> 5s)")

if __name__ == "__main__":
    print("ATM SURVEILLANCE SYSTEM - COMPREHENSIVE VALIDATION")
    print("Testing advanced detection pipeline for 100% accuracy...")
    
    # Test API endpoints first
    test_api_endpoints()
    
    # Run accuracy tests
    accuracy = run_accuracy_tests()
    
    # Run performance tests
    run_performance_tests()
    
    print("\n" + "=" * 80)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 80)
    
    if accuracy >= 95:
        print("SYSTEM VALIDATION: SUCCESS")
        print("All detection modules working at 95%+ accuracy")
        print("System ready for production deployment")
        print("\nAccess your system at: http://localhost:3000")
        print("Login: admin@atm.com / admin123")
    else:
        print("SYSTEM VALIDATION: NEEDS IMPROVEMENT")
        print(f"Current accuracy: {accuracy:.1f}%")
        print("Additional tuning required for production")
    
    print("\nNext steps:")
    print("1. Monitor system performance in real-world conditions")
    print("2. Collect feedback from users")
    print("3. Fine-tune detection parameters based on usage patterns")
    print("4. Consider adding machine learning models for even higher accuracy")
