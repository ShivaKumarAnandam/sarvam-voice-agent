# How to Implement Agent Orchestrator Using Existing Projects

## Overview

This guide explains how to build an Agent Orchestrator by leveraging components and patterns from your existing projects in the `Shiva` folder.

## Available Projects Analysis

### 1. **Voice Agent** (`Shiva/Voice Agent/`)
**What it provides:**
- Simple orchestration pattern (`voice_agent.py`)
- Modular STT, LLM, TTS components
- Conversation history management
- Basic error handling

**Key Files:**
- `voice_agent.py` - Main orchestrator class
- `stt_module.py` - STT implementation
- `llm_module.py` - LLM implementation  
- `tts_module.py` - TTS implementation

**What to extract:**
```python
# Pattern: Simple orchestration
class VoiceAgent:
    def __init__(self):
        self.stt = STTModule()
        self.llm = LLMModule()
        self.tts = TTSModule()
        self.conversation_history = []
    
    def conversation_loop(self):
        text = self.listen()      # STT
        response = self.think(text)  # LLM
        self.speak(response)       # TTS
```

### 2. **Indic Voice Agent** (`Shiva/Indic/`)
**What it provides:**
- Professional controller pattern (`src/controller.py`)
- Component initialization management
- Status tracking
- Error handling with custom exceptions
- Configuration management

**Key Files:**
- `src/controller.py` - `VoiceAgentController` class
- `src/config.py` - Configuration management
- `src/stt_engine.py`, `src/llm_engine.py`, `src/tts_engine.py`

**What to extract:**
```python
# Pattern: Professional controller with error handling
class VoiceAgentController:
    def __init__(self, config):
        self.config = config
        self._initialize_components()
    
    def start_conversation_turn(self):
        # Step 1: Capture audio
        # Step 2: Transcribe
        # Step 3: Generate response
        # Step 4: Synthesize
        # With proper error handling at each step
```

### 3. **Sarvam Voice Agent** (`Shiva/Sarvam_Voice_Agent-main/`)
**What it provides:**
- Async/await pattern for real-time processing
- Voice Activity Detection (VAD)
- Audio streaming and buffering
- Language selection via IVR
- Conversation context with language-specific prompts

**Key Files:**
- `twilio_server.py` - WebSocket-based real-time processing
- `sarvam_ai.py` - Unified STT/LLM/TTS client
- `audio_utils.py` - Audio format conversion

**What to extract:**
```python
# Pattern: Async orchestration with VAD
async def process_speech_buffer():
    # STT with language
    text, lang = await sarvam.speech_to_text(wav_data, language)
    # LLM with context
    response = await sarvam.chat(messages)
    # TTS with language
    tts_wav = await sarvam.text_to_speech(response, language)
```

### 4. **AgentJyothi** (`Shiva/AgentJyothi/`)
**What it provides:**
- Hardcoded Q&A routing
- Retry logic
- Conversation history with context window
- Language-specific system prompts

**Key Files:**
- `tgspdcl_agent.py` - `TGSPDCLVoiceAgent` class

**What to extract:**
```python
# Pattern: Task routing with fallbacks
def get_and_speak_response(self, user_text):
    # Check hardcoded Q&A first
    answer = find_hardcoded_answer(user_text)
    if answer:
        return answer
    # Fallback to LLM
    return self.get_llm_response(user_text)
```

## Implementation Strategy

### Step 1: Create Base Orchestrator Structure

Create a new `orchestrator` module in `Sarvam_Voice_Agent-main`:

```python
# orchestrator/agent_orchestrator.py
from typing import Optional, Dict, List
import asyncio
from loguru import logger

class AgentOrchestrator:
    """Central controller for STT, LLM, TTS coordination"""
    
    def __init__(self, stt_module, llm_module, tts_module):
        # Components (from existing projects)
        self.stt = stt_module
        self.llm = llm_module
        self.tts = tts_module
        
        # Orchestrator components
        self.context_manager = ContextManager()
        self.language_coordinator = LanguageCoordinator()
        self.task_router = TaskRouter(self.stt, self.llm, self.tts)
```

### Step 2: Extract Context Management

**From `Voice Agent/voice_agent.py`:**
```python
# Simple history management
self.conversation_history = []
self.conversation_history.append({"role": "user", "content": text})
if len(self.conversation_history) > 20:
    self.conversation_history = self.conversation_history[-20:]
```

**From `Sarvam_Voice_Agent-main/twilio_server.py`:**
```python
# Language-specific context
messages = [{
    "role": "system",
    "content": f"Respond ONLY in {selected_lang_name}"
}]
messages.append({"role": "user", "content": text})
```

**Combine into:**
```python
class ContextManager:
    def __init__(self, max_history=10):
        self.conversation_history = []
        self.max_history = max_history
    
    def add_turn(self, user_input, assistant_response, language):
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "language": language
        })
        self.conversation_history.append({
            "role": "assistant", 
            "content": assistant_response,
            "language": language
        })
        # Maintain sliding window
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
```

### Step 3: Extract Language Coordination

**From `Sarvam_Voice_Agent-main/twilio_server.py`:**
```python
# Language selection and consistency
selected_language = query_params.get("lang", "te-IN")
language_names = {"te-IN": "Telugu", "hi-IN": "Hindi", "en-IN": "English"}
selected_lang_name = language_names.get(selected_language, "Telugu")
```

**Combine with language detection from STT:**
```python
class LanguageCoordinator:
    def __init__(self):
        self.selected_language = None  # From IVR/user choice
        self.detected_language = None   # From STT
    
    def set_language(self, language_code):
        """Set language from IVR selection"""
        self.selected_language = language_code
    
    def get_processing_language(self):
        """Priority: selected > detected > default"""
        return self.selected_language or self.detected_language or "te-IN"
    
    def ensure_consistency(self, stt_lang, llm_lang, tts_lang):
        """Ensure all modules use same language"""
        target_lang = self.get_processing_language()
        return target_lang
```

### Step 4: Extract Task Routing

**From `Indic/src/controller.py`:**
```python
# Step-by-step routing with error handling
def start_conversation_turn(self):
    # Step 1: Capture audio
    audio_data = self.vdm.stop_recording()
    # Step 2: Transcribe
    text, language_code = self.stt_engine.transcribe(audio_data)
    # Step 3: Generate response
    response_text = self.llm_engine.generate_response(text, language_code)
    # Step 4: Synthesize
    audio_output = self.tts_engine.synthesize(response_text, language_code)
```

**From `AgentJyothi/tgspdcl_agent.py`:**
```python
# Routing with fallbacks
def get_and_speak_response(self, user_text):
    # Try hardcoded Q&A first
    answer = find_hardcoded_answer(user_text)
    if answer:
        return answer
    # Fallback to LLM
    return self.get_llm_response(user_text)
```

**Combine into:**
```python
class TaskRouter:
    def __init__(self, stt, llm, tts):
        self.stt = stt
        self.llm = llm
        self.tts = tts
    
    async def route_transcription(self, audio_data, language):
        """Route to STT with retry logic"""
        try:
            return await self.stt.transcribe(audio_data, language)
        except Exception as e:
            logger.error(f"STT failed: {e}")
            # Retry with different language or fallback
            return await self._retry_stt(audio_data)
    
    async def route_generation(self, text, context, language):
        """Route to LLM with context"""
        return await self.llm.generate(text, context, language)
    
    async def route_synthesis(self, text, language):
        """Route to TTS"""
        return await self.tts.synthesize(text, language)
```

### Step 5: Integrate Async Pattern

**From `Sarvam_Voice_Agent-main/twilio_server.py`:**
```python
# Async processing pattern
async def process_speech_buffer():
    # Prevent concurrent processing
    if is_processing:
        return
    
    is_processing = True
    try:
        # STT
        text, lang = await sarvam.speech_to_text(wav_data, language)
        # LLM
        response = await sarvam.chat(messages)
        # TTS
        tts_wav = await sarvam.text_to_speech(response, language)
    finally:
        is_processing = False
```

**Use in orchestrator:**
```python
class AgentOrchestrator:
    async def process_turn(self, audio_data, language=None):
        """Process one conversation turn"""
        # Lock processing
        if self.is_processing:
            return None
        
        self.is_processing = True
        try:
            # 1. STT
            text, detected_lang = await self.task_router.route_transcription(
                audio_data, language
            )
            
            # 2. Language coordination
            processing_lang = self.language_coordinator.get_processing_language()
            
            # 3. Context management
            context = self.context_manager.get_context()
            
            # 4. LLM
            response = await self.task_router.route_generation(
                text, context, processing_lang
            )
            
            # 5. Update context
            self.context_manager.add_turn(text, response, processing_lang)
            
            # 6. TTS
            audio_output = await self.task_router.route_synthesis(
                response, processing_lang
            )
            
            return {
                "text": text,
                "response": response,
                "audio": audio_output,
                "language": processing_lang
            }
        finally:
            self.is_processing = False
```

## Complete Implementation Example

### File: `orchestrator/agent_orchestrator.py`

```python
"""
Agent Orchestrator - Central controller for STT, LLM, TTS coordination
Combines patterns from Voice Agent, Indic, Sarvam, and AgentJyothi projects
"""

import asyncio
from typing import Optional, Dict, List
from loguru import logger

class ContextManager:
    """Manages conversation context (from Voice Agent + Sarvam patterns)"""
    def __init__(self, max_history=10):
        self.conversation_history = []
        self.max_history = max_history
    
    def add_turn(self, user_input, assistant_response, language):
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "language": language
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_response,
            "language": language
        })
        # Maintain sliding window (from Voice Agent)
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def get_context(self, system_prompt=None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.conversation_history)
        return messages

class LanguageCoordinator:
    """Coordinates language across modules (from Sarvam pattern)"""
    def __init__(self):
        self.selected_language = None
        self.detected_language = None
    
    def set_language(self, language_code):
        self.selected_language = language_code
    
    def get_processing_language(self):
        return self.selected_language or self.detected_language or "te-IN"

class TaskRouter:
    """Routes tasks between modules (from Indic + AgentJyothi patterns)"""
    def __init__(self, stt, llm, tts):
        self.stt = stt
        self.llm = llm
        self.tts = tts
    
    async def route_transcription(self, audio_data, language):
        return await self.stt.transcribe(audio_data, language)
    
    async def route_generation(self, text, context, language):
        return await self.llm.generate(text, context, language)
    
    async def route_synthesis(self, text, language):
        return await self.tts.synthesize(text, language)

class AgentOrchestrator:
    """Main orchestrator (combines all patterns)"""
    def __init__(self, stt_module, llm_module, tts_module):
        self.stt = stt_module
        self.llm = llm_module
        self.tts = tts_module
        
        self.context_manager = ContextManager()
        self.language_coordinator = LanguageCoordinator()
        self.task_router = TaskRouter(stt_module, llm_module, tts_module)
        
        self.is_processing = False
    
    async def process_turn(self, audio_data, language=None, system_prompt=None):
        """Process one conversation turn"""
        if self.is_processing:
            logger.warning("Already processing, skipping")
            return None
        
        self.is_processing = True
        try:
            # 1. STT
            text, detected_lang = await self.task_router.route_transcription(
                audio_data, language
            )
            self.language_coordinator.detected_language = detected_lang
            
            # 2. Get processing language
            processing_lang = self.language_coordinator.get_processing_language()
            
            # 3. Get context
            context = self.context_manager.get_context(system_prompt)
            
            # 4. LLM
            response = await self.task_router.route_generation(
                text, context, processing_lang
            )
            
            # 5. Update context
            self.context_manager.add_turn(text, response, processing_lang)
            
            # 6. TTS
            audio_output = await self.task_router.route_synthesis(
                response, processing_lang
            )
            
            return {
                "text": text,
                "response": response,
                "audio": audio_output,
                "language": processing_lang
            }
        finally:
            self.is_processing = False
```

## Integration with Existing Code

### Update `twilio_server.py`

Replace the embedded orchestration in `media_stream()`:

```python
# Before (embedded):
async def process_speech_buffer():
    text, lang = await sarvam.speech_to_text(wav_data, language)
    response = await sarvam.chat(messages)
    tts_wav = await sarvam.text_to_speech(response, language)

# After (with orchestrator):
from orchestrator import AgentOrchestrator

# Initialize orchestrator
orchestrator = AgentOrchestrator(sarvam, sarvam, sarvam)

async def process_speech_buffer():
    result = await orchestrator.process_turn(
        wav_data,
        language=selected_language,
        system_prompt=system_prompt
    )
    return result["audio"]
```

## Benefits of This Approach

1. **Reuses Existing Patterns**: Leverages proven patterns from your projects
2. **Incremental Migration**: Can be integrated gradually
3. **Maintains Compatibility**: Works with existing code
4. **Testable**: Each component can be tested independently
5. **Extensible**: Easy to add new features

## Next Steps

1. ✅ Review design document
2. ✅ Create orchestrator module structure
3. ⏳ Implement core orchestrator classes
4. ⏳ Integrate with `Sarvam_Voice_Agent-main`
5. ⏳ Test with existing workflows
6. ⏳ Extend to other projects

---

**Ready to implement?** Start with creating the `orchestrator/` directory and implementing the base classes!

