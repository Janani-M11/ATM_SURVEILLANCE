#!/usr/bin/env python3
"""
Debug Script for Helmet Detection Issues
This script helps identify why helmet detection is not working properly
"""

import cv2
import numpy as np
import base64
import io
from PIL import Image
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models_enhanced_people import EnhancedPeopleDetectionPipeline

class HelmetDetectionDebugger:
    def __init__(self):
        self.pipeline = EnhancedPeopleDetectionPipeline()
        
    def debug_helmet_detection(self, frame_path_or_data):
        """
        Debug helmet detection with detailed analysis
        """
        print("=" * 60)
        print("HELMET DETECTION DEBUG ANALYSIS")
        print("=" * 60)
        
        # Load frame
        if isinstance(frame_path_or_data, str):
            if frame_path_or_data.startswith('data:image'):
                # Base64 encoded image
                image_data = base64.b64decode(frame_path_or_data.split(',')[1])
                image = Image.open(io.BytesIO(image_data))
                frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                # File path
                frame = cv2.imread(frame_path_or_data)
        else:
            frame = frame_path_or_data
            
        if frame is None:
            print("ERROR: Could not load frame")
            return
            
        print(f"Frame loaded: {frame.shape}")
        
        # Test each detection method individually
        print("\n1. TESTING INDIVIDUAL DETECTION METHODS:")
        print("-" * 40)
        
        # Method 1: Color detection
        print("\n1.1 Color Detection:")
        helmet_color, conf_color = self.pipeline._detect_helmet_color_multi_space(frame)
        print(f"   Result: {helmet_color}, Confidence: {conf_color:.3f}")
        
        # Method 2: Template matching
        print("\n1.2 Template Matching:")
        helmet_template, conf_template = self.pipeline._detect_helmet_template_matching(frame)
        print(f"   Result: {helmet_template}, Confidence: {conf_template:.3f}")
        
        # Method 3: Hough circles
        print("\n1.3 Hough Circles:")
        helmet_hough, conf_hough = self.pipeline._detect_helmet_hough_circles(frame)
        print(f"   Result: {helmet_hough}, Confidence: {conf_hough:.3f}")
        
        # Method 4: Shape analysis
        print("\n1.4 Shape Analysis:")
        helmet_shape, conf_shape = self.pipeline._detect_helmet_advanced_shape(frame)
        print(f"   Result: {helmet_shape}, Confidence: {conf_shape:.3f}")
        
        # Method 5: Edge features
        print("\n1.5 Edge Features:")
        helmet_edge, conf_edge = self.pipeline._detect_helmet_edge_features(frame)
        print(f"   Result: {helmet_edge}, Confidence: {conf_edge:.3f}")
        
        # Test people detection first
        print("\n2. PEOPLE DETECTION:")
        print("-" * 40)
        people_count, people_conf = self.pipeline.detect_people(frame)
        print(f"People detected: {people_count}, Confidence: {people_conf:.3f}")
        
        if people_count == 0:
            print("WARNING: No people detected - helmet detection requires people in frame")
        
        # Test full helmet detection
        print("\n3. FULL HELMET DETECTION:")
        print("-" * 40)
        has_helmet, conf = self.pipeline.detect_helmet(frame)
        print(f"Final Result: {has_helmet}, Confidence: {conf:.3f}")
        
        # Analyze color ranges
        print("\n4. COLOR ANALYSIS:")
        print("-" * 40)
        self._analyze_colors(frame)
        
        # Visual analysis
        print("\n5. VISUAL ANALYSIS:")
        print("-" * 40)
        self._visual_analysis(frame)
        
        return {
            'people_count': people_count,
            'helmet_detected': has_helmet,
            'confidence': conf,
            'methods': {
                'color': (helmet_color, conf_color),
                'template': (helmet_template, conf_template),
                'hough': (helmet_hough, conf_hough),
                'shape': (helmet_shape, conf_shape),
                'edge': (helmet_edge, conf_edge)
            }
        }
    
    def _analyze_colors(self, frame):
        """Analyze colors in the frame for helmet detection"""
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            print("Color ranges being tested:")
            for color_name, ranges in self.pipeline.color_ranges['helmet'].items():
                print(f"  {color_name}: {len(ranges)} range(s)")
                
                for i, (lower, upper) in enumerate(ranges):
                    mask = cv2.inRange(hsv, lower, upper)
                    pixels = cv2.countNonZero(mask)
                    total_pixels = frame.shape[0] * frame.shape[1]
                    percentage = (pixels / total_pixels) * 100
                    
                    print(f"    Range {i+1}: {pixels} pixels ({percentage:.2f}%)")
                    
                    if percentage > 1.0:  # Significant color presence
                        print(f"    *** SIGNIFICANT {color_name.upper()} DETECTED ***")
                        
        except Exception as e:
            print(f"Color analysis error: {e}")
    
    def _visual_analysis(self, frame):
        """Perform visual analysis of the frame"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Check upper half of frame (where helmets typically appear)
            upper_half = frame[:frame.shape[0]//2, :]
            print(f"Upper half analysis (where helmets appear):")
            print(f"  Dimensions: {upper_half.shape}")
            
            # Check for circular shapes in upper half
            gray_upper = gray[:gray.shape[0]//2, :]
            circles = cv2.HoughCircles(
                gray_upper, cv2.HOUGH_GRADIENT, dp=1.2,
                minDist=50, param1=50, param2=30,
                minRadius=20, maxRadius=100
            )
            
            if circles is not None:
                print(f"  Circles found: {len(circles[0])}")
                for i, circle in enumerate(circles[0]):
                    x, y, r = circle
                    print(f"    Circle {i+1}: center=({x:.1f}, {y:.1f}), radius={r:.1f}")
            else:
                print("  No circles detected in upper half")
                
            # Check edge density in upper half
            edges = cv2.Canny(gray_upper, 50, 150)
            edge_pixels = cv2.countNonZero(edges)
            total_pixels = gray_upper.shape[0] * gray_upper.shape[1]
            edge_density = (edge_pixels / total_pixels) * 100
            print(f"  Edge density in upper half: {edge_density:.2f}%")
            
        except Exception as e:
            print(f"Visual analysis error: {e}")
    
    def test_with_sample_images(self):
        """Test with sample images if available"""
        print("\n6. TESTING WITH SAMPLE IMAGES:")
        print("-" * 40)
        
        # Look for test images
        test_dirs = ['datasets', 'test_images', 'samples']
        test_images = []
        
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                    import glob
                    test_images.extend(glob.glob(os.path.join(test_dir, ext)))
        
        if test_images:
            print(f"Found {len(test_images)} test images")
            for img_path in test_images[:3]:  # Test first 3 images
                print(f"\nTesting: {img_path}")
                self.debug_helmet_detection(img_path)
        else:
            print("No test images found in common directories")
            print("You can test with a specific image by calling:")
            print("  debugger.debug_helmet_detection('path/to/image.jpg')")

def main():
    """Main function for testing"""
    debugger = HelmetDetectionDebugger()
    
    print("Helmet Detection Debugger")
    print("This script will help identify helmet detection issues")
    print("\nUsage:")
    print("1. Run with no arguments to test with sample images")
    print("2. Run with image path: python debug_helmet_detection.py image.jpg")
    print("3. Run with base64 data: python debug_helmet_detection.py 'data:image/...'")
    
    if len(sys.argv) > 1:
        # Test with provided image
        image_path = sys.argv[1]
        debugger.debug_helmet_detection(image_path)
    else:
        # Test with sample images
        debugger.test_with_sample_images()

if __name__ == "__main__":
    main()
