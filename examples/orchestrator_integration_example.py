"""
Example: How to integrate Agent Orchestrator with existing Twilio server

This example shows how to use the orchestrator in your existing twilio_server.py
without disturbing the current implementation.
"""

import asyncio
from fastapi import WebSocket
from loguru import logger

# Import orchestrator components
from orchestrator import AgentOrchestrator, MetricsCollector
from sarvam_ai import SarvamAI
from audio_utils import mulaw_to_wav, wav_to_mulaw, encode_mulaw_base64
import json


async def example_media_stream_with_orchestrator(websocket: WebSocket):
    """
    Example WebSocket handler using Agent Orchestrator
    
    This replaces the inline orchestration logic in twilio_server.py
    """
    await websocket.accept()
    
    # Get selected language from query params
    query_params = dict(websocket.query_params)
    selected_language = query_params.get("lang", "te-IN")
    logger.info(f"🔌 WebSocket connected with language: {selected_language}")
    
    # Initialize Sarvam AI (STT, LLM, TTS all use same instance)
    try:
        sarvam = SarvamAI()
    except ValueError as e:
        logger.error(f"❌ Failed to initialize Sarvam AI: {e}")
        await websocket.close(code=1011, reason="Configuration error")
        return
    
    # Initialize orchestrator with metrics
    metrics_collector = MetricsCollector()
    
    # Create system prompt for electrical department
    system_prompt = """You are a helpful customer support agent for the Electrical Department in India.

Your responsibilities:
- Handle electrical complaints (power outages, voltage issues, meter problems)
- Provide information about electricity bills and payments
- Help with new connection requests
- Report electrical hazards and emergencies
- Provide lineman contact numbers and department information

Guidelines:
- Keep responses SHORT and CONCISE (2-3 sentences maximum for voice calls)
- Be professional, polite, and helpful
- Ask ONE clear question at a time
- If you don't have specific information, acknowledge briefly and offer to connect to a human agent
- For emergencies, prioritize safety and provide emergency contact: 1912"""
    
    orchestrator = AgentOrchestrator(
        stt_module=sarvam,
        llm_module=sarvam,
        tts_module=sarvam,
        max_history=10,
        default_language=selected_language,
        system_prompt=system_prompt,
        metrics_collector=metrics_collector,
        enable_circuit_breaker=True
    )
    
    # Set initial language
    orchestrator.set_language(selected_language)
    
    stream_sid = None
    stream_ready = False
    
    # Voice Activity Detection (VAD) settings
    audio_buffer = bytearray()
    is_speaking = False
    silence_threshold = 1600  # ~200ms of silence at 8kHz
    silence_buffer = bytearray()
    min_speech_length = 4000  # Minimum 0.5 seconds of speech
    
    async def process_speech_buffer():
        """Process accumulated speech buffer using orchestrator"""
        nonlocal is_speaking, audio_buffer, silence_buffer
        
        if len(audio_buffer) < min_speech_length:
            logger.warning(f"⚠️ Speech too short ({len(audio_buffer)} bytes), ignoring")
            audio_buffer.clear()
            silence_buffer.clear()
            is_speaking = False
            return
        
        logger.info(f"🔊 Processing {len(audio_buffer)} bytes of speech")
        
        # Convert to WAV
        mulaw_bytes = bytes(audio_buffer)
        wav_data = mulaw_to_wav(mulaw_bytes)
        
        # Reset buffers
        audio_buffer.clear()
        silence_buffer.clear()
        is_speaking = False
        
        if not wav_data or len(wav_data) < 100:
            logger.warning("⚠️ WAV conversion failed or too small")
            return
        
        # Use orchestrator to process turn
        try:
            result = await orchestrator.process_turn(wav_data)
            
            if result.get("error"):
                logger.error(f"❌ Orchestrator error: {result['error']}")
                return
            
            if not result.get("audio"):
                logger.warning("⚠️ No audio generated")
                return
            
            # Convert WAV to mulaw for Twilio
            response_mulaw = wav_to_mulaw(result["audio"])
            
            if not response_mulaw:
                logger.error("❌ Failed to convert TTS to mulaw")
                return
            
            # Stream audio in chunks
            chunk_size = 160  # 20ms chunks at 8kHz
            for i in range(0, len(response_mulaw), chunk_size):
                if websocket.client_state.name != "CONNECTED":
                    logger.warning("⚠️ WebSocket disconnected, stopping audio send")
                    break
                
                chunk = response_mulaw[i:i+chunk_size]
                encoded = encode_mulaw_base64(chunk)
                
                media_msg = {
                    "event": "media",
                    "streamSid": stream_sid,
                    "media": {"payload": encoded}
                }
                
                try:
                    await websocket.send_text(json.dumps(media_msg))
                    await asyncio.sleep(0.02)  # 20ms delay
                except Exception as send_error:
                    logger.warning(f"⚠️ Failed to send audio chunk: {send_error}")
                    break
            
            # Log metrics if available
            if result.get("metrics"):
                metrics = result["metrics"]
                logger.info(
                    f"⏱️ Turn completed - STT: {metrics['stt_time']:.2f}s, "
                    f"LLM: {metrics['llm_time']:.2f}s, TTS: {metrics['tts_time']:.2f}s, "
                    f"Total: {metrics['total_time']:.2f}s"
                )
                
        except Exception as e:
            logger.error(f"❌ Error processing turn: {e}")
    
    try:
        while True:
            data = await asyncio.wait_for(websocket.receive_text(), timeout=300.0)
            event = json.loads(data)
            
            event_type = event.get("event")
            
            if event_type == "start":
                stream_sid = event["start"]["streamSid"]
                stream_ready = True
                logger.info(f"🎙️ Stream started: {stream_sid}")
            
            elif event_type == "media":
                if not stream_ready or not stream_sid:
                    continue
                
                # Receive audio and buffer (VAD logic here)
                payload = event["media"]["payload"]
                mulaw_data = decode_mulaw_base64(payload)
                
                # Simple VAD: detect speech and buffer
                # (Your existing VAD logic here)
                audio_buffer.extend(mulaw_data)
                
                # When silence detected, process buffer
                # (Your existing silence detection logic here)
                if len(audio_buffer) >= min_speech_length:
                    await process_speech_buffer()
            
            elif event_type == "stop":
                logger.info("🛑 Stream stopped")
                break
    
    except asyncio.TimeoutError:
        logger.warning("⏱️ WebSocket timeout")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
    finally:
        # Print metrics report
        if metrics_collector:
            report = metrics_collector.generate_report()
            logger.info(f"\n{report}")
        
        await sarvam.close()
        if websocket.client_state.name == "CONNECTED":
            await websocket.close()


# Example: How to use orchestrator status endpoint
def get_orchestrator_status(orchestrator: AgentOrchestrator):
    """Get orchestrator status for monitoring"""
    status = orchestrator.get_status()
    return {
        "orchestrator": status,
        "metrics": orchestrator.metrics.get_average_latencies() if orchestrator.metrics else None
    }


if __name__ == "__main__":
    # Example usage
    print("This is an example integration file.")
    print("See twilio_server.py for actual implementation.")
    print("\nTo use the orchestrator:")
    print("1. Import AgentOrchestrator from orchestrator package")
    print("2. Initialize with STT, LLM, TTS modules")
    print("3. Call orchestrator.process_turn(audio_data) instead of inline logic")
    print("4. Handle the result dictionary with text, response, audio, language")
