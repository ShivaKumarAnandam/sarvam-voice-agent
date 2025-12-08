# Orchestrator Quick Start Guide

## Overview

This guide shows you how to integrate the Agent Orchestrator into your existing `twilio_server.py` without disturbing the current implementation.

## Architecture Flow

```
User Speaks → Twilio WebSocket → Audio Buffer → Orchestrator.process_turn()
    ↓
STT (Speech-to-Text) → Text
    ↓
Language Detection → Language Coordinator
    ↓
LLM (Language Model) → Response Text
    ↓
TTS (Text-to-Speech) → Audio
    ↓
Twilio WebSocket → User Hears Response
```

## Integration Steps

### Step 1: Import Orchestrator

Add to your `twilio_server.py`:

```python
from orchestrator import AgentOrchestrator, MetricsCollector
```

### Step 2: Initialize Orchestrator

In your `media_stream` WebSocket handler, replace the inline orchestration:

**Before (inline logic):**
```python
# STT
text, detected_lang = await sarvam.speech_to_text(wav_data, language=selected_language)
# LLM
response = await sarvam.chat(messages)
# TTS
tts_wav = await sarvam.text_to_speech(response, selected_language)
```

**After (with orchestrator):**
```python
# Initialize orchestrator
metrics_collector = MetricsCollector()
orchestrator = AgentOrchestrator(
    stt_module=sarvam,
    llm_module=sarvam,
    tts_module=sarvam,
    max_history=10,
    default_language=selected_language,
    system_prompt=your_system_prompt,
    metrics_collector=metrics_collector,
    enable_circuit_breaker=True
)

# Set language
orchestrator.set_language(selected_language)
```

### Step 3: Use Orchestrator in process_speech_buffer

Replace your `process_speech_buffer()` function:

```python
async def process_speech_buffer():
    """Process accumulated speech buffer using orchestrator"""
    nonlocal is_speaking, audio_buffer, silence_buffer
    
    if len(audio_buffer) < min_speech_length:
        return
    
    # Convert to WAV
    mulaw_bytes = bytes(audio_buffer)
    wav_data = mulaw_to_wav(mulaw_bytes)
    
    # Reset buffers
    audio_buffer.clear()
    silence_buffer.clear()
    is_speaking = False
    
    if not wav_data:
        return
    
    # Use orchestrator to process turn
    result = await orchestrator.process_turn(wav_data)
    
    if result.get("error"):
        logger.error(f"❌ Error: {result['error']}")
        return
    
    if not result.get("audio"):
        return
    
    # Convert WAV to mulaw and stream
    response_mulaw = wav_to_mulaw(result["audio"])
    
    # Stream audio chunks (your existing streaming logic)
    # ...
```

### Step 4: Handle Results

The orchestrator returns a dictionary:

```python
result = {
    "text": "Transcribed text",
    "response": "LLM response",
    "audio": b"WAV audio data",
    "language": "te-IN",
    "metrics": {
        "stt_time": 1.2,
        "llm_time": 0.8,
        "tts_time": 1.0,
        "total_time": 3.0
    }
}
```

## Benefits

### 1. Cleaner Code
- Separates orchestration logic from business logic
- Easier to read and maintain

### 2. Better Error Handling
- Automatic retries
- Circuit breakers
- Graceful degradation

### 3. Performance Monitoring
- Built-in metrics collection
- Latency tracking
- Success rate monitoring

### 4. Language Management
- Automatic language switching
- Language consistency across pipeline
- Multi-language support

### 5. Context Management
- Automatic conversation history
- Sliding window management
- System prompt handling

## Example: Complete Integration

See `examples/orchestrator_integration_example.py` for a complete example.

## Monitoring

### Get Status

```python
status = orchestrator.get_status()
# Returns:
# {
#     "is_processing": False,
#     "processing_state": "idle",
#     "current_language": "te-IN",
#     "turn_count": 5,
#     "language_switching": {...},
#     "circuit_breakers": {...}
# }
```

### Get Metrics

```python
averages = metrics_collector.get_average_latencies()
# Returns:
# {
#     "stt": 1.2,
#     "llm": 0.8,
#     "tts": 1.0,
#     "total": 3.0
# }

report = metrics_collector.generate_report()
print(report)
```

## Troubleshooting

### Issue: Orchestrator not processing

**Solution:** Check if `is_processing` flag is set. The orchestrator prevents concurrent processing.

### Issue: Language not switching

**Solution:** Check `language_switching` status. Auto-switch requires 2+ consecutive detections.

### Issue: Circuit breaker open

**Solution:** Check circuit breaker state. It opens after 5 failures and closes after 60 seconds.

### Issue: Empty responses

**Solution:** Check logs for STT/LLM/TTS errors. The orchestrator logs all failures.

## Next Steps

1. Review `orchestrator/README.md` for detailed API documentation
2. Check `docs/AGENT_ORCHESTRATOR_COMPLETE_IMPLEMENTATION.md` for full implementation details
3. Run tests: `pytest tests/`
4. Monitor metrics: `metrics_collector.generate_report()`

## Support

For issues or questions, refer to:
- `docs/AGENT_ORCHESTRATOR_DESIGN.md` - Design documentation
- `docs/TROUBLESHOOTING.md` - Troubleshooting guide
- `examples/orchestrator_integration_example.py` - Integration examples
