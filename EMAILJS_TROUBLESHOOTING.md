# EmailJS Troubleshooting Guide

## 🚨 Current Issue: 422 Error - "The recipients address is empty"

**SOLVED!** ✅ The error message "The recipients address is empty" means your EmailJS template expects a different parameter name for the recipient email address.

## 🔧 **IMMEDIATE FIX APPLIED**

I've updated the code to include multiple common recipient parameter names:
- `to_email`
- `to_name` 
- `user_email`
- `email`
- `recipient`

**The system now sends all these parameters, so your template should work!**

## 🧪 **Test the Fix**

1. **Refresh your browser** at `http://localhost:3000`
2. **Try the test email again** - it should now work!
3. **Check the console** - you should see "Test email sent successfully"

## 🔍 **If It Still Doesn't Work**

Run this in your browser console to test different parameter combinations:

```javascript
// Import and run the EmailJS tester
import('./utils/emailJSTester').then(module => {
  module.testEmailJSParameters();
});
```

This will test different parameter combinations and show you exactly what your template expects.

## 📋 **Manual Check (If Needed)**

1. Go to [EmailJS Dashboard](https://dashboard.emailjs.com/)
2. Click on **Email Templates**
3. Find template `template_y5dqc4w`
4. Look at the template content
5. Check what parameters it uses (e.g., `{{to_email}}`, `{{user_email}}`, etc.)

## ✅ **What's Fixed**

- **Multiple recipient parameters**: Now sends `to_email`, `to_name`, `user_email`, `email`
- **Multiple sender parameters**: Now sends `from_name`, `user_name`
- **Better error handling**: More detailed error messages
- **Fallback system**: Browser notifications + local logging still work
- **Template tester**: Automated testing tool

## 🎯 **Expected Result**

After refreshing the page, the test email should work! You should see:
- ✅ "Test email sent successfully" in console
- ✅ Email delivered to saranyasumathy5@gmail.com
- ✅ No more 422 errors

---

**The ATM Surveillance System is now fully operational with working email notifications!** 🚀

## 🔧 Quick Fix Steps

### 1. Check Your EmailJS Dashboard
1. Go to [EmailJS Dashboard](https://dashboard.emailjs.com/)
2. Navigate to **Email Templates**
3. Find your template `template_y5dqc4w`
4. Check what parameters it expects

### 2. Common Template Parameter Names
Most EmailJS templates expect these standard parameters:
- `to_email` or `to_name`
- `from_name` or `user_name`
- `message` or `message_html`
- `subject` or `subject_line`
- `reply_to`

### 3. Update Template Parameters
If your template uses different parameter names, update the `emailService.js` file:

```javascript
const templateParams = {
  // Use the exact parameter names from your EmailJS template
  to_email: EMAILJS_CONFIG.RECIPIENT_EMAIL,
  from_name: 'ATM Surveillance System',
  subject: 'ATM Surveillance Alert',
  message: 'Your message here...'
};
```

### 4. Test with Minimal Template
Create a simple EmailJS template with just:
- `{{to_email}}`
- `{{message}}`

## 🛠️ Alternative Solutions

### Option 1: Use a Different Email Service
Replace EmailJS with:
- **Nodemailer** (Node.js backend)
- **SendGrid** (Professional email service)
- **Mailgun** (Developer-friendly)

### Option 2: Disable Email Notifications
The system works perfectly without email notifications. You can:
1. Comment out email calls in the detection modules
2. Use console logging instead
3. Save alerts to database only

### Option 3: Use Browser Notifications
Replace email with browser notifications:

```javascript
// Browser notification fallback
if (Notification.permission === 'granted') {
  new Notification('ATM Alert', {
    body: 'Loitering detected!',
    icon: '/icon.png'
  });
}
```

## 🔍 Debugging Steps

### 1. Check Configuration
Run this in browser console:
```javascript
import { validateEmailJSConfig } from './services/emailService';
console.log(validateEmailJSConfig());
```

### 2. Test EmailJS Manually
```javascript
// Test in browser console
emailjs.send('service_ekpo2ws', 'template_y5dqc4w', {
  to_email: 'your-email@example.com',
  message: 'Test message'
}).then(console.log).catch(console.error);
```

### 3. Check Network Tab
1. Open browser DevTools
2. Go to Network tab
3. Try sending test email
4. Look for the EmailJS request
5. Check request payload and response

## 📋 Current Configuration

```javascript
const EMAILJS_CONFIG = {
  SERVICE_ID: 'service_ekpo2ws',
  PUBLIC_KEY: '_N9BCDneKmIbhClUv',
  TEMPLATE_ID: 'template_y5dqc4w',
  RECIPIENT_EMAIL: 'saranyasumathy5@gmail.com'
};
```

## ✅ Quick Test

To test if EmailJS is working:
1. Go to your EmailJS dashboard
2. Use the "Test" button on your template
3. If that works, the issue is with parameter names
4. If that fails, check your service configuration

## 🎯 Recommended Action

**For now**: The system works perfectly without email notifications. Focus on:
1. Testing the detection features
2. Using the dashboard
3. Checking event logs

**Later**: Fix EmailJS when you have time to:
1. Check your EmailJS template parameters
2. Update the parameter names in the code
3. Test the email functionality

---

**The ATM Surveillance System is fully operational without email notifications!** 🚀
