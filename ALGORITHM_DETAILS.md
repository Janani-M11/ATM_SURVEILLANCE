# 🔬 Detection Algorithms - Detailed Technical Specifications

This document continues from APPLICATION_FLOW_AND_ARCHITECTURE.md and provides detailed step-by-step flows for each detection algorithm.

---

## Table of Contents
- [4.2 Helmet Detection Algorithm](#42-helmet-detection-algorithm)
- [4.3 Face Cover Detection Algorithm](#43-face-cover-detection-algorithm)
- [4.4 Loitering Detection Algorithm](#44-loitering-detection-algorithm)
- [4.5 Posture Detection Algorithm](#45-posture-detection-algorithm)
- [5. Database Queries & Data Flow](#5-database-queries--data-flow)

---

## 4.2 Helmet Detection Algorithm (Detailed Flow)

```
INPUT: Frame (640x480 BGR image)
  │
  ├─► Step 0: Pre-check
  │    ├─► Run people detection first
  │    └─► If no people detected: RETURN (False, 0.0)
  │
  ├─► Step 1: Run 5 Different Detection Methods
  │    │
  │    ├─► Method 1: Multi-Color Space Analysis (Weight: 25%)
  │    │    ├─► Convert frame to 3 color spaces:
  │    │    │    - HSV (Hue-Saturation-Value)
  │    │    │    - LAB (Lightness-A-B)
  │    │    │    - YCrCb (Luma-Chroma)
  │    │    │
  │    │    ├─► For HSV color space:
  │    │    │    ├─► Apply 9 different helmet color ranges:
  │    │    │    │    1. Black: [0,0,0] to [180,255,50]
  │    │    │    │    2. White: [0,0,200] to [180,30,255]
  │    │    │    │    3. Dark Blue: [100,50,20] to [130,255,100]
  │    │    │    │    4. Light Blue: [90,30,100] to [110,255,255]
  │    │    │    │    5. Red (2 ranges): [0,50,50] to [10,255,255]
  │    │    │    │                   and [170,50,50] to [180,255,255]
  │    │    │    │    6. Yellow: [20,100,100] to [35,255,255]
  │    │    │    │    7. Orange: [10,100,100] to [25,255,255]
  │    │    │    │    8. Green: [35,50,50] to [85,255,255]
  │    │    │    │    9. Gray: [0,0,50] to [180,30,200]
  │    │    │    │
  │    │    │    ├─► Create mask for each color range:
  │    │    │    │    mask = cv2.inRange(hsv, lower_bound, upper_bound)
  │    │    │    │
  │    │    │    └─► Combine all masks with bitwise OR:
  │    │    │         combined_mask = mask1 | mask2 | mask3 | ...
  │    │    │
  │    │    ├─► Clean the combined mask:
  │    │    │    ├─► Morphological closing (7x7 ellipse) - fill small holes
  │    │    │    ├─► Morphological opening (7x7 ellipse) - remove noise
  │    │    │    └─► Gaussian blur (5x5) - smooth edges
  │    │    │
  │    │    ├─► Find contours in cleaned mask
  │    │    │
  │    │    ├─► For each contour:
  │    │    │    ├─► If area > 2000 pixels:
  │    │    │    │    ├─► Get bounding box (x, y, w, h)
  │    │    │    │    ├─► Check position: y < frame_height * 0.45 (upper 45%)
  │    │    │    │    ├─► Check aspect ratio: 0.7 <= w/h <= 1.4
  │    │    │    │    ├─► Calculate perimeter
  │    │    │    │    ├─► Calculate circularity = 4*π*area / perimeter²
  │    │    │    │    ├─► If circularity > 0.5:
  │    │    │    │    │    ├─► Fit ellipse to contour
  │    │    │    │    │    ├─► Calculate ellipse area = π*(w/2)*(h/2)
  │    │    │    │    │    ├─► Calculate fit_ratio = contour_area / ellipse_area
  │    │    │    │    │    └─► If fit_ratio > 0.75:
  │    │    │    │    │         └─► Helmet detected!
  │    │    │    │    │              confidence = min(0.95, circularity * fit_ratio)
  │    │    │    │    │              RETURN (True, confidence)
  │    │    │    │
  │    │    │    └─► If no valid helmet found: RETURN (False, 0.0)
  │    │    │
  │    │    └─► Result: (helmet_detected_color, confidence_color)
  │    │
  │    ├─► Method 2: Template Matching (Weight: 20%)
  │    │    ├─► Convert frame to grayscale
  │    │    ├─► Enhance contrast using histogram equalization
  │    │    ├─► Use 42 pre-generated helmet templates:
  │    │    │    - 3 types: circle, vertical ellipse, horizontal ellipse
  │    │    │    - 14 sizes each: radius 15-60 pixels (step 5)
  │    │    │
  │    │    ├─► For each template:
  │    │    │    ├─► For each scale [0.5, 0.7, 0.9, 1.0, 1.2, 1.5]:
  │    │    │    │    ├─► Resize template by scale factor
  │    │    │    │    ├─► If template larger than frame: skip
  │    │    │    │    ├─► For each matching method [CCOEFF_NORMED, CCORR_NORMED]:
  │    │    │    │    │    ├─► result = matchTemplate(gray, scaled_template, method)
  │    │    │    │    │    ├─► Find max match value and location
  │    │    │    │    │    ├─► If match in upper 45% of frame AND value > 0.6:
  │    │    │    │    │    │    └─► Helmet detected!
  │    │    │    │    │    │         max_confidence = max(max_confidence, match_value)
  │    │    │    │    │
  │    │    │    │    └─► Continue with next template/scale
  │    │    │    │
  │    │    │    └─► Result: (helmet_detected_template, max_confidence)
  │    │    │
  │    │    └─► Result: (helmet_detected_template, confidence_template)
  │    │
  │    ├─► Method 3: Circular Hough Transform (Weight: 25%)
  │    │    ├─► Convert to grayscale
  │    │    ├─► Apply Gaussian blur (9x9, sigma=2)
  │    │    ├─► Focus on upper half of frame (where helmets appear)
  │    │    ├─► Run Hough Circle detection with multiple parameter sets:
  │    │    │    For param1 in [50, 70, 100]:  # Edge detection threshold
  │    │    │      For param2 in [25, 30, 35]:  # Circle detection threshold
  │    │    │        circles = HoughCircles(
  │    │    │          upper_half_frame,
  │    │    │          method = HOUGH_GRADIENT,
  │    │    │          dp = 1.2,  # Inverse accumulator resolution ratio
  │    │    │          minDist = 50,  # Minimum distance between circles
  │    │    │          param1 = param1,
  │    │    │          param2 = param2,
  │    │    │          minRadius = 20,
  │    │    │          maxRadius = 100
  │    │    │        )
  │    │    │    ├─► Collect all detected circles
  │    │    │    ├─► Filter circles with radius 20-80 pixels
  │    │    │    ├─► Count valid circles
  │    │    │    └─► If valid_circles > 0:
  │    │    │         confidence = min(0.95, 0.7 + valid_circles * 0.1)
  │    │    │         RETURN (True, confidence)
  │    │    │
  │    │    └─► Result: (helmet_detected_hough, confidence_hough)
  │    │
  │    ├─► Method 4: Advanced Shape Analysis (Weight: 20%)
  │    │    ├─► Convert to grayscale
  │    │    ├─► Multi-threshold edge detection:
  │    │    │    edges1 = Canny(gray, 30, 90)
  │    │    │    edges2 = Canny(gray, 50, 150)
  │    │    │    edges3 = Canny(gray, 70, 200)
  │    │    │    edges = edges1 | edges2 | edges3
  │    │    │
  │    │    ├─► Morphological closing (5x5 ellipse)
  │    │    ├─► Find contours
  │    │    │
  │    │    ├─► For each contour:
  │    │    │    ├─► If area > 2000:
  │    │    │    │    ├─► Get bounding box
  │    │    │    │    ├─► Check if in upper 45% of frame
  │    │    │    │    ├─► Calculate perimeter
  │    │    │    │    ├─► Calculate circularity = 4*π*area / perimeter²
  │    │    │    │    ├─► Calculate aspect_ratio = w / h
  │    │    │    │    ├─► Calculate convex hull
  │    │    │    │    ├─► Calculate solidity = area / hull_area
  │    │    │    │    ├─► Fit ellipse to contour
  │    │    │    │    ├─► Calculate ellipse_fit = contour_area / ellipse_area
  │    │    │    │    │
  │    │    │    │    ├─► Calculate composite shape score:
  │    │    │    │    │    score = circularity * 0.35 +
  │    │    │    │    │            solidity * 0.25 +
  │    │    │    │    │            ellipse_fit * 0.25 +
  │    │    │    │    │            (1.0 if 0.7<=aspect_ratio<=1.3 else 0.5) * 0.15
  │    │    │    │    │
  │    │    │    │    └─► If score > 0.65:
  │    │    │    │         └─► Helmet detected! confidence = score
  │    │    │    │
  │    │    │    └─► Result: (helmet_detected_shape, confidence_shape)
  │    │    │
  │    │    └─► Result: (helmet_detected_shape, best_score)
  │    │
  │    └─► Method 5: Edge Feature Analysis (Weight: 10%)
  │         ├─► Convert to grayscale
  │         ├─► Apply bilateral filter (preserve edges)
  │         ├─► Calculate Sobel gradients:
  │         │    sobelx = Sobel(filtered, CV_64F, 1, 0, ksize=3)
  │         │    sobely = Sobel(filtered, CV_64F, 0, 1, ksize=3)
  │         │    magnitude = sqrt(sobelx² + sobely²)
  │         ├─► Threshold magnitude > 50
  │         ├─► Find contours
  │         ├─► For each contour with area > 1500:
  │         │    ├─► In upper 45% of frame
  │         │    ├─► Calculate circularity
  │         │    └─► If circularity > 0.6:
  │         │         └─► Helmet detected! confidence = circularity
  │         │
  │         └─► Result: (helmet_detected_edge, confidence_edge)
  │
  ├─► Step 2: Ensemble Voting
  │    ├─► Collect all results with weights:
  │    │    detections = [
  │    │      (helmet_color, confidence_color, 0.25),
  │    │      (helmet_template, confidence_template, 0.20),
  │    │      (helmet_hough, confidence_hough, 0.25),
  │    │      (helmet_shape, confidence_shape, 0.20),
  │    │      (helmet_edge, confidence_edge, 0.10)
  │    │    ]
  │    │
  │    ├─► For each detection with confidence > 0.5:
  │    │    total_confidence += confidence * weight
  │    │    detection_votes += 1
  │    │
  │    ├─► Require at least 2 methods to agree:
  │    │    helmet_detected = (detection_votes >= 2) AND (total_confidence > 0.5)
  │    │
  │    └─► Final confidence = min(0.95, total_confidence)
  │
  ├─► Step 3: Temporal Consistency
  │    ├─► Append result to helmet_history (max 20 frames)
  │    ├─► If history has >= 10 frames:
  │    │    ├─► Get last 10 detections
  │    │    ├─► Count True detections
  │    │    ├─► If >= 6 out of 10 are True (60% agreement):
  │    │    │    └─► RETURN (True, confidence * 1.2)
  │    │    └─► If <= 3 out of 10 are True:
  │    │         └─► RETURN (False, 0.0)
  │    │
  │    └─► Otherwise return current detection result
  │
  └─► OUTPUT: (helmet_detected, confidence)
       Example: (True, 0.93) means "Helmet detected with 93% confidence"
```

---

## 4.3 Face Cover Detection Algorithm (Detailed Flow)

```
INPUT: Frame (640x480 BGR image)
  │
  ├─► Step 1: Multi-Cascade Face Detection
  │    ├─► Convert frame to grayscale
  │    ├─► Run 4 different face detection cascades:
  │    │    ├─► Cascade 1: haarcascade_frontalface_default.xml
  │    │    │    faces1 = detectMultiScale(gray, 1.1, 5, minSize=(50,50))
  │    │    ├─► Cascade 2: haarcascade_frontalface_alt.xml
  │    │    │    faces2 = detectMultiScale(gray, 1.1, 5, minSize=(50,50))
  │    │    ├─► Cascade 3: haarcascade_frontalface_alt2.xml
  │    │    │    faces3 = detectMultiScale(gray, 1.1, 5, minSize=(50,50))
  │    │    └─► Cascade 4: haarcascade_profileface.xml
  │    │         faces4 = detectMultiScale(gray, 1.1, 5, minSize=(50,50))
  │    │
  │    ├─► Combine all detected faces
  │    │    all_faces = faces1 + faces2 + faces3 + faces4
  │    │
  │    ├─► Apply Non-Maximum Suppression (NMS):
  │    │    ├─► Purpose: Remove duplicate/overlapping face detections
  │    │    ├─► Algorithm:
  │    │    │    1. Calculate areas of all bounding boxes
  │    │    │    2. Sort by area (largest first)
  │    │    │    3. Keep largest box
  │    │    │    4. For remaining boxes:
  │    │    │       - Calculate overlap (IoU) with kept box
  │    │    │       - If overlap > 50%: discard
  │    │    │       - Else: keep
  │    │    │    5. Repeat until all boxes processed
  │    │    │
  │    │    └─► Result: unique_faces (no duplicates)
  │    │
  │    └─► If no faces detected: RETURN (False, 0.0)
  │
  ├─► Step 2: Analyze Each Detected Face
  │    │
  │    For each face (x, y, w, h):
  │    │
  │    ├─► Extract face region:
  │    │    face_region = frame[y:y+h, x:x+w]
  │    │
  │    ├─► Method 1: Advanced Color Analysis (Weight: 30%)
  │    │    ├─► Convert face to HSV color space
  │    │    ├─► Apply 6 mask color ranges:
  │    │    │    1. Blue Surgical: [100,100,50] to [130,255,200]
  │    │    │    2. White Surgical: [0,0,180] to [180,30,255]
  │    │    │    3. Black Cloth: [0,0,0] to [180,255,50]
  │    │    │    4. Light Blue: [90,50,100] to [110,255,255]
  │    │    │    5. Green Medical: [40,50,50] to [80,255,200]
  │    │    │    6. Gray Cloth: [0,0,50] to [180,50,150]
  │    │    │
  │    │    ├─► Create combined mask (OR all masks)
  │    │    │
  │    │    ├─► Calculate full face coverage:
  │    │    │    total_coverage = covered_pixels / total_face_pixels
  │    │    │
  │    │    ├─► Focus on lower 60% of face (mouth/nose area):
  │    │    │    ├─► Extract lower_face = face_region[0.4*h:, :]
  │    │    │    ├─► Apply same mask color ranges
  │    │    │    └─► Calculate lower_coverage
  │    │    │
  │    │    ├─► Weight lower face more heavily:
  │    │    │    final_coverage = total_coverage * 0.3 + lower_coverage * 0.7
  │    │    │
  │    │    └─► If final_coverage > 0.35 (35% coverage):
  │    │         └─► color_score = min(0.98, final_coverage * 1.5)
  │    │
  │    ├─► Method 2: Texture Analysis (Weight: 25%)
  │    │    ├─► Convert face to grayscale
  │    │    ├─► Calculate Local Binary Pattern approximation:
  │    │    │    kernel = [[-1,-1,-1], [-1,8,-1], [-1,-1,-1]]
  │    │    │    texture = filter2D(gray, -1, kernel)
  │    │    │
  │    │    ├─► Calculate texture statistics:
  │    │    │    texture_variance = var(texture)
  │    │    │
  │    │    ├─► Masks have more uniform texture (lower variance):
  │    │    │    If variance < 150:  texture_score = 0.9
  │    │    │    If variance < 300:  texture_score = 0.7
  │    │    │    If variance < 500:  texture_score = 0.5
  │    │    │    Else:                texture_score = 0.2
  │    │    │
  │    │    └─► Result: texture_score
  │    │
  │    ├─► Method 3: Edge Density Analysis (Weight: 20%)
  │    │    ├─► Convert face to grayscale
  │    │    ├─► Multi-scale edge detection:
  │    │    │    edges1 = Canny(gray, 30, 100)
  │    │    │    edges2 = Canny(gray, 50, 150)
  │    │    │    edges = edges1 | edges2
  │    │    │
  │    │    ├─► Calculate edge density:
  │    │    │    edge_density = edge_pixels / total_face_pixels
  │    │    │
  │    │    ├─► Lower density suggests mask (smoother surface):
  │    │    │    If density < 0.08:   edge_score = 0.95
  │    │    │    If density < 0.12:   edge_score = 0.85
  │    │    │    If density < 0.15:   edge_score = 0.65
  │    │    │    Else:                 edge_score = 0.3
  │    │    │
  │    │    └─► Result: edge_score
  │    │
  │    ├─► Method 4: Eye Visibility Check (Weight: 10%)
  │    │    ├─► Extract upper 50% of face (eye region)
  │    │    ├─► Run eye cascade detector:
  │    │    │    eyes = eye_cascade.detectMultiScale(upper_face, 1.1, 3)
  │    │    │
  │    │    ├─► Interpret results:
  │    │    │    If 0 eyes detected:  eye_score = 0.9  (likely covered)
  │    │    │    If 1 eye detected:   eye_score = 0.6  (partially covered)
  │    │    │    If 2+ eyes detected: eye_score = 0.2  (not covered)
  │    │    │
  │    │    └─► Result: eye_score
  │    │
  │    └─► Method 5: Lower Face Coverage Analysis (Weight: 15%)
  │         ├─► Extract lower 50% of face
  │         ├─► Convert to HSV
  │         ├─► Check for mask colors in lower face
  │         ├─► Calculate coverage ratio
  │         ├─► Calculate color uniformity:
  │         │    uniformity = 1.0 - mean(std_deviation) / 255
  │         │
  │         ├─► Combine coverage and uniformity:
  │         │    score = coverage_ratio * 0.6 + uniformity * 0.4
  │         │
  │         └─► If score > 0.5:
  │              └─► lower_face_score = min(0.95, score * 1.3)
  │
  ├─► Step 3: Combine All Scores (Weighted Average)
  │    combined_score = (color_score * 0.30 +
  │                     texture_score * 0.25 +
  │                     edge_score * 0.20 +
  │                     eye_score * 0.10 +
  │                     lower_face_score * 0.15)
  │
  ├─► Step 4: Threshold Check
  │    If combined_score > 0.70:  # High threshold for accuracy
  │      face_cover_detected = True
  │      max_confidence = combined_score
  │
  ├─► Step 5: Temporal Consistency
  │    ├─► Append result to face_cover_history (max 20 frames)
  │    ├─► If history has >= 10 frames:
  │    │    ├─► Get last 10 detections
  │    │    ├─► Count True detections
  │    │    ├─► If >= 7 out of 10 are True (70% agreement):
  │    │    │    └─► RETURN (True, confidence * 1.1)
  │    │    └─► If <= 2 out of 10 are True:
  │    │         └─► RETURN (False, 0.0)
  │    │
  │    └─► Otherwise return current detection result
  │
  └─► OUTPUT: (face_cover_detected, confidence)
       Example: (True, 0.94) means "Face cover detected with 94% confidence"
```

---

## 4.4 Loitering Detection Algorithm (Detailed Flow)

```
INPUT: Frame (640x480 BGR image)
  │
  ├─► Step 1: Motion Detection (Dual Background Subtraction)
  │    ├─► Convert frame to grayscale
  │    │
  │    ├─► Apply MOG2 background subtractor:
  │    │    fg_mask_mog2 = bg_subtractor_mog2.apply(gray)
  │    │    └─► Returns: foreground mask (white=motion, black=static)
  │    │
  │    ├─► Apply KNN background subtractor:
  │    │    fg_mask_knn = bg_subtractor_knn.apply(gray)
  │    │    └─► Returns: foreground mask
  │    │
  │    ├─► Combine both masks (AND operation for higher accuracy):
  │    │    fg_mask = fg_mask_mog2 AND fg_mask_knn
  │    │    └─► Only pixels detected by BOTH methods are considered motion
  │    │
  │    └─► Clean the mask:
  │         ├─► Morphological closing (7x7 ellipse) - fill holes
  │         ├─► Morphological opening (7x7 ellipse) - remove noise
  │         └─► Result: clean_fg_mask
  │
  ├─► Step 2: Find Motion Regions (Contours)
  │    ├─► Find contours in clean foreground mask
  │    │    contours = findContours(clean_fg_mask, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
  │    │
  │    └─► Filter significant motion regions (area > 3000 pixels)
  │
  ├─► Step 3: Track Each Moving Object
  │    │
  │    For each significant contour:
  │    │
  │    ├─► Calculate centroid (center point):
  │    │    M = moments(contour)
  │    │    cx = M["m10"] / M["m00"]
  │    │    cy = M["m01"] / M["m00"]
  │    │    Position: (cx, cy)
  │    │
  │    ├─► Find or create tracker for this object:
  │    │    │
  │    │    ├─► Search existing trackers:
  │    │    │    For each existing tracker:
  │    │    │      ├─► Get last known position
  │    │    │      ├─► Calculate distance to current position:
  │    │    │      │    distance = sqrt((cx - last_x)² + (cy - last_y)²)
  │    │    │      ├─► Check time since last update
  │    │    │      └─► If distance < 80 pixels AND time_gap < 5 seconds:
  │    │    │           └─► Match found! Use this tracker
  │    │    │
  │    │    └─► If no match found:
  │    │         ├─► Create new tracker with unique ID:
  │    │         │    tracker_id = "tracker_{timestamp}_{cx}_{cy}"
  │    │         │    tracker = {
  │    │         │      'positions': deque(maxlen=50),  # Last 50 positions
  │    │         │      'start_time': current_time,
  │    │         │      'timestamps': deque(maxlen=50)
  │    │         │    }
  │    │         │
  │    │         └─► Add to loitering_tracker dictionary
  │    │
  │    ├─► Update tracker:
  │    │    tracker['positions'].append((cx, cy))
  │    │    tracker['timestamps'].append(current_time)
  │    │
  │    └─► Analyze for loitering:
  │         │
  │         If tracker has >= 15 position records:
  │         │
  │         ├─► Get last 15 positions as numpy array
  │         │    positions = array(last_15_positions)
  │         │    Example: [[100,200], [102,201], [101,200], ...]
  │         │
  │         ├─► Calculate movement statistics:
  │         │    ├─► Calculate variance in X direction: var(positions[:, 0])
  │         │    ├─► Calculate variance in Y direction: var(positions[:, 1])
  │         │    └─► Total variance = var_x + var_y
  │         │
  │         ├─► Calculate time elapsed:
  │         │    elapsed_time = current_time - tracker['start_time']
  │         │
  │         ├─► Check loitering conditions:
  │         │    If total_variance < 200 (very little movement)
  │         │    AND elapsed_time > 25 seconds:
  │         │      └─► LOITERING DETECTED!
  │         │           ├─► Calculate confidence:
  │         │           │    confidence = min(0.98, 0.7 + elapsed_time/100)
  │         │           │    └─► Longer loitering = higher confidence
  │         │           │
  │         │           └─► RETURN (True, confidence)
  │         │
  │         └─► Example analysis:
  │              Positions: [(100,200), (101,201), (100,200), (102,199), ...]
  │              Variance: 15 (very low - almost stationary)
  │              Time: 35 seconds
  │              → LOITERING DETECTED (confidence: 0.85)
  │
  ├─► Step 4: Cleanup Old Trackers
  │    ├─► For each tracker in dictionary:
  │    │    ├─► Check time since last update
  │    │    └─► If not updated for > 180 seconds:
  │    │         └─► Remove tracker (person left the scene)
  │    │
  │    └─► Purpose: Prevent memory buildup from stale trackers
  │
  └─► OUTPUT: (loitering_detected, confidence)
       Example: (True, 0.92) means "Loitering detected with 92% confidence"
       
       If multiple people present, returns True if ANY person is loitering
```

---

## 4.5 Posture Detection Algorithm (Detailed Flow)

```
INPUT: Frame (640x480 BGR image)
  │
  ├─► Step 0: Pre-check
  │    ├─► Run people detection first
  │    └─► If no people detected: RETURN (False, 0.0)
  │
  ├─► Step 1: Multi-scale Edge Detection
  │    ├─► Convert frame to grayscale
  │    ├─► Apply Canny edge detection with 3 different thresholds:
  │    │    edges1 = Canny(gray, 20, 80)   # Low threshold - catch weak edges
  │    │    edges2 = Canny(gray, 40, 120)  # Medium threshold
  │    │    edges3 = Canny(gray, 60, 180)  # High threshold - strong edges only
  │    │
  │    ├─► Combine all edge maps:
  │    │    edges = edges1 | edges2 | edges3
  │    │    └─► Result: comprehensive edge map
  │    │
  │    └─► Morphological closing (3x3 kernel):
  │         └─► Connect nearby edges to form complete body contours
  │
  ├─► Step 2: Find and Analyze Body Contours
  │    ├─► Find contours in edge map
  │    │    contours = findContours(edges, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
  │    │
  │    └─► Filter significant contours (area > 3500 pixels)
  │
  ├─► Step 3: Analyze Each Person-Like Contour
  │    │
  │    For each significant contour:
  │    │
  │    ├─► Get bounding rectangle:
  │    │    x, y, w, h = boundingRect(contour)
  │    │
  │    ├─► Calculate aspect ratio:
  │    │    aspect_ratio = h / w
  │    │
  │    ├─► Check if person-like shape:
  │    │    If aspect_ratio > 1.5 AND h > 120 pixels:
  │    │      └─► Likely a person, continue analysis
  │    │
  │    ├─► Component 1: Solidity Analysis (Weight: 30%)
  │    │    ├─► Calculate convex hull of contour:
  │    │    │    hull = convexHull(contour)
  │    │    │    hull_area = contourArea(hull)
  │    │    │
  │    │    ├─► Calculate solidity:
  │    │    │    solidity = contour_area / hull_area
  │    │    │    └─► Measures how "solid" vs "fragmented" the shape is
  │    │    │
  │    │    └─► Interpret solidity:
  │    │         If solidity > 0.8:  score = 0.9  (very solid - good posture)
  │    │         If solidity > 0.7:  score = 0.7  (good posture)
  │    │         If solidity > 0.5:  score = 0.5  (moderate posture)
  │    │         Else:                score = 0.2  (poor posture - fragmented shape)
  │    │
  │    ├─► Component 2: Verticality Check (Weight: 25%)
  │    │    ├─► Calculate image moments:
  │    │    │    moments = moments(contour)
  │    │    │
  │    │    ├─► Calculate orientation angle:
  │    │    │    orientation = 0.5 * arctan2(2*mu11, mu20 - mu02)
  │    │    │    └─► Result in radians (-π/2 to π/2)
  │    │    │
  │    │    ├─► Calculate verticality score:
  │    │    │    verticality = 1.0 - |orientation| / (π/2)
  │    │    │    └─► 1.0 = perfectly vertical
  │    │    │        0.0 = perfectly horizontal
  │    │    │
  │    │    └─► Example:
  │    │         Upright person: orientation ≈ 0°  → verticality = 1.0
  │    │         Leaning person: orientation ≈ 30° → verticality = 0.67
  │    │         Horizontal: orientation ≈ 90°     → verticality = 0.0
  │    │
  │    ├─► Component 3: Aspect Ratio Score (Weight: 20%)
  │    │    ├─► Good posture typically has aspect ratio 2-4 (tall, narrow)
  │    │    │
  │    │    └─► Score based on aspect ratio:
  │    │         If 2.0 <= aspect_ratio <= 4.0:  score = 0.9
  │    │         If 1.5 <= aspect_ratio < 2.0:   score = 0.7
  │    │         If 4.0 < aspect_ratio <= 5.0:   score = 0.7
  │    │         Else:                            score = 0.4
  │    │
  │    ├─► Component 4: Balance Analysis (Weight: 15%)
  │    │    ├─► Divide contour into upper and lower halves:
  │    │    │    midpoint_y = y + h/2
  │    │    │    upper_half = contour points where y < midpoint_y
  │    │    │    lower_half = contour points where y >= midpoint_y
  │    │    │
  │    │    ├─► Calculate areas (if possible):
  │    │    │    upper_area = contourArea(upper_half)
  │    │    │    lower_area = contourArea(lower_half)
  │    │    │
  │    │    ├─► Calculate balance ratio:
  │    │    │    balance = min(upper_area/lower_area, lower_area/upper_area)
  │    │    │    └─► Values close to 1.0 indicate good balance
  │    │    │
  │    │    └─► Result: balance_score = balance
  │    │
  │    └─► Component 5: Symmetry Check (Weight: 10%)
  │         ├─► Divide contour into left and right halves:
  │         │    midpoint_x = x + w/2
  │         │    left_half = contour points where x < midpoint_x
  │         │    right_half = contour points where x >= midpoint_x
  │         │
  │         ├─► Calculate areas:
  │         │    left_area = contourArea(left_half)
  │         │    right_area = contourArea(right_half)
  │         │
  │         ├─► Calculate symmetry ratio:
  │         │    symmetry = min(left_area/right_area, right_area/left_area)
  │         │    └─► Values close to 1.0 indicate good symmetry
  │         │
  │         └─► Result: symmetry_score = symmetry
  │
  ├─► Step 4: Calculate Composite Posture Score
  │    composite_score = (solidity * 0.30 +
  │                      verticality * 0.25 +
  │                      aspect_score * 0.20 +
  │                      balance * 0.15 +
  │                      symmetry * 0.10)
  │
  │    Example calculation:
  │      solidity = 0.75    × 0.30 = 0.225
  │      verticality = 0.90 × 0.25 = 0.225
  │      aspect_score = 0.9 × 0.20 = 0.180
  │      balance = 0.85     × 0.15 = 0.128
  │      symmetry = 0.80    × 0.10 = 0.080
  │      ─────────────────────────────────
  │      Composite score = 0.838 (good posture)
  │
  ├─► Step 5: Store in History
  │    posture_history.append(composite_score)
  │    └─► Keep last 30 scores
  │
  ├─► Step 6: Temporal Smoothing
  │    │
  │    If history has >= 15 frames:
  │    │
  │    ├─► Calculate 15-frame moving average:
  │    │    recent_scores = last_15_scores
  │    │    smoothed_score = sum(recent_scores) / 15
  │    │
  │    ├─► Check threshold:
  │    │    If smoothed_score < 0.45:  # Strict threshold
  │    │      └─► Bad posture detected!
  │    │           confidence = 1.0 - smoothed_score
  │    │           └─► Lower score = higher confidence of bad posture
  │    │
  │    └─► Example:
  │         Recent scores: [0.35, 0.38, 0.40, 0.37, 0.36, ...]
  │         Smoothed: 0.37 (< 0.45 threshold)
  │         → BAD POSTURE DETECTED (confidence: 0.63)
  │
  └─► OUTPUT: (bad_posture_detected, confidence)
       Example: (True, 0.91) means "Bad posture detected with 91% confidence"
```

---

*[Continued in DATABASE_QUERIES.md for database operations...]*

