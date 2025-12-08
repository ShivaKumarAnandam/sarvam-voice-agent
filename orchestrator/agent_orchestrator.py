"""
Agent Orchestrator - Central controller for STT, LLM, TTS coordination
Combines patterns from Voice Agent, Indic, Sarvam, and AgentJyothi projects
"""

import asyncio
from typing import Optional, Dict, Any
from loguru import logger

from .context_manager import ContextManager
from .language_coordinator import LanguageCoordinator
from .task_router import TaskRouter


class AgentOrchestrator:
    """
    Main orchestrator that coordinates STT, LLM, and TTS modules
    """
    
    def __init__(self, stt_module, llm_module, tts_module, max_history: int = 10):
        """
        Initialize agent orchestrator
        
        Args:
            stt_module: STT module instance (e.g., SarvamAI)
            llm_module: LLM module instance (e.g., SarvamAI)
            tts_module: TTS module instance (e.g., SarvamAI)
            max_history: Maximum conversation history turns
        """
        # Store modules
        self.stt = stt_module
        self.llm = llm_module
        self.tts = tts_module
        
        # Initialize orchestrator components
        self.context_manager = ContextManager(max_history=max_history)
        self.language_coordinator = LanguageCoordinator()
        self.task_router = TaskRouter(stt_module, llm_module, tts_module)
        
        # State management
        self.is_processing = False
        self.processing_state = "idle"  # idle, listening, processing, speaking
    
    def set_language(self, language_code: str):
        """
        Set language for the conversation (from IVR/user selection)
        
        Args:
            language_code: Language code (e.g., "te-IN")
        """
        self.language_coordinator.set_language(language_code)
    
    def set_system_prompt(self, system_prompt: str):
        """
        Set system prompt for LLM
        
        Args:
            system_prompt: System prompt text
        """
        # Store in context manager's first message
        if not self.context_manager.conversation_history:
            self.context_manager.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })
        else:
            # Update existing system prompt
            for msg in self.context_manager.conversation_history:
                if msg.get("role") == "system":
                    msg["content"] = system_prompt
                    return
            # Add if not exists
            self.context_manager.conversation_history.insert(0, {
                "role": "system",
                "content": system_prompt
            })
    
    async def process_turn(
        self, 
        audio_data: bytes,
        language: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Process one complete conversation turn
        
        Args:
            audio_data: Audio data in bytes (WAV format)
            language: Language code (optional, uses coordinator's language if None)
            system_prompt: System prompt for LLM (optional)
            
        Returns:
            Dictionary with keys: text, response, audio, language
            Returns None if processing fails or is already in progress
        """
        # Prevent concurrent processing
        if self.is_processing:
            logger.warning("⚠️ Already processing, skipping new turn")
            return None
        
        self.is_processing = True
        self.processing_state = "processing"
        
        try:
            # Step 1: STT - Transcribe audio
            logger.info("📝 Step 1: Transcribing audio...")
            self.processing_state = "listening"
            
            processing_language = language or self.language_coordinator.get_processing_language()
            text, detected_lang = await self.task_router.route_transcription(
                audio_data, 
                language=processing_language
            )
            
            if not text:
                logger.warning("⚠️ STT failed, cannot continue")
                return None
            
            # Update detected language
            if detected_lang:
                self.language_coordinator.set_detected_language(detected_lang)
            
            # Step 2: Language coordination
            processing_language = self.language_coordinator.ensure_consistency()
            logger.info(f"🌐 Processing in: {self.language_coordinator.get_language_name(processing_language)}")
            
            # Step 3: Get context for LLM
            logger.info("📚 Step 2: Preparing context...")
            self.processing_state = "processing"
            
            context = self.context_manager.get_context(system_prompt=system_prompt)
            
            # Step 4: LLM - Generate response
            logger.info("🧠 Step 3: Generating response...")
            response = await self.task_router.route_generation(
                text,
                context,
                processing_language
            )
            
            if not response:
                logger.warning("⚠️ LLM failed, cannot continue")
                return None
            
            # Step 5: Update context
            self.context_manager.add_turn(text, response, processing_language)
            
            # Step 6: TTS - Synthesize audio
            logger.info("🔊 Step 4: Synthesizing audio...")
            self.processing_state = "speaking"
            
            audio_output = await self.task_router.route_synthesis(
                response,
                processing_language
            )
            
            if not audio_output:
                logger.warning("⚠️ TTS failed, but returning text response")
                # Return text response even if TTS fails
                return {
                    "text": text,
                    "response": response,
                    "audio": None,
                    "language": processing_language
                }
            
            # Success
            self.processing_state = "idle"
            logger.info("✅ Turn processed successfully")
            
            return {
                "text": text,
                "response": response,
                "audio": audio_output,
                "language": processing_language
            }
            
        except Exception as e:
            logger.error(f"❌ Error in process_turn: {e}")
            self.processing_state = "idle"
            return None
            
        finally:
            self.is_processing = False
    
    def get_context(self) -> list:
        """Get current conversation context"""
        return self.context_manager.get_context()
    
    def clear_context(self):
        """Clear conversation history"""
        self.context_manager.clear_history()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get orchestrator status
        
        Returns:
            Dictionary with orchestrator status information
        """
        return {
            "is_processing": self.is_processing,
            "processing_state": self.processing_state,
            "current_language": self.language_coordinator.get_processing_language(),
            "language_name": self.language_coordinator.get_language_name(),
            "turn_count": self.context_manager.get_turn_count(),
            "history_length": len(self.context_manager.conversation_history)
        }

