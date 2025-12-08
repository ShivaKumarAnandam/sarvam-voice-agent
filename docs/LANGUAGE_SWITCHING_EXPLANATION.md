# Automatic Language Detection - Clear Explanation

## Current Problem

**Scenario:**
1. User selects **Telugu** at the start
2. User continues conversation in Telugu for 5 minutes
3. User suddenly switches to **Hindi** mid-conversation
4. **Problem:** System still responds in Telugu (because user selected Telugu initially)

## Solution: Automatic Language Detection

### How It Works - Step by Step

#### **Step 1: User Selects Language (Initial)**
```
User: Presses "1" for Telugu
System: Stores selected_language = "te-IN"
System: Uses Telugu for all responses
```

#### **Step 2: Normal Conversation (Language Matches)**
```
Turn 1:
  User speaks: "నా బిల్ ఎంత?" (Telugu)
  STT detects: "te-IN" ✅
  Selected: "te-IN" ✅
  Match! → Continue in Telugu

Turn 2:
  User speaks: "ఎప్పుడు చెల్లించాలి?" (Telugu)
  STT detects: "te-IN" ✅
  Selected: "te-IN" ✅
  Match! → Continue in Telugu
```

#### **Step 3: User Switches Language (First Detection)**
```
Turn 3:
  User speaks: "मेरा बिल कितना है?" (Hindi)
  STT detects: "hi-IN" ❌ (Different from selected!)
  Selected: "te-IN"
  Mismatch detected! → But don't switch yet (might be accidental)
  
  Action: 
  - Store this detection in history
  - Count: 1 consecutive Hindi detection
  - Still respond in Telugu (waiting for confirmation)
```

#### **Step 4: User Continues in New Language (Second Detection)**
```
Turn 4:
  User speaks: "मुझे कब भुगतान करना है?" (Hindi again)
  STT detects: "hi-IN" ❌ (Different again!)
  Selected: "te-IN"
  
  Action:
  - Count: 2 consecutive Hindi detections
  - Threshold reached! (we set threshold = 2)
  - AUTO-SWITCH to Hindi
  - Update selected_language = "hi-IN"
  - Now respond in Hindi
```

#### **Step 5: System Responds in New Language**
```
Turn 5:
  System responds: "आपका बिल ₹500 है।" (Hindi) ✅
  User continues in Hindi
  All future responses in Hindi
```

## Implementation Details

### What We Need to Track:

1. **Language History**: Last few language detections
   ```
   Example:
   history = ["te-IN", "te-IN", "hi-IN", "hi-IN"]
   ```

2. **Consecutive Count**: How many times different language detected
   ```
   Example:
   selected = "te-IN"
   detected = "hi-IN"
   consecutive_different = 2  (Hindi detected 2 times in a row)
   ```

3. **Threshold**: How many times before switching
   ```
   threshold = 2  (switch after 2 consecutive detections)
   ```

### Algorithm Flow:

```
1. User speaks → STT detects language
2. Compare detected_language with selected_language
3. If SAME:
   - Reset counter
   - Continue normally
4. If DIFFERENT:
   - Increment counter
   - Check if counter >= threshold
   - If YES: Auto-switch to detected language
   - If NO: Keep current language, wait for more detections
```

## Visual Example

```
Time →  Turn 1    Turn 2    Turn 3    Turn 4    Turn 5    Turn 6
─────────────────────────────────────────────────────────────────
User:   Telugu     Telugu    Hindi     Hindi     Hindi     Hindi
        (te-IN)    (te-IN)   (hi-IN)   (hi-IN)   (hi-IN)   (hi-IN)

STT:    te-IN ✅   te-IN ✅  hi-IN ❌  hi-IN ❌  hi-IN ✅   hi-IN ✅
        (match)    (match)   (diff)    (diff)    (match)   (match)

Count:  0          0         1         2         0         0
        (reset)    (reset)   (inc)     (SWITCH!) (reset)   (reset)

System: Telugu     Telugu    Telugu    Hindi     Hindi     Hindi
        (te-IN)    (te-IN)   (te-IN)   (hi-IN)   (hi-IN)   (hi-IN)
                              ↑                    ↑
                         Still Telugu      Now switched!
                         (waiting...)      (threshold met)
```

## Why This Works

✅ **Prevents Accidental Switches**: 
   - Single word in different language won't trigger switch
   - Need 2-3 consecutive detections

✅ **Handles Real Switches**:
   - When user genuinely switches, detected quickly
   - No need for explicit commands

✅ **Natural Experience**:
   - User doesn't need to say "switch to Hindi"
   - System automatically adapts

## Configuration Options

```python
# Threshold: How many consecutive detections before switching
SWITCH_THRESHOLD = 2  # Switch after 2 consecutive detections

# History Size: How many recent detections to remember
HISTORY_SIZE = 5  # Remember last 5 detections

# Minimum Turns: Don't switch in first N turns (let user settle)
MIN_TURNS_BEFORE_SWITCH = 2  # Don't switch in first 2 turns
```

## Edge Cases Handled

1. **Brief Language Mixing**: 
   - User says one word in Hindi, then back to Telugu
   - Counter resets → No switch

2. **Code-Switching**:
   - User mixes languages in same sentence
   - System uses most common language detected

3. **Noisy Audio**:
   - STT might misdetect occasionally
   - Threshold prevents false switches

