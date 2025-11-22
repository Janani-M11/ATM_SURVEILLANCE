import cv2
import numpy as np
import time
from collections import deque
import math

class WorkingDetectionPipeline:
    def __init__(self):
        self.initialize_models()
        self.loitering_tracker = {}
        self.posture_history = deque(maxlen=30)
        self.face_cover_history = deque(maxlen=10)
        
    def initialize_models(self):
        """Initialize working detection models using only OpenCV"""
        try:
            # Initialize OpenCV HOG descriptor for people detection
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            
            # Initialize background subtractor for motion detection
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
            
            # Initialize face cascade for face detection
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            print("[SUCCESS] Working detection models initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Error initializing models: {e}")
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
        """Detect helmet presence (violation) - returns True if helmet IS detected when person is present"""
        try:
            # First check if there are people in the frame
            people_count, _ = self.detect_people(frame)
            if people_count == 0:
                return False, 0.0  # No people = no violation
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define very comprehensive helmet color ranges (very lenient)
            helmet_masks = []
            
            # Black helmets (most common) - very lenient range
            black_lower = np.array([0, 0, 0])
            black_upper = np.array([180, 255, 80])  # Even more lenient
            helmet_masks.append(cv2.inRange(hsv, black_lower, black_upper))
            
            # Dark colors (helmets are typically dark)
            dark_lower = np.array([0, 0, 0])
            dark_upper = np.array([180, 255, 100])
            helmet_masks.append(cv2.inRange(hsv, dark_lower, dark_upper))
            
            # Blue helmets - very lenient
            blue_lower = np.array([90, 20, 10])
            blue_upper = np.array([140, 255, 150])
            helmet_masks.append(cv2.inRange(hsv, blue_lower, blue_upper))
            
            # White helmets - very lenient
            white_lower = np.array([0, 0, 120])
            white_upper = np.array([180, 80, 255])
            helmet_masks.append(cv2.inRange(hsv, white_lower, white_upper))
            
            # Yellow helmets - very lenient
            yellow_lower = np.array([10, 30, 30])
            yellow_upper = np.array([40, 255, 255])
            helmet_masks.append(cv2.inRange(hsv, yellow_lower, yellow_upper))
            
            # Red helmets - very lenient
            red_lower = np.array([0, 30, 30])
            red_lower2 = np.array([160, 30, 30])
            red_upper = np.array([20, 255, 255])
            red_upper2 = np.array([180, 255, 255])
            helmet_masks.append(cv2.inRange(hsv, red_lower, red_upper))
            helmet_masks.append(cv2.inRange(hsv, red_lower2, red_upper2))
            
            # Orange helmets - very lenient
            orange_lower = np.array([0, 30, 30])
            orange_upper = np.array([30, 255, 255])
            helmet_masks.append(cv2.inRange(hsv, orange_lower, orange_upper))
            
            # Green helmets - very lenient
            green_lower = np.array([30, 30, 30])
            green_upper = np.array([90, 255, 255])
            helmet_masks.append(cv2.inRange(hsv, green_lower, green_upper))
            
            # Combine all helmet masks
            combined_mask = helmet_masks[0]
            for mask in helmet_masks[1:]:
                combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Apply minimal morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            helmet_found = False
            best_confidence = 0.0
            
            print(f"Found {len(contours)} contours for helmet detection")
            
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                print(f"Contour {i}: area={area}")
                
                if area > 500:  # Very low minimum area threshold
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    frame_height = frame.shape[0]
                    frame_width = frame.shape[1]
                    
                    print(f"Contour {i}: x={x}, y={y}, w={w}, h={h}, frame_h={frame_height}, frame_w={frame_width}")
                    
                    # Very lenient position check - anywhere in upper 70% of frame
                    if y < frame_height * 0.7:
                        # Very lenient aspect ratio check
                        aspect_ratio = w / h if h > 0 else 0
                        print(f"Contour {i}: aspect_ratio={aspect_ratio:.2f}")
                        
                        if 0.4 <= aspect_ratio <= 2.0:  # Very lenient range
                            # Very lenient size check
                            relative_area = area / (frame_height * frame_width)
                            print(f"Contour {i}: relative_area={relative_area:.4f}")
                            
                            if 0.005 <= relative_area <= 0.3:  # Very lenient size range
                                # Very lenient circularity check
                                perimeter = cv2.arcLength(contour, True)
                                if perimeter > 0:
                                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                                    print(f"Contour {i}: circularity={circularity:.2f}")
                                    
                                    if circularity > 0.2:  # Very lenient circularity
                                        helmet_found = True
                                        confidence = min(0.95, circularity * (area / 5000))
                                        best_confidence = max(best_confidence, confidence)
                                        print(f"HELMET DETECTED! Contour {i}: area={area}, circularity={circularity:.2f}, confidence={confidence:.2f}")
                                        break  # Found a helmet, no need to check more
            
            # Return True if helmet IS detected (violation), False if no helmet found (compliant)
            helmet_violation = helmet_found
            violation_confidence = best_confidence if helmet_violation else 0.1
            
            if helmet_violation:
                print(f"HELMET VIOLATION DETECTED with confidence: {violation_confidence:.2f}")
            else:
                print("No helmet detected")
            
            return helmet_violation, violation_confidence
            
        except Exception as e:
            print(f"Helmet detection error: {e}")
            import traceback
            traceback.print_exc()
            return False, 0.0
    
    def detect_face_cover(self, frame):
        """Detect face coverings using face detection and color analysis"""
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces with more strict parameters
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
            
            if len(faces) == 0:
                return False, 0.0
            
            face_cover_detected = False
            max_confidence = 0.0
            
            for (x, y, w, h) in faces:
                # Extract face region
                face_region = frame[y:y+h, x:x+w]
                
                if face_region.size > 0:
                    # Analyze face region for coverings
                    cover_prob = self._analyze_face_region(face_region)
                    if cover_prob > 0.7:  # Increased threshold for more accuracy
                        face_cover_detected = True
                        max_confidence = max(max_confidence, cover_prob)
            
            return face_cover_detected, max_confidence
            
        except Exception as e:
            print(f"Face cover detection error: {e}")
            return False, 0.0
    
    def _analyze_face_region(self, face_region):
        """Analyze face region for coverings"""
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)
            
            # Define mask colors for common face coverings with more specific ranges
            # Blue surgical masks
            blue_lower = np.array([100, 100, 50])
            blue_upper = np.array([130, 255, 200])
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            
            # White masks
            white_lower = np.array([0, 0, 180])
            white_upper = np.array([180, 30, 255])
            white_mask = cv2.inRange(hsv, white_lower, white_upper)
            
            # Black masks/scarves (more restrictive)
            black_lower = np.array([0, 0, 0])
            black_upper = np.array([180, 255, 40])
            black_mask = cv2.inRange(hsv, black_lower, black_upper)
            
            # Combine masks
            combined_mask = cv2.bitwise_or(blue_mask, cv2.bitwise_or(white_mask, black_mask))
            
            # Calculate coverage percentage
            total_pixels = face_region.shape[0] * face_region.shape[1]
            covered_pixels = cv2.countNonZero(combined_mask)
            coverage_ratio = covered_pixels / total_pixels
            
            # Only return high confidence if coverage is significant
            if coverage_ratio > 0.3:  # At least 30% of face covered
                return min(0.95, coverage_ratio * 1.5)  # More conservative scaling
            else:
                return 0.0
            
        except Exception as e:
            print(f"Face region analysis error: {e}")
            return 0.0
    
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
        """Detect posture violations using edge detection and contour analysis"""
        try:
            # First check if there are people in the frame
            people_count, _ = self.detect_people(frame)
            if people_count == 0:
                return False, 0.0
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection with better parameters
            edges = cv2.Canny(gray, 30, 100)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            posture_score = 0.5  # Default neutral posture
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 2000:  # Increased threshold for more significant contours
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate aspect ratio
                    aspect_ratio = h / w if w > 0 else 0
                    
                    # Check if contour looks like a person (tall and narrow)
                    if aspect_ratio > 1.8 and h > 150:  # More strict person-like shape requirements
                        # Analyze posture based on contour shape
                        hull = cv2.convexHull(contour)
                        hull_area = cv2.contourArea(hull)
                        
                        if hull_area > 0:
                            solidity = area / hull_area
                            
                            # Good posture: more solid, upright shape
                            if solidity > 0.75:  # More strict solidity requirement
                                posture_score = max(posture_score, 0.8)
                            else:
                                posture_score = min(posture_score, 0.3)
            
            # Store in history for smoothing
            self.posture_history.append(posture_score)
            
            # Calculate average posture over recent frames
            if len(self.posture_history) >= 10:
                avg_posture = sum(self.posture_history) / len(self.posture_history)
                bad_posture = avg_posture < 0.4  # More strict threshold for bad posture
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