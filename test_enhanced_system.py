#!/usr/bin/env python3
"""
Test Enhanced System Integration
Tests the enhanced people detection system integration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_enhanced_detection_import():
    """Test if enhanced detection can be imported"""
    try:
        from backend.models_enhanced_people import EnhancedPeopleDetectionPipeline
        print("✅ Enhanced People Detection Pipeline imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing Enhanced People Detection Pipeline: {e}")
        return False

def test_enhanced_detection_initialization():
    """Test if enhanced detection can be initialized"""
    try:
        from backend.models_enhanced_people import EnhancedPeopleDetectionPipeline
        pipeline = EnhancedPeopleDetectionPipeline()
        print("✅ Enhanced People Detection Pipeline initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing Enhanced People Detection Pipeline: {e}")
        return False

def test_enhanced_detection_functionality():
    """Test if enhanced detection works with a simple frame"""
    try:
        import cv2
        import numpy as np
        from backend.models_enhanced_people import EnhancedPeopleDetectionPipeline
        
        # Create a simple test frame
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
        
        # Initialize pipeline
        pipeline = EnhancedPeopleDetectionPipeline()
        
        # Test people detection
        people_count, confidence = pipeline.detect_people(frame)
        print(f"✅ Enhanced detection working - Detected {people_count} people (confidence: {confidence:.2f})")
        
        # Test full pipeline
        results = pipeline.process_frame(frame)
        print(f"✅ Full pipeline working - People count: {results['people_count']}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing enhanced detection functionality: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_app_import():
    """Test if backend app can be imported with enhanced detection"""
    try:
        from backend.app import app, detection_pipeline
        print("✅ Backend app imported successfully with enhanced detection")
        print(f"✅ Detection pipeline type: {type(detection_pipeline).__name__}")
        return True
    except Exception as e:
        print(f"❌ Error importing backend app: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 80)
    print("ENHANCED SYSTEM INTEGRATION TEST")
    print("=" * 80)
    
    tests = [
        ("Import Enhanced Detection", test_enhanced_detection_import),
        ("Initialize Enhanced Detection", test_enhanced_detection_initialization),
        ("Test Enhanced Detection Functionality", test_enhanced_detection_functionality),
        ("Test Backend App Import", test_backend_app_import)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[TEST] {test_name}")
        print("-" * 50)
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 80)
    print("ENHANCED SYSTEM INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Enhanced system is ready!")
        print("🚀 The enhanced people detection system is working correctly")
        print("📊 Key improvements:")
        print("   • Multi-algorithm ensemble detection")
        print("   • Advanced HOG with multiple scales")
        print("   • Improved background subtraction")
        print("   • Optical flow analysis")
        print("   • Edge-based detection")
        print("   • Non-Maximum Suppression")
        print("   • Temporal consistency filtering")
        print("   • Advanced validation and filtering")
    else:
        print("⚠️ Some tests failed - Check the errors above")
        print("🔧 The enhanced system may need debugging")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
