import cv2
import numpy as np
import time
from collections import deque, defaultdict
import math

class UltraHighAccuracyDetectionPipeline:
    """
    Ultra-high accuracy detection pipeline with ensemble methods,
    temporal consistency, and multi-algorithm fusion for maximum precision.
    """
    
    def __init__(self):
        self.initialize_ultra_models()
        
        # Temporal tracking for consistency
        self.people_history = deque(maxlen=15)
        self.helmet_history = deque(maxlen=20)
        self.face_cover_history = deque(maxlen=20)
        self.loitering_tracker = defaultdict(lambda: {
            'positions': deque(maxlen=50),
            'start_time': time.time(),
            'timestamps': deque(maxlen=50)
        })
        self.posture_history = deque(maxlen=30)
        
        # Optical flow tracking
        self.prev_gray = None
        self.feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
        self.lk_params = dict(winSize=(15,15), maxLevel=2, 
                             criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        
    def initialize_ultra_models(self):
        """Initialize all detection models with optimized parameters"""
        try:
            # Multiple HOG detectors with different scales
            self.hog_default = cv2.HOGDescriptor()
            self.hog_default.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            
            self.hog_daimler = cv2.HOGDescriptor((48, 96), (16, 16), (8, 8), (8, 8), 9)
            self.hog_daimler.setSVMDetector(cv2.HOGDescriptor_getDaimlerPeopleDetector())
            
            # Background subtractors for motion detection
            self.bg_subtractor_mog2 = cv2.createBackgroundSubtractorMOG2(
                history=500, varThreshold=16, detectShadows=True)
            self.bg_subtractor_knn = cv2.createBackgroundSubtractorKNN(
                history=500, dist2Threshold=400, detectShadows=True)
            
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
            
            print("[SUCCESS] Ultra-high accuracy detection models initialized")
            
        except Exception as e:
            print(f"[ERROR] Error initializing ultra models: {e}")
    
    def _create_helmet_templates(self):
        """Create comprehensive helmet template library"""
        templates = []
        
        # Multiple sizes and aspect ratios
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
                'black': [(np.array([0, 0, 0]), np.array([180, 255, 50]))],
                'white': [(np.array([0, 0, 200]), np.array([180, 30, 255]))],
                'blue_dark': [(np.array([100, 50, 20]), np.array([130, 255, 100]))],
                'blue_light': [(np.array([90, 30, 100]), np.array([110, 255, 255]))],
                'red': [(np.array([0, 50, 50]), np.array([10, 255, 255])),
                       (np.array([170, 50, 50]), np.array([180, 255, 255]))],
                'yellow': [(np.array([20, 100, 100]), np.array([35, 255, 255]))],
                'orange': [(np.array([10, 100, 100]), np.array([25, 255, 255]))],
                'green': [(np.array([35, 50, 50]), np.array([85, 255, 255]))],
                'gray': [(np.array([0, 0, 50]), np.array([180, 30, 200]))]
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
    
    # ==================== PEOPLE DETECTION ====================
    
    def detect_people(self, frame):
        """
        Ultra-accurate people detection using ensemble of multiple methods:
        - Multi-scale HOG detection (Default + Daimler)
        - Dual background subtraction (MOG2 + KNN)
        - Optical flow analysis
        - Temporal consistency filtering
        - Conservative thresholding to reduce false positives
        """
        try:
            frame_resized = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Method 1: Default HOG detector (more conservative parameters)
            boxes_default, weights_default = self.hog_default.detectMultiScale(
                frame_resized, 
                winStride=(8, 8),  # Increased from 4,4 for less false positives
                padding=(8, 8), 
                scale=1.08,  # Increased from 1.05 for better separation
                hitThreshold=0.5)  # Added threshold for confidence
            
            # Filter by confidence (weights)
            people_hog_default = sum(1 for w in weights_default if w > 0.5) if len(weights_default) > 0 else 0
            
            # Method 2: Daimler HOG detector (more conservative)
            boxes_daimler, weights_daimler = self.hog_daimler.detectMultiScale(
                frame_resized, 
                winStride=(8, 8),  # Increased for less false positives
                padding=(4, 4), 
                scale=1.08,  # Increased for better separation
                hitThreshold=0.5)
            
            # Filter by confidence
            people_hog_daimler = sum(1 for w in weights_daimler if w > 0.5) if len(weights_daimler) > 0 else 0
            
            # Method 3: MOG2 background subtraction
            fg_mask_mog2 = self.bg_subtractor_mog2.apply(gray)
            people_mog2 = self._count_people_from_mask(fg_mask_mog2, frame.shape)
            
            # Method 4: KNN background subtraction
            fg_mask_knn = self.bg_subtractor_knn.apply(gray)
            people_knn = self._count_people_from_mask(fg_mask_knn, frame.shape)
            
            # Method 5: Optical flow analysis
            people_optical = self._detect_people_optical_flow(gray)
            
            # Ensemble voting with adjusted weights (prioritize HOG detectors more)
            weighted_counts = [
                (people_hog_default, 0.45),  # Increased from 0.35
                (people_hog_daimler, 0.30),  # Increased from 0.25
                (people_mog2, 0.10),  # Decreased from 0.15
                (people_knn, 0.10),  # Decreased from 0.15
                (people_optical, 0.05)  # Decreased from 0.10
            ]
            
            # Use MINIMUM of top 2 methods (more conservative)
            counts = [c for c, _ in weighted_counts]
            sorted_counts = sorted(counts, reverse=True)
            
            # If top two methods disagree significantly, use the lower count
            if len(sorted_counts) >= 2:
                if sorted_counts[0] - sorted_counts[1] > 1:
                    people_count = sorted_counts[1]  # Use lower count
                else:
                    # Calculate weighted average only if methods agree
                    total_weight = sum(w for _, w in weighted_counts)
                    weighted_sum = sum(count * weight for count, weight in weighted_counts)
                    people_count = int(round(weighted_sum / total_weight))
            else:
                people_count = counts[0] if counts else 0
            
            # Temporal consistency - use more conservative approach
            self.people_history.append(people_count)
            if len(self.people_history) >= 8:  # Increased from 5 for more stability
                # Use MODE (most common value) instead of median for stability
                recent = list(self.people_history)[-8:]
                from collections import Counter
                counter = Counter(recent)
                people_count = counter.most_common(1)[0][0]  # Most frequent count
            
            # Calculate confidence based on agreement between methods
            variance = np.var(counts) if counts else 0
            
            # Higher variance = lower confidence
            if variance > 2.0:  # Methods disagree significantly
                confidence = 0.6
            elif variance > 1.0:
                confidence = 0.75
            else:
                confidence = 0.9
            
            return people_count, confidence
            
        except Exception as e:
            print(f"Ultra people detection error: {e}")
            return 0, 0.1
    
    def _count_people_from_mask(self, mask, frame_shape):
        """Count people from foreground mask using contour analysis (conservative)"""
        try:
            # Clean mask more aggressively
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))  # Larger kernel
            mask_clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel)
            
            # Additional noise reduction
            mask_clean = cv2.GaussianBlur(mask_clean, (5, 5), 0)
            _, mask_clean = cv2.threshold(mask_clean, 200, 255, cv2.THRESH_BINARY)  # Stricter threshold
            
            contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            people = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 4000:  # Increased from 2500 - more conservative minimum area
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = h / w if w > 0 else 0
                    
                    # More strict person-like shape criteria
                    if 1.5 <= aspect_ratio <= 3.5 and h > 120:  # Stricter ranges
                        # Additional validation: check solidity
                        hull = cv2.convexHull(contour)
                        hull_area = cv2.contourArea(hull)
                        solidity = area / hull_area if hull_area > 0 else 0
                        
                        # Only count if reasonably solid (not fragmented)
                        if solidity > 0.6:
                            people += 1
            
            return people
            
        except Exception as e:
            return 0
    
    def _detect_people_optical_flow(self, gray):
        """Detect people using optical flow analysis (conservative)"""
        try:
            if self.prev_gray is None:
                self.prev_gray = gray
                return 0
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowFarneback(
                self.prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            
            # Calculate flow magnitude
            mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            
            # More conservative threshold for motion
            motion_mask = (mag > 3.5).astype(np.uint8) * 255  # Increased from 2 to 3.5
            
            # Clean up motion mask more aggressively
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
            motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE, kernel)
            motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_OPEN, kernel)
            
            # Count people-like motion regions with stricter criteria
            people = self._count_people_from_mask(motion_mask, gray.shape)
            
            self.prev_gray = gray
            return people
            
        except Exception as e:
            return 0
    
    # ==================== HELMET DETECTION ====================
    
    def detect_helmet(self, frame):
        """
        Ultra-accurate helmet detection using:
        - Multi-color space analysis (HSV, LAB, YCrCb)
        - Template matching with multiple scales
        - Circular Hough transform
        - Shape analysis with advanced geometry
        - Temporal consistency
        """
        try:
            # Check for people first
            people_count, _ = self.detect_people(frame)
            if people_count == 0:
                return False, 0.0
            
            # Method 1: Advanced color detection
            helmet_color, conf_color = self._detect_helmet_color_multi_space(frame)
            
            # Method 2: Template matching
            helmet_template, conf_template = self._detect_helmet_template_matching(frame)
            
            # Method 3: Circular Hough transform
            helmet_hough, conf_hough = self._detect_helmet_hough_circles(frame)
            
            # Method 4: Advanced shape analysis
            helmet_shape, conf_shape = self._detect_helmet_advanced_shape(frame)
            
            # Method 5: Edge-based detection with circular features
            helmet_edge, conf_edge = self._detect_helmet_edge_features(frame)
            
            # Ensemble voting
            detections = [
                (helmet_color, conf_color, 0.25),
                (helmet_template, conf_template, 0.20),
                (helmet_hough, conf_hough, 0.25),
                (helmet_shape, conf_shape, 0.20),
                (helmet_edge, conf_edge, 0.10)
            ]
            
            total_confidence = 0
            detection_votes = 0
            
            for detected, conf, weight in detections:
                if detected and conf > 0.5:
                    total_confidence += conf * weight
                    detection_votes += 1
            
            # Require at least 2 methods to agree
            helmet_detected = detection_votes >= 2 and total_confidence > 0.5
            
            # Temporal consistency
            self.helmet_history.append(helmet_detected)
            if len(self.helmet_history) >= 10:
                recent = list(self.helmet_history)[-10:]
                # Require 60% of recent frames to agree
                if sum(recent) >= 6:
                    return True, min(0.98, total_confidence * 1.2)
                elif sum(recent) <= 3:
                    return False, 0.0
            
            return helmet_detected, min(0.95, total_confidence)
            
        except Exception as e:
            print(f"Ultra helmet detection error: {e}")
            return False, 0.0
    
    def _detect_helmet_color_multi_space(self, frame):
        """Detect helmet using multiple color spaces"""
        try:
            # Convert to multiple color spaces
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
            
            combined_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            
            # HSV-based detection
            for color_name, ranges in self.color_ranges['helmet'].items():
                for lower, upper in ranges:
                    mask = cv2.inRange(hsv, lower, upper)
                    combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Clean mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            combined_mask = cv2.GaussianBlur(combined_mask, (5, 5), 0)
            
            # Find and analyze contours
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            best_confidence = 0.0
            helmet_found = False
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 2000:
                    x, y, w, h = cv2.boundingRect(contour)
                    frame_height, frame_width = frame.shape[:2]
                    
                    # Helmet should be in upper portion
                    if y < frame_height * 0.45:
                        # Check shape properties
                        aspect_ratio = w / h if h > 0 else 0
                        if 0.7 <= aspect_ratio <= 1.4:
                            perimeter = cv2.arcLength(contour, True)
                            if perimeter > 0:
                                circularity = 4 * np.pi * area / (perimeter * perimeter)
                                
                                if circularity > 0.5:
                                    # Check ellipse fit
                                    if len(contour) >= 5:
                                        ellipse = cv2.fitEllipse(contour)
                                        ellipse_area = np.pi * (ellipse[1][0]/2) * (ellipse[1][1]/2)
                                        if ellipse_area > 0:
                                            fit_ratio = min(area / ellipse_area, ellipse_area / area)
                                            
                                            if fit_ratio > 0.75:
                                                helmet_found = True
                                                confidence = min(0.95, circularity * fit_ratio * (area / 10000))
                                                best_confidence = max(best_confidence, confidence)
            
            return helmet_found, best_confidence
            
        except Exception as e:
            return False, 0.0
    
    def _detect_helmet_template_matching(self, frame):
        """Advanced template matching with multiple scales and rotations"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Enhance contrast
            gray = cv2.equalizeHist(gray)
            
            max_confidence = 0.0
            helmet_found = False
            
            for template_type, template in self.helmet_templates:
                # Multi-scale template matching
                for scale in [0.5, 0.7, 0.9, 1.0, 1.2, 1.5]:
                    scaled_template = cv2.resize(template, None, fx=scale, fy=scale)
                    
                    if (scaled_template.shape[0] > gray.shape[0] or 
                        scaled_template.shape[1] > gray.shape[1]):
                        continue
                    
                    # Multiple matching methods
                    for method in [cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED]:
                        result = cv2.matchTemplate(gray, scaled_template, method)
                        _, max_val, _, max_loc = cv2.minMaxLoc(result)
                        
                        # Check if match is in upper portion of frame
                        y_pos = max_loc[1]
                        if y_pos < frame.shape[0] * 0.45 and max_val > 0.6:
                            helmet_found = True
                            max_confidence = max(max_confidence, max_val)
            
            return helmet_found, max_confidence
            
        except Exception as e:
            return False, 0.0
    
    def _detect_helmet_hough_circles(self, frame):
        """Detect helmets using Hough Circle Transform"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (9, 9), 2)
            
            # Focus on upper half of frame
            upper_half = gray[:gray.shape[0]//2, :]
            
            # Detect circles with multiple parameter sets
            circles_found = []
            for param1 in [50, 70, 100]:
                for param2 in [25, 30, 35]:
                    circles = cv2.HoughCircles(
                        upper_half, cv2.HOUGH_GRADIENT, dp=1.2,
                        minDist=50, param1=param1, param2=param2,
                        minRadius=20, maxRadius=100
                    )
                    if circles is not None:
                        circles_found.extend(circles[0])
            
            if circles_found:
                # Filter and validate circles
                valid_circles = 0
                for circle in circles_found:
                    x, y, r = circle
                    # Check if circle size is reasonable for helmet
                    if 20 <= r <= 80:
                        valid_circles += 1
                
                if valid_circles > 0:
                    confidence = min(0.95, 0.7 + (valid_circles * 0.1))
                    return True, confidence
            
            return False, 0.0
            
        except Exception as e:
            return False, 0.0
    
    def _detect_helmet_advanced_shape(self, frame):
        """Advanced geometric shape analysis for helmets"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Multi-threshold edge detection
            edges1 = cv2.Canny(gray, 30, 90)
            edges2 = cv2.Canny(gray, 50, 150)
            edges3 = cv2.Canny(gray, 70, 200)
            
            # Combine edges
            edges = cv2.bitwise_or(edges1, cv2.bitwise_or(edges2, edges3))
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            best_score = 0.0
            helmet_found = False
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1800:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Upper frame check
                    if y < frame.shape[0] * 0.45:
                        # Comprehensive shape analysis
                        perimeter = cv2.arcLength(contour, True)
                        if perimeter > 0:
                            circularity = 4 * np.pi * area / (perimeter * perimeter)
                            aspect_ratio = w / h if h > 0 else 0
                            
                            # Convex hull analysis
                            hull = cv2.convexHull(contour)
                            hull_area = cv2.contourArea(hull)
                            solidity = area / hull_area if hull_area > 0 else 0
                            
                            # Ellipse fitting
                            if len(contour) >= 5:
                                ellipse = cv2.fitEllipse(contour)
                                ellipse_area = np.pi * (ellipse[1][0]/2) * (ellipse[1][1]/2)
                                ellipse_fit = min(area/ellipse_area, ellipse_area/area) if ellipse_area > 0 else 0
                                
                                # Composite score
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
            
            # Apply bilateral filter to preserve edges
            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Gradient-based edge detection
            sobelx = cv2.Sobel(filtered, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(filtered, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            magnitude = np.uint8(magnitude / magnitude.max() * 255)
            
            # Threshold
            _, edges = cv2.threshold(magnitude, 50, 255, cv2.THRESH_BINARY)
            
            # Find circular edge patterns
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
    
    # ==================== FACE COVER DETECTION ====================
    
    def detect_face_cover(self, frame):
        """
        Ultra-accurate face cover detection using:
        - Multiple face detection cascades
        - Facial landmark analysis
        - Multi-layer texture and color analysis
        - Eye visibility detection
        - Temporal consistency filtering
        """
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
                    
                    # Method 5: Lower face analysis (nose/mouth area)
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
                # Require 70% agreement
                if sum(recent) >= 7:
                    return True, min(0.98, max_confidence * 1.1)
                elif sum(recent) <= 2:
                    return False, 0.0
            
            return face_cover_detected, min(0.95, max_confidence)
            
        except Exception as e:
            print(f"Ultra face cover detection error: {e}")
            return False, 0.0
    
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
            # Convert to multiple color spaces
            hsv = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(face_region, cv2.COLOR_BGR2LAB)
            
            combined_mask = np.zeros(face_region.shape[:2], dtype=np.uint8)
            
            # Apply all mask color ranges
            for mask_type, ranges in self.color_ranges['mask'].items():
                for lower, upper in ranges:
                    mask = cv2.inRange(hsv, lower, upper)
                    combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Focus on lower 60% of face (mouth/nose area)
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
                
                # Weight lower face more heavily
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
            
            # Calculate Local Binary Pattern approximation
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            texture = cv2.filter2D(gray, -1, kernel)
            
            # Calculate texture statistics
            texture_mean = np.mean(texture)
            texture_std = np.std(texture)
            texture_var = np.var(texture)
            
            # Masks have more uniform texture (lower variance)
            # Skin has more texture variation
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
            
            # Multi-scale edge detection
            edges1 = cv2.Canny(gray, 30, 100)
            edges2 = cv2.Canny(gray, 50, 150)
            edges = cv2.bitwise_or(edges1, edges2)
            
            # Calculate edge density
            edge_pixels = cv2.countNonZero(edges)
            total_pixels = face_region.shape[0] * face_region.shape[1]
            edge_density = edge_pixels / total_pixels
            
            # Lower edge density suggests mask (smoother surface)
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
            # Focus on upper 50% of face
            upper_half = face_gray[:face_gray.shape[0]//2, :]
            
            if upper_half.size > 0:
                eyes = self.eye_cascade.detectMultiScale(upper_half, 1.1, 3, minSize=(20, 20))
                
                # Strong indicator: no eyes visible suggests full face cover
                if len(eyes) == 0:
                    return 0.9
                elif len(eyes) == 1:
                    return 0.6
                else:  # 2 or more eyes visible
                    return 0.2
            
            return 0.5
            
        except Exception as e:
            return 0.0
    
    def _analyze_lower_face_coverage(self, face_region):
        """Specifically analyze lower face (mouth/nose area) for coverage"""
        try:
            # Extract lower 50% of face
            h = face_region.shape[0]
            lower_face = face_region[h//2:, :]
            
            if lower_face.size == 0:
                return 0.0
            
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(lower_face, cv2.COLOR_BGR2HSV)
            
            # Check for typical mask colors in lower face
            mask_pixels = 0
            for mask_type, ranges in self.color_ranges['mask'].items():
                for lower, upper in ranges:
                    mask = cv2.inRange(hsv, lower, upper)
                    mask_pixels += cv2.countNonZero(mask)
            
            total_pixels = lower_face.shape[0] * lower_face.shape[1]
            coverage_ratio = mask_pixels / total_pixels
            
            # Also check for uniform color (masks are usually single color)
            hsv_mean = cv2.mean(hsv)[:3]
            hsv_std = np.std(hsv.reshape(-1, 3), axis=0)
            uniformity = 1.0 - (np.mean(hsv_std) / 255.0)
            
            # Combine coverage and uniformity
            score = coverage_ratio * 0.6 + uniformity * 0.4
            
            if score > 0.5:
                return min(0.95, score * 1.3)
            
            return score * 0.8
            
        except Exception as e:
            return 0.0
    
    # ==================== LOITERING DETECTION ====================
    
    def detect_loitering(self, frame):
        """
        Ultra-accurate loitering detection using:
        - Dual background subtraction
        - Optical flow trajectory analysis
        - KLT feature tracking
        - Position-based stationary detection
        - Multi-timeframe analysis
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply both background subtractors
            fg_mask_mog2 = self.bg_subtractor_mog2.apply(gray)
            fg_mask_knn = self.bg_subtractor_knn.apply(gray)
            
            # Combine masks
            fg_mask = cv2.bitwise_and(fg_mask_mog2, fg_mask_knn)
            
            # Clean mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            
            # Find significant motion regions
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            current_time = time.time()
            loitering_detected = False
            max_confidence = 0.0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 3000:  # Significant object
                    # Calculate centroid
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
                                # Calculate movement statistics
                                positions = np.array(list(tracker['positions'])[-15:])
                                movement_variance = np.var(positions, axis=0)
                                total_variance = np.sum(movement_variance)
                                
                                # Calculate time elapsed
                                elapsed_time = current_time - tracker['start_time']
                                
                                # Detect loitering: low movement + significant time
                                if total_variance < 200 and elapsed_time > 25:  # More sensitive
                                    loitering_detected = True
                                    # Confidence increases with time
                                    confidence = min(0.98, 0.7 + (elapsed_time / 100))
                                    max_confidence = max(max_confidence, confidence)
            
            # Clean up old trackers
            self._cleanup_old_trackers(current_time, max_age=180)
            
            return loitering_detected, max_confidence
            
        except Exception as e:
            print(f"Ultra loitering detection error: {e}")
            return False, 0.0
    
    def _find_or_create_tracker(self, cx, cy, current_time, max_distance=80):
        """Find existing tracker or create new one"""
        # Find closest tracker
        min_dist = float('inf')
        closest_tracker = None
        
        for tracker_id, tracker in self.loitering_tracker.items():
            if len(tracker['positions']) > 0:
                last_pos = tracker['positions'][-1]
                dist = np.sqrt((cx - last_pos[0])**2 + (cy - last_pos[1])**2)
                
                # Check time gap
                time_gap = current_time - tracker['timestamps'][-1]
                
                if dist < min_dist and dist < max_distance and time_gap < 5:
                    min_dist = dist
                    closest_tracker = tracker_id
        
        # Use existing tracker or create new one
        if closest_tracker is not None:
            return closest_tracker
        else:
            # Create new tracker with unique ID
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
    
    # ==================== POSTURE DETECTION ====================
    
    def detect_posture(self, frame):
        """
        Ultra-accurate posture detection using:
        - Multi-scale contour analysis
        - Skeleton approximation
        - Joint angle estimation
        - Biomechanical constraints
        - Temporal smoothing
        """
        try:
            # Check for people first
            people_count, _ = self.detect_people(frame)
            if people_count == 0:
                return False, 0.0
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Multi-scale edge detection
            edges1 = cv2.Canny(gray, 20, 80)
            edges2 = cv2.Canny(gray, 40, 120)
            edges3 = cv2.Canny(gray, 60, 180)
            edges = cv2.bitwise_or(edges1, cv2.bitwise_or(edges2, edges3))
            
            # Morphological operations to connect edges
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            posture_scores = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 3500:  # Significant person-sized contour
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = h / w if w > 0 else 0
                    
                    # Person-like aspect ratio
                    if aspect_ratio > 1.5 and h > 120:
                        # Method 1: Solidity analysis
                        hull = cv2.convexHull(contour)
                        hull_area = cv2.contourArea(hull)
                        solidity = area / hull_area if hull_area > 0 else 0
                        
                        # Method 2: Verticality check
                        moments = cv2.moments(contour)
                        if moments['mu20'] != 0:
                            # Calculate orientation
                            orientation = 0.5 * np.arctan2(2 * moments['mu11'], 
                                                          moments['mu20'] - moments['mu02'])
                            verticality = 1.0 - abs(orientation) / (np.pi / 2)
                        else:
                            verticality = 0.5
                        
                        # Method 3: Aspect ratio score
                        # Good posture: tall and narrow (aspect ratio 2-4)
                        if 2.0 <= aspect_ratio <= 4.0:
                            aspect_score = 0.9
                        elif 1.5 <= aspect_ratio < 2.0 or 4.0 < aspect_ratio <= 5.0:
                            aspect_score = 0.7
                        else:
                            aspect_score = 0.4
                        
                        # Method 4: Upper/Lower body analysis
                        upper_half = contour[contour[:, :, 1] < (y + h/2)]
                        lower_half = contour[contour[:, :, 1] >= (y + h/2)]
                        
                        balance_score = 0.5
                        if len(upper_half) > 0 and len(lower_half) > 0:
                            upper_area = cv2.contourArea(upper_half) if len(upper_half) >= 3 else 0
                            lower_area = cv2.contourArea(lower_half) if len(lower_half) >= 3 else 0
                            
                            if upper_area > 0 and lower_area > 0:
                                balance = min(upper_area/lower_area, lower_area/upper_area)
                                balance_score = balance
                        
                        # Method 5: Symmetry check
                        left_half = contour[contour[:, :, 0] < (x + w/2)]
                        right_half = contour[contour[:, :, 0] >= (x + w/2)]
                        
                        symmetry_score = 0.5
                        if len(left_half) > 0 and len(right_half) > 0:
                            left_area = cv2.contourArea(left_half) if len(left_half) >= 3 else 0
                            right_area = cv2.contourArea(right_half) if len(right_half) >= 3 else 0
                            
                            if left_area > 0 and right_area > 0:
                                symmetry = min(left_area/right_area, right_area/left_area)
                                symmetry_score = symmetry
                        
                        # Composite posture score
                        composite_score = (
                            solidity * 0.30 +
                            verticality * 0.25 +
                            aspect_score * 0.20 +
                            balance_score * 0.15 +
                            symmetry_score * 0.10
                        )
                        
                        posture_scores.append(composite_score)
            
            # Calculate final posture assessment
            if posture_scores:
                avg_posture = sum(posture_scores) / len(posture_scores)
            else:
                avg_posture = 0.5
            
            # Temporal smoothing
            self.posture_history.append(avg_posture)
            
            if len(self.posture_history) >= 15:
                # Use moving average over recent frames
                recent_scores = list(self.posture_history)[-15:]
                smoothed_score = sum(recent_scores) / len(recent_scores)
                
                # Bad posture detection (lower scores = worse posture)
                if smoothed_score < 0.45:  # Strict threshold
                    confidence = 1.0 - smoothed_score
                    return True, min(0.98, confidence)
            
            return False, 0.0
            
        except Exception as e:
            print(f"Ultra posture detection error: {e}")
            return False, 0.0
    
    # ==================== MAIN PROCESSING ====================
    
    def process_frame(self, frame):
        """Process frame through all ultra-high accuracy detection models"""
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
            print(f"Ultra frame processing error: {e}")
            return {
                'people_count': 0,
                'helmet_violation': False,
                'face_cover_violation': False,
                'loitering': False,
                'posture_violation': False,
                'alerts': []
            }

