// Loitering Detection Test Utility
// Run this in your browser console to test loitering detection

export const testLoiteringDetection = {
  
  // Test 1: Check if detection is running
  checkDetectionStatus() {
    console.log('🔍 Checking detection status...');
    
    if (window.detectionActive) {
      console.log('✅ Detection is ACTIVE');
      return true;
    } else {
      console.log('❌ Detection is NOT ACTIVE');
      console.log('💡 Go to Detection Module and click "Start Detection"');
      return false;
    }
  },

  // Test 2: Simulate loitering alert
  async simulateLoiteringAlert() {
    console.log('🧪 Simulating loitering alert...');
    
    try {
      const { sendLoiteringAlert } = await import('./services/emailService');
      
      const testData = {
        confidence: 0.95,
        duration: '30 seconds',
        timestamp: new Date().toISOString(),
        type: 'loitering'
      };
      
      const result = await sendLoiteringAlert(testData);
      
      if (result.success) {
        console.log('✅ Test alert sent successfully!');
        console.log('📧 Email notification sent');
        console.log('🔔 Browser notification shown');
      } else {
        console.log('⚠️ Alert logged locally (email may have failed)');
        console.log('📝 Check Event Logs tab for the alert');
      }
      
      return result;
      
    } catch (error) {
      console.error('❌ Error testing alert:', error);
      return { success: false, error };
    }
  },

  // Test 3: Check stored alerts
  async checkStoredAlerts() {
    console.log('📊 Checking stored alerts...');
    
    try {
      const { getStoredAlerts } = await import('./services/emailService');
      const alerts = getStoredAlerts();
      
      console.log(`📈 Total alerts stored: ${alerts.length}`);
      
      const loiteringAlerts = alerts.filter(alert => 
        alert.data && alert.data.type === 'loitering'
      );
      
      console.log(`🚶 Loitering alerts: ${loiteringAlerts.length}`);
      
      if (loiteringAlerts.length > 0) {
        console.log('📋 Recent loitering alerts:');
        loiteringAlerts.slice(-3).forEach((alert, index) => {
          console.log(`${index + 1}. ${alert.timestamp} - Confidence: ${alert.data.confidence}`);
        });
      }
      
      return { total: alerts.length, loitering: loiteringAlerts.length };
      
    } catch (error) {
      console.error('❌ Error checking alerts:', error);
      return { total: 0, loitering: 0 };
    }
  },

  // Test 4: Check browser notifications
  testBrowserNotifications() {
    console.log('🔔 Testing browser notifications...');
    
    if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification('ATM Surveillance Test', {
          body: 'Browser notifications are working!',
          icon: '/icon.png'
        });
        console.log('✅ Browser notification sent');
        return true;
      } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            new Notification('ATM Surveillance Test', {
              body: 'Browser notifications enabled!',
              icon: '/icon.png'
            });
            console.log('✅ Browser notifications enabled');
          } else {
            console.log('❌ Browser notifications denied');
          }
        });
        return false;
      } else {
        console.log('❌ Browser notifications blocked');
        return false;
      }
    } else {
      console.log('❌ Browser does not support notifications');
      return false;
    }
  },

  // Test 5: Check EmailJS configuration
  async checkEmailJSConfig() {
    console.log('📧 Checking EmailJS configuration...');
    
    try {
      const { validateEmailJSConfig } = await import('./services/emailService');
      const config = validateEmailJSConfig();
      
      if (config.isValid) {
        console.log('✅ EmailJS configuration is valid');
        console.log('📧 Service ID:', config.config.SERVICE_ID);
        console.log('📧 Template ID:', config.config.TEMPLATE_ID);
        console.log('📧 Recipient:', config.config.RECIPIENT_EMAIL);
      } else {
        console.log('❌ EmailJS configuration issues:');
        config.issues.forEach(issue => console.log(`  - ${issue}`));
      }
      
      return config;
      
    } catch (error) {
      console.error('❌ Error checking EmailJS:', error);
      return { isValid: false, issues: ['Configuration check failed'] };
    }
  },

  // Run all tests
  async runAllTests() {
    console.log('🚀 Running complete loitering detection test suite...');
    console.log('='.repeat(50));
    
    const results = {
      detectionStatus: this.checkDetectionStatus(),
      browserNotifications: this.testBrowserNotifications(),
      emailJSConfig: await this.checkEmailJSConfig(),
      storedAlerts: await this.checkStoredAlerts(),
      simulatedAlert: await this.simulateLoiteringAlert()
    };
    
    console.log('='.repeat(50));
    console.log('📊 Test Results Summary:');
    console.log(`Detection Status: ${results.detectionStatus ? '✅ ACTIVE' : '❌ INACTIVE'}`);
    console.log(`Browser Notifications: ${results.browserNotifications ? '✅ WORKING' : '❌ ISSUES'}`);
    console.log(`EmailJS Config: ${results.emailJSConfig.isValid ? '✅ VALID' : '❌ ISSUES'}`);
    console.log(`Stored Alerts: ${results.storedAlerts.total} total, ${results.storedAlerts.loitering} loitering`);
    console.log(`Simulated Alert: ${results.simulatedAlert.success ? '✅ SUCCESS' : '❌ FAILED'}`);
    
    if (results.detectionStatus && results.browserNotifications && results.emailJSConfig.isValid) {
      console.log('🎉 All systems ready! Try standing still for 30+ seconds to test real loitering detection.');
    } else {
      console.log('⚠️ Some issues detected. Check the details above.');
    }
    
    return results;
  }
};

// Quick test function
export const quickLoiteringTest = () => {
  console.log('🧪 Quick Loitering Detection Test');
  console.log('Run: testLoiteringDetection.runAllTests()');
  
  return testLoiteringDetection.runAllTests();
};
