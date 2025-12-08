# Component Responsibilities Sheet

## Overview

This document defines the responsibilities of each component in the Agent Orchestrator system.

---

## Component Matrix

| Component | File | Primary Responsibilities | Key Methods |
|-----------|------|-------------------------|-------------|
| **STT Listener** | `orchestrator/task_router.py` | Route audio to STT, handle retries, return transcription | `route_transcription()` |
| **Context Handler** | `orchestrator/context_manager.py` | Store conversation history, manage sliding window, track metadata | `add_turn()`, `get_context()`, `clear_history()` |
| **Language Selector** | `orchestrator/language_coordinator.py` | Detect language, auto-switch, ensure consistency | `set_language()`, `set_detected_language()`, `ensure_consistency()` |
| **Response Router** | `orchestrator/task_router.py` | Route to LLM and TTS, handle retries | `route_generation()`, `route_synthesis()` |
| **Orchestrator** | `orchestrator/agent_orchestrator.py` | Coordinate all modules, manage workflow | `process_turn()`, `set_language()`, `set_system_prompt()` |
| **Metrics Collector** | `orchestrator/metrics.py` | Track latency metrics | `record_turn()`, `get_average_latencies()` |
| **Circuit Breaker** | `orchestrator/circuit_breaker.py` | Protect against cascading failures | `call()`, `get_state()`, `reset()` |

---

## Detailed Component Responsibilities

### 1. STT Listener (`TaskRouter.route_transcription()`)

**File:** `orchestrator/task_router.py:27-65`

**Responsibilities:**
- Accept audio data (WAV format, bytes)
- Route to STT module with language hint
- Retry on failure (2 attempts with 0.5s delay)
- Return transcription text and detected language
- Handle empty responses and exceptions

**Input:**
- `audio_data`: Audio bytes in WAV format
- `language`: Optional language hint (e.g., "te-IN", "hi-IN", "en-IN")
- `retry_count`: Number of retry attempts (default: 2)

**Output:**
- `(text, detected_language)`: Tuple of transcribed text and detected language code
- `(None, None)`: On failure

**Error Handling:**
- Retries up to `retry_count` times
- Logs errors at each attempt
- Returns `(None, None)` after all retries exhausted

**Example:**
```python
text, detected_lang = await task_router.route_transcription(
    audio_data=wav_bytes,
    language="te-IN",
    retry_count=2
)
```

---

### 2. Context Handler (`ContextManager`)

**File:** `orchestrator/context_manager.py`

**Responsibilities:**
- Store conversation history (user/assistant messages)
- Maintain sliding window (max_history turns)
- Track language per turn
- Store user metadata and session context
- Provide context for LLM (format: role/content messages)

**Key Methods:**

#### `add_turn(user_input, assistant_response, language)`
- Add conversation turn to history
- Maintains sliding window automatically
- Tracks language and timestamp

#### `get_context(system_prompt, include_metadata)`
- Get formatted context for LLM
- Returns list of messages in format: `[{"role": "...", "content": "..."}]`
- Handles system prompt (from history or provided)
- Optional metadata inclusion

#### `clear_history()`
- Clear all conversation history
- Preserves system prompt if present

#### `get_turn_count()`
- Get number of conversation turns (user + assistant pairs)

**Data Structure:**
```python
conversation_history = [
    {
        "role": "system",
        "content": "You are a helpful assistant...",
        "timestamp": "2025-01-01T12:00:00"
    },
    {
        "role": "user",
        "content": "Hello",
        "language": "te-IN",
        "timestamp": "2025-01-01T12:00:01"
    },
    {
        "role": "assistant",
        "content": "Hi there!",
        "language": "te-IN",
        "timestamp": "2025-01-01T12:00:02"
    }
]
```

**Example:**
```python
context_manager = ContextManager(max_history=10)
context_manager.add_turn("Hello", "Hi there!", "te-IN")
context = context_manager.get_context()
# Returns: [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]
```

---

### 3. Language Selector (`LanguageCoordinator`)

**File:** `orchestrator/language_coordinator.py`

**Responsibilities:**
- Set selected language (from IVR/user choice)
- Detect language from STT output
- Auto-switch language after 2 consecutive detections
- Ensure language consistency across pipeline
- Track language history and switching status

**Key Methods:**

#### `set_language(language_code)`
- Set selected language (from user choice)
- Validates language code
- Resets tracking counters

#### `set_detected_language(language_code)`
- Set detected language from STT
- Tracks language history
- Triggers auto-switch if threshold reached
- Increments turn count

#### `ensure_consistency()`
- Get processing language (selected > detected > default)
- Ensures all modules use same language

#### `get_switch_status()`
- Get current switching status
- Returns dictionary with:
  - `selected_language`: Currently selected language
  - `detected_language`: Last detected language
  - `consecutive_different_count`: Count of consecutive different detections
  - `can_switch`: Whether auto-switch can occur
  - `recent_history`: Last 3 language detections

**Auto-Switch Logic:**
- Triggers when: `consecutive_different_count >= switch_threshold` (default: 2)
- Requires: `turn_count >= min_turns_before_switch` (default: 1)
- Resets counter after switch

**Supported Languages:**
- `te-IN` - Telugu
- `hi-IN` - Hindi
- `en-IN` - English
- `gu-IN` - Gujarati

**Example:**
```python
coordinator = LanguageCoordinator(default_language="te-IN")
coordinator.set_language("te-IN")
coordinator.set_detected_language("hi-IN")  # First detection
coordinator.set_detected_language("hi-IN")  # Second detection → AUTO-SWITCH!
# coordinator.selected_language is now "hi-IN"
```

---

### 4. Response Router (`TaskRouter`)

**File:** `orchestrator/task_router.py`

**Responsibilities:**
- Route text to LLM with context
- Route text to TTS with language
- Handle retries for TTS (2 attempts)
- Return generated response or audio

**Key Methods:**

#### `route_generation(text, context, language)`
- Route to LLM module
- Prepares messages: context + current user input
- Returns generated response text
- Handles exceptions

**Input:**
- `text`: User input text
- `context`: Conversation context (list of messages)
- `language`: Language code for processing

**Output:**
- `response`: Generated response text
- `None`: On failure

#### `route_synthesis(text, language, retry_count)`
- Route to TTS module
- Retries on failure (default: 2 attempts)
- Returns audio data (WAV format)
- Handles exceptions

**Input:**
- `text`: Text to synthesize
- `language`: Language code for TTS
- `retry_count`: Number of retry attempts (default: 2)

**Output:**
- `audio_data`: WAV audio bytes
- `None`: On failure

**Example:**
```python
# LLM routing
response = await task_router.route_generation(
    text="Hello",
    context=[{"role": "system", ...}, ...],
    language="te-IN"
)

# TTS routing
audio = await task_router.route_synthesis(
    text=response,
    language="te-IN",
    retry_count=2
)
```

---

### 5. Orchestrator (`AgentOrchestrator`)

**File:** `orchestrator/agent_orchestrator.py`

**Responsibilities:**
- Coordinate all modules (STT, LLM, TTS)
- Manage complete workflow: STT → Intent → LLM → TTS
- Handle language coordination
- Manage context
- Track metrics
- Handle errors with circuit breakers

**Key Methods:**

#### `process_turn(audio_data, language, system_prompt)`
- Process complete conversation turn
- Returns dictionary with:
  - `text`: Transcribed text
  - `response`: LLM response
  - `audio`: TTS audio (WAV format)
  - `language`: Language used
  - `metrics`: Timing information
  - `error`: Error message if failed

**Workflow:**
1. STT: Transcribe audio
2. Language coordination (auto-switch if needed)
3. Context retrieval
4. LLM: Generate response
5. Context update
6. TTS: Synthesize audio
7. Metrics recording

#### `set_language(language_code)`
- Set processing language
- Updates system prompt for language

#### `set_system_prompt(prompt)`
- Set or update system prompt

#### `get_status()`
- Get current orchestrator status
- Returns dictionary with:
  - `is_processing`: Whether currently processing
  - `processing_state`: Current state (idle, stt, llm, tts, error)
  - `current_language`: Current processing language
  - `turn_count`: Number of turns processed
  - `language_switching`: Language switching status
  - `circuit_breakers`: Circuit breaker states

**Example:**
```python
orchestrator = AgentOrchestrator(
    stt_module=sarvam,
    llm_module=sarvam,
    tts_module=sarvam,
    default_language="te-IN"
)

result = await orchestrator.process_turn(audio_wav_data)
# result = {
#     "text": "Hello",
#     "response": "Hi there!",
#     "audio": b"WAV audio...",
#     "language": "te-IN",
#     "metrics": {...}
# }
```

---

### 6. Metrics Collector (`MetricsCollector`)

**File:** `orchestrator/metrics.py`

**Responsibilities:**
- Track latency metrics for each turn
- Calculate averages
- Generate performance reports
- Track success rates
- Group statistics by language

**Key Methods:**

#### `record_turn(stt_time, llm_time, tts_time, language, success, error_type)`
- Record metrics for a conversation turn
- Stores: STT latency, LLM latency, TTS latency, total latency
- Tracks success/failure and error types

#### `get_average_latencies()`
- Get average latencies across all turns
- Returns: `{"stt": 1.2, "llm": 0.8, "tts": 1.0, "total": 3.0}`

#### `get_language_statistics()`
- Get statistics grouped by language
- Returns per-language averages and counts

#### `get_success_rate()`
- Get success rate (percentage of successful turns)
- Returns float between 0.0 and 1.0

#### `generate_report()`
- Generate formatted performance report
- Returns formatted string with all statistics

**Example:**
```python
metrics = MetricsCollector()
orchestrator = AgentOrchestrator(..., metrics_collector=metrics)

# After processing turns
averages = metrics.get_average_latencies()
report = metrics.generate_report()
print(report)
```

---

### 7. Circuit Breaker (`CircuitBreaker`)

**File:** `orchestrator/circuit_breaker.py`

**Responsibilities:**
- Protect against cascading failures
- Open circuit after failure threshold
- Close circuit after timeout
- Half-open state for testing recovery

**Key Methods:**

#### `call(func, *args, **kwargs)`
- Call function with circuit breaker protection
- Raises `CircuitBreakerOpen` if circuit is open
- Tracks failures and successes

#### `get_state()`
- Get current circuit breaker state
- Returns dictionary with:
  - `state`: "closed", "open", or "half_open"
  - `failure_count`: Current failure count
  - `failure_threshold`: Threshold to open circuit
  - `timeout`: Timeout before retry
  - `time_until_retry`: Seconds until retry allowed

#### `reset()`
- Manually reset circuit breaker to closed state

**States:**
- **Closed**: Normal operation, failures tracked
- **Open**: Circuit open, calls rejected (after threshold reached)
- **Half-Open**: Testing recovery (after timeout), needs 2 successes to close

**Example:**
```python
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

try:
    result = await breaker.call(some_async_function, arg1, arg2)
except CircuitBreakerOpen:
    # Circuit is open, handle gracefully
    pass
```

---

## Communication Flow

```
User Audio
    ↓
[STT Listener] → Text + Detected Language
    ↓
[Language Selector] → Processing Language (may switch)
    ↓
[Context Handler] → Conversation Context
    ↓
[Response Router] → LLM → Response Text
    ↓
[Context Handler] → Update History
    ↓
[Response Router] → TTS → Audio
    ↓
User Hears Response
```

## Error Handling Flow

```
Error Occurs
    ↓
[Task Router] → Retry (2 attempts)
    ↓
Still Failing?
    ↓
[Circuit Breaker] → Track Failure
    ↓
Threshold Reached?
    ↓
[Circuit Breaker] → Open Circuit
    ↓
[Orchestrator] → Graceful Degradation
    ↓
Return Error in Result
```

---

## Summary

Each component has clear, well-defined responsibilities:

1. **STT Listener**: Handles audio transcription with retries
2. **Context Handler**: Manages conversation history
3. **Language Selector**: Coordinates multilingual workflows
4. **Response Router**: Routes to LLM and TTS
5. **Orchestrator**: Coordinates all components
6. **Metrics Collector**: Tracks performance
7. **Circuit Breaker**: Protects against failures

All components work together to provide a robust, scalable voice agent system.
