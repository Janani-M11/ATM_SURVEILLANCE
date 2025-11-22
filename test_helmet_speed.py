#!/usr/bin/env python3
"""
Speed Test for Optimized Helmet Detection
This script tests the speed improvements made to helmet detection
"""

import cv2
import numpy as np
import time
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models_enhanced_people import EnhancedPeopleDetectionPipeline

class HelmetDetectionSpeedTest:
    def __init__(self):
        self.pipeline = EnhancedPeopleDetectionPipeline()
        
    def create_test_image(self):
        """Create a test image with helmet"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Background
        cv2.rectangle(img, (0, 0), (640, 480), (60, 60, 60), -1)
        
        # Person
        cv2.rectangle(img, (280, 180), (360, 420), (80, 80, 80), -1)
        cv2.rectangle(img, (260, 200), (280, 350), (80, 80, 80), -1)  # Left arm
        cv2.rectangle(img, (360, 200), (380, 350), (80, 80, 80), -1)  # Right arm
        cv2.rectangle(img, (300, 420), (320, 480), (60, 60, 60), -1)  # Left leg
        cv2.rectangle(img, (320, 420), (340, 480), (60, 60, 60), -1)  # Right leg
        
        # Helmet
        cv2.circle(img, (320, 160), 60, (0, 0, 255), -1)  # Red helmet
        
        # Head
        cv2.circle(img, (320, 180), 35, (220, 180, 140), -1)
        
        # Add noise
        noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        
        return img
    
    def test_detection_speed(self, num_tests=10):
        """Test helmet detection speed"""
        print("=" * 60)
        print("HELMET DETECTION SPEED TEST")
        print("=" * 60)
        
        test_image = self.create_test_image()
        
        times = []
        detections = []
        confidences = []
        
        print(f"Running {num_tests} detection tests...")
        
        for i in range(num_tests):
            start_time = time.time()
            has_helmet, confidence = self.pipeline.detect_helmet(test_image)
            end_time = time.time()
            
            detection_time = end_time - start_time
            times.append(detection_time)
            detections.append(has_helmet)
            confidences.append(confidence)
            
            print(f"Test {i+1}: {detection_time:.3f}s - Helmet: {has_helmet}, Confidence: {confidence:.3f}")
        
        # Calculate statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        successful_detections = sum(detections)
        avg_confidence = sum(confidences) / len(confidences)
        
        print("\n" + "=" * 60)
        print("SPEED TEST RESULTS")
        print("=" * 60)
        print(f"Average Detection Time: {avg_time:.3f}s")
        print(f"Minimum Detection Time: {min_time:.3f}s")
        print(f"Maximum Detection Time: {max_time:.3f}s")
        print(f"Successful Detections: {successful_detections}/{num_tests}")
        print(f"Detection Rate: {(successful_detections/num_tests)*100:.1f}%")
        print(f"Average Confidence: {avg_confidence:.3f}")
        
        # Performance assessment
        if avg_time < 0.1:
            print("🚀 EXCELLENT SPEED - Very fast detection!")
        elif avg_time < 0.2:
            print("✅ GOOD SPEED - Fast detection")
        elif avg_time < 0.5:
            print("⚠️ MODERATE SPEED - Acceptable detection time")
        else:
            print("❌ SLOW SPEED - Detection needs optimization")
        
        return {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'detection_rate': successful_detections/num_tests,
            'avg_confidence': avg_confidence
        }
    
    def test_different_colors(self):
        """Test speed with different helmet colors"""
        print("\n" + "=" * 60)
        print("SPEED TEST WITH DIFFERENT HELMET COLORS")
        print("=" * 60)
        
        colors = [
            ("Black", (0, 0, 0)),
            ("White", (255, 255, 255)),
            ("Red", (0, 0, 255)),
            ("Blue", (255, 0, 0)),
            ("Green", (0, 255, 0))
        ]
        
        for color_name, color_bgr in colors:
            print(f"\nTesting {color_name} helmet:")
            
            # Create test image with colored helmet
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.rectangle(img, (0, 0), (640, 480), (60, 60, 60), -1)
            cv2.rectangle(img, (280, 180), (360, 420), (80, 80, 80), -1)
            cv2.circle(img, (320, 160), 60, color_bgr, -1)
            cv2.circle(img, (320, 180), 35, (220, 180, 140), -1)
            
            # Test speed
            times = []
            for _ in range(5):
                start_time = time.time()
                has_helmet, confidence = self.pipeline.detect_helmet(img)
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = sum(times) / len(times)
            print(f"  Average time: {avg_time:.3f}s")
            print(f"  Detection: {has_helmet}, Confidence: {confidence:.3f}")

def main():
    """Main function for speed testing"""
    tester = HelmetDetectionSpeedTest()
    
    print("Optimized Helmet Detection Speed Test")
    print("This script tests the speed improvements made to helmet detection")
    
    # Run speed test
    results = tester.test_detection_speed(10)
    
    # Test different colors
    tester.test_different_colors()
    
    print("\n" + "=" * 60)
    print("SPEED OPTIMIZATION SUMMARY")
    print("=" * 60)
    print("✅ Optimizations Applied:")
    print("  - Reduced frame processing size (320x240)")
    print("  - Limited color detection to priority colors")
    print("  - Reduced template matching parameters")
    print("  - Simplified Hough circle detection")
    print("  - Faster temporal consistency (5 frames vs 10)")
    print("  - Early exit strategies in detection methods")
    print("  - Reduced ensemble voting to 3 methods")
    
    if results['avg_time'] < 0.2:
        print("\n🎯 RESULT: Helmet detection is now FAST and RESPONSIVE!")
    else:
        print(f"\n⚠️ RESULT: Average detection time is {results['avg_time']:.3f}s")

if __name__ == "__main__":
    main()
