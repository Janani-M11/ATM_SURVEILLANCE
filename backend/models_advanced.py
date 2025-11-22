import cv2
import numpy as np
import time
from collections import deque
import math

class AdvancedDetectionPipeline:
    def __init__(self):
        self.initialize_advanced_models()
        self.loitering_tracker = {}
        self.posture_history = deque(maxlen=30)
        self.face_cover_history = deque(maxlen=10)
        self.helmet_history = deque(maxlen=10)
        
    def initialize_advanced_models(self):
        """Initialize advanced detection models using multiple algorithms"""
        try:
            # Initialize OpenCV HOG descriptor for people detection
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            
            # Initialize background subtractor for motion detection
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
            
            # Initialize multiple face cascades for better detection
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
            
            # Initialize eye cascade for better face validation
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            
            # Initialize template matching for helmet detection
            self.helmet_templates = self._create_helmet_templates()
            
            # Initialize color histograms for better detection
            self.helmet_color_ranges = self._define_helmet_color_ranges()
            self.mask_color_ranges = self._define_mask_color_ranges()
            
            print("[SUCCESS] Advanced detection models initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Error initializing advanced models: {e}")
            self.fallback_mode = True
    
    def _create_helmet_templates(self):
        """Create helmet templates for template matching"""
        templates = []
        # Create circular templates of different sizes
        for radius in [20, 30, 40, 50]:
            template = np.zeros((radius*2, radius*2), dtype=np.uint8)
            cv2.circle(template, (radius, radius), radius, 255, -1)
            templates.append(template)
        return templates
    
    def _define_helmet_color_ranges(self):
        """Define comprehensive helmet color ranges"""
        return {
            'black': [(np.array([0, 0, 0]), np.array([180, 255, 50]))],
            'white': [(np.array([0, 0, 200]), np.array([180, 30, 255]))],
            'blue': [(np.array([100, 50, 20]), np.array([130, 255, 100]))],
            'red': [(np.array([0, 50, 20]), np.array([10, 255, 100])), 
                   (np.array([170, 50, 20]), np.array([180, 255, 100]))],
            'yellow': [(np.array([20, 50, 20]), np.array([30, 255, 100]))],
            'green': [(np.array([40, 50, 20]), np.array([80, 255, 100]))]
        }
    
    def _define_mask_color_ranges(self):
        """Define comprehensive mask color ranges"""
        return {
            'blue_surgical': [(np.array([100, 100, 50]), np.array([130, 255, 200]))],
            'white_surgical': [(np.array([0, 0, 180]), np.array([180, 30, 255]))],
            'black_cloth': [(np.array([0, 0, 0]), np.array([180, 255, 40]))],
            'n95_blue': [(np.array([100, 80, 60]), np.array([130, 255, 180]))],
            'fabric_patterns': [(np.array([0, 50, 50]), np.array([180, 255, 150]))]
        }
    
    def detect_people(self, frame):
        """Advanced people detection using multiple methods"""
        try:
            # Method 1: HOG descriptor
            frame_resized = cv2.resize(frame, (640, 480))
            boxes, weights = self.hog.detectMultiScale(
                frame_resized,
                winStride=(8, 8),
                padding=(8, 8),
                scale=1.05
            )
            
            # Method 2: Background subtraction
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fg_mask = self.bg_subtractor.apply(gray)
            
            # Find motion contours
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            motion_people = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 3000:  # Significant motion area
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = h / w if w > 0 else 0
                    if aspect_ratio > 1.2:  # Person-like aspect ratio
                        motion_people += 1
            
            # Combine both methods
            hog_people = len(boxes)
            total_people = max(hog_people, motion_people)
            
            # Calculate confidence based on consistency
            confidence = 0.9 if hog_people > 0 and motion_people > 0 else 0.7
            
            return total_people, confidence
            
        except Exception as e:
            print(f"HOG detection error: {e}")
            return 0, 0.1
    
    def detect_helmet(self, frame):
        """Advanced helmet detection using multiple algorithms"""
        try:
            # First check if there are people in the frame
            people_count, _ = self.detect_people(frame)
            if people_count == 0:
                return False, 0.0
            
            # Method 1: Color-based detection with multiple ranges
            helmet_detected_color, confidence_color = self._detect_helmet_by_color(frame)
            
            # Method 2: Template matching
            helmet_detected_template, confidence_template = self._detect_helmet_by_template(frame)
            
            # Method 3: Shape analysis
            helmet_detected_shape, confidence_shape = self._detect_helmet_by_shape(frame)
            
            # Method 4: Edge detection
            helmet_detected_edge, confidence_edge = self._detect_helmet_by_edges(frame)
            
            # Combine all methods with weighted voting
            detections = [
                (helmet_detected_color, confidence_color, 0.3),
                (helmet_detected_template, confidence_template, 0.25),
                (helmet_detected_shape, confidence_shape, 0.25),
                (helmet_detected_edge, confidence_edge, 0.2)
            ]
            
            total_confidence = 0
            detection_count = 0
            
            for detected, conf, weight in detections:
                if detected:
                    total_confidence += conf * weight
                    detection_count += 1
            
            # Require at least 2 methods to agree for high confidence
            if detection_count >= 2 and total_confidence > 0.6:
                # Store in history for temporal consistency
                self.helmet_history.append(True)
                return True, min(0.95, total_confidence)
            elif detection_count >= 1 and total_confidence > 0.8:
                self.helmet_history.append(True)
                return True, min(0.95, total_confidence)
            else:
                self.helmet_history.append(False)
                return False, 0.0
            
        except Exception as e:
            print(f"Advanced helmet detection error: {e}")
            return False, 0.0
    
    def _detect_helmet_by_color(self, frame):
        """Detect helmet using comprehensive color analysis"""
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            
            # Apply all color ranges
            for color_name, ranges in self.helmet_color_ranges.items():
                for lower, upper in ranges:
                    mask = cv2.inRange(hsv, lower, upper)
                    combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Morphological operations to clean up the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1500:  # Minimum area
                    # Check position (should be in upper portion)
                    x, y, w, h = cv2.boundingRect(contour)
                    frame_height = frame.shape[0]
                    if y < frame_height * 0.5:  # Upper 50% of frame
                        # Check circularity
                        perimeter = cv2.arcLength(contour, True)
                        if perimeter > 0:
                            circularity = 4 * np.pi * area / (perimeter * perimeter)
                            if circularity > 0.3:  # Roughly circular
                                confidence = min(0.9, area / 10000)
                                return True, confidence
            
            return False, 0.0
            
        except Exception as e:
            print(f"Color-based helmet detection error: {e}")
            return False, 0.0
    
    def _detect_helmet_by_template(self, frame):
        """Detect helmet using template matching"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            max_match = 0
            
            for template in self.helmet_templates:
                # Template matching
                result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                max_match = max(max_match, max_val)
            
            # Threshold for template matching
            if max_match > 0.6:
                return True, max_match
            else:
                return False, 0.0
                
        except Exception as e:
            print(f"Template-based helmet detection error: {e}")
            return False, 0.0
    
    def _detect_helmet_by_shape(self, frame):
        """Detect helmet using advanced shape analysis"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 2000:
                    # Advanced shape analysis
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull)
                    
                    if hull_area > 0:
                        solidity = area / hull_area
                        
                        # Check for helmet-like properties
                        perimeter = cv2.arcLength(contour, True)
                        if perimeter > 0:
                            circularity = 4 * np.pi * area / (perimeter * perimeter)
                            
                            # Helmet characteristics: circular, solid, in upper frame
                            x, y, w, h = cv2.boundingRect(contour)
                            frame_height = frame.shape[0]
                            
                            if (circularity > 0.4 and solidity > 0.7 and 
                                y < frame_height * 0.4 and h > w * 0.8):
                                confidence = min(0.9, (circularity + solidity) / 2)
                                return True, confidence
            
            return False, 0.0
            
        except Exception as e:
            print(f"Shape-based helmet detection error: {e}")
            return False, 0.0
    
    def _detect_helmet_by_edges(self, frame):
        """Detect helmet using edge analysis"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection with different thresholds
            edges1 = cv2.Canny(blurred, 30, 100)
            edges2 = cv2.Canny(blurred, 50, 150)
            
            # Combine edge images
            combined_edges = cv2.bitwise_or(edges1, edges2)
            
            # Find contours
            contours, _ = cv2.findContours(combined_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1500:
                    # Check for circular edge patterns
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        
                        if circularity > 0.5:  # Very circular
                            x, y, w, h = cv2.boundingRect(contour)
                            frame_height = frame.shape[0]
                            
                            if y < frame_height * 0.4:  # Upper portion
                                confidence = min(0.9, circularity)
                                return True, confidence
            
            return False, 0.0
            
        except Exception as e:
            print(f"Edge-based helmet detection error: {e}")
            return False, 0.0
    
    def detect_face_cover(self, frame):
        """Advanced face cover detection using multiple algorithms"""
        try:
            # Method 1: Haar cascade face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Use multiple face detection methods
            faces_frontal = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
            faces_profile = self.profile_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
            
            # Combine face detections
            all_faces = list(faces_frontal) + list(faces_profile)
            
            if len(all_faces) == 0:
                return False, 0.0
            
            face_cover_detected = False
            max_confidence = 0.0
            
            for (x, y, w, h) in all_faces:
                # Extract face region
                face_region = frame[y:y+h, x:x+w]
                
                if face_region.size > 0:
                    # Method 1: Color analysis
                    color_prob = self._analyze_face_region_color(face_region)
                    
                    # Method 2: Texture analysis
                    texture_prob = self._analyze_face_region_texture(face_region)
                    
                    # Method 3: Edge analysis
                    edge_prob = self._analyze_face_region_edges(face_region)
                    
                    # Method 4: Eye detection (if eyes not visible, likely covered)
                    eye_prob = self._analyze_face_region_eyes(face_region)
                    
                    # Combine all methods
                    combined_prob = (color_prob * 0.4 + texture_prob * 0.3 + 
                                   edge_prob * 0.2 + eye_prob * 0.1)
                    
                    if combined_prob > 0.75:  # High threshold for accuracy
                        face_cover_detected = True
                        max_confidence = max(max_confidence, combined_prob)
            
            # Store in history for temporal consistency
            self.face_cover_history.append(face_cover_detected)
            
            # Check temporal consistency
            if len(self.face_cover_history) >= 5:
                recent_detections = list(self.face_cover_history)[-5:]
                if sum(recent_detections) >= 3:  # At least 3 out of 5 recent frames
                    return True, max_confidence
            
            return face_cover_detected, max_confidence
            
        except Exception as e:
            print(f"Advanced face cover detection error: {e}")
            return False, 0.0
    
    def _analyze_face_region_color(self, face_region):
        """Advanced color analysis for face coverings"""
        try:
            hsv = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)
            combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            
            # Apply all mask color ranges
            for mask_type, ranges in self.mask_color_ranges.items():
                for lower, upper in ranges:
                    mask = cv2.inRange(hsv, lower, upper)
                    combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Calculate coverage percentage
            total_pixels = face_region.shape[0] * face_region.shape[1]
            covered_pixels = cv2.countNonZero(combined_mask)
            coverage_ratio = covered_pixels / total_pixels
            
            # Focus on lower half of face (mouth/nose area)
            lower_half = face_region[face_region.shape[0]//2:, :]
            if lower_half.size > 0:
                lower_hsv = cv2.cvtColor(lower_half, cv2.COLOR_BGR2HSV)
                lower_mask = np.zeros(lower_hsv.shape[:2], dtype=np.uint8)
                
                for mask_type, ranges in self.mask_color_ranges.items():
                    for lower, upper in ranges:
                        mask = cv2.inRange(lower_hsv, lower, upper)
                        lower_mask = cv2.bitwise_or(lower_mask, mask)
                
                lower_coverage = cv2.countNonZero(lower_mask) / (lower_half.shape[0] * lower_half.shape[1])
                
                # Weight lower half more heavily
                final_coverage = coverage_ratio * 0.3 + lower_coverage * 0.7
                
                if final_coverage > 0.4:  # At least 40% coverage
                    return min(0.95, final_coverage * 1.2)
            
            return 0.0
            
        except Exception as e:
            print(f"Face color analysis error: {e}")
            return 0.0
    
    def _analyze_face_region_texture(self, face_region):
        """Analyze texture patterns for face coverings"""
        try:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Calculate texture features using Local Binary Pattern
            # This is a simplified version - in production, use proper LBP
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            texture = cv2.filter2D(gray, -1, kernel)
            
            # Calculate texture variance
            texture_variance = np.var(texture)
            
            # Masks typically have lower texture variance than skin
            if texture_variance < 100:  # Threshold for smooth texture
                return 0.8
            elif texture_variance < 200:
                return 0.6
            else:
                return 0.2
                
        except Exception as e:
            print(f"Face texture analysis error: {e}")
            return 0.0
    
    def _analyze_face_region_edges(self, face_region):
        """Analyze edge patterns for face coverings"""
        try:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Count edge pixels
            edge_pixels = cv2.countNonZero(edges)
            total_pixels = face_region.shape[0] * face_region.shape[1]
            edge_ratio = edge_pixels / total_pixels
            
            # Masks typically have fewer edges than uncovered faces
            if edge_ratio < 0.1:  # Very few edges
                return 0.9
            elif edge_ratio < 0.15:
                return 0.7
            else:
                return 0.3
                
        except Exception as e:
            print(f"Face edge analysis error: {e}")
            return 0.0
    
    def _analyze_face_region_eyes(self, face_region):
        """Analyze eye visibility for face coverings"""
        try:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Detect eyes in the upper half of face
            upper_half = gray[:gray.shape[0]//2, :]
            
            if upper_half.size > 0:
                eyes = self.eye_cascade.detectMultiScale(upper_half, 1.1, 3)
                
                # If no eyes detected, likely covered
                if len(eyes) == 0:
                    return 0.8
                elif len(eyes) == 1:
                    return 0.6
                else:
                    return 0.2
            
            return 0.5  # Neutral if can't analyze
            
        except Exception as e:
            print(f"Face eye analysis error: {e}")
            return 0.0
    
    def detect_loitering(self, frame):
        """Advanced loitering detection using motion tracking"""
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
                    'start_time': time.time(),
                    'positions': [],
                    'motion_threshold': 50  # pixels
                }
            
            # Find motion contours
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 2000:  # Significant motion
                    # Get centroid
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        # Track position
                        self.loitering_tracker[frame_id]['positions'].append((cx, cy))
                        
                        # Check for loitering (minimal movement over time)
                        positions = self.loitering_tracker[frame_id]['positions']
                        if len(positions) > 10:  # Enough data points
                            # Calculate movement variance
                            positions_array = np.array(positions[-10:])  # Last 10 positions
                            movement_variance = np.var(positions_array)
                            
                            # If movement is very low, person is loitering
                            if movement_variance < 100:  # Low movement threshold
                                elapsed_time = time.time() - self.loitering_tracker[frame_id]['start_time']
                                if elapsed_time > 30:  # 30 seconds threshold
                                    return True, 0.9
            
            # Clean up old trackers
            current_time = time.time()
            self.loitering_tracker = {
                k: v for k, v in self.loitering_tracker.items() 
                if current_time - v['start_time'] < 300  # Keep for 5 minutes
            }
            
            return False, 0.0
            
        except Exception as e:
            print(f"Advanced loitering detection error: {e}")
            return False, 0.0
    
    def detect_posture(self, frame):
        """Advanced posture detection using multiple analysis methods"""
        try:
            # First check if there are people in the frame
            people_count, _ = self.detect_people(frame)
            if people_count == 0:
                return False, 0.0
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Method 1: Edge detection
            edges = cv2.Canny(gray, 30, 100)
            
            # Method 2: Contour analysis
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            posture_scores = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 3000:  # Significant contour
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate aspect ratio
                    aspect_ratio = h / w if w > 0 else 0
                    
                    # Check if contour looks like a person (tall and narrow)
                    if aspect_ratio > 1.8 and h > 150:
                        # Advanced posture analysis
                        hull = cv2.convexHull(contour)
                        hull_area = cv2.contourArea(hull)
                        
                        if hull_area > 0:
                            solidity = area / hull_area
                            
                            # Analyze posture based on contour shape
                            if solidity > 0.8:  # Very solid shape (good posture)
                                posture_scores.append(0.9)
                            elif solidity > 0.7:  # Good posture
                                posture_scores.append(0.7)
                            elif solidity > 0.5:  # Moderate posture
                                posture_scores.append(0.5)
                            else:  # Poor posture
                                posture_scores.append(0.2)
            
            # Calculate average posture score
            if posture_scores:
                avg_posture = sum(posture_scores) / len(posture_scores)
            else:
                avg_posture = 0.5  # Default neutral posture
            
            # Store in history for smoothing
            self.posture_history.append(avg_posture)
            
            # Calculate average posture over recent frames
            if len(self.posture_history) >= 10:
                recent_avg = sum(list(self.posture_history)[-10:]) / 10
                
                # Posture violation if consistently poor posture
                if recent_avg < 0.4:  # Very strict threshold
                    return True, 1.0 - recent_avg
            
            return False, 0.0
            
        except Exception as e:
            print(f"Advanced posture detection error: {e}")
            return False, 0.0
    
    def process_frame(self, frame):
        """Process frame through all advanced detection models"""
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
                    'message': 'Poor posture detected - Please stand properly',
                    'confidence': conf
                })
            
            return results
            
        except Exception as e:
            print(f"Advanced frame processing error: {e}")
            return {
                'people_count': 0,
                'helmet_violation': False,
                'face_cover_violation': False,
                'loitering': False,
                'posture_violation': False,
                'alerts': []
            }
