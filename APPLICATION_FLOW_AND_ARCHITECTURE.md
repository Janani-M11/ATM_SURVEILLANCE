# 🏗️ ATM Surveillance System - Complete Application Flow & Architecture

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Application Flow](#application-flow)
3. [Database Schema](#database-schema)
4. [Detection Algorithms Flow](#detection-algorithms-flow)
5. [Data Flow & Queries](#data-flow--queries)
6. [Complete Request-Response Cycle](#complete-request-response-cycle)

---

## 1. System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐             │
│  │   Login    │  │  Dashboard  │  │  Detection   │             │
│  │   Page     │  │   Analytics │  │   Module     │             │
│  └────────────┘  └─────────────┘  └──────────────┘             │
│         │                │                 │                     │
│         └────────────────┴─────────────────┘                     │
│                          │                                       │
│                   React Frontend                                 │
│                   (Port 3000)                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST API
                           │ (Axios requests)
┌──────────────────────────▼──────────────────────────────────────┐
│                    Flask Backend Server                          │
│                      (Port 5000)                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              API Endpoints (Routes)                      │   │
│  │  /api/login  /api/process-video  /api/event-logs       │   │
│  │  /api/analytics  /api/health                            │   │
│  └────────────┬─────────────────────────────┬──────────────┘   │
│               │                             │                   │
│  ┌────────────▼─────────────┐  ┌───────────▼──────────────┐   │
│  │  Ultra Detection Pipeline │  │  Database Operations     │   │
│  │  (models_ultra.py)        │  │  (SQLAlchemy ORM)        │   │
│  │  - People Detection       │  │  - Admin Management      │   │
│  │  - Helmet Detection       │  │  - Event Logging         │   │
│  │  - Face Cover Detection   │  │  - Statistics Storage    │   │
│  │  - Loitering Detection    │  │  - Query Execution       │   │
│  │  - Posture Detection      │  │                          │   │
│  └───────────────────────────┘  └───────────┬──────────────┘   │
└───────────────────────────────────────────────┬──────────────────┘
                                                │
                                   ┌────────────▼─────────────┐
                                   │   SQLite Database        │
                                   │  (atm_surveillance.db)   │
                                   │  - admin table           │
                                   │  - event_log table       │
                                   │  - detection_stats table │
                                   └──────────────────────────┘
```

### Technology Stack

**Frontend:**
- React.js 18.2.0
- React Router DOM (navigation)
- Axios (HTTP requests)
- Recharts (analytics visualization)
- React Webcam (camera access)

**Backend:**
- Flask (web framework)
- Flask-CORS (cross-origin requests)
- Flask-SQLAlchemy (ORM)
- OpenCV (computer vision)
- NumPy (numerical operations)
- pyttsx3 (text-to-speech)

**Database:**
- SQLite 3 (embedded database)

---

## 2. Application Flow

### 2.1 System Startup Flow

```
START
  │
  ├─► Frontend Startup (npm start)
  │    ├─► Load React components
  │    ├─► Initialize React Router
  │    ├─► Set proxy to http://localhost:5000
  │    └─► Start dev server on port 3000
  │
  └─► Backend Startup (python backend/app.py)
       ├─► Load Flask application
       ├─► Initialize CORS
       ├─► Load environment variables (.env)
       ├─► Configure SQLAlchemy
       ├─► Initialize Ultra Detection Pipeline
       │    ├─► Load HOG descriptors (Default + Daimler)
       │    ├─► Initialize background subtractors (MOG2 + KNN)
       │    ├─► Load Haar Cascade classifiers (4 face detectors)
       │    ├─► Create helmet templates (42 templates)
       │    ├─► Initialize color ranges (helmet + mask colors)
       │    └─► Initialize tracking data structures
       ├─► Connect to SQLite database
       ├─► Create tables if not exist (admin, event_log, detection_stats)
       ├─► Create default admin user (if not exists)
       └─► Start Flask server on port 5000
```

### 2.2 User Authentication Flow

```
User opens http://localhost:3000
  │
  ├─► React Router loads Login.js component
  │
  ├─► User enters credentials
  │    Email: admin@atm.com
  │    Password: admin123
  │
  ├─► Frontend sends POST request
  │    URL: http://localhost:5000/api/login
  │    Body: { email: "admin@atm.com", password: "admin123" }
  │
  ├─► Backend receives request at /api/login route
  │
  ├─► Extract email and password from request JSON
  │
  ├─► Query database for admin user
  │    SQL: SELECT * FROM admin WHERE email = 'admin@atm.com' LIMIT 1
  │
  ├─► If user found:
  │    ├─► Compare password hash using check_password_hash()
  │    ├─► If password matches:
  │    │    └─► Return success response
  │    │         { success: true, message: "Login successful", 
  │    │           user: { email: "admin@atm.com" } }
  │    └─► If password doesn't match:
  │         └─► Return error response (401)
  │              { success: false, message: "Invalid credentials" }
  │
  ├─► Frontend receives response
  │
  ├─► If successful:
  │    ├─► Store user session
  │    ├─► Redirect to Dashboard
  │    └─► Show success notification
  │
  └─► If failed:
       ├─► Show error message
       └─► Stay on login page
```

### 2.3 Detection Module Flow (Main Application)

```
User clicks "Detection Module" in sidebar
  │
  ├─► React Router loads DetectionModule.js component
  │
  ├─► Component requests camera access
  │    navigator.mediaDevices.getUserMedia({ video: true })
  │
  ├─► If camera access granted:
  │    ├─► Initialize React Webcam component
  │    ├─► Start capturing video frames
  │    └─► Begin frame processing loop
  │
  └─► Frame Processing Loop (every 500ms):
       │
       ├─► Capture current video frame from webcam
       │    const imageSrc = webcamRef.current.getScreenshot()
       │    Format: base64-encoded JPEG
       │
       ├─► Send frame to backend for processing
       │    POST request to http://localhost:5000/api/process-video
       │    Body: { frame: "data:image/jpeg;base64,/9j/4AAQSkZJRg..." }
       │
       ├─► Backend receives frame at /api/process-video route
       │    │
       │    ├─► Decode base64 image data
       │    │    image_data = base64.b64decode(frame_data.split(',')[1])
       │    │
       │    ├─► Convert to PIL Image
       │    │    image = Image.open(io.BytesIO(image_data))
       │    │
       │    ├─► Convert to OpenCV format (BGR)
       │    │    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
       │    │
       │    ├─► Send frame to Detection Pipeline
       │    │    results = detection_pipeline.process_frame(frame)
       │    │    │
       │    │    └─► Detection Pipeline Processing:
       │    │         │
       │    │         ├─► 1. PEOPLE DETECTION
       │    │         │    └─► [See detailed flow in section 4.1]
       │    │         │
       │    │         ├─► 2. HELMET DETECTION
       │    │         │    └─► [See detailed flow in section 4.2]
       │    │         │
       │    │         ├─► 3. FACE COVER DETECTION
       │    │         │    └─► [See detailed flow in section 4.3]
       │    │         │
       │    │         ├─► 4. LOITERING DETECTION
       │    │         │    └─► [See detailed flow in section 4.4]
       │    │         │
       │    │         └─► 5. POSTURE DETECTION
       │    │              └─► [See detailed flow in section 4.5]
       │    │
       │    ├─► Process detection results
       │    │    │
       │    │    ├─► For each alert in results['alerts']:
       │    │    │    ├─► Speak alert message (TTS)
       │    │    │    │    speak_alert(alert['message'])
       │    │    │    │
       │    │    │    └─► Save event to database
       │    │    │         INSERT INTO event_log
       │    │    │         (event_type, description, confidence, timestamp)
       │    │    │         VALUES (?, ?, ?, ?)
       │    │    │
       │    │    └─► Update daily statistics
       │    │         ├─► Get or create today's stats record
       │    │         │    SELECT * FROM detection_stats 
       │    │         │    WHERE date = CURRENT_DATE
       │    │         │
       │    │         ├─► Increment counters
       │    │         │    people_count += results['people_count']
       │    │         │    if helmet_violation: helmet_violations += 1
       │    │         │    if face_cover_violation: face_cover_violations += 1
       │    │         │    if loitering: loitering_events += 1
       │    │         │    if posture_violation: posture_violations += 1
       │    │         │
       │    │         └─► Commit to database
       │    │              UPDATE detection_stats SET ...
       │    │
       │    └─► Return results to frontend
       │         { success: true, results: {...} }
       │
       ├─► Frontend receives results
       │    │
       │    ├─► Update UI with detection results
       │    │    - Display people count
       │    │    - Show violation indicators
       │    │    - Update confidence scores
       │    │
       │    ├─► If alerts present:
       │    │    └─► Show alert notifications
       │    │
       │    └─► Wait 500ms and capture next frame
       │
       └─► Loop continues until user leaves page
```

---

## 3. Database Schema

### 3.1 Complete Database Schema

```sql
-- Database: atm_surveillance.db (SQLite 3)

-- Table 1: admin
CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: event_log
CREATE TABLE event_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    image_path VARCHAR(255)
);

-- Table 3: detection_stats
CREATE TABLE detection_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    people_count INTEGER DEFAULT 0,
    helmet_violations INTEGER DEFAULT 0,
    face_cover_violations INTEGER DEFAULT 0,
    loitering_events INTEGER DEFAULT 0,
    posture_violations INTEGER DEFAULT 0,
    UNIQUE(date)
);

-- Indexes for performance
CREATE INDEX idx_event_log_timestamp ON event_log(timestamp);
CREATE INDEX idx_event_log_type ON event_log(event_type);
CREATE INDEX idx_detection_stats_date ON detection_stats(date);
```

### 3.2 Table Descriptions

#### Table 1: `admin`
**Purpose:** Store admin user credentials for authentication

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique admin ID |
| `email` | VARCHAR(120) | NOT NULL, UNIQUE | Admin email (login username) |
| `password_hash` | VARCHAR(255) | NOT NULL | Hashed password (using Werkzeug) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

**Example Data:**
```
id | email            | password_hash                                  | created_at
1  | admin@atm.com    | pbkdf2:sha256:260000$abc...                   | 2025-10-21 10:00:00
```

#### Table 2: `event_log`
**Purpose:** Store all detection events and alerts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique event ID |
| `event_type` | VARCHAR(100) | NOT NULL | Type: people_count, helmet, face_cover, loitering, posture |
| `description` | TEXT | NOT NULL | Human-readable description of event |
| `confidence` | FLOAT | NOT NULL | Detection confidence (0.0-1.0) |
| `timestamp` | DATETIME | DEFAULT CURRENT_TIMESTAMP | When event occurred |
| `image_path` | VARCHAR(255) | NULLABLE | Optional path to captured image |

**Example Data:**
```
id | event_type  | description                         | confidence | timestamp           | image_path
1  | helmet      | Helmet detected - Please remove...  | 0.93       | 2025-10-21 10:05:23 | NULL
2  | face_cover  | Face covering detected...           | 0.94       | 2025-10-21 10:05:45 | NULL
3  | people_count| Multiple people detected: 3         | 0.87       | 2025-10-21 10:06:12 | NULL
```

#### Table 3: `detection_stats`
**Purpose:** Store daily aggregated statistics

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique stats record ID |
| `date` | DATE | NOT NULL, UNIQUE | Date for statistics |
| `people_count` | INTEGER | DEFAULT 0 | Total people detected today |
| `helmet_violations` | INTEGER | DEFAULT 0 | Number of helmet violations |
| `face_cover_violations` | INTEGER | DEFAULT 0 | Number of face cover violations |
| `loitering_events` | INTEGER | DEFAULT 0 | Number of loitering events |
| `posture_violations` | INTEGER | DEFAULT 0 | Number of posture violations |

**Example Data:**
```
id | date       | people_count | helmet_violations | face_cover_violations | loitering_events | posture_violations
1  | 2025-10-21 | 45           | 3                 | 2                     | 1                | 0
2  | 2025-10-22 | 52           | 5                 | 4                     | 2                | 1
```

### 3.3 Database Relationships

```
┌─────────────┐
│    admin    │
│             │  (No foreign key relationships)
│  - id       │  Used only for authentication
│  - email    │
│  - password │
└─────────────┘

┌──────────────┐
│  event_log   │
│              │  (No foreign key relationships)
│  - id        │  Stores all detection events independently
│  - event_type│
│  - timestamp │
└──────────────┘

┌──────────────────┐
│ detection_stats  │
│                  │  (No foreign key relationships)
│  - id            │  One record per day for aggregated statistics
│  - date (UNIQUE) │
│  - counters      │
└──────────────────┘
```

---

## 4. Detection Algorithms Flow

### 4.1 People Detection Algorithm (Detailed Flow)

```
INPUT: Frame (640x480 BGR image from webcam)
  │
  ├─► Step 1: Image Preprocessing
  │    ├─► Resize to 640x480 (if different)
  │    └─► Convert to grayscale for some algorithms
  │
  ├─► Step 2: Run 5 Different Detection Methods in Parallel
  │    │
  │    ├─► Method 1: Default HOG Detector (Weight: 45%)
  │    │    ├─► Call hog_default.detectMultiScale()
  │    │    ├─► Parameters:
  │    │    │    - winStride: (8, 8) - step size
  │    │    │    - padding: (8, 8) - border padding
  │    │    │    - scale: 1.08 - pyramid scale factor
  │    │    │    - hitThreshold: 0.5 - confidence minimum
  │    │    ├─► Returns: boxes, weights
  │    │    └─► Filter: Keep only detections with weight > 0.5
  │    │         people_hog_default = count of high-confidence detections
  │    │
  │    ├─► Method 2: Daimler HOG Detector (Weight: 30%)
  │    │    ├─► Call hog_daimler.detectMultiScale()
  │    │    ├─► Parameters: Similar to Method 1
  │    │    └─► Filter by weight > 0.5
  │    │         people_hog_daimler = count
  │    │
  │    ├─► Method 3: MOG2 Background Subtraction (Weight: 10%)
  │    │    ├─► Apply bg_subtractor_mog2.apply(gray)
  │    │    ├─► Returns foreground mask (white = motion, black = background)
  │    │    ├─► Call _count_people_from_mask():
  │    │    │    ├─► Clean mask with morphology
  │    │    │    │    - Closing (fill holes): 7x7 ellipse kernel
  │    │    │    │    - Opening (remove noise): 7x7 ellipse kernel
  │    │    │    │    - Gaussian blur: 5x5
  │    │    │    │    - Threshold: 200 (strict)
  │    │    │    ├─► Find contours in cleaned mask
  │    │    │    ├─► For each contour:
  │    │    │    │    ├─► If area > 4000 pixels:
  │    │    │    │    │    ├─► Get bounding rectangle (x, y, w, h)
  │    │    │    │    │    ├─► Calculate aspect_ratio = h / w
  │    │    │    │    │    ├─► If 1.5 <= aspect_ratio <= 3.5:
  │    │    │    │    │    │    └─► If height > 120 pixels:
  │    │    │    │    │    │         ├─► Calculate convex hull
  │    │    │    │    │    │         ├─► Calculate solidity = area / hull_area
  │    │    │    │    │    │         └─► If solidity > 0.6:
  │    │    │    │    │    │              INCREMENT people counter
  │    │    │    └─► Return: people_mog2 = count
  │    │    │
  │    │    └─► people_mog2 = count from mask
  │    │
  │    ├─► Method 4: KNN Background Subtraction (Weight: 10%)
  │    │    ├─► Apply bg_subtractor_knn.apply(gray)
  │    │    └─► Same processing as Method 3
  │    │         people_knn = count
  │    │
  │    └─► Method 5: Optical Flow Analysis (Weight: 5%)
  │         ├─► If first frame: save and return 0
  │         ├─► Calculate optical flow between previous and current frame
  │         │    flow = calcOpticalFlowFarneback(prev_gray, current_gray)
  │         ├─► Calculate magnitude and angle of flow vectors
  │         │    mag, ang = cartToPolar(flow[x], flow[y])
  │         ├─► Create motion mask where magnitude > 3.5 pixels
  │         ├─► Clean motion mask with morphology (9x9 kernel)
  │         └─► Count people from mask (same as Method 3)
  │              people_optical = count
  │
  ├─► Step 3: Ensemble Voting (Conservative Strategy)
  │    ├─► Collect all counts: [people_hog_default, people_hog_daimler, 
  │    │                         people_mog2, people_knn, people_optical]
  │    ├─► Sort counts in descending order
  │    ├─► Check agreement between top 2 methods:
  │    │    ├─► If top_count - second_count > 1:
  │    │    │    └─► Use second_count (lower, more conservative)
  │    │    └─► Else (methods agree):
  │    │         └─► Calculate weighted average:
  │    │              people_count = (people_hog_default * 0.45 +
  │    │                             people_hog_daimler * 0.30 +
  │    │                             people_mog2 * 0.10 +
  │    │                             people_knn * 0.10 +
  │    │                             people_optical * 0.05)
  │    └─► Round to nearest integer
  │
  ├─► Step 4: Temporal Consistency Filtering
  │    ├─► Append current count to history (max 8 frames)
  │    ├─► If history has >= 8 frames:
  │    │    ├─► Get last 8 counts
  │    │    ├─► Use MODE (most frequent value)
  │    │    │    Example: [1, 1, 1, 2, 1, 1, 1, 2] → MODE = 1
  │    │    └─► people_count = MODE value
  │    └─► This provides stable, flicker-free detection
  │
  ├─► Step 5: Calculate Confidence Score
  │    ├─► Calculate variance of all method counts
  │    ├─► If variance > 2.0: confidence = 0.6 (methods disagree)
  │    ├─► If variance > 1.0: confidence = 0.75 (some disagreement)
  │    └─► Else: confidence = 0.9 (methods agree)
  │
  └─► OUTPUT: (people_count, confidence)
       Example: (1, 0.9) means "1 person detected with 90% confidence"
```

**See ALGORITHM_DETAILS.md for the remaining 4 detection algorithms (Helmet, Face Cover, Loitering, Posture)**

---

*[Continued in next file due to length...]*

