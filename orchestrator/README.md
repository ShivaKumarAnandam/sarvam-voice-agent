# Agent Orchestrator Module

## Overview

The Agent Orchestrator is a central controller that manages interactions between STT (Speech-to-Text), LLM (Language Model), and TTS (Text-to-Speech) modules. It coordinates task routing, context management, and multilingual workflows.

## Structure

```
orchestrator/
├── __init__.py                 # Module exports
├── agent_orchestrator.py       # Main orchestrator class
├── context_manager.py          # Conversation context management
├── language_coordinator.py     # Language coordination
└── task_router.py              # Task routing between modules
```

## Components

### 1. AgentOrchestrator
Main orchestrator class that coordinates all components.

**Usage:**
```python
from orchestrator import AgentOrchestrator

# Initialize with STT, LLM, TTS modules
orchestrator = AgentOrchestrator(sarvam, sarvam, sarvam, max_history=10)

# Set language
orchestrator.set_language("te-IN")

# Set system prompt
orchestrator.set_system_prompt("You are a helpful assistant...")

# Process a conversation turn
result = await orchestrator.process_turn(audio_data, language="te-IN")
```

### 2. ContextManager
Manages conversation history with sliding window.

**Features:**
- Maintains conversation history
- Sliding window to keep last N turns
- Tracks language per turn
- Stores user metadata

### 3. LanguageCoordinator
Ensures language consistency across STT → LLM → TTS.

**Features:**
- Tracks selected language (from IVR)
- Tracks detected language (from STT)
- Ensures consistency across pipeline
- Language name mapping

### 4. TaskRouter
Routes tasks between modules with error handling.

**Features:**
- Routes transcription (STT)
- Routes generation (LLM)
- Routes synthesis (TTS)
- Retry logic for failures

## Integration

The orchestrator is integrated into `twilio_server.py` in the `media_stream()` function. It replaces the embedded orchestration logic while maintaining all existing functionality:

- ✅ Voice Activity Detection (VAD)
- ✅ Audio buffering
- ✅ Transfer keyword detection
- ✅ Error handling
- ✅ Analytics tracking

## Benefits

1. **Separation of Concerns**: Orchestration logic separated from business logic
2. **Reusability**: Can be used across different projects
3. **Testability**: Each component can be tested independently
4. **Maintainability**: Easier to update and extend
5. **Consistency**: Same orchestration pattern across all voice agents

## Status

✅ **Implemented and Integrated**
- All components created
- Integrated into twilio_server.py
- Maintains backward compatibility
- No breaking changes

---

For detailed design, see `docs/AGENT_ORCHESTRATOR_DESIGN.md` and `docs/ORCHESTRATOR_IMPLEMENTATION_GUIDE.md`.

