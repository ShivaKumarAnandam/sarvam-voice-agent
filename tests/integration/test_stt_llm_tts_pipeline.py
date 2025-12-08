"""
Integration tests for complete STT → LLM → TTS pipeline
"""

import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_complete_pipeline(orchestrator):
    """Test complete pipeline: STT → LLM → TTS"""
    # Mock audio data
    audio_data = b"fake_audio_wav_data"
    
    # Process turn
    result = await orchestrator.process_turn(audio_data, language="en-IN")
    
    # Verify result structure
    assert "text" in result
    assert "response" in result
    assert "audio" in result
    assert "language" in result
    
    # Verify values
    assert result["text"] == "Hello, this is a test"
    assert result["response"] == "This is a test response"
    assert result["audio"] == b"fake_wav_audio_data"
    assert result["language"] == "en-IN"


@pytest.mark.asyncio
async def test_pipeline_with_language_switching(orchestrator):
    """Test pipeline with language switching"""
    audio_data = b"fake_audio_wav_data"
    
    # Set initial language
    orchestrator.set_language("te-IN")
    
    # Mock STT to return different language
    orchestrator.task_router.stt.speech_to_text = AsyncMock(
        return_value=("Hello", "en-IN")
    )
    
    # Process turn
    result = await orchestrator.process_turn(audio_data)
    
    # Language coordinator should track the detection
    assert orchestrator.language_coordinator.detected_language == "en-IN"


@pytest.mark.asyncio
async def test_pipeline_error_handling(orchestrator):
    """Test pipeline error handling"""
    audio_data = b"fake_audio_wav_data"
    
    # Make STT fail
    orchestrator.task_router.stt.speech_to_text = AsyncMock(
        side_effect=Exception("STT error")
    )
    
    # Process turn
    result = await orchestrator.process_turn(audio_data)
    
    # Should return error
    assert result["text"] is None
    assert "error" in result


@pytest.mark.skip(reason="Requires real audio samples and API keys")
def test_pipeline_with_real_audio():
    """Placeholder for E2E test with real audio samples"""
    # TODO: Implement E2E test with real audio samples
    # - Test complete flow: audio → text → response → audio
    # - Validate accuracy
    # - Check continuity
    # - Measure responsiveness
    pass
