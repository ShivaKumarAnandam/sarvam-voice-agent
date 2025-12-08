"""
Pytest configuration and fixtures
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_stt_module():
    """Mock STT module"""
    stt = AsyncMock()
    stt.speech_to_text = AsyncMock(return_value=("Hello, this is a test", "en-IN"))
    return stt


@pytest.fixture
def mock_llm_module():
    """Mock LLM module"""
    llm = AsyncMock()
    llm.chat = AsyncMock(return_value="This is a test response")
    return llm


@pytest.fixture
def mock_tts_module():
    """Mock TTS module"""
    tts = AsyncMock()
    # Return mock WAV audio data
    tts.text_to_speech = AsyncMock(return_value=b"fake_wav_audio_data")
    return tts


@pytest.fixture
def orchestrator(mock_stt_module, mock_llm_module, mock_tts_module):
    """Create orchestrator instance with mocked modules"""
    from orchestrator import AgentOrchestrator
    
    return AgentOrchestrator(
        stt_module=mock_stt_module,
        llm_module=mock_llm_module,
        tts_module=mock_tts_module,
        max_history=5,
        default_language="en-IN"
    )
