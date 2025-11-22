// Test the new notification system
import { sendBrowserNotification, logAlert, getStoredAlerts } from './services/emailService';

// Test browser notifications
export const testBrowserNotifications = () => {
  sendBrowserNotification(
    'ATM Surveillance Test',
    'This is a test notification from the ATM Surveillance System'
  );
};

// Test alert logging
export const testAlertLogging = () => {
  const testAlert = {
    type: 'test',
    confidence: 0.95,
    duration: '5 seconds',
    timestamp: new Date().toISOString()
  };
  
  logAlert(testAlert);
  console.log('Test alert logged:', testAlert);
  
  // Show stored alerts
  const storedAlerts = getStoredAlerts();
  console.log('All stored alerts:', storedAlerts);
};

// Test EmailJS configuration
export const testEmailJSConfig = () => {
  import('./services/emailService').then(({ validateEmailJSConfig }) => {
    const config = validateEmailJSConfig();
    console.log('EmailJS Configuration:', config);
    
    if (!config.isValid) {
      console.warn('EmailJS Issues:', config.issues);
    }
  });
};

// Run all tests
export const runNotificationTests = () => {
  console.log('🧪 Running ATM Surveillance Notification Tests...');
  
  testEmailJSConfig();
  testAlertLogging();
  testBrowserNotifications();
  
  console.log('✅ Tests completed! Check console for results.');
};
