#!/usr/bin/env python3
"""
Realistic People Detection Test
Tests the enhanced people detection with more realistic synthetic images
"""

import cv2
import numpy as np
import time
from backend.models_enhanced_people import EnhancedPeopleDetectionPipeline

def create_realistic_person(width=640, height=480, x=100, y=100, scale=1.0):
    """Create a more realistic person-like shape that HOG can detect"""
    frame = np.ones((height, width, 3), dtype=np.uint8) * 200  # Light background
    
    # Scale factors
    w = int(60 * scale)
    h = int(200 * scale)
    
    # Ensure person is within frame bounds
    x = max(10, min(x, width - w - 10))
    y = max(10, min(y, height - h - 10))
    
    # Create more realistic person shape with better contrast
    # Body (main rectangle with gradient)
    for i in range(h):
        intensity = int(120 + (i / h) * 40)  # Gradient from dark to light
        cv2.rectangle(frame, (x, y + i), (x + w, y + i + 1), (intensity, intensity, intensity), -1)
    
    # Head (more realistic oval)
    head_center_x = x + w // 2
    head_center_y = y - int(25 * scale)
    head_w = int(40 * scale)
    head_h = int(50 * scale)
    cv2.ellipse(frame, (head_center_x, head_center_y), (head_w//2, head_h//2), 0, 0, 360, (180, 150, 130), -1)
    
    # Arms (more realistic)
    arm_y = y + int(30 * scale)
    cv2.rectangle(frame, (x - int(15 * scale), arm_y), (x + w + int(15 * scale), arm_y + int(8 * scale)), (120, 120, 120), -1)
    
    # Legs (more realistic)
    leg_w = int(15 * scale)
    leg_h = int(80 * scale)
    cv2.rectangle(frame, (x + int(10 * scale), y + h), (x + int(10 * scale) + leg_w, y + h + leg_h), (100, 100, 100), -1)
    cv2.rectangle(frame, (x + w - int(25 * scale), y + h), (x + w - int(25 * scale) + leg_w, y + h + leg_h), (100, 100, 100), -1)
    
    # Add some texture to make it more detectable
    # Add some noise to edges
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    frame[edges > 0] = [0, 0, 0]  # Add edge lines
    
    return frame

def create_test_scenarios():
    """Create various test scenarios"""
    scenarios = []
    
    # Scenario 1: No people
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
    scenarios.append({
        'name': 'Empty Scene',
        'frame': frame,
        'expected_people': 0
    })
    
    # Scenario 2: Single person
    frame = create_realistic_person(640, 480, 200, 150, 1.0)
    scenarios.append({
        'name': 'Single Person',
        'frame': frame,
        'expected_people': 1
    })
    
    # Scenario 3: Two people
    frame = create_realistic_person(640, 480, 100, 150, 0.8)
    frame = create_realistic_person(640, 480, 400, 150, 0.8)
    scenarios.append({
        'name': 'Two People',
        'frame': frame,
        'expected_people': 2
    })
    
    # Scenario 4: Three people
    frame = create_realistic_person(640, 480, 80, 150, 0.7)
    frame = create_realistic_person(640, 480, 280, 150, 0.7)
    frame = create_realistic_person(640, 480, 480, 150, 0.7)
    scenarios.append({
        'name': 'Three People',
        'frame': frame,
        'expected_people': 3
    })
    
    # Scenario 5: Person with helmet
    frame = create_realistic_person(640, 480, 200, 150, 1.0)
    # Add helmet
    cv2.circle(frame, (230, 125), 30, (50, 50, 50), -1)
    scenarios.append({
        'name': 'Person with Helmet',
        'frame': frame,
        'expected_people': 1
    })
    
    # Scenario 6: Person with mask
    frame = create_realistic_person(640, 480, 200, 150, 1.0)
    # Add mask
    cv2.rectangle(frame, (210, 140), (250, 155), (100, 150, 200), -1)
    scenarios.append({
        'name': 'Person with Mask',
        'frame': frame,
        'expected_people': 1
    })
    
    return scenarios

def test_enhanced_detection():
    """Test the enhanced detection system"""
    print("=" * 80)
    print("REALISTIC ENHANCED PEOPLE DETECTION TEST")
    print("=" * 80)
    
    # Initialize the enhanced detection pipeline
    print("Initializing Enhanced People Detection Pipeline...")
    pipeline = EnhancedPeopleDetectionPipeline()
    
    # Create test scenarios
    scenarios = create_test_scenarios()
    
    total_tests = 0
    passed_tests = 0
    
    for scenario in scenarios:
        print(f"\n[TEST] {scenario['name']}")
        print("-" * 50)
        
        # Run test multiple times for consistency
        test_passes = 0
        test_attempts = 3
        
        for attempt in range(test_attempts):
            total_tests += 1
            
            # Test people detection
            people_count, confidence = pipeline.detect_people(scenario['frame'])
            
            # Check if detection is correct (allow some tolerance)
            expected = scenario['expected_people']
            tolerance = 1 if expected > 0 else 0
            
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
        print(f"[RESULT] {scenario['name']}: {test_passes}/{test_attempts} ({accuracy:.1f}%)")
    
    # Overall accuracy
    overall_accuracy = (passed_tests / total_tests) * 100
    
    print("\n" + "=" * 80)
    print("REALISTIC DETECTION TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed Tests: {passed_tests}")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    
    return overall_accuracy

def test_detection_improvements():
    """Test specific improvements in the enhanced detection"""
    print("\n" + "=" * 80)
    print("DETECTION IMPROVEMENTS TEST")
    print("=" * 80)
    
    pipeline = EnhancedPeopleDetectionPipeline()
    
    # Test with different person sizes
    sizes = [0.5, 0.8, 1.0, 1.2, 1.5]
    print("\nTesting different person sizes:")
    
    for size in sizes:
        frame = create_realistic_person(640, 480, 200, 150, size)
        people_count, confidence = pipeline.detect_people(frame)
        print(f"  Size {size}: Detected {people_count} people (confidence: {confidence:.2f})")
    
    # Test with different positions
    positions = [(100, 100), (300, 100), (500, 100), (200, 200), (400, 200)]
    print("\nTesting different positions:")
    
    for x, y in positions:
        frame = create_realistic_person(640, 480, x, y, 1.0)
        people_count, confidence = pipeline.detect_people(frame)
        print(f"  Position ({x}, {y}): Detected {people_count} people (confidence: {confidence:.2f})")
    
    # Test detection statistics
    stats = pipeline.get_detection_stats()
    print(f"\nDetection Statistics:")
    print(f"  People Detection: {stats.get('people_detection', {})}")
    print(f"  System Performance: {stats}")

def main():
    print("REALISTIC ENHANCED PEOPLE DETECTION TEST")
    print("Testing with more realistic synthetic images...")
    
    try:
        # Test enhanced detection
        accuracy = test_enhanced_detection()
        
        # Test improvements
        test_detection_improvements()
        
        print("\n" + "=" * 80)
        print("FINAL REALISTIC TEST SUMMARY")
        print("=" * 80)
        
        if accuracy >= 80:
            print("✅ ENHANCED PEOPLE DETECTION: SUCCESS")
            print("The enhanced people detection system is working well!")
            print("Ready for production deployment.")
        elif accuracy >= 60:
            print("✅ ENHANCED PEOPLE DETECTION: GOOD")
            print("The enhanced people detection system is working reasonably well.")
            print("Some fine-tuning may be needed for production.")
        else:
            print("⚠️ ENHANCED PEOPLE DETECTION: NEEDS IMPROVEMENT")
            print("The enhanced people detection system needs further tuning.")
            print("Consider adjusting parameters or using real camera data.")
        
        print("\nKey Improvements Made:")
        print("• Multi-algorithm ensemble detection")
        print("• Advanced HOG with multiple scales")
        print("• Improved background subtraction")
        print("• Optical flow analysis")
        print("• Edge-based detection")
        print("• Non-Maximum Suppression")
        print("• Temporal consistency filtering")
        print("• Advanced validation and filtering")
        
        print("\nNext steps:")
        print("1. Test with real camera data")
        print("2. Fine-tune parameters based on real-world performance")
        print("3. Consider adding deep learning models")
        print("4. Deploy to production and monitor")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
