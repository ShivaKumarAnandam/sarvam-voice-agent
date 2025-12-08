"""
Unit tests for ContextManager
"""

import pytest
from orchestrator.context_manager import ContextManager


def test_context_manager_initialization():
    """Test ContextManager initialization"""
    cm = ContextManager(max_history=5)
    assert cm.max_history == 5
    assert len(cm.conversation_history) == 0
    assert cm.current_language is None


def test_add_turn():
    """Test adding conversation turns"""
    cm = ContextManager(max_history=3)
    cm.add_turn("Hello", "Hi there!", "en-IN")
    
    assert len(cm.conversation_history) == 2  # user + assistant
    assert cm.conversation_history[0]["role"] == "user"
    assert cm.conversation_history[0]["content"] == "Hello"
    assert cm.conversation_history[1]["role"] == "assistant"
    assert cm.conversation_history[1]["content"] == "Hi there!"


def test_sliding_window():
    """Test sliding window maintenance"""
    cm = ContextManager(max_history=2)
    
    # Add 3 turns (should keep only last 2)
    cm.add_turn("Turn 1", "Response 1", "en-IN")
    cm.add_turn("Turn 2", "Response 2", "en-IN")
    cm.add_turn("Turn 3", "Response 3", "en-IN")
    
    # Should have 2 turns * 2 messages = 4 messages
    assert len(cm.conversation_history) == 4
    assert "Turn 1" not in [msg["content"] for msg in cm.conversation_history]
    assert "Turn 3" in [msg["content"] for msg in cm.conversation_history]


def test_set_system_prompt():
    """Test setting system prompt"""
    cm = ContextManager()
    cm.set_system_prompt("You are a helpful assistant.")
    
    context = cm.get_context()
    assert len(context) == 1
    assert context[0]["role"] == "system"
    assert context[0]["content"] == "You are a helpful assistant."


def test_get_context():
    """Test getting context for LLM"""
    cm = ContextManager()
    cm.set_system_prompt("System prompt")
    cm.add_turn("User message", "Assistant response", "en-IN")
    
    context = cm.get_context()
    assert len(context) == 3  # system + user + assistant
    assert context[0]["role"] == "system"
    assert context[1]["role"] == "user"
    assert context[2]["role"] == "assistant"


def test_clear_history():
    """Test clearing history"""
    cm = ContextManager()
    cm.set_system_prompt("System prompt")
    cm.add_turn("User message", "Assistant response", "en-IN")
    
    cm.clear_history()
    
    # System prompt should remain
    assert len(cm.conversation_history) == 1
    assert cm.conversation_history[0]["role"] == "system"


def test_get_turn_count():
    """Test getting turn count"""
    cm = ContextManager()
    assert cm.get_turn_count() == 0
    
    cm.add_turn("Message 1", "Response 1", "en-IN")
    assert cm.get_turn_count() == 1
    
    cm.add_turn("Message 2", "Response 2", "en-IN")
    assert cm.get_turn_count() == 2
