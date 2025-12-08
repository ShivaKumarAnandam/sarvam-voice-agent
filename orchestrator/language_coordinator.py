"""
Language Coordinator - Handles multilingual workflows
Ensures language consistency across STT → LLM → TTS pipeline
Supports automatic language switching based on detection
"""

from typing import Optional, List
from loguru import logger


class LanguageCoordinator:
    """Coordinates language across modules with automatic switching"""
    
    # Language name mapping
    LANGUAGE_NAMES = {
        "te-IN": "Telugu",
        "hi-IN": "Hindi",
        "en-IN": "English",
        "gu-IN": "Gujarati"
    }
    
    def __init__(self, switch_threshold: int = 2, history_size: int = 5, min_turns_before_switch: int = 2):
        """
        Initialize language coordinator
        
        Args:
            switch_threshold: Number of consecutive different language detections before auto-switching (default: 2)
            history_size: Maximum number of recent language detections to remember (default: 5)
            min_turns_before_switch: Minimum turns before allowing auto-switch (default: 2)
        """
        self.selected_language: Optional[str] = None  # From IVR/user choice
        self.detected_language: Optional[str] = None  # From STT
        self.language_consistency: bool = True
        
        # Automatic language switching
        self.switch_threshold = switch_threshold
        self.history_size = history_size
        self.min_turns_before_switch = min_turns_before_switch
        self.language_history: List[str] = []  # Track recent language detections
        self.consecutive_different_count: int = 0  # Count consecutive different language detections
        self.turn_count: int = 0  # Track number of conversation turns
        self.last_different_language: Optional[str] = None  # Track which different language was detected
    
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
        Set detected language (from STT) and check for auto-switch
        
        Args:
            language_code: Detected language code
        """
        self.detected_language = language_code
        
        # Add to history
        self.language_history.append(language_code)
        if len(self.language_history) > self.history_size:
            self.language_history.pop(0)  # Keep only recent history
        
        # Check if detected language is different from selected
        if self.selected_language and language_code != self.selected_language:
            # Different language detected
            if self.last_different_language == language_code:
                # Same different language as before - increment counter
                self.consecutive_different_count += 1
                logger.info(
                    f"🔍 Language mismatch detected: {self.get_language_name(language_code)} "
                    f"(selected: {self.get_language_name(self.selected_language)}). "
                    f"Consecutive count: {self.consecutive_different_count}/{self.switch_threshold}"
                )
            else:
                # Different language from previous detection - reset counter
                self.consecutive_different_count = 1
                self.last_different_language = language_code
                logger.info(
                    f"🔍 Language mismatch detected: {self.get_language_name(language_code)} "
                    f"(selected: {self.get_language_name(self.selected_language)}). "
                    f"Starting count: 1/{self.switch_threshold}"
                )
            
            # Check if we should auto-switch
            if (self.consecutive_different_count >= self.switch_threshold and 
                self.turn_count >= self.min_turns_before_switch):
                # Auto-switch to detected language
                old_language = self.selected_language
                self.selected_language = language_code
                self.consecutive_different_count = 0  # Reset counter
                self.last_different_language = None
                self.language_consistency = True
                logger.info(
                    f"🔄 AUTO-SWITCHED language: {self.get_language_name(old_language)} → "
                    f"{self.get_language_name(language_code)} "
                    f"(after {self.switch_threshold} consecutive detections)"
                )
        else:
            # Languages match - reset counter
            if self.consecutive_different_count > 0:
                logger.debug(
                    f"✅ Language match: {self.get_language_name(language_code)}. "
                    f"Resetting consecutive counter."
                )
            self.consecutive_different_count = 0
            self.last_different_language = None
            self.language_consistency = True
        
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
        Note: Auto-switching is now handled in set_detected_language()
        
        Returns:
            Language code to use for all modules
        """
        target_language = self.get_processing_language()
        
        # Increment turn count for auto-switch logic
        self.turn_count += 1
        
        # Check consistency (for logging)
        if self.selected_language and self.detected_language:
            if self.selected_language != self.detected_language:
                # This is expected during language switching - don't log as warning
                self.language_consistency = False
            else:
                self.language_consistency = True
        
        return target_language
    
    def reset(self):
        """Reset language coordinator"""
        self.selected_language = None
        self.detected_language = None
        self.language_consistency = True
        self.language_history = []
        self.consecutive_different_count = 0
        self.turn_count = 0
        self.last_different_language = None
        logger.debug("🔄 Language coordinator reset")
    
    def get_switch_status(self) -> dict:
        """
        Get current language switching status
        
        Returns:
            Dictionary with switching status information
        """
        return {
            "selected_language": self.selected_language,
            "detected_language": self.detected_language,
            "consecutive_different_count": self.consecutive_different_count,
            "switch_threshold": self.switch_threshold,
            "turn_count": self.turn_count,
            "min_turns_before_switch": self.min_turns_before_switch,
            "can_switch": (
                self.consecutive_different_count >= self.switch_threshold and
                self.turn_count >= self.min_turns_before_switch
            ),
            "recent_history": self.language_history[-3:] if len(self.language_history) >= 3 else self.language_history
        }

