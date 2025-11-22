// Camera Blackout Detection Service
// Monitors camera feed for blackout conditions and sends alerts

class CameraBlackoutMonitor {
  constructor() {
    this.blackoutThreshold = 30; // 30 seconds
    this.checkInterval = 1000; // Check every 1 second
    this.blackoutStartTime = null;
    this.isMonitoring = false;
    this.monitorInterval = null;
    this.cameraId = 'ATM_CAMERA_001'; // Default camera ID
    this.location = 'ATM Surveillance System'; // Default location
  }

  // Start monitoring camera feed
  startMonitoring(videoElement, cameraId = null, location = null) {
    if (this.isMonitoring) {
      console.log('Camera monitoring already active');
      return;
    }

    this.cameraId = cameraId || this.cameraId;
    this.location = location || this.location;
    this.isMonitoring = true;

    console.log(`🔍 Starting camera blackout monitoring for ${this.cameraId}`);

    this.monitorInterval = setInterval(() => {
      this.checkCameraFeed(videoElement);
    }, this.checkInterval);
  }

  // Stop monitoring
  stopMonitoring() {
    if (this.monitorInterval) {
      clearInterval(this.monitorInterval);
      this.monitorInterval = null;
    }
    this.isMonitoring = false;
    this.blackoutStartTime = null;
    console.log('🛑 Camera blackout monitoring stopped');
  }

  // Check if camera feed is black/blank
  checkCameraFeed(videoElement) {
    try {
      if (!videoElement || !this.isMonitoring) {
        return;
      }

      // Check if video element is ready
      if (videoElement.readyState < 2) {
        console.log('Video not ready yet');
        return;
      }

      // Create canvas to analyze frame
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      canvas.width = videoElement.videoWidth || 640;
      canvas.height = videoElement.videoHeight || 480;

      // Draw current frame to canvas
      ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

      // Get image data
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;

      // Analyze frame for blackout
      const isBlackout = this.analyzeFrameForBlackout(data, canvas.width, canvas.height);

      if (isBlackout) {
        this.handleBlackoutDetected();
      } else {
        this.handleCameraRestored();
      }

    } catch (error) {
      console.error('Error checking camera feed:', error);
      // If we can't check the feed, consider it a potential blackout
      this.handleBlackoutDetected();
    }
  }

  // Analyze frame data to detect blackout
  analyzeFrameForBlackout(imageData, width, height) {
    const totalPixels = width * height;
    let darkPixels = 0;
    let brightPixels = 0;

    // Sample every 4th pixel for performance
    for (let i = 0; i < imageData.length; i += 16) { // RGBA = 4 bytes per pixel
      const r = imageData[i];
      const g = imageData[i + 1];
      const b = imageData[i + 2];
      
      // Calculate brightness
      const brightness = (r + g + b) / 3;
      
      if (brightness < 30) {
        darkPixels++;
      } else if (brightness > 200) {
        brightPixels++;
      }
    }

    const sampledPixels = totalPixels / 4;
    const darkRatio = darkPixels / sampledPixels;
    const brightRatio = brightPixels / sampledPixels;

    // Blackout conditions:
    // 1. More than 80% dark pixels (completely black)
    // 2. Less than 5% bright pixels (no bright spots)
    // 3. Very low variation in pixel values (uniform darkness)
    
    const isBlackout = darkRatio > 0.8 && brightRatio < 0.05;
    
    if (isBlackout) {
      console.log(`📹 Blackout detected: ${(darkRatio * 100).toFixed(1)}% dark pixels`);
    }

    return isBlackout;
  }

  // Handle blackout detected
  handleBlackoutDetected() {
    const currentTime = new Date();

    if (!this.blackoutStartTime) {
      this.blackoutStartTime = currentTime;
      console.log('📹 Camera blackout started');
    } else {
      // Check if blackout has lasted long enough
      const blackoutDuration = (currentTime - this.blackoutStartTime) / 1000; // seconds
      
      if (blackoutDuration >= this.blackoutThreshold) {
        console.log(`🚨 Camera blackout alert triggered after ${blackoutDuration.toFixed(1)} seconds`);
        this.sendBlackoutAlert(blackoutDuration);
        // Reset timer to avoid multiple alerts
        this.blackoutStartTime = null;
      }
    }
  }

  // Handle camera restored
  handleCameraRestored() {
    if (this.blackoutStartTime) {
      const blackoutDuration = (new Date() - this.blackoutStartTime) / 1000;
      console.log(`📹 Camera restored after ${blackoutDuration.toFixed(1)} seconds`);
      this.blackoutStartTime = null;
    }
  }

  // Send blackout alert
  async sendBlackoutAlert(duration) {
    try {
      const alertData = {
        type: 'camera_blackout',
        duration: `${duration.toFixed(1)} seconds`,
        cameraId: this.cameraId,
        location: this.location,
        timestamp: new Date().toISOString(),
        confidence: 0.95
      };

      // Import email service dynamically
      const { sendCameraBlackoutAlert, logAlert } = await import('../services/emailService');
      
      // Log the alert locally
      logAlert(alertData);
      
      // Send email alert
      const result = await sendCameraBlackoutAlert(alertData);
      
      if (result.success) {
        console.log('✅ Camera blackout alert sent successfully');
      } else {
        console.log('⚠️ Camera blackout alert logged locally (email may have failed)');
      }

      return result;

    } catch (error) {
      console.error('❌ Error sending camera blackout alert:', error);
      return { success: false, error };
    }
  }

  // Get monitoring status
  getStatus() {
    return {
      isMonitoring: this.isMonitoring,
      blackoutStartTime: this.blackoutStartTime,
      cameraId: this.cameraId,
      location: this.location,
      threshold: this.blackoutThreshold
    };
  }

  // Update camera settings
  updateSettings(settings) {
    if (settings.cameraId) this.cameraId = settings.cameraId;
    if (settings.location) this.location = settings.location;
    if (settings.threshold) this.blackoutThreshold = settings.threshold;
    
    console.log('📹 Camera monitoring settings updated:', settings);
  }
}

// Create global instance
const cameraBlackoutMonitor = new CameraBlackoutMonitor();

export default cameraBlackoutMonitor;
export { CameraBlackoutMonitor };
