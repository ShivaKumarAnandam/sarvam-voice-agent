# Agent Orchestrator

Central controller for managing STT, LLM, and TTS interactions in voice agent systems.

## Overview

The Agent Orchestrator provides a clean, modular architecture for coordinating speech-to-text, language model, and text-to-speech operations. It handles:

- **Task Routing**: Routes audio/text between STT, LLM, and TTS modules
- **Context Management**: Maintains conversation history with sliding window
- **Language Coordination**: Handles multilingual workflows and auto-switching
- **Error Handling**: Circuit breakers, retries, and graceful degradation
- **Performance Metrics**: Tracks latency and success rates

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Agent Orchestrator                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Task Router  │  │ Context      │  │ Language     │   │
│  │              │  │ Manager      │  │ Coordinator  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
    ┌────▼────┐          ┌────▼────┐         ┌────▼────┐
    │   STT   │          │   LLM   │         │   TTS   │
    │ Module  │          │ Module  │         │ Module  │
    └─────────┘          └─────────┘         └─────────┘
```

## Quick Start

### Basic Usage

```python
from orchestrator import AgentOrchestrator
from sarvam_ai import SarvamAI

# Initialize modules
sarvam = SarvamAI()

# Create orchestrator
orchestrator = AgentOrchestrator(
    stt_module=sarvam,
    llm_module=sarvam,
    tts_module=sarvam,
    default_language="te-IN"
)

# Process a conversation turn
result = await orchestrator.process_turn(audio_wav_data)

# Result contains:
# - text: Transcribed text
# - response: LLM response
# - audio: TTS audio (WAV format)
# - language: Language used
# - metrics: Timing information
```

### With Metrics

```python
from orchestrator import AgentOrchestrator, MetricsCollector

metrics = MetricsCollector()
orchestrator = AgentOrchestrator(
    stt_module=sarvam,
    llm_module=sarvam,
    tts_module=sarvam,
    metrics_collector=metrics
)

# After processing turns
averages = metrics.get_average_latencies()
print(f"Average STT: {averages['stt']:.2f}s")
print(f"Average LLM: {averages['llm']:.2f}s")
print(f"Average TTS: {averages['tts']:.2f}s")
```

## Components

### AgentOrchestrator

Main orchestrator class that coordinates all operations.

**Key Methods:**
- `process_turn(audio_data, language, system_prompt)` - Process complete turn
- `set_language(language_code)` - Set processing language
- `set_system_prompt(prompt)` - Set system prompt
- `get_status()` - Get current status
- `clear_history()` - Clear conversation history

### TaskRouter

Routes tasks between STT, LLM, and TTS modules with retry logic.

**Key Methods:**
- `route_transcription(audio_data, language)` - Route to STT
- `route_generation(text, context, language)` - Route to LLM
- `route_synthesis(text, language)` - Route to TTS

### ContextManager

Manages conversation history and context.

**Key Methods:**
- `add_turn(user_input, assistant_response, language)` - Add turn
- `get_context(system_prompt)` - Get formatted context
- `clear_history()` - Clear history
- `get_turn_count()` - Get number of turns

### LanguageCoordinator

Handles multilingual workflows and auto-switching.

**Key Methods:**
- `set_language(language_code)` - Set selected language
- `set_detected_language(language_code)` - Set detected language
- `ensure_consistency()` - Get processing language
- `get_switch_status()` - Get switching status

### MetricsCollector

Tracks performance metrics.

**Key Methods:**
- `record_turn(stt_time, llm_time, tts_time, language)` - Record metrics
- `get_average_latencies()` - Get averages
- `get_language_statistics()` - Get per-language stats
- `generate_report()` - Generate formatted report

### CircuitBreaker

Protects against cascading failures.

**Key Methods:**
- `call(func, *args, **kwargs)` - Call function with protection
- `get_state()` - Get current state
- `reset()` - Reset to closed state

## Workflow

The orchestrator follows this workflow:

1. **STT**: Transcribe audio to text
2. **Language Detection**: Detect/confirm language
3. **Language Coordination**: Auto-switch if needed
4. **Context Retrieval**: Get conversation history
5. **LLM**: Generate response with context
6. **Context Update**: Store turn in history
7. **TTS**: Synthesize audio from response
8. **Metrics**: Record timing information

## Language Support

Supported languages:
- `te-IN` - Telugu
- `hi-IN` - Hindi
- `en-IN` - English
- `gu-IN` - Gujarati

### Auto-Switching

The orchestrator can automatically switch languages if:
- Different language is detected 2+ times consecutively
- Minimum 1 turn has been processed

## Error Handling

### Retry Logic
- STT: 2 retry attempts with 0.5s delay
- TTS: 2 retry attempts with 0.5s delay
- LLM: 2 retry attempts with 0.5s delay

### Circuit Breaker
- Opens after 5 consecutive failures
- Closes after 60 seconds timeout
- Half-open state for testing recovery

### Graceful Degradation
- If TTS fails, returns text response
- If STT fails, returns error with context
- If LLM fails, returns error with transcribed text

## Testing

Run tests:

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests
pytest tests/
```

## Integration

See `examples/orchestrator_integration_example.py` for integration examples with Twilio WebSocket.

## Documentation

- [Complete Implementation Guide](../docs/AGENT_ORCHESTRATOR_COMPLETE_IMPLEMENTATION.md)
- [Design Document](../docs/AGENT_ORCHESTRATOR_DESIGN.md)

## License

Part of the Sarvam Voice Agent project.
