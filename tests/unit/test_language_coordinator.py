"""
Unit tests for LanguageCoordinator
"""

import pytest
from orchestrator.language_coordinator import LanguageCoordinator


def test_language_coordinator_initialization():
    """Test LanguageCoordinator initialization"""
    lc = LanguageCoordinator(default_language="en-IN")
    assert lc.selected_language == "en-IN"
    assert lc.detected_language is None


def test_set_language():
    """Test setting language"""
    lc = LanguageCoordinator(default_language="te-IN")
    lc.set_language("hi-IN")
    assert lc.selected_language == "hi-IN"


def test_set_detected_language():
    """Test setting detected language"""
    lc = LanguageCoordinator(default_language="te-IN")
    lc.set_detected_language("en-IN")
    assert lc.detected_language == "en-IN"
    assert lc.turn_count == 1


def test_auto_switch():
    """Test auto-switching language"""
    lc = LanguageCoordinator(
        default_language="te-IN",
        switch_threshold=2,
        min_turns_before_switch=1
    )
    
    # Set initial language
    lc.set_language("te-IN")
    
    # Detect different language twice (should trigger switch)
    lc.set_detected_language("hi-IN")
    lc.set_detected_language("hi-IN")
    
    # Should have switched
    assert lc.selected_language == "hi-IN"
    assert lc.switch_count == 1


def test_ensure_consistency():
    """Test language consistency"""
    lc = LanguageCoordinator(default_language="te-IN")
    lc.set_language("hi-IN")
    
    assert lc.ensure_consistency() == "hi-IN"
    
    # If no selected, should use detected
    lc.selected_language = None
    lc.detected_language = "en-IN"
    assert lc.ensure_consistency() == "en-IN"
    
    # If neither, should use default
    lc.detected_language = None
    assert lc.ensure_consistency() == "te-IN"


def test_get_language_name():
    """Test getting language name"""
    lc = LanguageCoordinator()
    assert lc.get_language_name("te-IN") == "Telugu"
    assert lc.get_language_name("hi-IN") == "Hindi"
    assert lc.get_language_name("en-IN") == "English"


def test_get_switch_status():
    """Test getting switch status"""
    lc = LanguageCoordinator()
    status = lc.get_switch_status()
    
    assert "selected_language" in status
    assert "detected_language" in status
    assert "processing_language" in status
    assert "can_switch" in status
