import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import { useDropzone } from 'react-dropzone';
import { 
  Camera, 
  Upload, 
  Play, 
  Pause, 
  Square, 
  AlertTriangle, 
  Users, 
  Shield, 
  Eye, 
  Clock, 
  Activity,
  Volume2,
  VolumeX,
  Mail
} from 'lucide-react';
import toast from 'react-hot-toast';
import { sendLoiteringAlert, sendTestEmail } from '../services/emailService';
import cameraBlackoutMonitor from '../services/cameraBlackoutMonitor';
import './DetectionModule.css';

const DetectionModule = () => {
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectionResults, setDetectionResults] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [videoSource, setVideoSource] = useState('webcam'); // 'webcam' or 'upload'
  const [videoElement, setVideoElement] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [isMuted, setIsMuted] = useState(false);
  const [alertHistory, setAlertHistory] = useState([]);
  const [emailAlertsEnabled, setEmailAlertsEnabled] = useState(true);
  const [lastLoiteringAlert, setLastLoiteringAlert] = useState(null);
  const [cameraBlackoutEnabled, setCameraBlackoutEnabled] = useState(true);
  const [cameraId, setCameraId] = useState('ATM_CAMERA_001');
  const [location, setLocation] = useState('ATM Surveillance System');
  
  const webcamRef = useRef(null);
  const detectionIntervalRef = useRef(null);

  // Cleanup video URL on unmount
  useEffect(() => {
    return () => {
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
      }
      // Stop camera blackout monitoring on unmount
      cameraBlackoutMonitor.stopMonitoring();
    };
  }, [videoUrl]);

  const resetVideo = () => {
    if (videoUrl) {
      URL.revokeObjectURL(videoUrl);
      setVideoUrl(null);
    }
    setSelectedFile(null);
    setVideoElement(null);
  };

  const handleVideoLoaded = () => {
    if (videoElement && !isDetecting) {
      toast.success('Video loaded - Starting detection automatically');
      startDetection();
    }
  };

  const switchVideoSource = (source) => {
    if (isDetecting) {
      stopDetection();
    }
    resetVideo();
    setVideoSource(source);
  };

  const detectionModules = [
    { name: 'People Detection', icon: Users, color: '#667eea', threshold: '> 2 people' },
    { name: 'Helmet Detection', icon: Shield, color: '#f56565', threshold: 'Any helmet' },
    { name: 'Face Cover Detection', icon: Eye, color: '#ed8936', threshold: 'Mask/scarf' },
    { name: 'Loitering Detection', icon: Clock, color: '#9f7aea', threshold: '> 30 seconds' },
    { name: 'Posture Detection', icon: Activity, color: '#38b2ac', threshold: 'Bending detected' }
  ];

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file && file.type.startsWith('video/')) {
      setSelectedFile(file);
      setVideoSource('upload');
      
      // Create video URL for playback and frame extraction
      const url = URL.createObjectURL(file);
      setVideoUrl(url);
      
      toast.success('Video file uploaded successfully - Detection will start automatically');
      
    } else {
      toast.error('Please upload a valid video file');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.wmv', '.flv']
    },
    multiple: false
  });

  const startDetection = async () => {
    if (videoSource === 'webcam' && !webcamRef.current) {
      toast.error('Webcam not available');
      return;
    }

    if (videoSource === 'upload' && !selectedFile) {
      toast.error('Please upload a video file first');
      return;
    }

    setIsDetecting(true);
    toast.success('Detection started');

    // Start camera blackout monitoring if enabled
    if (cameraBlackoutEnabled && videoSource === 'webcam') {
      const videoElement = webcamRef.current?.video;
      if (videoElement) {
        cameraBlackoutMonitor.startMonitoring(videoElement, cameraId, location);
        console.log('📹 Camera blackout monitoring started');
      }
    }

    // Start detection loop
    detectionIntervalRef.current = setInterval(async () => {
      try {
        const frame = await captureFrame();
        if (frame) {
          await processFrame(frame);
        }
      } catch (error) {
        console.error('Detection error:', error);
      }
    }, 1000); // Process every second
  };

  const stopDetection = () => {
    setIsDetecting(false);
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
    }
    
    // Stop camera blackout monitoring
    cameraBlackoutMonitor.stopMonitoring();
    
    toast.success('Detection stopped');
  };

  const captureFrame = async () => {
    if (videoSource === 'webcam' && webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      return imageSrc;
    }
    
    if (videoSource === 'upload' && videoElement) {
      try {
        // Advance video time for frame-by-frame processing
        if (videoElement.currentTime < videoElement.duration) {
          videoElement.currentTime += 0.1; // Advance by 100ms
        } else {
          // Loop back to beginning if video ended
          videoElement.currentTime = 0;
        }
        
        // Create a canvas to capture the current video frame
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Set canvas dimensions to match video
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        
        // Draw the current video frame to canvas
        ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        
        // Convert canvas to base64 image
        const imageSrc = canvas.toDataURL('image/jpeg', 0.8);
        return imageSrc;
      } catch (error) {
        console.error('Error capturing video frame:', error);
        return null;
      }
    }
    
    return null;
  };

  const processFrame = async (frameData) => {
    try {
      const response = await fetch('/api/process-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ frame: frameData }),
      });

      const data = await response.json();
      
      if (data.success) {
        setDetectionResults(data.results);
        
        // Handle alerts
        if (data.results.alerts && data.results.alerts.length > 0) {
          data.results.alerts.forEach(alert => {
            const alertItem = {
              id: Date.now() + Math.random(),
              type: alert.type,
              message: alert.message,
              confidence: alert.confidence,
              timestamp: new Date().toLocaleTimeString()
            };
            
            setAlertHistory(prev => [alertItem, ...prev.slice(0, 9)]); // Keep last 10 alerts
            
            // Show toast notification
            toast.error(alert.message, {
              duration: 4000,
              icon: '🚨'
            });

            // Send email alert for loitering detection
            if (alert.type === 'loitering' && emailAlertsEnabled) {
              const now = Date.now();
              // Only send email if 30 seconds have passed since last loitering alert
              if (!lastLoiteringAlert || (now - lastLoiteringAlert) > 30000) {
                setLastLoiteringAlert(now);
                
                const emailData = {
                  confidence: alert.confidence,
                  duration: 'Ongoing',
                  timestamp: new Date().toISOString()
                };
                
                sendLoiteringAlert(emailData).then(result => {
                  if (result.success) {
                    toast.success('📧 Email alert sent to security team', {
                      duration: 5000,
                      icon: '📧'
                    });
                  } else {
                    toast.error('Failed to send email alert', {
                      duration: 3000
                    });
                  }
                });
              }
            }
          });
        }
      }
    } catch (error) {
      console.error('Error processing frame:', error);
      toast.error('Error processing video frame');
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
    toast.success(isMuted ? 'Alerts unmuted' : 'Alerts muted');
  };

  const toggleEmailAlerts = () => {
    setEmailAlertsEnabled(!emailAlertsEnabled);
    toast.success(emailAlertsEnabled ? 'Email alerts disabled' : 'Email alerts enabled');
  };

  const testEmailAlert = async () => {
    toast.loading('Sending test email...', { id: 'test-email' });
    
    const result = await sendTestEmail();
    
    if (result.success) {
      toast.success('📧 Test email sent successfully!', { 
        id: 'test-email',
        duration: 5000,
        icon: '📧'
      });
    } else {
      toast.error('Failed to send test email', { 
        id: 'test-email',
        duration: 3000
      });
    }
  };

  const getDetectionStatus = (moduleName) => {
    if (!detectionResults) return 'inactive';
    
    switch (moduleName) {
      case 'People Detection':
        return detectionResults.people_count > 2 ? 'alert' : 'normal';
      case 'Helmet Detection':
        return detectionResults.helmet_violation ? 'alert' : 'normal';
      case 'Face Cover Detection':
        return detectionResults.face_cover_violation ? 'alert' : 'normal';
      case 'Loitering Detection':
        return detectionResults.loitering ? 'alert' : 'normal';
      case 'Posture Detection':
        return detectionResults.posture_violation ? 'alert' : 'normal';
      default:
        return 'inactive';
    }
  };

  return (
    <div className="detection-module">
      <div className="detection-header">
        <h1>Real-time Detection Module</h1>
        <p>Advanced AI-powered surveillance with 5 detection models</p>
      </div>

      <div className="detection-controls">
        <div className="video-source-selector">
          <button
            className={`source-btn ${videoSource === 'webcam' ? 'active' : ''}`}
            onClick={() => switchVideoSource('webcam')}
          >
            <Camera size={20} />
            Webcam
          </button>
          <button
            className={`source-btn ${videoSource === 'upload' ? 'active' : ''}`}
            onClick={() => switchVideoSource('upload')}
          >
            <Upload size={20} />
            Upload Video
          </button>
        </div>

        <div className="detection-actions">
          <button
            className={`action-btn ${isDetecting ? 'stop' : 'start'}`}
            onClick={isDetecting ? stopDetection : startDetection}
          >
            {isDetecting ? (
              <>
                <Square size={20} />
                Stop Detection
              </>
            ) : (
              <>
                <Play size={20} />
                Start Detection
              </>
            )}
          </button>
          
          <button
            className={`mute-btn ${isMuted ? 'muted' : ''}`}
            onClick={toggleMute}
          >
            {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
            {isMuted ? 'Unmute' : 'Mute'}
          </button>

          <button
            className={`email-btn ${emailAlertsEnabled ? 'enabled' : 'disabled'}`}
            onClick={toggleEmailAlerts}
          >
            <Mail size={20} />
            {emailAlertsEnabled ? 'Email ON' : 'Email OFF'}
          </button>

          <button
            className="test-email-btn"
            onClick={testEmailAlert}
          >
            <Mail size={20} />
            Test Email
          </button>
        </div>

        <div className="camera-settings">
          <div className="setting-group">
            <label className="setting-label">
              <input
                type="checkbox"
                checked={cameraBlackoutEnabled}
                onChange={(e) => setCameraBlackoutEnabled(e.target.checked)}
              />
              <span>Camera Blackout Detection</span>
            </label>
          </div>
          
          <div className="setting-group">
            <label className="setting-label">
              Camera ID:
              <input
                type="text"
                value={cameraId}
                onChange={(e) => setCameraId(e.target.value)}
                className="setting-input"
                placeholder="ATM_CAMERA_001"
              />
            </label>
          </div>
          
          <div className="setting-group">
            <label className="setting-label">
              Location:
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="setting-input"
                placeholder="ATM Surveillance System"
              />
            </label>
          </div>
        </div>
      </div>

      <div className="detection-content">
        <div className="video-section">
          <div className="video-container">
            {videoSource === 'webcam' ? (
              <Webcam
                ref={webcamRef}
                audio={false}
                width={640}
                height={480}
                screenshotFormat="image/jpeg"
                className="webcam-video"
              />
            ) : (
              <div className="upload-area" {...getRootProps()}>
                <input {...getInputProps()} />
                {selectedFile ? (
                  <div className="selected-file">
                    <video
                      ref={setVideoElement}
                      src={videoUrl}
                      controls
                      className="uploaded-video"
                      onLoadedMetadata={handleVideoLoaded}
                      onCanPlay={handleVideoLoaded}
                    />
                    <p className="file-name">{selectedFile.name}</p>
                  </div>
                ) : (
                  <div className="upload-placeholder">
                    <Upload size={48} />
                    <p>{isDragActive ? 'Drop video here' : 'Drag & drop video file'}</p>
                    <p className="upload-hint">or click to select</p>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="detection-overlay">
            {detectionResults && (
              <div className="overlay-stats">
                <div className="stat-item">
                  <Users size={16} />
                  <span>People: {detectionResults.people_count}</span>
                </div>
                <div className="stat-item">
                  <AlertTriangle size={16} />
                  <span>Alerts: {detectionResults.alerts?.length || 0}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="detection-sidebar">
          <div className="modules-status">
            <h3>Detection Modules</h3>
            <div className="modules-list">
              {detectionModules.map((module, index) => {
                const Icon = module.icon;
                const status = getDetectionStatus(module.name);
                return (
                  <div key={index} className={`module-item ${status}`}>
                    <div className="module-icon" style={{ backgroundColor: module.color }}>
                      <Icon size={16} />
                    </div>
                    <div className="module-info">
                      <span className="module-name">{module.name}</span>
                      <span className="module-threshold">{module.threshold}</span>
                    </div>
                    <div className={`status-indicator ${status}`}></div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="alerts-panel">
            <h3>Live Alerts</h3>
            <div className="alerts-list">
              {alertHistory.length > 0 ? (
                alertHistory.map((alert) => (
                  <div key={alert.id} className="alert-item">
                    <div className="alert-icon">
                      <AlertTriangle size={14} />
                    </div>
                    <div className="alert-content">
                      <p className="alert-message">{alert.message}</p>
                      <div className="alert-meta">
                        <span className="alert-time">{alert.timestamp}</span>
                        <span className="alert-confidence">
                          {Math.round(alert.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-alerts">
                  <p>No active alerts</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="detection-info">
        <div className="info-card">
          <h4>Detection Pipeline</h4>
          <p>Our advanced AI pipeline processes video frames through 5 specialized models:</p>
          <ol>
            <li><strong>Input Layer:</strong> Video frame preprocessing and normalization</li>
            <li><strong>Detection Layer:</strong> Multi-model parallel processing</li>
            <li><strong>Event Decision Layer:</strong> Rule-based alert generation</li>
            <li><strong>Alert Layer:</strong> Real-time notifications and voice alerts</li>
          </ol>
        </div>
        
        <div className="info-card">
          <h4>Voice Alerts</h4>
          <p>System provides 3 consecutive voice alerts for face covering violations (helmet, mask, scarf) to ensure compliance.</p>
        </div>
      </div>
    </div>
  );
};

export default DetectionModule;
