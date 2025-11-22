#!/usr/bin/env python3
"""
Test Script for Enhanced Helmet Detection
This script tests the improved helmet detection system
"""

import cv2
import numpy as np
import base64
import io
from PIL import Image
import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models_enhanced_people import EnhancedPeopleDetectionPipeline

class HelmetDetectionTester:
    def __init__(self):
        self.pipeline = EnhancedPeopleDetectionPipeline()
        self.test_results = []
        
    def test_with_video_frame(self, frame_data):
        """Test helmet detection with a video frame"""
        print("=" * 60)
        print("TESTING HELMET DETECTION WITH VIDEO FRAME")
        print("=" * 60)
        
        try:
            # Decode base64 image
            if isinstance(frame_data, str) and frame_data.startswith('data:image'):
                image_data = base64.b64decode(frame_data.split(',')[1])
                image = Image.open(io.BytesIO(image_data))
                frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                print("ERROR: Invalid frame data format")
                return None
                
            if frame is None:
                print("ERROR: Could not decode frame")
                return None
                
            print(f"Frame loaded successfully: {frame.shape}")
            
            # Test helmet detection
            start_time = time.time()
            has_helmet, confidence = self.pipeline.detect_helmet(frame)
            detection_time = time.time() - start_time
            
            result = {
                'helmet_detected': has_helmet,
                'confidence': confidence,
                'detection_time': detection_time,
                'frame_shape': frame.shape
            }
            
            print(f"\nRESULT:")
            print(f"  Helmet Detected: {has_helmet}")
            print(f"  Confidence: {confidence:.3f}")
            print(f"  Detection Time: {detection_time:.3f}s")
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            print(f"ERROR during testing: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_with_image_file(self, image_path):
        """Test helmet detection with an image file"""
        print("=" * 60)
        print(f"TESTING HELMET DETECTION WITH IMAGE: {image_path}")
        print("=" * 60)
        
        try:
            frame = cv2.imread(image_path)
            if frame is None:
                print(f"ERROR: Could not load image {image_path}")
                return None
                
            print(f"Image loaded successfully: {frame.shape}")
            
            # Test helmet detection
            start_time = time.time()
            has_helmet, confidence = self.pipeline.detect_helmet(frame)
            detection_time = time.time() - start_time
            
            result = {
                'helmet_detected': has_helmet,
                'confidence': confidence,
                'detection_time': detection_time,
                'image_path': image_path,
                'frame_shape': frame.shape
            }
            
            print(f"\nRESULT:")
            print(f"  Helmet Detected: {has_helmet}")
            print(f"  Confidence: {confidence:.3f}")
            print(f"  Detection Time: {detection_time:.3f}s")
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            print(f"ERROR during testing: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_test_helmet_image(self):
        """Create a synthetic test image with a helmet"""
        print("=" * 60)
        print("CREATING SYNTHETIC HELMET TEST IMAGE")
        print("=" * 60)
        
        # Create a test image with more realistic features
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add textured background
        cv2.rectangle(img, (0, 0), (640, 480), (60, 60, 60), -1)  # Background
        cv2.rectangle(img, (0, 0), (640, 480), (40, 40, 40), 2)   # Border
        
        # Draw a more realistic person
        # Body (larger rectangle with some texture)
        cv2.rectangle(img, (280, 180), (360, 420), (80, 80, 80), -1)  # Body
        cv2.rectangle(img, (280, 180), (360, 420), (100, 100, 100), 2)  # Body outline
        
        # Arms
        cv2.rectangle(img, (260, 200), (280, 350), (80, 80, 80), -1)  # Left arm
        cv2.rectangle(img, (360, 200), (380, 350), (80, 80, 80), -1)  # Right arm
        
        # Legs
        cv2.rectangle(img, (300, 420), (320, 480), (60, 60, 60), -1)  # Left leg
        cv2.rectangle(img, (320, 420), (340, 480), (60, 60, 60), -1)  # Right leg
        
        # Draw a helmet (circle on top)
        cv2.circle(img, (320, 160), 60, (0, 0, 255), -1)  # Red helmet
        cv2.circle(img, (320, 160), 60, (0, 0, 200), 3)   # Helmet outline
        
        # Draw head (smaller circle)
        cv2.circle(img, (320, 180), 35, (220, 180, 140), -1)  # Skin color
        cv2.circle(img, (320, 180), 35, (200, 160, 120), 2)   # Head outline
        
        # Add some facial features
        cv2.circle(img, (310, 175), 3, (0, 0, 0), -1)  # Left eye
        cv2.circle(img, (330, 175), 3, (0, 0, 0), -1)  # Right eye
        cv2.ellipse(img, (320, 185), (8, 4), 0, 0, 180, (0, 0, 0), 2)  # Mouth
        
        # Add some noise/texture to make it more realistic
        noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        
        # Save test image
        test_path = "test_helmet_image.jpg"
        cv2.imwrite(test_path, img)
        print(f"Test image created: {test_path}")
        
        return test_path
    
    def run_comprehensive_test(self):
        """Run comprehensive helmet detection tests"""
        print("=" * 60)
        print("COMPREHENSIVE HELMET DETECTION TEST")
        print("=" * 60)
        
        # Test 1: Create and test synthetic helmet image
        test_image_path = self.create_test_helmet_image()
        result1 = self.test_with_image_file(test_image_path)
        
        # Test 2: Test with different helmet colors
        self.test_different_helmet_colors()
        
        # Test 3: Test with no helmet
        self.test_no_helmet_image()
        
        # Summary
        self.print_test_summary()
        
        # Cleanup
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
    
    def test_different_helmet_colors(self):
        """Test helmet detection with different colors"""
        print("\n" + "=" * 60)
        print("TESTING DIFFERENT HELMET COLORS")
        print("=" * 60)
        
        colors = [
            ("Black", (0, 0, 0)),
            ("White", (255, 255, 255)),
            ("Red", (0, 0, 255)),
            ("Blue", (255, 0, 0)),
            ("Yellow", (0, 255, 255)),
            ("Green", (0, 255, 0))
        ]
        
        for color_name, color_bgr in colors:
            print(f"\nTesting {color_name} helmet:")
            
            # Create test image with colored helmet
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.rectangle(img, (0, 0), (640, 480), (50, 50, 50), -1)  # Background
            cv2.rectangle(img, (300, 200), (340, 400), (100, 100, 100), -1)  # Body
            cv2.circle(img, (320, 180), 50, color_bgr, -1)  # Colored helmet
            cv2.circle(img, (320, 200), 30, (220, 180, 140), -1)  # Head
            
            # Test detection
            has_helmet, confidence = self.pipeline.detect_helmet(img)
            print(f"  Result: {has_helmet}, Confidence: {confidence:.3f}")
            
            self.test_results.append({
                'helmet_detected': has_helmet,
                'confidence': confidence,
                'helmet_color': color_name
            })
    
    def test_no_helmet_image(self):
        """Test helmet detection with no helmet"""
        print("\n" + "=" * 60)
        print("TESTING NO HELMET IMAGE")
        print("=" * 60)
        
        # Create test image without helmet
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(img, (0, 0), (640, 480), (50, 50, 50), -1)  # Background
        cv2.rectangle(img, (300, 200), (340, 400), (100, 100, 100), -1)  # Body
        cv2.circle(img, (320, 200), 30, (220, 180, 140), -1)  # Head only (no helmet)
        
        # Test detection
        has_helmet, confidence = self.pipeline.detect_helmet(img)
        print(f"Result: {has_helmet}, Confidence: {confidence:.3f}")
        
        self.test_results.append({
            'helmet_detected': has_helmet,
            'confidence': confidence,
            'test_type': 'no_helmet'
        })
    
    def print_test_summary(self):
        """Print summary of all test results"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        if not self.test_results:
            print("No test results available")
            return
        
        total_tests = len(self.test_results)
        successful_detections = sum(1 for r in self.test_results if r['helmet_detected'])
        avg_confidence = sum(r['confidence'] for r in self.test_results) / total_tests
        avg_time = sum(r.get('detection_time', 0) for r in self.test_results) / total_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful Detections: {successful_detections}")
        print(f"Detection Rate: {(successful_detections/total_tests)*100:.1f}%")
        print(f"Average Confidence: {avg_confidence:.3f}")
        print(f"Average Detection Time: {avg_time:.3f}s")
        
        print("\nDetailed Results:")
        for i, result in enumerate(self.test_results, 1):
            print(f"  Test {i}: Helmet={result['helmet_detected']}, "
                  f"Confidence={result['confidence']:.3f}")
            if 'helmet_color' in result:
                print(f"    Color: {result['helmet_color']}")
            if 'test_type' in result:
                print(f"    Type: {result['test_type']}")

def main():
    """Main function for testing"""
    tester = HelmetDetectionTester()
    
    print("Enhanced Helmet Detection Tester")
    print("This script tests the improved helmet detection system")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "comprehensive":
            tester.run_comprehensive_test()
        elif sys.argv[1].endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            tester.test_with_image_file(sys.argv[1])
        else:
            print("Invalid argument. Use:")
            print("  python test_helmet_detection.py comprehensive")
            print("  python test_helmet_detection.py image.jpg")
    else:
        print("\nRunning comprehensive test...")
        tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
