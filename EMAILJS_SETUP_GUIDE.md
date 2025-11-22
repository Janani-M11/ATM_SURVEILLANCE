# EmailJS Configuration Guide

## EmailJS Setup Instructions

### 1. EmailJS Account Setup
- Go to [EmailJS.com](https://www.emailjs.com/)
- Create an account or sign in
- Your Service ID: `service_ekpo2ws`
- Your Public Key: `_N9BCDneKmIbhClUv`

### 2. Create Email Template

1. **Go to Email Templates** in your EmailJS dashboard
2. **Use Your Existing Template** with these settings:
   - **Template ID**: `template_y5dqc4w` ✅ (Already configured)
   - **Template Name**: "Password Reset" (Your existing template)

3. **Template Content** (Use these exact fields):
```html
Subject: {{subject}}

To: {{to_email}}

{{message}}

---
ATM Surveillance System
Automated Alert Notification
```

4. **Template Variables** (Only these 3 fields are needed):
   - `{{to_email}}` - Recipient email (saranyasumathy5@gmail.com)
   - `{{subject}}` - Email subject line
   - `{{message}}` - Alert message content

### 3. Email Service Configuration

1. **Go to Email Services** in your EmailJS dashboard
2. **Add Email Service** (Gmail, Outlook, etc.)
3. **Service ID**: `service_ekpo2ws` (should match your service)

### 4. Test Configuration

Once the template is created, you can test the email system:

1. **Start the project**: `.\start.bat`
2. **Open**: http://localhost:3000
3. **Login** with: admin@atm.com / admin123
4. **Go to Detection Module**
5. **Click "Test Email"** button
6. **Check** saranyasumathy5@gmail.com for the test email

### 5. How It Works

- **Loitering Detection**: When loitering is detected, an email alert is automatically sent
- **Rate Limiting**: Emails are sent only once every 30 seconds to prevent spam
- **Email Content**: Includes detection details, timestamp, and confidence level
- **Recipient**: All alerts go to saranyasumathy5@gmail.com

### 6. Email Alert Features

✅ **Automatic Detection**: Sends email when loitering is detected  
✅ **Rate Limited**: Prevents email spam (30-second cooldown)  
✅ **Detailed Information**: Includes timestamp, confidence, and location  
✅ **Test Function**: Test email button to verify configuration  
✅ **Toggle Control**: Enable/disable email alerts with button  

### 7. Troubleshooting

If emails are not being sent:

1. **Check EmailJS Dashboard**: Verify template and service are active
2. **Check Browser Console**: Look for EmailJS errors
3. **Verify Template ID**: Must be exactly `template_loitering_alert`
4. **Check Service ID**: Must be exactly `service_ekpo2ws`
5. **Test Email**: Use the "Test Email" button first

### 8. Email Template Example

The system will send emails like this:

```
Subject: 🚨 ATM Surveillance Alert - Loitering Detected

To: saranyasumathy5@gmail.com

🚨 LOITERING ALERT 🚨

ATM Surveillance System has detected suspicious loitering activity.

Detection Details:
- Time: 10/25/2025, 2:30:15 PM
- Location: ATM Surveillance System
- Alert Type: Loitering Detection
- Confidence: 85.3%
- Duration: Ongoing

This is an automated alert from the ATM Surveillance System.
Please investigate the situation immediately.

System Status: ACTIVE
Timestamp: 2025-10-25T14:30:15.000Z

---
ATM Surveillance System
Automated Alert Notification
```

## Ready to Use!

Once you've set up the EmailJS template, the system will automatically send email alerts to saranyasumathy5@gmail.com whenever loitering is detected!
