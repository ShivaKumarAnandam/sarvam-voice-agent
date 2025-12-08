"""
Integration tests for multilingual switching
"""

import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_multilingual_auto_switch(orchestrator):
    """Test automatic language switching"""
    # Set initial language
    orchestrator.set_language("te-IN")
    
    # Mock STT to return different language twice
    orchestrator.task_router.stt.speech_to_text = AsyncMock(
        return_value=("Hello", "hi-IN")
    )
    
    audio_data = b"fake_audio"
    
    # Process first turn
    await orchestrator.process_turn(audio_data)
    
    # Process second turn (should trigger switch)
    await orchestrator.process_turn(audio_data)
    
    # Check if language switched
    status = orchestrator.language_coordinator.get_switch_status()
    assert status["consecutive_different_count"] >= 2


@pytest.mark.asyncio
async def test_language_consistency_across_pipeline(orchestrator):
    """Test that language is consistent across STT → LLM → TTS"""
    orchestrator.set_language("hi-IN")
    
    audio_data = b"fake_audio"
    result = await orchestrator.process_turn(audio_data, language="hi-IN")
    
    # Verify all modules used same language
    assert result["language"] == "hi-IN"
    
    # Check that TTS was called with correct language
    orchestrator.task_router.tts.text_to_speech.assert_called_with(
        result["response"],
        "hi-IN"
    )
