"""
Context Manager - Manages conversation history and context
Combines patterns from Voice Agent and Sarvam projects
"""

from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger


class ContextManager:
    """Manages conversation context with sliding window"""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize context manager
        
        Args:
            max_history: Maximum number of conversation turns to keep
        """
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = max_history
        self.user_metadata: Dict = {}
        self.session_context: Dict = {}
        self.current_language: Optional[str] = None
    
    def add_turn(self, user_input: str, assistant_response: str, language: str):
        """
        Add a conversation turn to history
        
        Args:
            user_input: User's input text
            assistant_response: Assistant's response text
            language: Language code used (e.g., "te-IN")
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
        
        # Maintain sliding window (keep last max_history * 2 messages)
        if len(self.conversation_history) > self.max_history * 2:
            # Keep system message if exists, then last N turns
            system_messages = [msg for msg in self.conversation_history if msg.get("role") == "system"]
            recent_messages = self.conversation_history[-(self.max_history * 2):]
            self.conversation_history = system_messages + recent_messages
        
        self.current_language = language
        logger.debug(f"📝 Added turn to context (total: {len(self.conversation_history)} messages)")
    
    def get_context(self, system_prompt: Optional[str] = None, include_metadata: bool = False) -> List[Dict[str, str]]:
        """
        Get current context for LLM
        
        Args:
            system_prompt: Optional system prompt to include
            include_metadata: Whether to include user metadata
            
        Returns:
            List of messages in format expected by LLM
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add conversation history
        # Convert to LLM format (remove timestamp and language from content)
        for msg in self.conversation_history:
            llm_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            messages.append(llm_msg)
        
        # Add metadata if requested
        if include_metadata and self.user_metadata:
            metadata_msg = {
                "role": "system",
                "content": f"User metadata: {self.user_metadata}"
            }
            messages.insert(1, metadata_msg)  # Insert after system prompt
        
        return messages
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("🗑️ Conversation history cleared")
    
    def get_last_user_query(self) -> Optional[str]:
        """Get the last user query"""
        for msg in reversed(self.conversation_history):
            if msg.get("role") == "user":
                return msg.get("content")
        return None
    
    def get_turn_count(self) -> int:
        """Get number of conversation turns"""
        return len([msg for msg in self.conversation_history if msg.get("role") == "user"])

