# 🔊 Voice Alerts System - Complete Guide

## Overview

The ATM Surveillance System now features customized voice alerts for each detection type with intelligent timing and alarm sounds.

---

## 🎯 Custom Voice Messages

### 1. **Multiple People Detection** (>2 people)
**Voice Message:**
> "Please go out of the ATM. More than 2 people cannot stand inside the ATM."

**When it triggers:**
- Detects more than 2 people in the frame
- Speaks immediately when detected

**Purpose:**
- Prevent crowding inside ATM
- Ensure only authorized number of people

---

### 2. **Helmet Detection**
**Voice Message:**
> "Please remove your helmet."

**Special Features:**
- ⏱️ **10-second delay** before speaking
- ⏱️ **10-second cooldown** between repeated alerts

**When it triggers:**
- Detects helmet on any person
- Waits 10 seconds before first alert
- Won't repeat within 10 seconds

**Purpose:**
- Give person time to remove helmet naturally
- Avoid annoying repeated alerts
- Security requirement (face visibility)

**Flow:**
```
Helmet Detected (frame 1)
  ↓
Wait 10 seconds...
  ↓
Still detected? → Speak: "Please remove your helmet"
  ↓
Start 10-second cooldown timer
  ↓
Within 10 seconds: No more alerts
  ↓
After 10 seconds: Can alert again if still detected
```

---

### 3. **Face Cover Detection**
**Voice Message:**
> "Please uncover yourself."

**When it triggers:**
- Detects mask, scarf, or face covering
- Speaks immediately when detected

**Purpose:**
- Face visibility requirement
- Security and identification

---

### 4. **Loitering Detection**
**Alert Type:**
> 🚨 **ALARM SOUND** (not voice)

**Sound:**
- Loud repeated alert: "Alert! Alert! Alert!"
- Plays 3 times rapidly
- High volume (100%)
- Fast speech rate (200 words/min)

**When it triggers:**
- Person stationary for >25 seconds
- Movement variance < 200 pixels

**Purpose:**
- Draw immediate attention
- Deter suspicious behavior
- Alert security personnel

---

### 5. **Posture Detection**
**Voice Message:**
> "Don't bend inside the ATM."

**When it triggers:**
- Detects unusual posture (bending, slouching)
- Posture score < 0.45
- Speaks immediately when detected

**Purpose:**
- Prevent tampering
- Detect suspicious behavior
- Ensure proper ATM usage

---

## 🔧 Technical Implementation

### Voice Alert Function

```python
def speak_alert(message, alert_type=None, delay=0):
    """
    Text to speech for alerts with optional delay
    
    Parameters:
    - message: Text to speak
    - alert_type: Type of alert ('helmet', 'loitering', etc.)
    - delay: Seconds to wait before speaking
    """
    # Creates separate thread for non-blocking speech
    # Supports delayed alerts (helmet: 10s)
    # Special handling for loitering (alarm sound)
```

### Alarm Sound Function

```python
def play_alarm_sound():
    """
    Play alarm sound for loitering detection
    
    Features:
    - Plays "Alert! Alert! Alert!" 3 times
    - High volume (100%)
    - Fast speech rate (200 wpm)
    - Non-blocking (separate thread)
    """
```

---

## 📊 Alert Summary Table

| Detection Type | Voice Message | Delay | Cooldown | Volume | Special |
|---------------|---------------|-------|----------|--------|---------|
| **Multiple People** | "Please go out of the ATM. More than 2 people cannot stand inside the ATM." | 0s | None | 90% | Immediate |
| **Helmet** | "Please remove your helmet." | 10s | 10s | 90% | Delayed start |
| **Face Cover** | "Please uncover yourself." | 0s | None | 90% | Immediate |
| **Loitering** | ALARM SOUND | 0s | None | 100% | 3x repeat |
| **Posture** | "Don't bend inside the ATM." | 0s | None | 90% | Immediate |

---

## 🎛️ Voice Settings

### Current Configuration:
- **Speech Rate:** 150 words per minute (normal)
- **Volume:** 90% (clear and audible)
- **Engine:** pyttsx3 (Text-to-Speech)
- **Threading:** Non-blocking (doesn't freeze system)

### Alarm Settings:
- **Speech Rate:** 200 words per minute (fast/urgent)
- **Volume:** 100% (maximum)
- **Repetitions:** 3 times
- **Type:** Rapid alert beeps

---

## 🔄 Alert Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              DETECTION OCCURS IN FRAME                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │   What type of detection?  │
         └────────────┬───────────────┘
                      │
        ┌─────────────┴─────────────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                   ┌──────────────────┐
│ Multiple People  │                   │     Helmet       │
│    (>2 people)   │                   │    Detected      │
└────────┬─────────┘                   └────────┬─────────┘
         │                                      │
         │ Immediate                            │ Wait 10s
         ▼                                      ▼
    "Please go out                         Check cooldown
    of the ATM..."                              │
         │                                      ▼
         │                              If >10s since last:
         │                              "Please remove
         │                               your helmet"
         │                                      │
         └──────────────┬───────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Face Cover   │ │  Loitering   │ │   Posture    │
│   Detected   │ │   Detected   │ │   Detected   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │ Immediate      │ Immediate      │ Immediate
       ▼                ▼                ▼
  "Please          🚨 ALARM         "Don't bend
   uncover         SOUND            inside the
   yourself"       (3x Alert!)      ATM"
       │                │                │
       └────────────────┴────────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │  Log Event to Database       │
         │  Continue Monitoring         │
         └──────────────────────────────┘
```

---

## 🧪 Testing the Alerts

### How to Test Each Alert:

**1. Multiple People Alert:**
```
1. Start detection module
2. Have 3+ people in frame
3. Hear: "Please go out of the ATM..."
```

**2. Helmet Alert (with 10s delay):**
```
1. Start detection module
2. Wear a helmet
3. Wait 10 seconds...
4. Hear: "Please remove your helmet"
5. Wait another 10 seconds to test cooldown
```

**3. Face Cover Alert:**
```
1. Start detection module
2. Wear a mask or scarf
3. Hear immediately: "Please uncover yourself"
```

**4. Loitering Alert (alarm sound):**
```
1. Start detection module
2. Stand completely still for 30 seconds
3. Hear: "Alert! Alert! Alert!" (3 times, loud)
```

**5. Posture Alert:**
```
1. Start detection module
2. Bend down or slouch significantly
3. Hear: "Don't bend inside the ATM"
```

---

## 🎯 Benefits of This System

### 1. **User-Friendly**
- Clear, specific instructions
- Natural language messages
- Polite but firm tone

### 2. **Intelligent Timing**
- Helmet alert has 10s delay (natural behavior)
- Cooldown prevents alert spam
- Immediate alerts for urgent issues

### 3. **Attention-Grabbing**
- Loitering uses alarm sound (more urgent)
- High volume for important alerts
- Different alert types for different severity

### 4. **Non-Blocking**
- Alerts run in separate threads
- System continues detecting while speaking
- No performance impact

### 5. **Configurable**
- Easy to change messages
- Adjustable delays and cooldowns
- Customizable voice settings

---

## ⚙️ Customization Guide

### Change Voice Messages

Edit in `backend/app.py` around line 159-181:

```python
# Example: Change helmet message
elif alert_type == 'helmet':
    voice_message = "Your custom message here"
    speak_alert(voice_message, alert_type=alert_type, delay=10)
```

### Adjust Helmet Delay

Change the delay parameter (currently 10 seconds):

```python
# Line 167
speak_alert(voice_message, alert_type=alert_type, delay=15)  # 15 seconds
```

### Adjust Cooldown Period

Change the cooldown check (currently 10 seconds):

```python
# Line 166
if alert_type not in helmet_alert_timer or (current_time - helmet_alert_timer[alert_type]) >= 15:
    # Will cooldown for 15 seconds instead of 10
```

### Change Voice Speed

Edit in `backend/app.py` around line 93:

```python
engine.setProperty('rate', 120)  # Slower (was 150)
# or
engine.setProperty('rate', 180)  # Faster (was 150)
```

### Change Volume

Edit in `backend/app.py` around line 94:

```python
engine.setProperty('volume', 1.0)  # Maximum (was 0.9)
# or
engine.setProperty('volume', 0.7)  # Quieter (was 0.9)
```

### Change Alarm Repetitions

Edit in `backend/app.py` around line 73:

```python
for _ in range(5):  # 5 times instead of 3
    engine.say("Alert! Alert! Alert!")
```

---

## 🔍 Troubleshooting

### No Sound / Alerts Not Working

**Check:**
1. ✅ System volume not muted
2. ✅ Speakers/headphones connected
3. ✅ pyttsx3 installed: `pip install pyttsx3`
4. ✅ Backend server restarted after changes

**Test TTS:**
```python
import pyttsx3
engine = pyttsx3.init()
engine.say("Test message")
engine.runAndWait()
```

### Helmet Alert Not Waiting 10 Seconds

**Check:**
1. ✅ Delay parameter is set: `delay=10`
2. ✅ helmet_alert_timer is initialized
3. ✅ Backend server restarted

### Alerts Repeating Too Often

**Solution:**
- Increase cooldown period in code
- Currently 10 seconds for helmet
- Add cooldown for other alert types if needed

### Loitering Not Playing Alarm

**Check:**
1. ✅ `play_alarm_sound()` function defined
2. ✅ Alert type is exactly 'loitering'
3. ✅ TTS engine initialized properly

---

## 📝 Code Locations

### Main Alert Logic
**File:** `backend/app.py`
**Lines:** 155-189 (process-video endpoint)

### Voice Alert Function
**File:** `backend/app.py`
**Lines:** 83-108

### Alarm Sound Function
**File:** `backend/app.py`
**Lines:** 64-81

### Timer Initialization
**File:** `backend/app.py`
**Line:** 62

---

## 🎓 How It Works

### Voice Alert Process:

1. **Detection occurs** in frame
2. **Alert generated** with type and message
3. **Custom message selected** based on type
4. **Delay applied** if helmet (10s)
5. **Cooldown checked** for helmet
6. **Speak or play alarm** in separate thread
7. **Event logged** to database
8. **Continue monitoring** next frame

### Threading Model:

```
Main Thread (Detection Loop)
  │
  ├─► Detection Pipeline
  │    └─► Returns results
  │
  ├─► Alert Processing
  │    ├─► Create voice message
  │    ├─► Start new thread
  │    │    └─► speak_alert() or play_alarm_sound()
  │    │         └─► Runs independently
  │    │
  │    └─► Log to database
  │
  └─► Wait 500ms, capture next frame
```

**Benefits:**
- ✅ No blocking (alerts don't freeze system)
- ✅ Continues detecting while speaking
- ✅ Multiple alerts can overlap if needed
- ✅ System remains responsive

---

## 🎉 Summary

### Custom Voice Alerts Implemented:

✅ **Multiple People:** "Please go out of the ATM. More than 2 people cannot stand inside the ATM."
✅ **Helmet:** "Please remove your helmet." (10s delay + 10s cooldown)
✅ **Face Cover:** "Please uncover yourself."
✅ **Loitering:** Alarm sound (3x "Alert!")
✅ **Posture:** "Don't bend inside the ATM."

### Features:
- ✅ Non-blocking threaded alerts
- ✅ Intelligent timing (delays & cooldowns)
- ✅ Alarm sound for urgent situations
- ✅ Clear, specific instructions
- ✅ Easy to customize

---

**🔊 Your voice alert system is ready! Restart the backend to activate.**

```bash
# Restart backend server
python backend/app.py
```

**Then test each alert type to ensure they work as expected!**

