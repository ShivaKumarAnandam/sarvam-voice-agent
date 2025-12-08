"""
Agent Orchestrator - Central controller for managing STT, LLM, and TTS interactions
"""

import time
from typing import Optional, Dict, Any, List
from loguru import logger

from typing import Optional
from .task_router import TaskRouter
from .context_manager import ContextManager
from .language_coordinator import LanguageCoordinator
from .metrics import MetricsCollector
from .circuit_breaker import CircuitBreaker


class AgentOrchestrator:
    """
    Central orchestrator that coordinates STT, LLM, and TTS modules.
    Manages the complete workflow: STT → Intent → LLM → TTS
    """
    
    def __init__(
        self,
        stt_module,
        llm_module,
        tts_module,
        max_history: int = 10,
        default_language: str = "te-IN",
        system_prompt: Optional[str] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        enable_circuit_breaker: bool = True
    ):
        """
        Initialize agent orchestrator
        
        Args:
            stt_module: STT module instance
            llm_module: LLM module instance
            tts_module: TTS module instance
            max_history: Maximum conversation history turns (default: 10)
            default_language: Default language code (default: "te-IN")
            system_prompt: Optional system prompt for LLM
            metrics_collector: Optional metrics collector instance
            enable_circuit_breaker: Enable circuit breaker for error handling (default: True)
        """
        # Initialize core components
        self.task_router = TaskRouter(stt_module, llm_module, tts_module)
        self.context_manager = ContextManager(max_history=max_history)
        self.language_coordinator = LanguageCoordinator(default_language=default_language)
        self.metrics = metrics_collector
        
        # Circuit breakers for each module
        self.circuit_breakers = {}
        if enable_circuit_breaker:
            self.circuit_breakers = {
                "stt": CircuitBreaker(failure_threshold=5, timeout=60),
                "llm": CircuitBreaker(failure_threshold=5, timeout=60),
                "tts": CircuitBreaker(failure_threshold=5, timeout=60)
            }
        
        # Set system prompt if provided
        if system_prompt:
            self.context_manager.set_system_prompt(system_prompt)
        
        # State management
        self.is_processing = False
        self.processing_state = "idle"  # idle, stt, llm, tts, error
        self.last_error: Optional[str] = None
    
    def set_language(self, language_code: str):
        """
        Set the language for processing
        
        Args:
            language_code: Language code (e.g., "te-IN", "hi-IN", "en-IN")
        """
        self.language_coordinator.set_language(language_code)
        self._update_system_prompt_for_language(language_code)
    
    def set_system_prompt(self, system_prompt: str):
        """
        Set or update the system prompt
        
        Args:
            system_prompt: System prompt text
        """
        self.context_manager.set_system_prompt(system_prompt)
    
    def _update_system_prompt_for_language(self, language_code: str):
        """
        Update system prompt to include language instruction
        
        Args:
            language_code: Language code
        """
        language_name = self.language_coordinator.get_language_name(language_code)
        
        # Get existing system prompt or use default
        existing_context = self.context_manager.get_context()
        existing_system = None
        for msg in existing_context:
            if msg.get("role") == "system":
                existing_system = msg.get("content", "")
                break
        
        # Extract base prompt (remove language instruction if present)
        base_prompt = existing_system
        if base_prompt and "CRITICAL: User selected" in base_prompt:
            # Extract the base prompt before language instruction
            parts = base_prompt.split("CRITICAL: User selected")
            if parts:
                base_prompt = parts[0].strip()
        
        # If no base prompt, use default
        if not base_prompt:
            base_prompt = """You are a helpful customer support agent for the Electrical Department in India.

Your responsibilities:
- Handle electrical complaints (power outages, voltage issues, meter problems)
- Provide information about electricity bills and payments
- Help with new connection requests
- Report electrical hazards and emergencies
- Provide lineman contact numbers and department information

Guidelines:
- Keep responses SHORT and CONCISE (2-3 sentences maximum for voice calls)
- Be professional, polite, and helpful
- Ask ONE clear question at a time
- If you don't have specific information, acknowledge briefly and offer to connect to a human agent
- For emergencies, prioritize safety and provide emergency contact: 1912"""
        
        # Add language instruction
        new_prompt = f"""{base_prompt}

CRITICAL: User selected {language_name} language. You MUST respond ONLY in {language_name}.

Remember: ALWAYS respond in {language_name} language only!"""
        
        self.context_manager.set_system_prompt(new_prompt)
    
    async def process_turn(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a complete conversation turn: STT → LLM → TTS
        
        Args:
            audio_data: Audio data in WAV format (bytes)
            language: Optional language hint (if None, uses selected/detected language)
            system_prompt: Optional system prompt override
            
        Returns:
            Dictionary with:
                - text: Transcribed text
                - response: LLM response
                - audio: TTS audio (WAV format) or None
                - language: Language used
                - metrics: Optional timing metrics
        """
        # Prevent concurrent processing
        if self.is_processing:
            logger.warning("⚠️ Already processing a turn, ignoring new request")
            return {
                "text": None,
                "response": None,
                "audio": None,
                "language": None,
                "error": "Already processing"
            }
        
        self.is_processing = True
        self.processing_state = "stt"
        self.last_error = None
        
        try:
            # Determine processing language
            processing_language = language or self.language_coordinator.ensure_consistency()
            
            # Step 1: STT - Transcribe audio
            logger.info(f"📝 Step 1: Transcribing audio... (lang: {processing_language})")
            stt_start = time.perf_counter()
            
            try:
                if "stt" in self.circuit_breakers:
                    text, detected_lang = await self.circuit_breakers["stt"].call(
                        self.task_router.route_transcription,
                        audio_data,
                        language=processing_language
                    )
                else:
                    text, detected_lang = await self.task_router.route_transcription(
                        audio_data,
                        language=processing_language
                    )
            except Exception as e:
                logger.error(f"❌ STT failed: {e}")
                self.processing_state = "error"
                self.last_error = f"STT error: {str(e)}"
                return {
                    "text": None,
                    "response": None,
                    "audio": None,
                    "language": processing_language,
                    "error": self.last_error
                }
            
            stt_time = time.perf_counter() - stt_start
            
            if not text:
                logger.warning("⚠️ STT returned no text")
                self.processing_state = "error"
                self.last_error = "STT returned empty text"
                return {
                    "text": None,
                    "response": None,
                    "audio": None,
                    "language": processing_language,
                    "error": self.last_error
                }
            
            # Step 2: Language coordination (auto-switch if needed)
            previous_language = self.language_coordinator.selected_language
            if detected_lang:
                self.language_coordinator.set_detected_language(detected_lang)
            
            # Get processing language (may have switched)
            processing_language = self.language_coordinator.ensure_consistency()
            
            # If language switched, update system prompt
            if previous_language != self.language_coordinator.selected_language:
                self._update_system_prompt_for_language(processing_language)
            
            # Step 3: Get context for LLM
            self.processing_state = "llm"
            logger.info(f"🧠 Step 3: Generating response... (lang: {processing_language})")
            context = self.context_manager.get_context(system_prompt=system_prompt)
            
            # Step 4: LLM - Generate response
            llm_start = time.perf_counter()
            
            try:
                if "llm" in self.circuit_breakers:
                    response = await self.circuit_breakers["llm"].call(
                        self.task_router.route_generation,
                        text,
                        context,
                        processing_language
                    )
                else:
                    response = await self.task_router.route_generation(
                        text,
                        context,
                        processing_language
                    )
            except Exception as e:
                logger.error(f"❌ LLM failed: {e}")
                self.processing_state = "error"
                self.last_error = f"LLM error: {str(e)}"
                return {
                    "text": text,
                    "response": None,
                    "audio": None,
                    "language": processing_language,
                    "error": self.last_error
                }
            
            llm_time = time.perf_counter() - llm_start
            
            if not response:
                logger.warning("⚠️ LLM returned no response")
                self.processing_state = "error"
                self.last_error = "LLM returned empty response"
                return {
                    "text": text,
                    "response": None,
                    "audio": None,
                    "language": processing_language,
                    "error": self.last_error
                }
            
            # Step 5: Update context
            self.context_manager.add_turn(text, response, processing_language)
            
            # Step 6: TTS - Synthesize audio
            self.processing_state = "tts"
            logger.info(f"🔊 Step 4: Synthesizing audio... (lang: {processing_language})")
            tts_start = time.perf_counter()
            
            try:
                if "tts" in self.circuit_breakers:
                    audio_output = await self.circuit_breakers["tts"].call(
                        self.task_router.route_synthesis,
                        response,
                        processing_language
                    )
                else:
                    audio_output = await self.task_router.route_synthesis(
                        response,
                        processing_language
                    )
            except Exception as e:
                logger.error(f"❌ TTS failed: {e}")
                # Graceful degradation: return text response even if TTS fails
                tts_time = time.perf_counter() - tts_start
                if self.metrics:
                    self.metrics.record_turn(
                        stt_time, llm_time, tts_time, processing_language,
                        success=False, error_type="TTS"
                    )
                self.processing_state = "idle"
                self.is_processing = False
                return {
                    "text": text,
                    "response": response,
                    "audio": None,  # No audio, but text available
                    "language": processing_language,
                    "error": f"TTS error: {str(e)}"
                }
            
            tts_time = time.perf_counter() - tts_start
            
            # Record metrics if collector provided
            if self.metrics:
                self.metrics.record_turn(
                    stt_time, llm_time, tts_time, processing_language,
                    success=True
                )
            
            # Log total time
            total_time = stt_time + llm_time + tts_time
            logger.info(f"⏱️ Total turn time: {total_time:.2f}s (STT: {stt_time:.2f}s, LLM: {llm_time:.2f}s, TTS: {tts_time:.2f}s)")
            
            self.processing_state = "idle"
            self.is_processing = False
            
            return {
                "text": text,
                "response": response,
                "audio": audio_output,  # WAV format
                "language": processing_language,
                "metrics": {
                    "stt_time": stt_time,
                    "llm_time": llm_time,
                    "tts_time": tts_time,
                    "total_time": total_time
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in process_turn: {e}")
            self.processing_state = "error"
            self.last_error = f"Unexpected error: {str(e)}"
            self.is_processing = False
            return {
                "text": None,
                "response": None,
                "audio": None,
                "language": None,
                "error": self.last_error
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current orchestrator status
        
        Returns:
            Dictionary with status information
        """
        return {
            "is_processing": self.is_processing,
            "processing_state": self.processing_state,
            "current_language": self.language_coordinator.get_processing_language(),
            "language_name": self.language_coordinator.get_language_name(),
            "turn_count": self.context_manager.get_turn_count(),
            "history_length": len(self.context_manager.conversation_history),
            "language_switching": self.language_coordinator.get_switch_status(),
            "last_error": self.last_error,
            "circuit_breakers": {
                name: breaker.get_state()
                for name, breaker in self.circuit_breakers.items()
            } if self.circuit_breakers else {}
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.context_manager.clear_history()
        logger.info("🗑️ Conversation history cleared")
