"""
Language Coordinator - Handles multilingual workflows and auto-switching
"""

from typing import Optional, Dict, List
from loguru import logger


class LanguageCoordinator:
    """
    Coordinates language across STT, LLM, and TTS modules.
    Supports auto-switching based on detected language.
    """
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        "te-IN": "Telugu",
        "hi-IN": "Hindi",
        "en-IN": "English",
        "gu-IN": "Gujarati"
    }
    
    def __init__(
        self,
        default_language: str = "te-IN",
        switch_threshold: int = 2,
        min_turns_before_switch: int = 1,
        history_size: int = 5
    ):
        """
        Initialize language coordinator
        
        Args:
            default_language: Default language code (default: "te-IN")
            switch_threshold: Number of consecutive detections before auto-switch (default: 2)
            min_turns_before_switch: Minimum turns before allowing switch (default: 1)
            history_size: Size of language detection history (default: 5)
        """
        self.selected_language: Optional[str] = default_language
        self.detected_language: Optional[str] = None
        self.default_language = default_language
        self.switch_threshold = switch_threshold
        self.min_turns_before_switch = min_turns_before_switch
        self.history_size = history_size
        
        # Tracking for auto-switch
        self.language_history: List[str] = []
        self.consecutive_different_count = 0
        self.last_different_language: Optional[str] = None
        self.turn_count = 0
        self.switch_count = 0
    
    def set_language(self, language_code: str):
        """
        Set selected language (from IVR/user choice)
        
        Args:
            language_code: Language code to set
        """
        if language_code not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"⚠️ Unsupported language code: {language_code}, using default")
            language_code = self.default_language
        
        if self.selected_language != language_code:
            old_language = self.selected_language
            self.selected_language = language_code
            logger.info(f"🌐 Language set to: {self.get_language_name(language_code)} ({language_code})")
            # Reset tracking when manually setting language
            self.consecutive_different_count = 0
            self.last_different_language = None
    
    def set_detected_language(self, language_code: str):
        """
        Set detected language from STT (may trigger auto-switch)
        
        Args:
            language_code: Detected language code
        """
        if language_code not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"⚠️ Unsupported detected language: {language_code}")
            return
        
        self.detected_language = language_code
        
        # Track history (last N detections)
        self.language_history.append(language_code)
        if len(self.language_history) > self.history_size:
            self.language_history.pop(0)
        
        # Increment turn count
        self.turn_count += 1
        
        # Check if different from selected
        if self.selected_language and language_code != self.selected_language:
            # Same different language as before?
            if self.last_different_language == language_code:
                self.consecutive_different_count += 1
            else:
                # New different language - reset counter
                self.consecutive_different_count = 1
                self.last_different_language = language_code
            
            # Auto-switch after threshold
            if (self.consecutive_different_count >= self.switch_threshold and 
                self.turn_count >= self.min_turns_before_switch):
                old_language = self.selected_language
                self.selected_language = language_code  # SWITCH!
                self.consecutive_different_count = 0
                self.switch_count += 1
                logger.info(f"🔄 AUTO-SWITCHED: {self.get_language_name(old_language)} ({old_language}) → {self.get_language_name(language_code)} ({language_code})")
        else:
            # Languages match - reset counter
            self.consecutive_different_count = 0
            self.last_different_language = None
    
    def ensure_consistency(self) -> str:
        """
        Get the language to use for processing (ensures consistency)
        
        Returns:
            Language code to use (selected > detected > default)
        """
        language = self.selected_language or self.detected_language or self.default_language
        return language
    
    def get_processing_language(self) -> str:
        """Alias for ensure_consistency()"""
        return self.ensure_consistency()
    
    def get_language_name(self, language_code: Optional[str] = None) -> str:
        """
        Get human-readable language name
        
        Args:
            language_code: Language code (if None, uses selected language)
            
        Returns:
            Language name
        """
        code = language_code or self.selected_language or self.default_language
        return self.SUPPORTED_LANGUAGES.get(code, code)
    
    def get_switch_status(self) -> Dict[str, any]:
        """
        Get current language switching status
        
        Returns:
            Dictionary with switching status information
        """
        return {
            "selected_language": self.selected_language,
            "detected_language": self.detected_language,
            "processing_language": self.ensure_consistency(),
            "consecutive_different_count": self.consecutive_different_count,
            "switch_threshold": self.switch_threshold,
            "can_switch": (
                self.consecutive_different_count >= self.switch_threshold and
                self.turn_count >= self.min_turns_before_switch
            ),
            "turn_count": self.turn_count,
            "switch_count": self.switch_count,
            "recent_history": self.language_history[-3:] if len(self.language_history) >= 3 else self.language_history
        }
    
    def reset(self):
        """Reset language coordinator state"""
        self.detected_language = None
        self.language_history.clear()
        self.consecutive_different_count = 0
        self.last_different_language = None
        self.turn_count = 0
        logger.debug("🔄 Language coordinator reset")
