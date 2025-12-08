"""
Language Coordinator - Handles multilingual workflows
Ensures language consistency across STT → LLM → TTS pipeline
"""

from typing import Optional
from loguru import logger


class LanguageCoordinator:
    """Coordinates language across modules"""
    
    # Language name mapping
    LANGUAGE_NAMES = {
        "te-IN": "Telugu",
        "hi-IN": "Hindi",
        "en-IN": "English",
        "gu-IN": "Gujarati"
    }
    
    def __init__(self):
        """Initialize language coordinator"""
        self.selected_language: Optional[str] = None  # From IVR/user choice
        self.detected_language: Optional[str] = None  # From STT
        self.language_consistency: bool = True
    
    def set_language(self, language_code: str):
        """
        Set selected language (from IVR/user choice)
        
        Args:
            language_code: Language code (e.g., "te-IN")
        """
        if language_code in self.LANGUAGE_NAMES:
            self.selected_language = language_code
            logger.info(f"🌐 Language set to: {self.get_language_name(language_code)} ({language_code})")
        else:
            logger.warning(f"⚠️ Unknown language code: {language_code}, defaulting to Telugu")
            self.selected_language = "te-IN"
    
    def set_detected_language(self, language_code: str):
        """
        Set detected language (from STT)
        
        Args:
            language_code: Detected language code
        """
        self.detected_language = language_code
        logger.debug(f"🔍 Language detected: {self.get_language_name(language_code)} ({language_code})")
    
    def get_processing_language(self) -> str:
        """
        Get language to use for processing
        Priority: selected > detected > default
        
        Returns:
            Language code to use
        """
        language = self.selected_language or self.detected_language or "te-IN"
        return language
    
    def get_language_name(self, language_code: Optional[str] = None) -> str:
        """
        Get human-readable language name
        
        Args:
            language_code: Language code (uses processing language if None)
            
        Returns:
            Language name
        """
        if language_code is None:
            language_code = self.get_processing_language()
        return self.LANGUAGE_NAMES.get(language_code, "Telugu")
    
    def ensure_consistency(self) -> str:
        """
        Ensure language consistency across pipeline
        
        Returns:
            Language code to use for all modules
        """
        target_language = self.get_processing_language()
        
        # Check consistency
        if self.selected_language and self.detected_language:
            if self.selected_language != self.detected_language:
                logger.warning(
                    f"⚠️ Language mismatch: selected={self.selected_language}, "
                    f"detected={self.detected_language}. Using selected: {self.selected_language}"
                )
                self.language_consistency = False
            else:
                self.language_consistency = True
        
        return target_language
    
    def reset(self):
        """Reset language coordinator"""
        self.selected_language = None
        self.detected_language = None
        self.language_consistency = True
        logger.debug("🔄 Language coordinator reset")

