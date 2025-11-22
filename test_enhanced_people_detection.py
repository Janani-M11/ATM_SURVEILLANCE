#!/usr/bin/env python3
"""
Test script for Enhanced People Detection
Tests the new enhanced people detection system
"""

import cv2
import numpy as np
import time
from backend.enhanced_people_detection import EnhancedPeopleDetection
from backend.models_enhanced_people import EnhancedPeopleDetectionPipeline

def create_test_frame_with_people(width=640, height=480, num_people=1):
    """Create a synthetic test frame with specified number of people"""
    frame = np.ones((height, width, 3), dtype=np.uint8) * 200  # Light gray background
    
    for i in range(num_people):
        # Calculate position for each person
        x = 100 + (i * 200) % (width - 200)
        y = 100
        
        # Draw person-like shape
        # Body (rectangle)
        cv2.rectangle(frame, (x, y), (x + 60, y + 200), (100, 100, 100), -1)
        
        # Head (circle)
        cv2.circle(frame, (x + 30, y - 20), 25, (180, 150, 130), -1)
        
        # Arms (lines)
        cv2.line(frame, (x - 10, y + 50), (x + 70, y + 50), (100, 100, 100), 8)
        
        # Legs (lines)
        cv2.line(frame, (x + 15, y + 200), (x + 15, y + 280), (100, 100, 100), 8)
        cv2.line(frame, (x + 45, y + 200), (x + 45, y + 280), (100, 100, 100), 8)
    
    return frame

def create_test_frame_with_helmet(width=640, height=480):
    """Create a test frame with a person wearing a helmet"""
    frame = create_test_frame_with_people(width, height, 1)
    
    # Add a helmet (dark blue circle on head)
    cv2.circle(frame, (190, 80), 30, (100, 50, 20), -1)  # Dark blue helmet
    
    return frame

def create_test_frame_with_mask(width=640, height=480):
    """Create a test frame with a person wearing a mask"""
    frame = create_test_frame_with_people(width, height, 1)
    
    # Add a blue mask on lower face
    cv2.rectangle(frame, (160, 110), (220, 130), (200, 100, 50), -1)
    
    return frame

def test_enhanced_people_detection():
    """Test the enhanced people detection system"""
    print("=" * 80)
    print("ENHANCED PEOPLE DETECTION TEST")
    print("=" * 80)
    
    # Initialize the enhanced detection pipeline
    print("Initializing Enhanced People Detection Pipeline...")
    pipeline = EnhancedPeopleDetectionPipeline()
    
    # Test cases
    test_cases = [
        {
            'name': 'No People',
            'frame_func': lambda: create_test_frame_with_people(640, 480, 0),
            'expected_people': 0
        },
        {
            'name': '1 Person',
            'frame_func': lambda: create_test_frame_with_people(640, 480, 1),
            'expected_people': 1
        },
        {
            'name': '2 People',
            'frame_func': lambda: create_test_frame_with_people(640, 480, 2),
            'expected_people': 2
        },
        {
            'name': '3 People',
            'frame_func': lambda: create_test_frame_with_people(640, 480, 3),
            'expected_people': 3
        },
        {
            'name': 'Person with Helmet',
            'frame_func': lambda: create_test_frame_with_helmet(640, 480),
            'expected_people': 1
        },
        {
            'name': 'Person with Mask',
            'frame_func': lambda: create_test_frame_with_mask(640, 480),
            'expected_people': 1
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
            
            # Create test frame
            test_frame = test_case['frame_func']()
            
            # Test people detection
            people_count, confidence = pipeline.detect_people(test_frame)
            
            # Check if detection is correct (allow some tolerance)
            expected = test_case['expected_people']
            tolerance = 1 if expected > 0 else 0  # Allow 1 person tolerance for synthetic images
            
            if abs(people_count - expected) <= tolerance:
                test_passes += 1
                passed_tests += 1
                print(f"[PASS] Attempt {attempt + 1}: Detected {people_count} people (expected {expected}) - Confidence: {confidence:.2f}")
            else:
                print(f"[FAIL] Attempt {attempt + 1}: Detected {people_count} people (expected {expected}) - Confidence: {confidence:.2f}")
            
            # Small delay between attempts
            time.sleep(0.1)
        
        # Calculate accuracy for this test case
        accuracy = (test_passes / test_attempts) * 100
        print(f"[RESULT] {test_case['name']}: {test_passes}/{test_attempts} ({accuracy:.1f}%)")
    
    # Overall accuracy
    overall_accuracy = (passed_tests / total_tests) * 100
    
    print("\n" + "=" * 80)
    print("ENHANCED PEOPLE DETECTION TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed Tests: {passed_tests}")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    
    if overall_accuracy >= 90:
        print("[SUCCESS] Enhanced people detection achieved 90%+ accuracy!")
        print("[STATUS] Ready for production use")
    elif overall_accuracy >= 80:
        print("[GOOD] Enhanced people detection achieved 80%+ accuracy")
        print("[STATUS] Good for testing, minor improvements needed")
    elif overall_accuracy >= 70:
        print("[FAIR] Enhanced people detection achieved 70%+ accuracy")
        print("[STATUS] Needs improvement before production")
    else:
        print("[POOR] Enhanced people detection accuracy below 70%")
        print("[STATUS] Significant improvements required")
    
    return overall_accuracy

def test_detection_performance():
    """Test the performance of the enhanced detection system"""
    print("\n" + "=" * 80)
    print("PERFORMANCE TEST")
    print("=" * 80)
    
    pipeline = EnhancedPeopleDetectionPipeline()
    test_frame = create_test_frame_with_people(640, 480, 2)
    
    # Test processing speed
    times = []
    for i in range(10):
        start_time = time.time()
        people_count, confidence = pipeline.detect_people(test_frame)
        end_time = time.time()
        
        processing_time = end_time - start_time
        times.append(processing_time)
        print(f"[PERF] Test {i+1}: {processing_time:.3f}s - Detected: {people_count} people")
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n[PERF] Average Processing Time: {avg_time:.3f}s")
    print(f"[PERF] Min Processing Time: {min_time:.3f}s")
    print(f"[PERF] Max Processing Time: {max_time:.3f}s")
    
    if avg_time < 0.5:
        print("[PASS] Performance: Excellent (< 0.5s)")
    elif avg_time < 1.0:
        print("[PASS] Performance: Good (< 1.0s)")
    elif avg_time < 2.0:
        print("[FAIR] Performance: Acceptable (< 2.0s)")
    else:
        print("[POOR] Performance: Needs optimization (> 2.0s)")

def test_full_detection_pipeline():
    """Test the full detection pipeline with all detection types"""
    print("\n" + "=" * 80)
    print("FULL DETECTION PIPELINE TEST")
    print("=" * 80)
    
    pipeline = EnhancedPeopleDetectionPipeline()
    
    # Test with person wearing helmet
    helmet_frame = create_test_frame_with_helmet(640, 480)
    results = pipeline.process_frame(helmet_frame)
    
    print("Helmet Test Results:")
    print(f"  People Count: {results['people_count']}")
    print(f"  Helmet Violation: {results['helmet_violation']}")
    print(f"  Face Cover Violation: {results['face_cover_violation']}")
    print(f"  Loitering: {results['loitering']}")
    print(f"  Posture Violation: {results['posture_violation']}")
    print(f"  Alerts: {len(results['alerts'])}")
    
    # Test with person wearing mask
    mask_frame = create_test_frame_with_mask(640, 480)
    results = pipeline.process_frame(mask_frame)
    
    print("\nMask Test Results:")
    print(f"  People Count: {results['people_count']}")
    print(f"  Helmet Violation: {results['helmet_violation']}")
    print(f"  Face Cover Violation: {results['face_cover_violation']}")
    print(f"  Loitering: {results['loitering']}")
    print(f"  Posture Violation: {results['posture_violation']}")
    print(f"  Alerts: {len(results['alerts'])}")
    
    # Get detection statistics
    stats = pipeline.get_detection_stats()
    print(f"\nDetection Statistics:")
    print(f"  People Detection Stats: {stats.get('people_detection', {})}")
    print(f"  Helmet Detections: {stats.get('helmet_detections', 0)}")
    print(f"  Face Cover Detections: {stats.get('face_cover_detections', 0)}")
    print(f"  Active Trackers: {stats.get('active_trackers', 0)}")
    print(f"  Posture Violations: {stats.get('posture_violations', 0)}")

def main():
    print("ENHANCED PEOPLE DETECTION SYSTEM TEST")
    print("Testing the new enhanced people detection with multiple algorithms...")
    
    try:
        # Test enhanced people detection
        accuracy = test_enhanced_people_detection()
        
        # Test performance
        test_detection_performance()
        
        # Test full pipeline
        test_full_detection_pipeline()
        
        print("\n" + "=" * 80)
        print("FINAL TEST SUMMARY")
        print("=" * 80)
        
        if accuracy >= 90:
            print("✅ ENHANCED PEOPLE DETECTION: SUCCESS")
            print("The enhanced people detection system is working excellently!")
            print("Ready for production deployment.")
        elif accuracy >= 80:
            print("✅ ENHANCED PEOPLE DETECTION: GOOD")
            print("The enhanced people detection system is working well.")
            print("Minor improvements may be needed for production.")
        else:
            print("⚠️ ENHANCED PEOPLE DETECTION: NEEDS IMPROVEMENT")
            print("The enhanced people detection system needs further tuning.")
            print("Consider adjusting parameters or adding more training data.")
        
        print("\nNext steps:")
        print("1. Deploy the enhanced system to production")
        print("2. Monitor real-world performance")
        print("3. Collect feedback and fine-tune as needed")
        print("4. Consider adding deep learning models for even higher accuracy")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
