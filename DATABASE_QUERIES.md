# 🗄️ Database Queries & Data Flow - Complete Reference

This document provides detailed SQL queries and data flow for all database operations in the ATM Surveillance System.

---

## Table of Contents
- [5.1 Database Connection Setup](#51-database-connection-setup)
- [5.2 Admin Authentication Queries](#52-admin-authentication-queries)
- [5.3 Event Logging Queries](#53-event-logging-queries)
- [5.4 Statistics Queries](#54-statistics-queries)
- [5.5 Analytics Queries](#55-analytics-queries)
- [5.6 Complete Data Flow Diagram](#56-complete-data-flow-diagram)

---

## 5.1 Database Connection Setup

### Initialization Flow

```python
# In backend/app.py

# Step 1: Load environment variables
load_dotenv()  # Loads .env file if exists

# Step 2: Configure database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'sqlite:///atm_surveillance.db'  # Default to SQLite
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Step 3: Initialize SQLAlchemy
db = SQLAlchemy(app)

# Step 4: Define models (creates schema)
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventLog(db.Model):
    __tablename__ = 'event_log'
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(255))

class DetectionStats(db.Model):
    __tablename__ = 'detection_stats'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    people_count = db.Column(db.Integer, default=0)
    helmet_violations = db.Column(db.Integer, default=0)
    face_cover_violations = db.Column(db.Integer, default=0)
    loitering_events = db.Column(db.Integer, default=0)
    posture_violations = db.Column(db.Integer, default=0)

# Step 5: Create tables on startup (if not exist)
with app.app_context():
    db.create_all()  # Executes CREATE TABLE IF NOT EXISTS statements
```

### Generated SQL (Executed by SQLAlchemy)

```sql
-- Table creation (executed once on first run)

CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    confidence REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    image_path VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS detection_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    people_count INTEGER DEFAULT 0,
    helmet_violations INTEGER DEFAULT 0,
    face_cover_violations INTEGER DEFAULT 0,
    loitering_events INTEGER DEFAULT 0,
    posture_violations INTEGER DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_event_log_timestamp ON event_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_event_log_type ON event_log(event_type);
CREATE INDEX IF NOT EXISTS idx_detection_stats_date ON detection_stats(date);
```

---

## 5.2 Admin Authentication Queries

### 5.2.1 Create Default Admin User

**Python Code:**
```python
def create_admin_user():
    """Create default admin user if not exists"""
    with app.app_context():
        # Query: Check if admin exists
        admin = Admin.query.filter_by(email='admin@atm.com').first()
        
        if not admin:
            # Create new admin
            admin = Admin(
                email='admin@atm.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
```

**Generated SQL:**
```sql
-- Step 1: Check if admin exists
SELECT admin.id, admin.email, admin.password_hash, admin.created_at 
FROM admin 
WHERE admin.email = 'admin@atm.com'
LIMIT 1;

-- Step 2: If not found, insert new admin
INSERT INTO admin (email, password_hash, created_at) 
VALUES (
    'admin@atm.com', 
    'pbkdf2:sha256:260000$randomsalt$hashedpassword...', 
    '2025-10-21 10:00:00'
);
```

### 5.2.2 Login Authentication

**API Endpoint:** `POST /api/login`

**Python Code:**
```python
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Query database for user
    admin = Admin.query.filter_by(email=email).first()
    
    if admin and check_password_hash(admin.password_hash, password):
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {'email': admin.email}
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid credentials'
        }), 401
```

**Generated SQL:**
```sql
-- Query to find admin by email
SELECT admin.id, admin.email, admin.password_hash, admin.created_at 
FROM admin 
WHERE admin.email = ?
LIMIT 1;
-- Parameters: ('admin@atm.com',)
```

**Data Flow:**
```
User Input → Frontend
  ↓
POST request: { email: "admin@atm.com", password: "admin123" }
  ↓
Backend receives request
  ↓
Execute SQL: SELECT * FROM admin WHERE email = 'admin@atm.com'
  ↓
Found record: {id: 1, email: "admin@atm.com", password_hash: "pbkdf2..."}
  ↓
Compare password: check_password_hash(stored_hash, input_password)
  ↓
Match? → Return success response
  ↓
Frontend → Store session → Redirect to dashboard
```

---

## 5.3 Event Logging Queries

### 5.3.1 Create Event Log Entry

**Context:** Called when detection alert is triggered

**Python Code:**
```python
# In /api/process-video endpoint

for alert in results['alerts']:
    # Speak alert
    speak_alert(alert['message'])
    
    # Create event log entry
    event = EventLog(
        event_type=alert['type'],
        description=alert['message'],
        confidence=alert['confidence']
    )
    db.session.add(event)

db.session.commit()  # Commit all events at once
```

**Generated SQL:**
```sql
-- Insert event log entry
INSERT INTO event_log (event_type, description, confidence, timestamp, image_path) 
VALUES (?, ?, ?, ?, ?);
-- Parameters: ('helmet', 'Helmet detected - Please remove helmet', 0.93, '2025-10-21 10:05:23', NULL)

-- Another example
INSERT INTO event_log (event_type, description, confidence, timestamp, image_path) 
VALUES (?, ?, ?, ?, ?);
-- Parameters: ('face_cover', 'Face covering detected - Please remove mask/scarf', 0.94, '2025-10-21 10:05:45', NULL)
```

**Complete Data Flow for Event Logging:**
```
Frame Processing → Detection Pipeline
  ↓
Results: {
  'alerts': [
    {'type': 'helmet', 'message': '...', 'confidence': 0.93},
    {'type': 'face_cover', 'message': '...', 'confidence': 0.94}
  ]
}
  ↓
For each alert:
  ├─► Speak message (TTS)
  └─► Create EventLog object
       └─► Add to session
  ↓
Commit session (execute all INSERTs)
  ↓
SQL: INSERT INTO event_log (event_type, description, confidence, timestamp)
     VALUES ('helmet', 'Helmet detected...', 0.93, '2025-10-21 10:05:23');
  ↓
Database stores event
  ↓
Event ID auto-generated and returned
```

### 5.3.2 Retrieve Event Logs (with Pagination)

**API Endpoint:** `GET /api/event-logs?page=1&per_page=10`

**Python Code:**
```python
@app.route('/api/event-logs', methods=['GET'])
def get_event_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    logs = EventLog.query.order_by(EventLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [{
            'id': log.id,
            'event_type': log.event_type,
            'description': log.description,
            'confidence': log.confidence,
            'timestamp': log.timestamp.isoformat()
        } for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': page
    })
```

**Generated SQL:**
```sql
-- Step 1: Count total records (for pagination info)
SELECT COUNT(*) AS count_1 
FROM event_log;
-- Result: 150 (total events)

-- Step 2: Retrieve paginated records
SELECT event_log.id, event_log.event_type, event_log.description, 
       event_log.confidence, event_log.timestamp, event_log.image_path
FROM event_log 
ORDER BY event_log.timestamp DESC
LIMIT 10 OFFSET 0;
-- Parameters: LIMIT = per_page, OFFSET = (page - 1) * per_page

-- For page 2:
-- LIMIT 10 OFFSET 10
```

**Data Flow:**
```
Frontend Request: GET /api/event-logs?page=1&per_page=10
  ↓
Backend extracts parameters: page=1, per_page=10
  ↓
Execute count query: SELECT COUNT(*) FROM event_log
  ↓
Result: total = 150 events
  ↓
Execute paginated query:
  SELECT * FROM event_log ORDER BY timestamp DESC LIMIT 10 OFFSET 0
  ↓
Result: 10 most recent events
  ↓
Format response JSON:
{
  "logs": [
    {
      "id": 150,
      "event_type": "helmet",
      "description": "Helmet detected...",
      "confidence": 0.93,
      "timestamp": "2025-10-21T10:05:23"
    },
    ... (9 more records)
  ],
  "total": 150,
  "pages": 15,
  "current_page": 1
}
  ↓
Return to frontend
  ↓
Frontend displays events in EventLogs component
```

---

## 5.4 Statistics Queries

### 5.4.1 Update Daily Statistics

**Context:** Called after every frame with detection results

**Python Code:**
```python
# In /api/process-video endpoint

# Get or create today's stats
today = datetime.utcnow().date()
stats = DetectionStats.query.filter_by(date=today).first()

if not stats:
    stats = DetectionStats(date=today)
    db.session.add(stats)

# Initialize fields if NULL
if stats.people_count is None:
    stats.people_count = 0
if stats.helmet_violations is None:
    stats.helmet_violations = 0
# ... (similar for other fields)

# Update counters
stats.people_count += results['people_count']
if results['helmet_violation']:
    stats.helmet_violations += 1
if results['face_cover_violation']:
    stats.face_cover_violations += 1
if results['loitering']:
    stats.loitering_events += 1
if results['posture_violation']:
    stats.posture_violations += 1

db.session.commit()
```

**Generated SQL:**
```sql
-- Step 1: Check if today's stats exist
SELECT detection_stats.id, detection_stats.date, 
       detection_stats.people_count, detection_stats.helmet_violations,
       detection_stats.face_cover_violations, detection_stats.loitering_events,
       detection_stats.posture_violations
FROM detection_stats 
WHERE detection_stats.date = ?
LIMIT 1;
-- Parameters: ('2025-10-21',)

-- Step 2a: If not found, create new record
INSERT INTO detection_stats (date, people_count, helmet_violations, 
                             face_cover_violations, loitering_events, 
                             posture_violations)
VALUES (?, 0, 0, 0, 0, 0);
-- Parameters: ('2025-10-21',)

-- Step 2b: If found, update record
UPDATE detection_stats 
SET people_count = people_count + ?,
    helmet_violations = helmet_violations + ?,
    face_cover_violations = face_cover_violations + ?,
    loitering_events = loitering_events + ?,
    posture_violations = posture_violations + ?
WHERE detection_stats.id = ?;
-- Parameters: (1, 1, 0, 0, 0, 5)
-- Example: detected 1 person, 1 helmet violation, stats id=5
```

**Complete Data Flow:**
```
Detection Results:
{
  'people_count': 1,
  'helmet_violation': True,
  'face_cover_violation': False,
  'loitering': False,
  'posture_violation': False
}
  ↓
Get today's date: '2025-10-21'
  ↓
Query: SELECT * FROM detection_stats WHERE date = '2025-10-21'
  ↓
Found existing record: {id: 5, people_count: 45, helmet_violations: 3, ...}
  ↓
Update values:
  people_count: 45 + 1 = 46
  helmet_violations: 3 + 1 = 4
  (others unchanged)
  ↓
Execute UPDATE:
  UPDATE detection_stats 
  SET people_count = 46, helmet_violations = 4
  WHERE id = 5;
  ↓
Commit transaction
  ↓
Database updated
```

---

## 5.5 Analytics Queries

### 5.5.1 Get 7-Day Analytics Data

**API Endpoint:** `GET /api/analytics`

**Python Code:**
```python
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    # Get stats for the last 7 days
    from datetime import timedelta
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)
    
    stats = DetectionStats.query.filter(
        DetectionStats.date >= start_date,
        DetectionStats.date <= end_date
    ).all()
    
    # Format data for charts
    chart_data = {
        'dates': [],
        'people_count': [],
        'helmet_violations': [],
        'face_cover_violations': [],
        'loitering_events': [],
        'posture_violations': []
    }
    
    for stat in stats:
        chart_data['dates'].append(stat.date.isoformat())
        chart_data['people_count'].append(stat.people_count)
        chart_data['helmet_violations'].append(stat.helmet_violations)
        chart_data['face_cover_violations'].append(stat.face_cover_violations)
        chart_data['loitering_events'].append(stat.loitering_events)
        chart_data['posture_violations'].append(stat.posture_violations)
    
    # Calculate totals
    totals = {
        'total_people': sum(chart_data['people_count']),
        'total_helmet_violations': sum(chart_data['helmet_violations']),
        'total_face_cover_violations': sum(chart_data['face_cover_violations']),
        'total_loitering_events': sum(chart_data['loitering_events']),
        'total_posture_violations': sum(chart_data['posture_violations'])
    }
    
    return jsonify({
        'chart_data': chart_data,
        'totals': totals
    })
```

**Generated SQL:**
```sql
-- Retrieve 7 days of statistics
SELECT detection_stats.id, detection_stats.date,
       detection_stats.people_count, detection_stats.helmet_violations,
       detection_stats.face_cover_violations, detection_stats.loitering_events,
       detection_stats.posture_violations
FROM detection_stats
WHERE detection_stats.date >= ? AND detection_stats.date <= ?
ORDER BY detection_stats.date ASC;
-- Parameters: ('2025-10-14', '2025-10-21')
```

**Complete Data Flow:**
```
Frontend Request: GET /api/analytics
  ↓
Backend calculates date range:
  end_date = 2025-10-21 (today)
  start_date = 2025-10-14 (7 days ago)
  ↓
Execute Query:
  SELECT * FROM detection_stats 
  WHERE date >= '2025-10-14' AND date <= '2025-10-21'
  ORDER BY date ASC;
  ↓
Result (7 records):
[
  {date: '2025-10-15', people_count: 45, helmet_violations: 3, ...},
  {date: '2025-10-16', people_count: 52, helmet_violations: 5, ...},
  {date: '2025-10-17', people_count: 48, helmet_violations: 2, ...},
  {date: '2025-10-18', people_count: 60, helmet_violations: 4, ...},
  {date: '2025-10-19', people_count: 55, helmet_violations: 3, ...},
  {date: '2025-10-20', people_count: 50, helmet_violations: 1, ...},
  {date: '2025-10-21', people_count: 46, helmet_violations: 4, ...}
]
  ↓
Transform to chart format:
{
  chart_data: {
    dates: ['2025-10-15', '2025-10-16', ...],
    people_count: [45, 52, 48, 60, 55, 50, 46],
    helmet_violations: [3, 5, 2, 4, 3, 1, 4],
    ...
  },
  totals: {
    total_people: 356,
    total_helmet_violations: 22,
    ...
  }
}
  ↓
Return JSON to frontend
  ↓
Frontend (Analytics.js) receives data
  ↓
Recharts library renders graphs:
  - Line chart for people count over time
  - Bar chart for violations by type
  - Summary cards with totals
```

---

## 5.6 Complete Data Flow Diagram

### End-to-End Detection to Database Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERACTION                            │
│                                                                  │
│  User at webcam → Camera captures frame → Sends to frontend    │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FRONTEND (React)                               │
│                                                                  │
│  1. Capture frame from webcam (base64 JPEG)                     │
│  2. Send POST request to /api/process-video                     │
│     Body: { frame: "data:image/jpeg;base64,..." }              │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP POST
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                BACKEND (Flask) - app.py                          │
│                                                                  │
│  3. Receive request at /api/process-video route                 │
│  4. Decode base64 → PIL Image → OpenCV format (BGR)            │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│          DETECTION PIPELINE - models_ultra.py                    │
│                                                                  │
│  5. Call detection_pipeline.process_frame(frame)                │
│                                                                  │
│  For EACH detection model:                                      │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ People Detection:                                      │    │
│  │  - Run 5 algorithms (HOG x2, BG Sub x2, Optical Flow) │    │
│  │  - Ensemble voting                                     │    │
│  │  - Temporal consistency (8-frame MODE)                 │    │
│  │  → Output: (people_count, confidence)                  │    │
│  └───────────────────────────────────────────────────────┘    │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ Helmet Detection:                                      │    │
│  │  - 5 methods (Color, Template, Hough, Shape, Edge)    │    │
│  │  - Ensemble voting (≥2 must agree)                     │    │
│  │  - Temporal consistency (10-frame, 60% agreement)      │    │
│  │  → Output: (helmet_violation, confidence)              │    │
│  └───────────────────────────────────────────────────────┘    │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ Face Cover Detection:                                  │    │
│  │  - Multi-cascade face detection (4 cascades + NMS)     │    │
│  │  - 5 analysis methods (Color, Texture, Edge, Eyes,    │    │
│  │    Lower Face)                                         │    │
│  │  - Temporal consistency (10-frame, 70% agreement)      │    │
│  │  → Output: (face_cover_violation, confidence)          │    │
│  └───────────────────────────────────────────────────────┘    │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ Loitering Detection:                                   │    │
│  │  - Dual background subtraction (MOG2 + KNN)            │    │
│  │  - Object tracking with unique IDs                     │    │
│  │  - Movement variance analysis (50-point history)       │    │
│  │  - Time tracking (>25 seconds threshold)               │    │
│  │  → Output: (loitering, confidence)                     │    │
│  └───────────────────────────────────────────────────────┘    │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ Posture Detection:                                     │    │
│  │  - Multi-scale edge detection (3 thresholds)           │    │
│  │  - 5-component analysis (Solidity, Verticality,       │    │
│  │    Aspect Ratio, Balance, Symmetry)                    │    │
│  │  - Temporal smoothing (15-frame moving average)        │    │
│  │  → Output: (posture_violation, confidence)             │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                  │
│  6. Combine all results:                                        │
│     results = {                                                 │
│       'people_count': 1,                                        │
│       'helmet_violation': True,                                 │
│       'face_cover_violation': False,                            │
│       'loitering': False,                                       │
│       'posture_violation': False,                               │
│       'alerts': [                                               │
│         {type: 'helmet', message: '...', confidence: 0.93}     │
│       ]                                                         │
│     }                                                           │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND - POST-PROCESSING                           │
│                                                                  │
│  7. Process alerts:                                             │
│     For each alert in results['alerts']:                        │
│       ├─► speak_alert(alert['message'])  # Text-to-speech      │
│       └─► Create EventLog entry                                 │
│            event = EventLog(...)                                │
│            db.session.add(event)                                │
│                                                                  │
│  8. Update statistics:                                          │
│     ├─► Query today's stats                                     │
│     │    SQL: SELECT * FROM detection_stats                     │
│     │         WHERE date = CURRENT_DATE                         │
│     │                                                           │
│     ├─► If not found: Create new record                        │
│     │    SQL: INSERT INTO detection_stats(...)                 │
│     │                                                           │
│     └─► Update counters                                        │
│          SQL: UPDATE detection_stats SET                        │
│               people_count = people_count + 1,                 │
│               helmet_violations = helmet_violations + 1        │
│               WHERE id = ?                                      │
│                                                                  │
│  9. Commit database transaction                                 │
│     db.session.commit()                                         │
│     ├─► Executes INSERT INTO event_log (...)                   │
│     └─► Executes UPDATE detection_stats SET ...                │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQLITE DATABASE                               │
│                 (atm_surveillance.db)                            │
│                                                                  │
│  Tables Updated:                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ event_log table:                                     │       │
│  │ New row inserted:                                    │       │
│  │ id=151, type='helmet', description='Helmet...',      │       │
│  │ confidence=0.93, timestamp='2025-10-21 10:05:23'    │       │
│  └─────────────────────────────────────────────────────┘       │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ detection_stats table:                               │       │
│  │ Row updated:                                         │       │
│  │ date='2025-10-21', people_count=46→47,              │       │
│  │ helmet_violations=3→4                                │       │
│  └─────────────────────────────────────────────────────┘       │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│             BACKEND - RESPONSE TO FRONTEND                       │
│                                                                  │
│  10. Return JSON response:                                      │
│      {                                                          │
│        success: true,                                           │
│        results: {                                               │
│          people_count: 1,                                       │
│          helmet_violation: true,                                │
│          face_cover_violation: false,                           │
│          loitering: false,                                      │
│          posture_violation: false,                              │
│          alerts: [{...}]                                        │
│        }                                                        │
│      }                                                          │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP 200 OK
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FRONTEND - UPDATE UI                           │
│                                                                  │
│  11. Receive response                                           │
│  12. Update UI components:                                      │
│      ├─► Display people count: "1 person detected"             │
│      ├─► Show helmet violation indicator (red)                 │
│      ├─► Display alert notification                            │
│      └─► Update confidence scores                              │
│                                                                  │
│  13. Wait 500ms                                                 │
│  14. Capture next frame                                         │
│  15. Loop continues...                                          │
└─────────────────────────────────────────────────────────────────┘

PARALLEL: Analytics Dashboard continuously polls:
          GET /api/analytics (every 5 seconds)
            ↓
          SELECT * FROM detection_stats WHERE date >= ?
            ↓
          Returns chart data
            ↓
          Recharts updates graphs
```

---

## Summary of All Database Operations

### CREATE Operations (INSERT)
1. **Admin Creation** - Once on first run
2. **Event Logging** - After every detection alert
3. **Statistics Creation** - Once per day (first detection)

### READ Operations (SELECT)
1. **Login Authentication** - User login
2. **Event Logs Retrieval** - View event history (paginated)
3. **Analytics Data** - Dashboard graphs (7-day range)
4. **Statistics Check** - Before updating daily stats
5. **Health Check** - System monitoring

### UPDATE Operations (UPDATE)
1. **Statistics Counters** - After every frame with detections

### No DELETE Operations
- System does not delete data
- Event logs and statistics accumulate over time
- Manual cleanup required if needed

---

## Performance Considerations

### Database Indexes
```sql
CREATE INDEX idx_event_log_timestamp ON event_log(timestamp);
CREATE INDEX idx_event_log_type ON event_log(event_type);
CREATE INDEX idx_detection_stats_date ON detection_stats(date);
```

### Query Optimization
- Pagination prevents loading all event logs at once
- Date range queries for analytics (only 7 days)
- Single transaction for multiple inserts (better performance)
- Indexes on commonly queried columns

### Connection Pooling
- SQLAlchemy manages connection pool automatically
- Default pool size: 5 connections
- Pool overflow: 10 additional connections
- Sufficient for single-user ATM surveillance

---

**Complete documentation of all system flows and queries! 🎉**

