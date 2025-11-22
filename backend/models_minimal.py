import cv2
import numpy as np
import time
from collections import deque

class MinimalDetectionPipeline:
    def __init__(self):
        self.initialize_models()
        self.loitering_tracker = {}
        self.posture_history = deque(maxlen=30)
        
    def initialize_models(self):
        """Initialize minimal detection models using only OpenCV"""
        try:
            # Initialize OpenCV HOG descriptor for people detection
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            
            # Initialize background subtractor for motion detection
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
            
            print("✅ Minimal detection models initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing models: {e}")
            self.fallback_mode = True
    
    def detect_people(self, frame):
        """Detect people in frame using HOG descriptor"""
        try:
            # Resize frame for better detection
            frame_resized = cv2.resize(frame, (640, 480))
            
            # Detect people
            boxes, weights = self.hog.detectMultiScale(
                frame_resized,
                winStride=(8, 8),
                padding=(8, 8),
                scale=1.05
            )
            
            people_count = len(boxes)
            confidence = 0.8 if people_count > 0 else 0.1
            
            return people_count, confidence
            
        except Exception as e:
            print(f"HOG detection error: {e}")
            return 0, 0.1
    
    def detect_helmet(self, frame):
        """Detect helmet using color analysis"""
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define helmet color ranges (dark colors)
            helmet_lower = np.array([0, 0, 0])
            helmet_upper = np.array([180, 255, 50])
            
            # Create mask for dark colors
            mask = cv2.inRange(hsv, helmet_lower, helmet_upper)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            helmet_detected = False
            confidence = 0.0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Minimum area threshold
                    helmet_detected = True
                    confidence = min(0.9, area / 10000)
                    break
            
            return helmet_detected, confidence
            
        except Exception as e:
            print(f"Helmet detection error: {e}")
            return False, 0.0
    
    def detect_face_cover(self, frame):
        """Detect face coverings using color analysis"""
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define mask colors for common face coverings
            # Blue masks
            blue_lower = np.array([100, 50, 50])
            blue_upper = np.array([130, 255, 255])
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            
            # White masks
            white_lower = np.array([0, 0, 200])
            white_upper = np.array([180, 30, 255])
            white_mask = cv2.inRange(hsv, white_lower, white_upper)
            
            # Black masks/scarves
            black_lower = np.array([0, 0, 0])
            black_upper = np.array([180, 255, 50])
            black_mask = cv2.inRange(hsv, black_lower, black_upper)
            
            # Combine masks
            combined_mask = cv2.bitwise_or(blue_mask, cv2.bitwise_or(white_mask, black_mask))
            
            # Calculate coverage percentage
            total_pixels = frame.shape[0] * frame.shape[1]
            covered_pixels = cv2.countNonZero(combined_mask)
            coverage_ratio = covered_pixels / total_pixels
            
            # Threshold for face covering detection
            has_face_cover = coverage_ratio > 0.05  # 5% coverage threshold
            confidence = min(0.95, coverage_ratio * 10)  # Scale confidence
            
            return has_face_cover, confidence
            
        except Exception as e:
            print(f"Face cover detection error: {e}")
            return False, 0.0
    
    def detect_loitering(self, frame):
        """Detect loitering behavior using motion tracking"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply background subtraction
            fg_mask = self.bg_subtractor.apply(gray)
            
            # Use frame timestamp as unique identifier
            frame_id = int(time.time() * 1000)
            
            # Initialize tracker for this frame
            if frame_id not in self.loitering_tracker:
                self.loitering_tracker[frame_id] = {
                    'motion_pixels': [],
                    'start_time': time.time(),
                    'last_movement': time.time()
                }
            
            # Count motion pixels
            motion_pixels = cv2.countNonZero(fg_mask)
            self.loitering_tracker[frame_id]['motion_pixels'].append(motion_pixels)
            
            # Keep only recent motion data
            if len(self.loitering_tracker[frame_id]['motion_pixels']) > 30:
                self.loitering_tracker[frame_id]['motion_pixels'] = self.loitering_tracker[frame_id]['motion_pixels'][-30:]
            
            # Check for loitering (low motion over time)
            if len(self.loitering_tracker[frame_id]['motion_pixels']) >= 10:
                avg_motion = sum(self.loitering_tracker[frame_id]['motion_pixels'][-10:]) / 10
                
                if avg_motion < 500:  # Low motion threshold
                    stationary_time = time.time() - self.loitering_tracker[frame_id]['last_movement']
                    if stationary_time > 30:  # 30 seconds threshold
                        return True, min(0.9, stationary_time / 60)
                else:
                    self.loitering_tracker[frame_id]['last_movement'] = time.time()
            
            # Clean up old trackers
            current_time = time.time()
            self.loitering_tracker = {
                k: v for k, v in self.loitering_tracker.items() 
                if current_time - v['start_time'] < 300  # Keep for 5 minutes
            }
            
            return False, 0.0
            
        except Exception as e:
            print(f"Loitering detection error: {e}")
            return False, 0.0
    
    def detect_posture(self, frame):
        """Detect posture violations using simple edge detection"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            posture_score = 0.5  # Default neutral posture
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Significant contour
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate aspect ratio
                    aspect_ratio = h / w if w > 0 else 0
                    
                    # Check if contour looks like a person (tall and narrow)
                    if aspect_ratio > 1.5 and h > 100:  # Person-like shape
                        # Analyze posture based on contour shape
                        hull = cv2.convexHull(contour)
                        hull_area = cv2.contourArea(hull)
                        
                        if hull_area > 0:
                            solidity = area / hull_area
                            
                            # Good posture: more solid, upright shape
                            if solidity > 0.7:
                                posture_score = max(posture_score, 0.8)
                            else:
                                posture_score = min(posture_score, 0.3)
            
            # Store in history for smoothing
            self.posture_history.append(posture_score)
            
            # Calculate average posture over recent frames
            if len(self.posture_history) >= 10:
                avg_posture = sum(self.posture_history) / len(self.posture_history)
                bad_posture = avg_posture < 0.4  # Threshold for bad posture
                confidence = 1.0 - avg_posture
                
                return bad_posture, confidence
            
            return False, 0.0
            
        except Exception as e:
            print(f"Posture detection error: {e}")
            return False, 0.0
    
    def process_frame(self, frame):
        """Process frame through all detection models"""
        try:
            results = {
                'people_count': 0,
                'helmet_violation': False,
                'face_cover_violation': False,
                'loitering': False,
                'posture_violation': False,
                'alerts': []
            }
            
            # People detection
            people_count, conf = self.detect_people(frame)
            results['people_count'] = people_count
            if people_count > 2:
                results['alerts'].append({
                    'type': 'people_count',
                    'message': f'Multiple people detected: {people_count}',
                    'confidence': conf
                })
            
            # Helmet detection
            has_helmet, conf = self.detect_helmet(frame)
            if has_helmet:
                results['helmet_violation'] = True
                results['alerts'].append({
                    'type': 'helmet',
                    'message': 'Helmet detected - Please remove helmet',
                    'confidence': conf
                })
            
            # Face cover detection
            has_face_cover, conf = self.detect_face_cover(frame)
            if has_face_cover:
                results['face_cover_violation'] = True
                results['alerts'].append({
                    'type': 'face_cover',
                    'message': 'Face covering detected - Please remove mask/scarf',
                    'confidence': conf
                })
            
            # Loitering detection
            is_loitering, conf = self.detect_loitering(frame)
            if is_loitering:
                results['loitering'] = True
                results['alerts'].append({
                    'type': 'loitering',
                    'message': 'Loitering detected - Please move away',
                    'confidence': conf
                })
            
            # Posture detection
            bad_posture, conf = self.detect_posture(frame)
            if bad_posture:
                results['posture_violation'] = True
                results['alerts'].append({
                    'type': 'posture',
                    'message': 'Improper posture detected - Please stand straight',
                    'confidence': conf
                })
            
            return results
            
        except Exception as e:
            print(f"Frame processing error: {e}")
            return {
                'people_count': 0,
                'helmet_violation': False,
                'face_cover_violation': False,
                'loitering': False,
                'posture_violation': False,
                'alerts': []
            }

