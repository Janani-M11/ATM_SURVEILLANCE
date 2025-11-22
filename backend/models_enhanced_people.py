import cv2
import numpy as np
import time
from collections import deque, defaultdict
import math
from enhanced_people_detection import EnhancedPeopleDetection

class EnhancedPeopleDetectionPipeline:
    """
    Enhanced Detection Pipeline with Improved People Detection
    Uses the new EnhancedPeopleDetection class for better accuracy
    """
    
    def __init__(self):
        self.initialize_enhanced_models()
        
        # Initialize enhanced people detection
        self.enhanced_people_detector = EnhancedPeopleDetection()
        
        # Temporal tracking for other detections
        self.helmet_history = deque(maxlen=20)
        self.face_cover_history = deque(maxlen=20)
        self.loitering_tracker = defaultdict(lambda: {
            'positions': deque(maxlen=50),
            'start_time': time.time(),
            'timestamps': deque(maxlen=50)
        })
        self.posture_history = deque(maxlen=30)
        
    def initialize_enhanced_models(self):
        """Initialize other detection models (helmet, face cover, etc.)"""
        try:
            # Face detection cascades
            self.face_cascade_default = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.face_cascade_alt = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
            self.face_cascade_alt2 = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
            self.profile_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_profileface.xml')
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml')
            
            # Initialize template libraries
            self.helmet_templates = self._create_helmet_templates()
            self.color_ranges = self._initialize_color_ranges()
            
            print("[SUCCESS] Enhanced detection models initialized")
            
        except Exception as e:
            print(f"[ERROR] Error initializing enhanced models: {e}")
    
    def _create_helmet_templates(self):
        """Create helmet templates for template matching"""
        templates = []
        for radius in range(15, 65, 5):
            # Perfect circle
            template = np.zeros((radius*2, radius*2), dtype=np.uint8)
            cv2.circle(template, (radius, radius), radius, 255, -1)
            templates.append(('circle', template))
            
            # Ellipse (vertical)
            template = np.zeros((radius*2, int(radius*1.6)), dtype=np.uint8)
            cv2.ellipse(template, (int(radius*0.8), radius), (int(radius*0.8), radius), 0, 0, 360, 255, -1)
            templates.append(('ellipse_v', template))
            
            # Ellipse (horizontal)
            template = np.zeros((int(radius*1.6), radius*2), dtype=np.uint8)
            cv2.ellipse(template, (radius, int(radius*0.8)), (radius, int(radius*0.8)), 0, 0, 360, 255, -1)
            templates.append(('ellipse_h', template))
        
        return templates
    
    def _initialize_color_ranges(self):
        """Initialize comprehensive color ranges for all detections"""
        return {
            'helmet': {
                # Enhanced black range - more sensitive
                'black': [(np.array([0, 0, 0]), np.array([180, 255, 80])),
                         (np.array([0, 0, 0]), np.array([180, 50, 50]))],
                # Enhanced white range - more sensitive
                'white': [(np.array([0, 0, 180]), np.array([180, 30, 255])),
                         (np.array([0, 0, 200]), np.array([180, 20, 255]))],
                # Enhanced blue ranges
                'blue_dark': [(np.array([100, 50, 20]), np.array([130, 255, 120])),
                             (np.array([100, 30, 10]), np.array([130, 255, 100]))],
                'blue_light': [(np.array([90, 30, 100]), np.array([110, 255, 255])),
                              (np.array([100, 20, 80]), np.array([120, 255, 255]))],
                # Enhanced red ranges
                'red': [(np.array([0, 50, 50]), np.array([10, 255, 255])),
                       (np.array([170, 50, 50]), np.array([180, 255, 255])),
                       (np.array([0, 30, 30]), np.array([15, 255, 255])),
                       (np.array([165, 30, 30]), np.array([180, 255, 255]))],
                # Enhanced yellow range
                'yellow': [(np.array([15, 100, 100]), np.array([35, 255, 255])),
                          (np.array([20, 80, 80]), np.array([40, 255, 255]))],
                # Enhanced orange range
                'orange': [(np.array([5, 100, 100]), np.array([25, 255, 255])),
                          (np.array([10, 80, 80]), np.array([30, 255, 255]))],
                # Enhanced green range
                'green': [(np.array([35, 50, 50]), np.array([85, 255, 255])),
                         (np.array([40, 30, 30]), np.array([80, 255, 255]))],
                # Enhanced gray range
                'gray': [(np.array([0, 0, 50]), np.array([180, 30, 200])),
                        (np.array([0, 0, 30]), np.array([180, 50, 180]))],
                # Additional common helmet colors
                'silver': [(np.array([0, 0, 100]), np.array([180, 20, 200])),
                          (np.array([0, 0, 80]), np.array([180, 30, 180]))],
                'brown': [(np.array([10, 50, 20]), np.array([20, 255, 200])),
                         (np.array([5, 30, 10]), np.array([25, 255, 150]))],
                'purple': [(np.array([130, 50, 50]), np.array([160, 255, 255])),
                          (np.array([125, 30, 30]), np.array([165, 255, 200]))]
            },
            'mask': {
                'blue_surgical': [(np.array([100, 100, 50]), np.array([130, 255, 200]))],
                'white_surgical': [(np.array([0, 0, 180]), np.array([180, 30, 255]))],
                'black_cloth': [(np.array([0, 0, 0]), np.array([180, 255, 50]))],
                'light_blue': [(np.array([90, 50, 100]), np.array([110, 255, 255]))],
                'green_medical': [(np.array([40, 50, 50]), np.array([80, 255, 200]))],
                'gray_cloth': [(np.array([0, 0, 50]), np.array([180, 50, 150]))]
            }
        }
    
    def detect_people(self, frame):
        """
        Enhanced people detection using the new EnhancedPeopleDetection class
        """
        try:
            return self.enhanced_people_detector.detect_people_enhanced(frame)
        except Exception as e:
            print(f"Enhanced people detection error: {e}")
            return 0, 0.1
    
    def detect_helmet(self, frame):
        """Enhanced helmet detection with improved accuracy"""
        try:
            # First check if there are people in the frame
            people_count, _ = self.detect_people(frame)
            if people_count == 0:
                print("[HELMET DEBUG] No people detected, skipping helmet detection")
                return False, 0.0
            
            print(f"[HELMET DEBUG] People detected: {people_count}, proceeding with helmet detection")
            
            # FAST DETECTION - Use only most effective methods
            # Method 1: Fast color detection
            helmet_color, conf_color = self._detect_helmet_color_multi_space(frame)
            print(f"[HELMET DEBUG] Color detection: {helmet_color}, confidence: {conf_color:.3f}")
            
            # Method 2: Fast template matching
            helmet_template, conf_template = self._detect_helmet_template_matching(frame)
            print(f"[HELMET DEBUG] Template matching: {helmet_template}, confidence: {conf_template:.3f}")
            
            # Method 3: Fast Hough circles
            helmet_hough, conf_hough = self._detect_helmet_hough_circles(frame)
            print(f"[HELMET DEBUG] Hough circles: {helmet_hough}, confidence: {conf_hough:.3f}")
            
            # Fast ensemble voting - only 3 methods for speed
            detections = [
                (helmet_color, conf_color, 0.40),      # Higher weight for color
                (helmet_template, conf_template, 0.35), # Higher weight for template
                (helmet_hough, conf_hough, 0.25)        # Lower weight for hough
            ]
            
            total_confidence = 0
            detection_votes = 0
            
            # Lower confidence threshold for individual methods
            for detected, conf, weight in detections:
                if detected and conf > 0.3:  # Lowered from 0.5 to 0.3
                    total_confidence += conf * weight
                    detection_votes += 1
            
            # More lenient voting - require at least 1 method with high confidence OR 2 methods with medium confidence
            helmet_detected = (
                (detection_votes >= 2 and total_confidence > 0.4) or  # Lowered threshold
                (detection_votes >= 1 and total_confidence > 0.7)     # Single high-confidence detection
            )
            
            print(f"[HELMET DEBUG] Detection votes: {detection_votes}, Total confidence: {total_confidence:.3f}")
            print(f"[HELMET DEBUG] Helmet detected: {helmet_detected}")
            
            # Faster temporal consistency - reduced history requirement
            self.helmet_history.append(helmet_detected)
            if len(self.helmet_history) >= 5:  # Reduced from 10 to 5
                recent = list(self.helmet_history)[-5:]
                recent_positive = sum(recent)
                print(f"[HELMET DEBUG] Recent detections: {recent_positive}/5")
                
                if recent_positive >= 3:  # Reduced from 6 to 3
                    final_result = True, min(0.98, total_confidence * 1.2)
                    print(f"[HELMET DEBUG] Temporal consistency: HELMET DETECTED (confidence: {final_result[1]:.3f})")
                    return final_result
                elif recent_positive <= 1:  # Reduced from 3 to 1
                    print("[HELMET DEBUG] Temporal consistency: NO HELMET")
                    return False, 0.0
            
            final_result = helmet_detected, min(0.95, total_confidence)
            print(f"[HELMET DEBUG] Final result: {final_result[0]}, confidence: {final_result[1]:.3f}")
            return final_result
            
        except Exception as e:
            print(f"Enhanced helmet detection error: {e}")
            return False, 0.0
    
    def detect_face_cover(self, frame):
        """Enhanced face cover detection with improved accuracy"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Multi-cascade face detection
            faces = []
            for cascade in [self.face_cascade_default, self.face_cascade_alt, 
                           self.face_cascade_alt2, self.profile_cascade]:
                detected = cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
                faces.extend(detected)
            
            # Remove duplicate face detections
            faces = self._merge_overlapping_faces(faces)
            
            if len(faces) == 0:
                return False, 0.0
            
            max_confidence = 0.0
            face_cover_detected = False
            
            for (x, y, w, h) in faces:
                face_region = frame[y:y+h, x:x+w]
                
                if face_region.size > 0:
                    # Method 1: Advanced color analysis
                    color_score = self._analyze_face_cover_color_advanced(face_region)
                    
                    # Method 2: Texture analysis
                    texture_score = self._analyze_face_cover_texture(face_region)
                    
                    # Method 3: Edge density analysis
                    edge_score = self._analyze_face_cover_edges(face_region)
                    
                    # Method 4: Eye visibility check
                    eye_score = self._analyze_eye_visibility(face_region, gray[y:y+h, x:x+w])
                    
                    # Method 5: Lower face analysis
                    lower_face_score = self._analyze_lower_face_coverage(face_region)
                    
                    # Weighted ensemble
                    combined_score = (
                        color_score * 0.30 +
                        texture_score * 0.25 +
                        edge_score * 0.20 +
                        eye_score * 0.10 +
                        lower_face_score * 0.15
                    )
                    
                    if combined_score > 0.70:
                        face_cover_detected = True
                        max_confidence = max(max_confidence, combined_score)
            
            # Temporal consistency
            self.face_cover_history.append(face_cover_detected)
            if len(self.face_cover_history) >= 10:
                recent = list(self.face_cover_history)[-10:]
                if sum(recent) >= 7:
                    return True, min(0.98, max_confidence * 1.1)
                elif sum(recent) <= 2:
                    return False, 0.0
            
            return face_cover_detected, min(0.95, max_confidence)
            
        except Exception as e:
            print(f"Enhanced face cover detection error: {e}")
            return False, 0.0
    
    def detect_loitering(self, frame):
        """Enhanced loitering detection with improved accuracy"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Use enhanced people detection first
            people_count, _ = self.detect_people(frame)
            if people_count == 0:
                return False, 0.0
            
            # Apply background subtraction
            fg_mask = cv2.createBackgroundSubtractorMOG2().apply(gray)
            
            # Find motion contours
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            current_time = time.time()
            loitering_detected = False
            max_confidence = 0.0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 3000:
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        # Find matching tracker or create new one
                        tracker_id = self._find_or_create_tracker(cx, cy, current_time)
                        
                        if tracker_id is not None:
                            tracker = self.loitering_tracker[tracker_id]
                            tracker['positions'].append((cx, cy))
                            tracker['timestamps'].append(current_time)
                            
                            # Analyze if person has been stationary
                            if len(tracker['positions']) >= 15:
                                positions = np.array(list(tracker['positions'])[-15:])
                                movement_variance = np.var(positions, axis=0)
                                total_variance = np.sum(movement_variance)
                                
                                elapsed_time = current_time - tracker['start_time']
                                
                                if total_variance < 200 and elapsed_time > 25:
                                    loitering_detected = True
                                    confidence = min(0.98, 0.7 + (elapsed_time / 100))
                                    max_confidence = max(max_confidence, confidence)
            
            # Clean up old trackers
            self._cleanup_old_trackers(current_time, max_age=180)
            
            return loitering_detected, max_confidence
            
        except Exception as e:
            print(f"Enhanced loitering detection error: {e}")
            return False, 0.0
    
    def detect_posture(self, frame):
        """Enhanced posture detection with improved accuracy"""
        try:
            # First check if there are people in the frame
            people_count, _ = self.detect_people(frame)
            if people_count == 0:
                return False, 0.0
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Multi-scale edge detection
            edges1 = cv2.Canny(gray, 20, 80)
            edges2 = cv2.Canny(gray, 40, 120)
            edges3 = cv2.Canny(gray, 60, 180)
            edges = cv2.bitwise_or(edges1, cv2.bitwise_or(edges2, edges3))
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            posture_scores = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 3500:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = h / w if w > 0 else 0
                    
                    if aspect_ratio > 1.5 and h > 120:
                        # Advanced posture analysis
                        hull = cv2.convexHull(contour)
                        hull_area = cv2.contourArea(hull)
                        
                        if hull_area > 0:
                            solidity = area / hull_area
                            
                            # Analyze posture based on contour shape
                            if solidity > 0.8:
                                posture_scores.append(0.9)
                            elif solidity > 0.7:
                                posture_scores.append(0.7)
                            elif solidity > 0.5:
                                posture_scores.append(0.5)
                            else:
                                posture_scores.append(0.2)
            
            # Calculate final posture assessment
            if posture_scores:
                avg_posture = sum(posture_scores) / len(posture_scores)
            else:
                avg_posture = 0.5
            
            # Temporal smoothing
            self.posture_history.append(avg_posture)
            
            if len(self.posture_history) >= 15:
                recent_avg = sum(list(self.posture_history)[-15:]) / 15
                
                if recent_avg < 0.45:
                    return True, 1.0 - recent_avg
            
            return False, 0.0
            
        except Exception as e:
            print(f"Enhanced posture detection error: {e}")
            return False, 0.0
    
    def process_frame(self, frame):
        """Process frame through all enhanced detection models"""
        try:
            results = {
                'people_count': 0,
                'helmet_violation': False,
                'face_cover_violation': False,
                'loitering': False,
                'posture_violation': False,
                'alerts': []
            }
            
            # Enhanced people detection
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
                    'message': 'Poor posture detected - Please stand properly',
                    'confidence': conf
                })
            
            return results
            
        except Exception as e:
            print(f"Enhanced frame processing error: {e}")
            return {
                'people_count': 0,
                'helmet_violation': False,
                'face_cover_violation': False,
                'loitering': False,
                'posture_violation': False,
                'alerts': []
            }
    
    # Helper methods for helmet detection
    def _detect_helmet_color_multi_space(self, frame):
        """Detect helmet using multiple color spaces - OPTIMIZED FOR SPEED"""
        try:
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (320, 240))
            hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)
            combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            
            # Process only most common helmet colors for speed
            priority_colors = ['black', 'white', 'red', 'blue', 'gray']
            for color_name in priority_colors:
                if color_name in self.color_ranges['helmet']:
                    ranges = self.color_ranges['helmet'][color_name]
                    for lower, upper in ranges:
                        mask = cv2.inRange(hsv, lower, upper)
                        combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Fast mask cleaning - simplified for speed
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            
            # Find and analyze contours - optimized
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            best_confidence = 0.0
            helmet_found = False
            
            # Process only largest contours for speed
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]  # Only top 5 largest
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 200:  # Lowered threshold for speed
                    x, y, w, h = cv2.boundingRect(contour)
                    small_height, small_width = small_frame.shape[:2]
                    
                    if y < small_height * 0.6:  # Use small frame dimensions
                        aspect_ratio = w / h if h > 0 else 0
                        if 0.5 <= aspect_ratio <= 2.0:
                            # Simplified circularity check for speed
                            perimeter = cv2.arcLength(contour, True)
                            if perimeter > 0:
                                circularity = 4 * np.pi * area / (perimeter * perimeter)
                                
                                if circularity > 0.3:  # Slightly higher threshold for speed
                                    helmet_found = True
                                    confidence = min(0.95, circularity * (area / 2000))  # Simplified calculation
                                    best_confidence = max(best_confidence, confidence)
                                    break  # Found one, no need to check more
            
            return helmet_found, best_confidence
            
        except Exception as e:
            return False, 0.0
    
    def _detect_helmet_template_matching(self, frame):
        """Fast template matching - OPTIMIZED FOR SPEED"""
        try:
            # Resize for faster processing
            small_frame = cv2.resize(frame, (320, 240))
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            
            max_confidence = 0.0
            helmet_found = False
            
            # Use only most effective templates and scales for speed
            priority_templates = [('circle', template) for template_type, template in self.helmet_templates if template_type == 'circle'][:3]  # Only first 3 circle templates
            
            for template_type, template in priority_templates:
                for scale in [0.8, 1.0, 1.2]:  # Reduced scales for speed
                    scaled_template = cv2.resize(template, None, fx=scale, fy=scale)
                    
                    if (scaled_template.shape[0] > gray.shape[0] or 
                        scaled_template.shape[1] > gray.shape[1]):
                        continue
                    
                    # Use only one method for speed
                    result = cv2.matchTemplate(gray, scaled_template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(result)
                    
                    y_pos = max_loc[1]
                    if y_pos < small_frame.shape[0] * 0.5 and max_val > 0.5:  # Lowered threshold for speed
                        helmet_found = True
                        max_confidence = max(max_confidence, max_val)
                        break  # Found match, no need to check more scales
                
                if helmet_found:
                    break  # Found match, no need to check more templates
            
            return helmet_found, max_confidence
            
        except Exception as e:
            return False, 0.0
    
    def _detect_helmet_hough_circles(self, frame):
        """Detect helmets using Hough Circle Transform - OPTIMIZED FOR SPEED"""
        try:
            # Resize for faster processing
            small_frame = cv2.resize(frame, (320, 240))
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 1)  # Smaller blur for speed
            
            upper_half = gray[:gray.shape[0]//2, :]
            
            # Faster - fewer parameter combinations
            circles_found = []
            for param1 in [50, 70]:  # Reduced from 4 to 2
                for param2 in [20, 30]:  # Reduced from 5 to 2
                    circles = cv2.HoughCircles(
                        upper_half, cv2.HOUGH_GRADIENT, dp=1.0,
                        minDist=40, param1=param1, param2=param2,
                        minRadius=10, maxRadius=80  # Smaller range for speed
                    )
                    if circles is not None:
                        circles_found.extend(circles[0])
                        break  # Found circles, no need to try more parameters
            
            if circles_found:
                valid_circles = 0
                for circle in circles_found:
                    x, y, r = circle
                    if 10 <= r <= 60:  # Smaller range for speed
                        valid_circles += 1
                
                if valid_circles > 0:
                    confidence = min(0.95, 0.7 + (valid_circles * 0.1))  # Faster calculation
                    return True, confidence
            
            return False, 0.0
            
        except Exception as e:
            return False, 0.0
    
    def _detect_helmet_advanced_shape(self, frame):
        """Advanced geometric shape analysis for helmets"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            edges1 = cv2.Canny(gray, 30, 90)
            edges2 = cv2.Canny(gray, 50, 150)
            edges3 = cv2.Canny(gray, 70, 200)
            edges = cv2.bitwise_or(edges1, cv2.bitwise_or(edges2, edges3))
            
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            best_score = 0.0
            helmet_found = False
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1800:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    if y < frame.shape[0] * 0.45:
                        perimeter = cv2.arcLength(contour, True)
                        if perimeter > 0:
                            circularity = 4 * np.pi * area / (perimeter * perimeter)
                            aspect_ratio = w / h if h > 0 else 0
                            
                            hull = cv2.convexHull(contour)
                            hull_area = cv2.contourArea(hull)
                            solidity = area / hull_area if hull_area > 0 else 0
                            
                            if len(contour) >= 5:
                                ellipse = cv2.fitEllipse(contour)
                                ellipse_area = np.pi * (ellipse[1][0]/2) * (ellipse[1][1]/2)
                                ellipse_fit = min(area/ellipse_area, ellipse_area/area) if ellipse_area > 0 else 0
                                
                                shape_score = (
                                    circularity * 0.35 +
                                    solidity * 0.25 +
                                    ellipse_fit * 0.25 +
                                    (1.0 if 0.7 <= aspect_ratio <= 1.3 else 0.5) * 0.15
                                )
                                
                                if shape_score > 0.65:
                                    helmet_found = True
                                    best_score = max(best_score, shape_score)
            
            return helmet_found, best_score
            
        except Exception as e:
            return False, 0.0
    
    def _detect_helmet_edge_features(self, frame):
        """Detect helmet using edge feature analysis"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            
            sobelx = cv2.Sobel(filtered, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(filtered, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            magnitude = np.uint8(magnitude / magnitude.max() * 255)
            
            _, edges = cv2.threshold(magnitude, 50, 255, cv2.THRESH_BINARY)
            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1500:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    if y < frame.shape[0] * 0.45:
                        perimeter = cv2.arcLength(contour, True)
                        if perimeter > 0:
                            circularity = 4 * np.pi * area / (perimeter * perimeter)
                            
                            if circularity > 0.6:
                                return True, min(0.9, circularity)
            
            return False, 0.0
            
        except Exception as e:
            return False, 0.0
    
    # Helper methods for face cover detection
    def _merge_overlapping_faces(self, faces):
        """Merge overlapping face detections using Non-Maximum Suppression"""
        if len(faces) == 0:
            return []
        
        faces = np.array(faces)
        x1 = faces[:, 0]
        y1 = faces[:, 1]
        x2 = faces[:, 0] + faces[:, 2]
        y2 = faces[:, 1] + faces[:, 3]
        
        areas = faces[:, 2] * faces[:, 3]
        order = np.argsort(areas)[::-1]
        
        keep = []
        while len(order) > 0:
            i = order[0]
            keep.append(faces[i])
            
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            
            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)
            
            overlap = (w * h) / areas[order[1:]]
            
            order = order[np.where(overlap < 0.5)[0] + 1]
        
        return keep
    
    def _analyze_face_cover_color_advanced(self, face_region):
        """Advanced multi-color space analysis for mask detection"""
        try:
            hsv = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)
            combined_mask = np.zeros(face_region.shape[:2], dtype=np.uint8)
            
            for mask_type, ranges in self.color_ranges['mask'].items():
                for lower, upper in ranges:
                    mask = cv2.inRange(hsv, lower, upper)
                    combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            lower_portion = face_region[int(face_region.shape[0]*0.4):, :]
            if lower_portion.size > 0:
                lower_hsv = cv2.cvtColor(lower_portion, cv2.COLOR_BGR2HSV)
                lower_mask = np.zeros(lower_hsv.shape[:2], dtype=np.uint8)
                
                for mask_type, ranges in self.color_ranges['mask'].items():
                    for lower, upper in ranges:
                        mask = cv2.inRange(lower_hsv, lower, upper)
                        lower_mask = cv2.bitwise_or(lower_mask, mask)
                
                lower_coverage = cv2.countNonZero(lower_mask) / (lower_hsv.shape[0] * lower_hsv.shape[1])
                total_coverage = cv2.countNonZero(combined_mask) / (face_region.shape[0] * face_region.shape[1])
                
                final_score = total_coverage * 0.3 + lower_coverage * 0.7
                
                if final_score > 0.35:
                    return min(0.98, final_score * 1.5)
            
            return 0.0
            
        except Exception as e:
            return 0.0
    
    def _analyze_face_cover_texture(self, face_region):
        """Analyze texture patterns to detect masks"""
        try:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            texture = cv2.filter2D(gray, -1, kernel)
            
            texture_var = np.var(texture)
            
            if texture_var < 150:
                return 0.9
            elif texture_var < 300:
                return 0.7
            elif texture_var < 500:
                return 0.5
            else:
                return 0.2
                
        except Exception as e:
            return 0.0
    
    def _analyze_face_cover_edges(self, face_region):
        """Analyze edge density for mask detection"""
        try:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            edges1 = cv2.Canny(gray, 30, 100)
            edges2 = cv2.Canny(gray, 50, 150)
            edges = cv2.bitwise_or(edges1, edges2)
            
            edge_pixels = cv2.countNonZero(edges)
            total_pixels = face_region.shape[0] * face_region.shape[1]
            edge_density = edge_pixels / total_pixels
            
            if edge_density < 0.08:
                return 0.95
            elif edge_density < 0.12:
                return 0.85
            elif edge_density < 0.15:
                return 0.65
            else:
                return 0.3
                
        except Exception as e:
            return 0.0
    
    def _analyze_eye_visibility(self, face_region, face_gray):
        """Check eye visibility - covered faces have fewer/no eyes visible"""
        try:
            upper_half = face_gray[:face_gray.shape[0]//2, :]
            
            if upper_half.size > 0:
                eyes = self.eye_cascade.detectMultiScale(upper_half, 1.1, 3, minSize=(20, 20))
                
                if len(eyes) == 0:
                    return 0.9
                elif len(eyes) == 1:
                    return 0.6
                else:
                    return 0.2
            
            return 0.5
            
        except Exception as e:
            return 0.0
    
    def _analyze_lower_face_coverage(self, face_region):
        """Specifically analyze lower face (mouth/nose area) for coverage"""
        try:
            h = face_region.shape[0]
            lower_face = face_region[h//2:, :]
            
            if lower_face.size == 0:
                return 0.0
            
            hsv = cv2.cvtColor(lower_face, cv2.COLOR_BGR2HSV)
            
            mask_pixels = 0
            for mask_type, ranges in self.color_ranges['mask'].items():
                for lower, upper in ranges:
                    mask = cv2.inRange(hsv, lower, upper)
                    mask_pixels += cv2.countNonZero(mask)
            
            total_pixels = lower_face.shape[0] * lower_face.shape[1]
            coverage_ratio = mask_pixels / total_pixels
            
            hsv_mean = cv2.mean(hsv)[:3]
            hsv_std = np.std(hsv.reshape(-1, 3), axis=0)
            uniformity = 1.0 - (np.mean(hsv_std) / 255.0)
            
            score = coverage_ratio * 0.6 + uniformity * 0.4
            
            if score > 0.5:
                return min(0.95, score * 1.3)
            
            return score * 0.8
            
        except Exception as e:
            return 0.0
    
    # Helper methods for loitering detection
    def _find_or_create_tracker(self, cx, cy, current_time, max_distance=80):
        """Find existing tracker or create new one"""
        min_dist = float('inf')
        closest_tracker = None
        
        for tracker_id, tracker in self.loitering_tracker.items():
            if len(tracker['positions']) > 0:
                last_pos = tracker['positions'][-1]
                dist = np.sqrt((cx - last_pos[0])**2 + (cy - last_pos[1])**2)
                
                time_gap = current_time - tracker['timestamps'][-1]
                
                if dist < min_dist and dist < max_distance and time_gap < 5:
                    min_dist = dist
                    closest_tracker = tracker_id
        
        if closest_tracker is not None:
            return closest_tracker
        else:
            new_id = f"tracker_{int(current_time * 1000)}_{cx}_{cy}"
            self.loitering_tracker[new_id] = {
                'positions': deque(maxlen=50),
                'start_time': current_time,
                'timestamps': deque(maxlen=50)
            }
            return new_id
    
    def _cleanup_old_trackers(self, current_time, max_age=180):
        """Remove trackers that haven't been updated recently"""
        to_remove = []
        for tracker_id, tracker in self.loitering_tracker.items():
            if len(tracker['timestamps']) > 0:
                time_since_update = current_time - tracker['timestamps'][-1]
                if time_since_update > max_age:
                    to_remove.append(tracker_id)
        
        for tracker_id in to_remove:
            del self.loitering_tracker[tracker_id]
    
    def get_detection_stats(self):
        """Get comprehensive detection statistics"""
        try:
            people_stats = self.enhanced_people_detector.get_detection_stats()
            
            return {
                'people_detection': people_stats,
                'helmet_detections': len([x for x in self.helmet_history if x]),
                'face_cover_detections': len([x for x in self.face_cover_history if x]),
                'active_trackers': len(self.loitering_tracker),
                'posture_violations': len([x for x in self.posture_history if x < 0.5])
            }
            
        except Exception as e:
            return {'error': str(e)}
