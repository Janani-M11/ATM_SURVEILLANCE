#!/usr/bin/env python3
"""
Debug Detection System
Debug the enhanced people detection to see why it's not working
"""

import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def debug_detection_pipeline():
    """Debug the detection pipeline step by step"""
    print("=" * 80)
    print("DEBUGGING ENHANCED PEOPLE DETECTION")
    print("=" * 80)
    
    try:
        from backend.models_enhanced_people import EnhancedPeopleDetectionPipeline
        print("✅ Successfully imported EnhancedPeopleDetectionPipeline")
        
        # Initialize pipeline
        pipeline = EnhancedPeopleDetectionPipeline()
        print("✅ Successfully initialized pipeline")
        
        # Create a simple test frame
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
        print(f"✅ Created test frame: {frame.shape}")
        
        # Test people detection directly
        print("\n[DEBUG] Testing people detection...")
        people_count, confidence = pipeline.detect_people(frame)
        print(f"People detected: {people_count}, Confidence: {confidence:.2f}")
        
        # Test full pipeline
        print("\n[DEBUG] Testing full pipeline...")
        results = pipeline.process_frame(frame)
        print(f"Full pipeline results: {results}")
        
        # Test with a more realistic frame
        print("\n[DEBUG] Testing with realistic frame...")
        realistic_frame = create_realistic_test_frame()
        people_count2, confidence2 = pipeline.detect_people(realistic_frame)
        print(f"Realistic frame - People detected: {people_count2}, Confidence: {confidence2:.2f}")
        
        results2 = pipeline.process_frame(realistic_frame)
        print(f"Realistic frame results: {results2}")
        
        # Test individual detection methods
        print("\n[DEBUG] Testing individual detection methods...")
        debug_individual_methods(pipeline, realistic_frame)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in debug: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_realistic_test_frame():
    """Create a more realistic test frame"""
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
    
    # Draw a person-like shape
    # Body
    cv2.rectangle(frame, (200, 150), (280, 350), (100, 100, 100), -1)
    
    # Head
    cv2.circle(frame, (240, 120), 30, (180, 150, 130), -1)
    
    # Arms
    cv2.rectangle(frame, (180, 200), (300, 210), (100, 100, 100), -1)
    
    # Legs
    cv2.rectangle(frame, (210, 350), (230, 450), (100, 100, 100), -1)
    cv2.rectangle(frame, (250, 350), (270, 450), (100, 100, 100), -1)
    
    # Add some texture
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    frame[edges > 0] = [0, 0, 0]
    
    return frame

def debug_individual_methods(pipeline, frame):
    """Debug individual detection methods"""
    try:
        # Test HOG detection directly
        print("Testing HOG detection...")
        hog_detections = pipeline._detect_people_hog_enhanced(frame)
        print(f"HOG detections: {hog_detections}")
        
        # Test background subtraction
        print("Testing background subtraction...")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bg_detections = pipeline._detect_people_background_enhanced(gray, frame.shape)
        print(f"Background detections: {bg_detections}")
        
        # Test optical flow
        print("Testing optical flow...")
        optical_detections = pipeline._detect_people_optical_enhanced(gray)
        print(f"Optical flow detections: {optical_detections}")
        
        # Test edge detection
        print("Testing edge detection...")
        edge_detections = pipeline._detect_people_edges_enhanced(gray)
        print(f"Edge detections: {edge_detections}")
        
    except Exception as e:
        print(f"Error in individual methods debug: {e}")

def test_with_real_camera_simulation():
    """Test with simulated real camera data"""
    print("\n" + "=" * 80)
    print("TESTING WITH SIMULATED REAL CAMERA DATA")
    print("=" * 80)
    
    try:
        from backend.models_enhanced_people import EnhancedPeopleDetectionPipeline
        pipeline = EnhancedPeopleDetectionPipeline()
        
        # Create multiple test scenarios
        test_scenarios = [
            ("Empty frame", np.ones((480, 640, 3), dtype=np.uint8) * 200),
            ("Person frame", create_realistic_test_frame()),
            ("Multiple people", create_multiple_people_frame()),
            ("Person with helmet", create_person_with_helmet_frame()),
            ("Person with mask", create_person_with_mask_frame())
        ]
        
        for scenario_name, frame in test_scenarios:
            print(f"\n[SCENARIO] {scenario_name}")
            print("-" * 40)
            
            # Test people detection
            people_count, confidence = pipeline.detect_people(frame)
            print(f"People detected: {people_count}, Confidence: {confidence:.2f}")
            
            # Test full pipeline
            results = pipeline.process_frame(frame)
            print(f"Results: {results}")
            
            # Test detection statistics
            stats = pipeline.get_detection_stats()
            print(f"Stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in real camera simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_multiple_people_frame():
    """Create frame with multiple people"""
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
    
    # Person 1
    cv2.rectangle(frame, (100, 150), (180, 350), (100, 100, 100), -1)
    cv2.circle(frame, (140, 120), 30, (180, 150, 130), -1)
    
    # Person 2
    cv2.rectangle(frame, (300, 150), (380, 350), (100, 100, 100), -1)
    cv2.circle(frame, (340, 120), 30, (180, 150, 130), -1)
    
    # Person 3
    cv2.rectangle(frame, (500, 150), (580, 350), (100, 100, 100), -1)
    cv2.circle(frame, (540, 120), 30, (180, 150, 130), -1)
    
    return frame

def create_person_with_helmet_frame():
    """Create frame with person wearing helmet"""
    frame = create_realistic_test_frame()
    # Add helmet
    cv2.circle(frame, (240, 100), 35, (50, 50, 50), -1)
    return frame

def create_person_with_mask_frame():
    """Create frame with person wearing mask"""
    frame = create_realistic_test_frame()
    # Add mask
    cv2.rectangle(frame, (220, 140), (260, 155), (100, 150, 200), -1)
    return frame

def main():
    print("DEBUGGING ENHANCED PEOPLE DETECTION SYSTEM")
    print("This will help identify why detection is not working properly...")
    
    # Debug basic pipeline
    success1 = debug_detection_pipeline()
    
    # Test with simulated real camera data
    success2 = test_with_real_camera_simulation()
    
    print("\n" + "=" * 80)
    print("DEBUG SUMMARY")
    print("=" * 80)
    
    if success1 and success2:
        print("✅ Debug completed successfully")
        print("🔍 Check the output above to identify detection issues")
    else:
        print("❌ Debug failed - check errors above")
    
    print("\nNext steps:")
    print("1. Analyze the debug output")
    print("2. Identify which detection methods are failing")
    print("3. Adjust parameters based on findings")
    print("4. Test with real camera data")

if __name__ == "__main__":
    main()

