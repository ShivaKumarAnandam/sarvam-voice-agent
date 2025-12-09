"""
Task Router - Routes tasks between STT, LLM, and TTS modules
Handles retry logic and error recovery
"""

from typing import Optional, Tuple, List, Dict
import asyncio
from loguru import logger


class TaskRouter:
    """Routes tasks between modules with error handling"""
    
    def __init__(self, stt_module, llm_module, tts_module):
        """
        Initialize task router
        
        Args:
            stt_module: STT module instance (e.g., SarvamAI)
            llm_module: LLM module instance (e.g., SarvamAI)
            tts_module: TTS module instance (e.g., SarvamAI)
        """
        self.stt = stt_module
        self.llm = llm_module
        self.tts = tts_module
    
    async def route_transcription(
        self, 
        audio_data: bytes, 
        language: Optional[str] = None,
        retry_count: int = 2
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Route audio to STT module with retry logic
        
        Args:
            audio_data: Audio data in bytes (WAV format)
            language: Language code (optional)
            retry_count: Number of retry attempts
            
        Returns:
            Tuple of (text, detected_language) or (None, None) on failure
        """
        for attempt in range(retry_count):
            try:
                logger.debug(f"🎤 Routing to STT (attempt {attempt + 1}/{retry_count})")
                text, detected_lang = await self.stt.speech_to_text(
                    audio_data, 
                    language=language
                )
                
                if text and len(text.strip()) > 0:
                    logger.info(f"✅ STT successful: '{text[:50]}...' (lang: {detected_lang})")
                    return text, detected_lang
                else:
                    logger.warning(f"⚠️ STT returned empty text (attempt {attempt + 1})")
                    
            except Exception as e:
                logger.error(f"❌ STT failed (attempt {attempt + 1}): {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(0.5)  # Brief delay before retry
                else:
                    return None, None
        
        return None, None
    
    async def route_generation(
        self, 
        text: str, 
        context: List[Dict[str, str]], 
        language: str
    ) -> Optional[str]:
        """
        Route text to LLM module with context
        
        Args:
            text: User input text
            context: Conversation context (messages)
            language: Language code
            
        Returns:
            Generated response text or None on failure
        """
        try:
            logger.debug(f"🧠 Routing to LLM (lang: {language})")
            
            # Add current user input to context
            messages = context.copy()
            messages.append({
                "role": "user",
                "content": text
            })
            
            # Generate response
            response = await self.llm.chat(messages)
            
            if response and len(response.strip()) > 0:
                logger.info(f"✅ LLM successful: '{response[:50]}...'")
                return response
            else:
                logger.warning("⚠️ LLM returned empty response")
                return None
                
        except Exception as e:
            logger.error(f"❌ LLM failed: {e}")
            return None
    
    async def route_synthesis(
        self, 
        text: str, 
        language: str,
        retry_count: int = 2
    ) -> Optional[bytes]:
        """
        Route text to TTS module
        
        Args:
            text: Text to synthesize
            language: Language code
            retry_count: Number of retry attempts
            
        Returns:
            Audio data in bytes (WAV format) or None on failure
        """
        for attempt in range(retry_count):
            try:
                logger.debug(f"🔊 Routing to TTS (attempt {attempt + 1}/{retry_count}, lang: {language})")
                audio_data = await self.tts.text_to_speech(text, language)
                
                if audio_data and len(audio_data) > 0:
                    logger.info(f"✅ TTS successful: {len(audio_data)} bytes")
                    return audio_data
                else:
                    logger.warning(f"⚠️ TTS returned empty audio (attempt {attempt + 1})")
                    
            except Exception as e:
                logger.error(f"❌ TTS failed (attempt {attempt + 1}): {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(0.5)  # Brief delay before retry
                else:
                    return None
        
        return None

