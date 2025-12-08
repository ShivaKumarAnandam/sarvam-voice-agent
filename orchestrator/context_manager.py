"""
Context Manager - Manages conversation history and context
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from loguru import logger


class ContextManager:
    """
    Manages conversation history and context for the LLM.
    Maintains a sliding window of recent conversation turns.
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize context manager
        
        Args:
            max_history: Maximum number of conversation turns to keep (default: 10)
        """
        self.conversation_history: List[Dict[str, Any]] = []
        self.max_history = max_history
        self.user_metadata: Dict[str, Any] = {}
        self.session_context: Dict[str, Any] = {}
        self.current_language: Optional[str] = None
    
    def add_turn(self, user_input: str, assistant_response: str, language: str):
        """
        Add a conversation turn to history
        
        Args:
            user_input: User's input text
            assistant_response: Assistant's response text
            language: Language code for this turn
        """
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "language": language,
            "timestamp": datetime.now().isoformat()
        })
        
        # Add assistant message
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_response,
            "language": language,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update current language
        self.current_language = language
        
        # Maintain sliding window: keep last max_history * 2 messages (user + assistant pairs)
        if len(self.conversation_history) > self.max_history * 2:
            # Preserve system messages
            system_messages = [msg for msg in self.conversation_history if msg.get("role") == "system"]
            # Keep most recent messages
            recent_messages = self.conversation_history[-(self.max_history * 2):]
            self.conversation_history = system_messages + recent_messages
            logger.debug(f"📝 Trimmed conversation history to {len(self.conversation_history)} messages")
    
    def set_system_prompt(self, system_prompt: str):
        """
        Set or update the system prompt
        
        Args:
            system_prompt: System prompt text
        """
        # Remove existing system messages
        self.conversation_history = [msg for msg in self.conversation_history if msg.get("role") != "system"]
        
        # Add new system message at the beginning
        self.conversation_history.insert(0, {
            "role": "system",
            "content": system_prompt,
            "timestamp": datetime.now().isoformat()
        })
        logger.debug("📝 System prompt updated")
    
    def get_context(self, system_prompt: Optional[str] = None, include_metadata: bool = False) -> List[Dict[str, str]]:
        """
        Get formatted context for LLM
        
        Args:
            system_prompt: Optional system prompt to use (if not in history)
            include_metadata: Whether to include metadata in context
            
        Returns:
            List of messages in format expected by LLM (role/content)
        """
        messages = []
        
        # Add system prompt (from history or provided)
        system_messages = [msg for msg in self.conversation_history if msg.get("role") == "system"]
        if system_messages:
            messages.append({"role": "system", "content": system_messages[0]["content"]})
        elif system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history (role/content only for LLM)
        for msg in [m for m in self.conversation_history if m.get("role") != "system"]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Optionally include metadata
        if include_metadata and self.user_metadata:
            metadata_str = f"\n[User Metadata: {self.user_metadata}]"
            if messages and messages[-1]["role"] == "user":
                messages[-1]["content"] += metadata_str
        
        return messages
    
    def clear_history(self):
        """Clear all conversation history (except system prompt)"""
        system_messages = [msg for msg in self.conversation_history if msg.get("role") == "system"]
        self.conversation_history = system_messages
        logger.info("🗑️ Conversation history cleared")
    
    def get_turn_count(self) -> int:
        """Get number of conversation turns (user + assistant pairs)"""
        user_messages = [msg for msg in self.conversation_history if msg.get("role") == "user"]
        return len(user_messages)
    
    def get_recent_history(self, n: int = 3) -> List[Dict[str, Any]]:
        """
        Get recent conversation history
        
        Args:
            n: Number of recent turns to return
            
        Returns:
            List of recent conversation messages
        """
        return self.conversation_history[-(n * 2):] if n > 0 else []
    
    def set_user_metadata(self, key: str, value: Any):
        """Set user metadata"""
        self.user_metadata[key] = value
    
    def get_user_metadata(self, key: str, default: Any = None) -> Any:
        """Get user metadata"""
        return self.user_metadata.get(key, default)
    
    def set_session_context(self, key: str, value: Any):
        """Set session context"""
        self.session_context[key] = value
    
    def get_session_context(self, key: str, default: Any = None) -> Any:
        """Get session context"""
        return self.session_context.get(key, default)
