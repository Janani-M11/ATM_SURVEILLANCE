# Loitering Detection Test Scenarios

## 🎯 **Test Scenario 1: Basic Loitering (30 seconds)**

**Setup:**
1. Position yourself 2-3 feet from camera
2. Stand still with minimal movement
3. Stay in frame for 30+ seconds

**Expected Result:**
- ✅ Loitering alert after 25-30 seconds
- ✅ Confidence: 0.90-0.95
- ✅ Email notification sent
- ✅ Browser notification shown

**Console Output:**
```
Loitering detected with confidence: 0.95
🚨 ATM ALERT: {type: 'loitering', confidence: 0.95}
Email sent successfully
```

---

## 🎯 **Test Scenario 2: Extended Loitering (60 seconds)**

**Setup:**
1. Stand still for 60+ seconds
2. Make only very small movements
3. Stay in same general area

**Expected Result:**
- ✅ Higher confidence (0.95-0.98)
- ✅ Multiple alerts possible
- ✅ Stronger email notifications

---

## 🎯 **Test Scenario 3: False Positive Test (Normal Movement)**

**Setup:**
1. Walk around normally
2. Don't stay in one place
3. Move continuously for 30+ seconds

**Expected Result:**
- ❌ NO loitering alerts
- ✅ Normal movement detected
- ✅ System working correctly

---

## 🎯 **Test Scenario 4: Edge Case (Sitting/Leaning)**

**Setup:**
1. Sit or lean against wall
2. Stay in same position
3. Minimal movement for 30+ seconds

**Expected Result:**
- ✅ Loitering detected (if stationary enough)
- ✅ Confidence: 0.85-0.95
- ✅ Appropriate alert level

---

## 🔧 **Manual Testing Commands**

### Test 1: Check Detection Status
```javascript
// Run in browser console
console.log('Testing loitering detection...');

// Check if detection is running
if (window.detectionActive) {
    console.log('✅ Detection is active');
} else {
    console.log('❌ Detection not active - start detection first');
}
```

### Test 2: Simulate Loitering Alert
```javascript
// Run in browser console to test alert system
import('./services/emailService').then(module => {
    const testData = {
        confidence: 0.95,
        duration: '30 seconds',
        timestamp: new Date().toISOString()
    };
    
    module.sendLoiteringAlert(testData).then(result => {
        console.log('Test alert result:', result);
    });
});
```

### Test 3: Check Stored Alerts
```javascript
// Run in browser console
import('./services/emailService').then(module => {
    const alerts = module.getStoredAlerts();
    console.log('Stored alerts:', alerts);
    
    // Filter loitering alerts
    const loiteringAlerts = alerts.filter(alert => 
        alert.data && alert.data.type === 'loitering'
    );
    console.log('Loitering alerts:', loiteringAlerts);
});
```

---

## 📊 **Monitoring Dashboard**

### Real-Time Metrics to Watch:

1. **Detection Status**: Should show "ACTIVE"
2. **Frame Rate**: Should be 10-30 FPS
3. **Confidence Scores**: Should show 0.85-0.98 for loitering
4. **Alert Count**: Should increment when loitering detected

### Event Logs to Check:

1. **Event Type**: "loitering"
2. **Confidence**: High values (0.90+)
3. **Description**: Should mention loitering detection
4. **Timestamp**: Recent entries

---

## 🚨 **Troubleshooting**

### If No Alerts Are Generated:

1. **Check Camera Access**: Make sure camera is working
2. **Check Detection Status**: Ensure detection is active
3. **Check Console Errors**: Look for error messages
4. **Check Lighting**: Ensure good lighting conditions
5. **Check Distance**: Stay 2-4 feet from camera

### If False Positives:

1. **Check Movement**: Are you moving too much?
2. **Check Background**: Is background stable?
3. **Check Lighting**: Is lighting consistent?

### If Low Confidence:

1. **Stay Still Longer**: Try 45+ seconds
2. **Reduce Movement**: Minimize all movement
3. **Check Position**: Stay centered in frame

---

## 📈 **Performance Benchmarks**

### Expected Performance:

- **Detection Time**: 25-30 seconds
- **Confidence Range**: 0.85-0.98
- **False Positive Rate**: <1%
- **Processing Speed**: 80-120ms per frame

### Success Criteria:

- ✅ Alert generated within 30 seconds of standing still
- ✅ Confidence > 0.90
- ✅ Email notification received
- ✅ Browser notification shown
- ✅ Event logged in dashboard

---

## 🎯 **Quick Test Checklist**

- [ ] Camera access granted
- [ ] Detection module active
- [ ] Console open (F12)
- [ ] Stand 2-3 feet from camera
- [ ] Stay still for 30+ seconds
- [ ] Watch for console messages
- [ ] Check Event Logs tab
- [ ] Verify email notification
- [ ] Check browser notification

**If all items pass, your loitering detection is working perfectly!** ✅
