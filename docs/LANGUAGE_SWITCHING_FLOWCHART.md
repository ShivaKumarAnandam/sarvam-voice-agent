# Automatic Language Switching - Simple Flowchart

## Simple Example: User Switches from Telugu to Hindi

```
┌─────────────────────────────────────────────────────────────┐
│  START: User selected Telugu (te-IN)                        │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  Turn 1: User speaks Telugu   │
        │  STT detects: te-IN           │
        │  Selected: te-IN              │
        │  Match? ✅ YES                 │
        └───────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  Turn 2: User speaks Telugu   │
        │  STT detects: te-IN           │
        │  Selected: te-IN              │
        │  Match? ✅ YES                 │
        └───────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  Turn 3: User speaks Hindi    │
        │  STT detects: hi-IN           │
        │  Selected: te-IN              │
        │  Match? ❌ NO                  │
        │                               │
        │  Counter = 1                  │
        │  Threshold = 2                │
        │  Switch? ❌ NO (not enough)    │
        │                               │
        │  Action: Keep Telugu          │
        │  (Wait for more detections)   │
        └───────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  Turn 4: User speaks Hindi    │
        │  STT detects: hi-IN           │
        │  Selected: te-IN              │
        │  Match? ❌ NO                  │
        │                               │
        │  Counter = 2                  │
        │  Threshold = 2                │
        │  Switch? ✅ YES!              │
        │                               │
        │  Action: AUTO-SWITCH          │
        │  selected_language = "hi-IN"  │
        └───────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  Turn 5: System responds      │
        │  in Hindi (hi-IN) ✅          │
        │                               │
        │  User continues in Hindi      │
        │  All future responses         │
        │  in Hindi                     │
        └───────────────────────────────┘
```

## Decision Logic (Simple Code Logic)

```python
# Pseudo-code explanation:

if detected_language == selected_language:
    # Languages match - everything is fine
    counter = 0  # Reset counter
    use_language = selected_language
    
else:
    # Languages don't match - user might be switching
    counter = counter + 1  # Increment counter
    
    if counter >= THRESHOLD:  # Threshold = 2
        # User has spoken different language 2+ times
        # They probably want to switch
        selected_language = detected_language  # SWITCH!
        counter = 0  # Reset counter
        use_language = detected_language
        
    else:
        # Not enough detections yet - might be accidental
        # Keep using original language
        use_language = selected_language
```

## Real-World Scenario

**Conversation Flow:**

```
User: [Selects Telugu]
System: "తెలుగు. మీకు ఎలా సహాయం చేయగలను?" (Telugu)

User: "నా బిల్ ఎంత?" (Telugu - "What is my bill?")
System: "మీ బిల్ ₹500." (Telugu - responds in Telugu) ✅

User: "ఎప్పుడు చెల్లించాలి?" (Telugu - "When to pay?")
System: "మీరు ఈ నెలలో చెల్లించవచ్చు." (Telugu) ✅

User: "मेरा बिल कितना है?" (Hindi - "What is my bill?")
System: "మీ బిల్ ₹500." (Telugu - still Telugu) ⚠️
        [Counter = 1, waiting...]

User: "मुझे कब भुगतान करना है?" (Hindi again - "When to pay?")
System: "आपका बिल ₹500 है।" (Hindi - SWITCHED!) ✅
        [Counter = 2, threshold met, switched to Hindi]

User: "धन्यवाद" (Hindi - "Thank you")
System: "आपका स्वागत है।" (Hindi - continues in Hindi) ✅
```

## Key Points

1. **Threshold = 2**: Need 2 consecutive detections before switching
2. **Counter resets**: If languages match, counter goes back to 0
3. **Automatic**: No user command needed - system detects and switches
4. **Safe**: Won't switch on single accidental word in different language

