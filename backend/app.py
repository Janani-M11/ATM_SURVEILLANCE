from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import sys
from dotenv import load_dotenv
import cv2
import numpy as np
import base64
import io
from PIL import Image
import pyttsx3
import threading
import time
from models_enhanced_people import EnhancedPeopleDetectionPipeline

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration - Import from config.py for better management
# Add current directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)

# Database Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(255))

class DetectionStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    people_count = db.Column(db.Integer, default=0)
    helmet_violations = db.Column(db.Integer, default=0)
    face_cover_violations = db.Column(db.Integer, default=0)
    loitering_events = db.Column(db.Integer, default=0)
    posture_violations = db.Column(db.Integer, default=0)

# Initialize TTS engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)
tts_engine.setProperty('volume', 0.8)

# Global variables for detection pipeline
detection_pipeline = None
alert_counters = {}
helmet_alert_timer = {}  # Track helmet alert timing

def play_alarm_sound():
    """Play alarm sound for loitering detection"""
    def alarm():
        try:
            # Create alarm beep sound using TTS
            engine = pyttsx3.init()
            engine.setProperty('rate', 200)
            engine.setProperty('volume', 1.0)
            # Repeat alarm message multiple times
            for _ in range(3):
                engine.say("Alert! Alert! Alert!")
            engine.runAndWait()
        except Exception as e:
            print(f"Alarm Error: {e}")
    
    thread = threading.Thread(target=alarm)
    thread.daemon = True
    thread.start()

def speak_alert(message, alert_type=None, delay=0):
    """Text to speech for alerts with optional delay"""
    def speak():
        try:
            # Wait for delay if specified
            if delay > 0:
                time.sleep(delay)
            
            # Create a new TTS engine instance for each thread
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            
            # For loitering, play alarm sound instead
            if alert_type == 'loitering':
                play_alarm_sound()
                return
            
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
    
    thread = threading.Thread(target=speak)
    thread.daemon = True
    thread.start()

# Initialize Ultra-High Accuracy Detection Pipeline
# This pipeline uses ensemble methods with multiple algorithms for each detection type
detection_pipeline = EnhancedPeopleDetectionPipeline()

# Routes
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
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

@app.route('/api/process-video', methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        frame_data = data.get('frame')
        
        if not frame_data:
            return jsonify({'error': 'No frame data provided'}), 400
        
        # Validate frame data format
        if not isinstance(frame_data, str):
            return jsonify({'error': 'Frame data must be a string'}), 400
            
        if not frame_data.startswith('data:image'):
            return jsonify({'error': 'Invalid frame data format'}), 400
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(frame_data.split(',')[1])
            image = Image.open(io.BytesIO(image_data))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            return jsonify({'error': f'Error decoding image: {str(e)}'}), 400
        
        # Validate frame dimensions
        if frame is None or frame.size == 0:
            return jsonify({'error': 'Invalid frame dimensions'}), 400
        
        # Process through detection pipeline
        results = detection_pipeline.process_frame(frame)
        
        # Handle alerts with custom voice messages
        current_time = time.time()
        
        for alert in results['alerts']:
            alert_type = alert['type']
            
            # Customize voice message based on detection type
            if alert_type == 'people_count':
                voice_message = "Please go out of the ATM. More than 2 people cannot stand inside the ATM."
                speak_alert(voice_message, alert_type=alert_type)
                
            elif alert_type == 'helmet':
                voice_message = "Please remove your helmet."
                # Check if 10 seconds have passed since last helmet alert
                if alert_type not in helmet_alert_timer or (current_time - helmet_alert_timer[alert_type]) >= 10:
                    speak_alert(voice_message, alert_type=alert_type, delay=10)
                    helmet_alert_timer[alert_type] = current_time
                    
            elif alert_type == 'face_cover':
                voice_message = "Please uncover yourself."
                speak_alert(voice_message, alert_type=alert_type)
                
            elif alert_type == 'loitering':
                voice_message = "Loitering detected - Alarm activated"
                # This will play alarm sound instead of speaking
                speak_alert(voice_message, alert_type=alert_type)
                
            elif alert_type == 'posture':
                voice_message = "Don't bend inside the ATM."
                speak_alert(voice_message, alert_type=alert_type)
            
            # Log the event
            event = EventLog(
                event_type=alert['type'],
                description=alert['message'],  # Keep original description for logging
                confidence=alert['confidence']
            )
            db.session.add(event)
        
        # Update daily stats
        today = datetime.utcnow().date()
        stats = DetectionStats.query.filter_by(date=today).first()
        if not stats:
            stats = DetectionStats(date=today)
            db.session.add(stats)
        
        # Ensure all fields are initialized
        if stats.people_count is None:
            stats.people_count = 0
        if stats.helmet_violations is None:
            stats.helmet_violations = 0
        if stats.face_cover_violations is None:
            stats.face_cover_violations = 0
        if stats.loitering_events is None:
            stats.loitering_events = 0
        if stats.posture_violations is None:
            stats.posture_violations = 0
        
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
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        print(f"Error processing video frame: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error processing video frame: {str(e)}'}), 500

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

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

def create_admin_user():
    """Create default admin user if not exists"""
    with app.app_context():
        admin = Admin.query.filter_by(email='admin@atm.com').first()
        if not admin:
            admin = Admin(
                email='admin@atm.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
