# Agent Orchestrator Design

## Overview

The Agent Orchestrator is a central controller that manages interactions between STT (Speech-to-Text), LLM (Language Model), and TTS (Text-to-Speech) modules. It coordinates task routing, context management, and multilingual workflows to ensure efficient, real-time responses in voice agent systems.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Task Router  │  │ Context      │  │ Language     │           │
│  │              │  │ Manager      │  │ Coordinator  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         │                    │                    │
    ┌────▼────┐          ┌────▼────┐         ┌────▼────┐
    │   STT   │          │   LLM   │         │   TTS   │
    │ Module  │          │ Module  │         │ Module  │
    └─────────┘          └─────────┘         └─────────┘
```

## Core Components

### 1. Task Router
- **Purpose**: Routes tasks between STT, LLM, and TTS modules
- **Responsibilities**:
  - Determine execution order
  - Handle task dependencies
  - Manage retry logic
  - Route based on task type (transcription, generation, synthesis)

### 2. Context Manager
- **Purpose**: Maintains conversation history and context
- **Responsibilities**:
  - Store conversation history
  - Manage context window (sliding window)
  - Track language preferences
  - Store user metadata (session info, preferences)

### 3. Language Coordinator
- **Purpose**: Handles multilingual workflows
- **Responsibilities**:
  - Detect/select language
  - Ensure language consistency across STT → LLM → TTS
  - Route to language-specific models
  - Handle language switching

## Implementation Strategy

### Based on Existing Projects

#### From `Voice Agent` project:
- Simple orchestration pattern: `VoiceAgent` class
- Direct method calls: `listen()` → `think()` → `speak()`
- Conversation history management

#### From `Indic` project:
- `VoiceAgentController` with proper error handling
- Component initialization management
- Status tracking

#### From `Sarvam_Voice_Agent-main`:
- Async/await pattern for real-time processing
- Voice Activity Detection (VAD)
- Audio buffering and streaming
- Language selection via IVR

#### From `AgentJyothi`:
- Hardcoded Q&A routing
- Retry logic
- Conversation history with context window

## Proposed Orchestrator Class

```python
class AgentOrchestrator:
    """
    Central controller for managing STT, LLM, and TTS interactions
    """
    
    def __init__(self, config):
        # Initialize components
        self.stt = STTModule(...)
        self.llm = LLMModule(...)
        self.tts = TTSModule(...)
        
        # Core orchestrator components
        self.task_router = TaskRouter()
        self.context_manager = ContextManager()
        self.language_coordinator = LanguageCoordinator()
        
        # State management
        self.current_session = None
        self.processing_state = "idle"  # idle, listening, processing, speaking
```

## Key Features

### 1. Task Routing

```python
class TaskRouter:
    """Routes tasks between modules"""
    
    def route_transcription(self, audio_data, language=None):
        """Route audio to STT module"""
        return self.stt.transcribe(audio_data, language)
    
    def route_generation(self, text, context, language):
        """Route text to LLM with context"""
        return self.llm.generate(text, context, language)
    
    def route_synthesis(self, text, language):
        """Route text to TTS module"""
        return self.tts.synthesize(text, language)
```

### 2. Context Management

```python
class ContextManager:
    """Manages conversation context"""
    
    def __init__(self, max_history=10):
        self.conversation_history = []
        self.max_history = max_history
        self.user_metadata = {}
        self.session_context = {}
    
    def add_turn(self, user_input, assistant_response, language):
        """Add conversation turn"""
        self.conversation_history.append({
            "user": user_input,
            "assistant": assistant_response,
            "language": language,
            "timestamp": datetime.now()
        })
        # Maintain sliding window
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_context(self, include_metadata=True):
        """Get current context for LLM"""
        context = {
            "history": self.conversation_history,
            "language": self.current_language
        }
        if include_metadata:
            context["metadata"] = self.user_metadata
        return context
```

### 3. Language Coordination

```python
class LanguageCoordinator:
    """Coordinates language across modules"""
    
    def __init__(self):
        self.selected_language = None
        self.detected_language = None
        self.language_consistency = True
    
    def set_language(self, language_code):
        """Set selected language (from IVR/user choice)"""
        self.selected_language = language_code
    
    def detect_language(self, audio_data):
        """Detect language from audio"""
        # Use STT language detection
        self.detected_language = self.stt.detect_language(audio_data)
        return self.detected_language
    
    def get_language_for_processing(self):
        """Get language to use (selected > detected > default)"""
        return self.selected_language or self.detected_language or "te-IN"
    
    def ensure_consistency(self):
        """Ensure language consistency across pipeline"""
        language = self.get_language_for_processing()
        # Force all modules to use same language
        return language
```

## Workflow Patterns

### Pattern 1: Standard Conversation Turn

```
1. User speaks → Audio captured
2. Task Router → Route to STT
3. STT → Transcribe audio (with language)
4. Language Coordinator → Ensure language consistency
5. Context Manager → Add user input to history
6. Task Router → Route to LLM
7. LLM → Generate response (with context)
8. Context Manager → Add assistant response to history
9. Task Router → Route to TTS
10. TTS → Synthesize audio (in same language)
11. Audio → Playback to user
```

### Pattern 2: Multilingual Workflow

```
1. Language Selection (IVR/User choice)
   → Language Coordinator.set_language("te-IN")
   
2. STT Processing
   → Use selected language: "te-IN"
   → Transcribe in Telugu
   
3. LLM Processing
   → System prompt: "Respond ONLY in Telugu"
   → Generate Telugu response
   
4. TTS Processing
   → Use Telugu TTS model
   → Synthesize in Telugu
   
5. Consistency Check
   → Verify all modules used same language
```

### Pattern 3: Error Handling & Retry

```
1. STT fails → Retry with different language
2. LLM fails → Retry with simplified prompt
3. TTS fails → Fallback to alternative TTS
4. Context Manager → Track failures
5. Task Router → Route to fallback handler
```

## Integration with Existing Code

### For Sarvam_Voice_Agent-main

Current implementation in `twilio_server.py` has orchestration logic embedded in `media_stream()` function. We can extract this into an orchestrator:

```python
# Current (embedded in media_stream):
async def process_speech_buffer():
    # STT
    text, detected_lang = await sarvam.speech_to_text(wav_data, language=selected_language)
    # LLM
    response = await sarvam.chat(messages)
    # TTS
    tts_wav = await sarvam.text_to_speech(response, selected_language)

# Proposed (with orchestrator):
orchestrator = AgentOrchestrator(config)
result = await orchestrator.process_turn(audio_data, language=selected_language)
```

### For Voice Agent project

Current `VoiceAgent` class is already a simple orchestrator. We can enhance it:

```python
# Current:
class VoiceAgent:
    def conversation_loop(self):
        text = self.listen()
        response = self.think(text)
        self.speak(response)

# Enhanced:
class VoiceAgent:
    def __init__(self):
        self.orchestrator = AgentOrchestrator(config)
    
    def conversation_loop(self):
        result = self.orchestrator.process_turn()
```

## Implementation Plan

### Phase 1: Core Orchestrator
1. Create `AgentOrchestrator` base class
2. Implement `TaskRouter`
3. Implement `ContextManager`
4. Implement `LanguageCoordinator`

### Phase 2: Integration
1. Integrate with `Sarvam_Voice_Agent-main`
2. Extract orchestration logic from `media_stream()`
3. Add orchestrator to `twilio_server.py`

### Phase 3: Advanced Features
1. Add task queuing
2. Add parallel processing support
3. Add analytics and monitoring
4. Add A/B testing support

## File Structure

```
Sarvam_Voice_Agent-main/
├── orchestrator/
│   ├── __init__.py
│   ├── agent_orchestrator.py    # Main orchestrator class
│   ├── task_router.py            # Task routing logic
│   ├── context_manager.py        # Context management
│   ├── language_coordinator.py   # Language coordination
│   └── config.py                 # Orchestrator configuration
├── twilio_server.py              # Updated to use orchestrator
└── docs/
    └── AGENT_ORCHESTRATOR_DESIGN.md  # This file
```

## Benefits

1. **Separation of Concerns**: Orchestration logic separated from business logic
2. **Reusability**: Orchestrator can be used across different projects
3. **Testability**: Each component can be tested independently
4. **Maintainability**: Easier to update and extend
5. **Consistency**: Same orchestration pattern across all voice agents
6. **Monitoring**: Centralized logging and analytics

## Next Steps

1. Review this design document
2. Create implementation plan
3. Start with Phase 1: Core Orchestrator
4. Test with existing `Sarvam_Voice_Agent-main`
5. Extend to other projects

---

**Status**: Design Document - Ready for Implementation Review

