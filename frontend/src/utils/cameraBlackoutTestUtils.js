// Camera Blackout Detection Test Utility
// Run this in your browser console to test camera blackout detection

export const testCameraBlackoutDetection = {
  
  // Test 1: Check camera blackout monitoring status
  checkMonitoringStatus() {
    console.log('🔍 Checking camera blackout monitoring status...');
    
    try {
      const monitor = window.cameraBlackoutMonitor || 
        (window.cameraBlackoutMonitor = require('./services/cameraBlackoutMonitor').default);
      
      const status = monitor.getStatus();
      console.log('📹 Camera monitoring status:', status);
      
      if (status.isMonitoring) {
        console.log('✅ Camera blackout monitoring is ACTIVE');
        console.log(`📹 Camera ID: ${status.cameraId}`);
        console.log(`📍 Location: ${status.location}`);
        console.log(`⏱️ Threshold: ${status.threshold} seconds`);
      } else {
        console.log('❌ Camera blackout monitoring is NOT ACTIVE');
        console.log('💡 Go to Detection Module and start detection with webcam');
      }
      
      return status;
      
    } catch (error) {
      console.error('❌ Error checking monitoring status:', error);
      return { isMonitoring: false, error };
    }
  },

  // Test 2: Simulate camera blackout alert
  async simulateBlackoutAlert() {
    console.log('🧪 Simulating camera blackout alert...');
    
    try {
      const { sendCameraBlackoutAlert } = await import('./services/emailService');
      
      const testData = {
        type: 'camera_blackout',
        duration: '30.5 seconds',
        cameraId: 'ATM_CAMERA_001',
        location: 'ATM Surveillance System',
        timestamp: new Date().toISOString(),
        confidence: 0.95
      };
      
      const result = await sendCameraBlackoutAlert(testData);
      
      if (result.success) {
        console.log('✅ Test blackout alert sent successfully!');
        console.log('📧 Email notification sent');
        console.log('🔔 Browser notification shown');
      } else {
        console.log('⚠️ Alert logged locally (email may have failed)');
        console.log('📝 Check Event Logs tab for the alert');
      }
      
      return result;
      
    } catch (error) {
      console.error('❌ Error testing blackout alert:', error);
      return { success: false, error };
    }
  },

  // Test 3: Check stored blackout alerts
  async checkStoredBlackoutAlerts() {
    console.log('📊 Checking stored blackout alerts...');
    
    try {
      const { getStoredAlerts } = await import('./services/emailService');
      const alerts = getStoredAlerts();
      
      console.log(`📈 Total alerts stored: ${alerts.length}`);
      
      const blackoutAlerts = alerts.filter(alert => 
        alert.data && alert.data.type === 'camera_blackout'
      );
      
      console.log(`📹 Camera blackout alerts: ${blackoutAlerts.length}`);
      
      if (blackoutAlerts.length > 0) {
        console.log('📋 Recent blackout alerts:');
        blackoutAlerts.slice(-3).forEach((alert, index) => {
          console.log(`${index + 1}. ${alert.timestamp} - Camera: ${alert.data.cameraId} - Duration: ${alert.data.duration}`);
        });
      }
      
      return { total: alerts.length, blackout: blackoutAlerts.length };
      
    } catch (error) {
      console.error('❌ Error checking blackout alerts:', error);
      return { total: 0, blackout: 0 };
    }
  },

  // Test 4: Test camera blackout detection manually
  testManualBlackoutDetection() {
    console.log('🧪 Testing manual camera blackout detection...');
    
    // This simulates what happens when camera goes black
    const videoElement = document.querySelector('video');
    
    if (!videoElement) {
      console.log('❌ No video element found');
      console.log('💡 Make sure webcam is active in Detection Module');
      return false;
    }
    
    console.log('📹 Video element found:', videoElement);
    console.log('📏 Video dimensions:', videoElement.videoWidth, 'x', videoElement.videoHeight);
    console.log('🎬 Video ready state:', videoElement.readyState);
    
    // Create a test canvas to simulate blackout detection
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = videoElement.videoWidth || 640;
    canvas.height = videoElement.videoHeight || 480;
    
    // Draw current frame
    ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
    
    // Analyze frame
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    
    let darkPixels = 0;
    let brightPixels = 0;
    
    // Sample every 4th pixel
    for (let i = 0; i < data.length; i += 16) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const brightness = (r + g + b) / 3;
      
      if (brightness < 30) darkPixels++;
      if (brightness > 200) brightPixels++;
    }
    
    const totalPixels = (canvas.width * canvas.height) / 4;
    const darkRatio = darkPixels / totalPixels;
    const brightRatio = brightPixels / totalPixels;
    
    console.log('📊 Frame analysis:');
    console.log(`  Dark pixels: ${(darkRatio * 100).toFixed(1)}%`);
    console.log(`  Bright pixels: ${(brightRatio * 100).toFixed(1)}%`);
    console.log(`  Blackout detected: ${darkRatio > 0.8 && brightRatio < 0.05 ? 'YES' : 'NO'}`);
    
    return {
      darkRatio,
      brightRatio,
      isBlackout: darkRatio > 0.8 && brightRatio < 0.05
    };
  },

  // Test 5: Update camera settings
  updateCameraSettings(settings) {
    console.log('⚙️ Updating camera settings...');
    
    try {
      const monitor = window.cameraBlackoutMonitor || 
        (window.cameraBlackoutMonitor = require('./services/cameraBlackoutMonitor').default);
      
      monitor.updateSettings(settings);
      console.log('✅ Camera settings updated:', settings);
      
      return true;
      
    } catch (error) {
      console.error('❌ Error updating camera settings:', error);
      return false;
    }
  },

  // Run all tests
  async runAllTests() {
    console.log('🚀 Running complete camera blackout detection test suite...');
    console.log('='.repeat(60));
    
    const results = {
      monitoringStatus: this.checkMonitoringStatus(),
      manualDetection: this.testManualBlackoutDetection(),
      storedAlerts: await this.checkStoredBlackoutAlerts(),
      simulatedAlert: await this.simulateBlackoutAlert()
    };
    
    console.log('='.repeat(60));
    console.log('📊 Camera Blackout Test Results Summary:');
    console.log(`Monitoring Status: ${results.monitoringStatus.isMonitoring ? '✅ ACTIVE' : '❌ INACTIVE'}`);
    console.log(`Manual Detection: ${results.manualDetection ? '✅ WORKING' : '❌ ISSUES'}`);
    console.log(`Stored Alerts: ${results.storedAlerts.total} total, ${results.storedAlerts.blackout} blackout`);
    console.log(`Simulated Alert: ${results.simulatedAlert.success ? '✅ SUCCESS' : '❌ FAILED'}`);
    
    if (results.monitoringStatus.isMonitoring && results.manualDetection) {
      console.log('🎉 Camera blackout detection is working! Try covering your camera for 30+ seconds to test.');
    } else {
      console.log('⚠️ Some issues detected. Check the details above.');
    }
    
    return results;
  }
};

// Quick test function
export const quickCameraBlackoutTest = () => {
  console.log('🧪 Quick Camera Blackout Detection Test');
  console.log('Run: testCameraBlackoutDetection.runAllTests()');
  
  return testCameraBlackoutDetection.runAllTests();
};
