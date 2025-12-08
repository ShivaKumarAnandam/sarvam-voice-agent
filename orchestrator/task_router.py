"""
Task Router - Routes tasks between STT, LLM, and TTS modules
"""

import asyncio
from typing import Optional, Tuple, List, Dict, Any
from loguru import logger


class TaskRouter:
    """
    Routes tasks between STT, LLM, and TTS modules.
    Handles retry logic and error handling.
    """
    
    def __init__(self, stt_module, llm_module, tts_module):
        """
        Initialize task router
        
        Args:
            stt_module: STT module instance (must have speech_to_text method)
            llm_module: LLM module instance (must have chat method)
            tts_module: TTS module instance (must have text_to_speech method)
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
        Route audio to STT module for transcription
        
        Args:
            audio_data: Audio data in WAV format (bytes)
            language: Optional language hint for STT
            retry_count: Number of retry attempts (default: 2)
            
        Returns:
            Tuple of (transcribed_text, detected_language) or (None, None) on failure
        """
        for attempt in range(retry_count):
            try:
                logger.info(f"🎤 STT: Routing transcription (attempt {attempt + 1}/{retry_count})")
                text, detected_lang = await self.stt.speech_to_text(audio_data, language=language)
                
                if text and len(text.strip()) > 0:
                    logger.info(f"✅ STT successful: '{text[:50]}...' (lang: {detected_lang})")
                    return text, detected_lang
                else:
                    logger.warning(f"⚠️ STT returned empty text (attempt {attempt + 1}/{retry_count})")
                    if attempt < retry_count - 1:
                        await asyncio.sleep(0.5)  # Delay before retry
                        continue
                    return None, None
                    
            except Exception as e:
                logger.error(f"❌ STT failed (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(0.5)  # Delay before retry
                    continue
                return None, None
        
        return None, None
    
    async def route_generation(
        self,
        text: str,
        context: List[Dict[str, str]],
        language: str
    ) -> Optional[str]:
        """
        Route text to LLM module for response generation
        
        Args:
            text: User input text
            context: Conversation context (list of messages)
            language: Language code for processing
            
        Returns:
            Generated response text or None on failure
        """
        try:
            logger.info(f"🧠 LLM: Routing generation for text: '{text[:50]}...'")
            
            # Prepare messages: context + current user input
            messages = context.copy()
            messages.append({"role": "user", "content": text})
            
            # Call LLM
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
        Route text to TTS module for audio synthesis
        
        Args:
            text: Text to synthesize
            language: Language code for TTS
            retry_count: Number of retry attempts (default: 2)
            
        Returns:
            Audio data (WAV format) or None on failure
        """
        for attempt in range(retry_count):
            try:
                logger.info(f"🔊 TTS: Routing synthesis (attempt {attempt + 1}/{retry_count})")
                audio_data = await self.tts.text_to_speech(text, language)
                
                if audio_data and len(audio_data) > 0:
                    logger.info(f"✅ TTS successful: {len(audio_data)} bytes")
                    return audio_data
                else:
                    logger.warning(f"⚠️ TTS returned empty audio (attempt {attempt + 1}/{retry_count})")
                    if attempt < retry_count - 1:
                        await asyncio.sleep(0.5)  # Delay before retry
                        continue
                    return None
                    
            except Exception as e:
                logger.error(f"❌ TTS failed (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(0.5)  # Delay before retry
                    continue
                return None
        
        return None
