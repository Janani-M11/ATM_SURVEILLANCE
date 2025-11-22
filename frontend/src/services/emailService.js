// EmailJS Configuration
import emailjs from '@emailjs/browser';

// EmailJS Configuration
const EMAILJS_CONFIG = {
  SERVICE_ID: 'service_ekpo2ws',
  PUBLIC_KEY: '_N9BCDneKmIbhClUv',
  TEMPLATE_ID: 'template_y5dqc4w', // Your template ID
  RECIPIENT_EMAIL: 'saranyasumathy5@gmail.com'
};

// Initialize EmailJS
emailjs.init(EMAILJS_CONFIG.PUBLIC_KEY);

// Configuration validation
export const validateEmailJSConfig = () => {
  const config = EMAILJS_CONFIG;
  const issues = [];
  
  if (!config.SERVICE_ID || config.SERVICE_ID === 'your_service_id') {
    issues.push('SERVICE_ID not configured');
  }
  
  if (!config.PUBLIC_KEY || config.PUBLIC_KEY === 'your_public_key') {
    issues.push('PUBLIC_KEY not configured');
  }
  
  if (!config.TEMPLATE_ID || config.TEMPLATE_ID === 'your_template_id') {
    issues.push('TEMPLATE_ID not configured');
  }
  
  if (!config.RECIPIENT_EMAIL || config.RECIPIENT_EMAIL === 'your_email@example.com') {
    issues.push('RECIPIENT_EMAIL not configured');
  }
  
  return {
    isValid: issues.length === 0,
    issues,
    config
  };
};

export const sendLoiteringAlert = async (detectionData) => {
  // Always log the alert locally
  const alertData = {
    type: 'loitering',
    confidence: detectionData.confidence,
    duration: detectionData.duration,
    timestamp: new Date().toISOString()
  };
  
  logAlert(alertData);
  
  // Send browser notification
  sendBrowserNotification(
    '🚨 Loitering Alert',
    `Suspicious loitering detected with ${detectionData.confidence ? (detectionData.confidence * 100).toFixed(1) + '%' : 'high'} confidence`
  );

  // Try EmailJS as secondary notification
  try {
    const templateParams = {
      // Common recipient parameter names
      to_email: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      to_name: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      user_email: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      email: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      
      // Common sender parameters
      from_name: 'ATM Surveillance System',
      user_name: 'ATM Surveillance System',
      
      // Alert content
      subject: '🚨 ATM Surveillance Alert - Loitering Detected',
      message: `🚨 LOITERING ALERT 🚨

ATM Surveillance System has detected suspicious loitering activity.

Detection Details:
- Time: ${new Date().toLocaleString()}
- Location: ATM Surveillance System
- Alert Type: Loitering Detection
- Confidence: ${detectionData.confidence ? (detectionData.confidence * 100).toFixed(1) + '%' : 'High'}
- Duration: ${detectionData.duration || 'Ongoing'}

This is an automated alert from the ATM Surveillance System.
Please investigate the situation immediately.

System Status: ACTIVE
Timestamp: ${new Date().toISOString()}`,
      
      // Reply information
      reply_to: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      reply_email: EMAILJS_CONFIG.RECIPIENT_EMAIL
    };

    const response = await emailjs.send(
      EMAILJS_CONFIG.SERVICE_ID,
      EMAILJS_CONFIG.TEMPLATE_ID,
      templateParams
    );

    console.log('Email sent successfully:', response);
    return { success: true, response, alertLogged: true };
    
  } catch (error) {
    console.error('Failed to send email:', error);
    
    // Email failed, but alert was still logged and browser notification sent
    return { 
      success: false, 
      error: 'EmailJS failed, but alert logged locally',
      alertLogged: true,
      browserNotificationSent: true
    };
  }
};

export const sendTestEmail = async () => {
  // First, validate the configuration
  const configValidation = validateEmailJSConfig();
  if (!configValidation.isValid) {
    console.warn('EmailJS Configuration Issues:', configValidation.issues);
    return {
      success: false,
      error: 'EmailJS configuration incomplete',
      issues: configValidation.issues,
      fallback: 'Please configure EmailJS properly for email notifications'
    };
  }

  try {
    // Try with common EmailJS template parameter names
    const templateParams = {
      // Common recipient parameter names
      to_email: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      to_name: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      user_email: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      email: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      
      // Common sender parameters
      from_name: 'ATM Surveillance System',
      user_name: 'ATM Surveillance System',
      
      // Message content
      subject: 'ATM Surveillance System - Test Email',
      message: `This is a test email from the ATM Surveillance System.

System Status: OPERATIONAL
Test Time: ${new Date().toLocaleString()}

If you receive this email, the notification system is working correctly.`,
      
      // Reply information
      reply_to: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      reply_email: EMAILJS_CONFIG.RECIPIENT_EMAIL
    };

    console.log('Attempting to send test email with parameters:', templateParams);

    const response = await emailjs.send(
      EMAILJS_CONFIG.SERVICE_ID,
      EMAILJS_CONFIG.TEMPLATE_ID,
      templateParams
    );

    console.log('Test email sent successfully:', response);
    return { success: true, response };
    
  } catch (error) {
    console.error('Failed to send test email:', error);
    
    // Provide more detailed error information
    let errorMessage = 'EmailJS service error';
    if (error.status === 422) {
      errorMessage = 'EmailJS template parameters mismatch (422) - check template configuration';
    } else if (error.status === 400) {
      errorMessage = 'EmailJS bad request (400) - check service configuration';
    } else if (error.status === 401) {
      errorMessage = 'EmailJS unauthorized (401) - check public key';
    }
    
    console.log('EmailJS service unavailable, but system is operational');
    return { 
      success: false, 
      error: errorMessage,
      status: error.status,
      fallback: 'System is operational, email notifications disabled',
      suggestion: 'Check EmailJS dashboard for correct template parameters'
    };
  }
};

// Fallback notification system (works without EmailJS)
export const sendBrowserNotification = (title, message) => {
  if ('Notification' in window) {
    if (Notification.permission === 'granted') {
      new Notification(title, {
        body: message,
        icon: '/icon.png',
        badge: '/badge.png'
      });
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          new Notification(title, {
            body: message,
            icon: '/icon.png'
          });
        }
      });
    }
  }
};

export const logAlert = (alertData) => {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    type: 'ALERT',
    data: alertData
  };
  
  // Store in localStorage for persistence
  const existingLogs = JSON.parse(localStorage.getItem('atm_alerts') || '[]');
  existingLogs.push(logEntry);
  
  // Keep only last 100 alerts
  if (existingLogs.length > 100) {
    existingLogs.splice(0, existingLogs.length - 100);
  }
  
  localStorage.setItem('atm_alerts', JSON.stringify(existingLogs));
  
  // Also log to console
  console.log('🚨 ATM ALERT:', logEntry);
  
  return logEntry;
};

export const getStoredAlerts = () => {
  return JSON.parse(localStorage.getItem('atm_alerts') || '[]');
};

export const clearStoredAlerts = () => {
  localStorage.removeItem('atm_alerts');
};

// Camera blackout alert function
export const sendCameraBlackoutAlert = async (alertData) => {
  // Always log the alert locally
  logAlert(alertData);
  
  // Send browser notification
  sendBrowserNotification(
    '📹 Camera Blackout Alert',
    `Camera ${alertData.cameraId} has been black for ${alertData.duration}`
  );

  // Try EmailJS as secondary notification
  try {
    const templateParams = {
      // Common recipient parameter names
      to_email: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      to_name: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      user_email: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      email: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      
      // Common sender parameters
      from_name: 'ATM Surveillance System',
      user_name: 'ATM Surveillance System',
      
      // Alert content
      subject: '📹 ATM Surveillance Alert - Camera Blackout Detected',
      message: `📹 CAMERA BLACKOUT ALERT 📹

ATM Surveillance System has detected a camera blackout condition.

Detection Details:
- Time Detected: ${new Date().toLocaleString()}
- Location: ${alertData.location}
- Camera ID: ${alertData.cameraId}
- Duration: ${alertData.duration}
- Confidence: ${alertData.confidence ? (alertData.confidence * 100).toFixed(1) + '%' : 'High'}

This could indicate:
- Camera malfunction
- Camera disconnected
- Camera lens covered
- Power failure
- Network issues

Please investigate the camera system immediately.

System Status: ACTIVE
Timestamp: ${alertData.timestamp}`,
      
      // Reply information
      reply_to: EMAILJS_CONFIG.RECIPIENT_EMAIL,
      reply_email: EMAILJS_CONFIG.RECIPIENT_EMAIL
    };

    const response = await emailjs.send(
      EMAILJS_CONFIG.SERVICE_ID,
      EMAILJS_CONFIG.TEMPLATE_ID,
      templateParams
    );

    console.log('Camera blackout email sent successfully:', response);
    return { success: true, response, alertLogged: true };
    
  } catch (error) {
    console.error('Failed to send camera blackout email:', error);
    
    // Email failed, but alert was still logged and browser notification sent
    return { 
      success: false, 
      error: 'EmailJS failed, but alert logged locally',
      alertLogged: true,
      browserNotificationSent: true
    };
  }
};

export default EMAILJS_CONFIG;
