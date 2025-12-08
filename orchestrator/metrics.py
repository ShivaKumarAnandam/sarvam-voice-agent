"""
Metrics collection utilities for measuring orchestrator latency.
Optional helper used by AgentOrchestrator to record per-turn timings.
"""

from dataclasses import dataclass
from typing import List, Dict
import time
from loguru import logger


@dataclass
class TurnMetrics:
    """Holds timing information for one conversation turn."""
    stt_latency: float
    llm_latency: float
    tts_latency: float
    total_latency: float
    language: str
    timestamp: float


class MetricsCollector:
    """Collects latency metrics for conversation turns."""

    def __init__(self):
        self.turn_metrics: List[TurnMetrics] = []

    def record_turn(
        self,
        stt_time: float,
        llm_time: float,
        tts_time: float,
        language: str,
    ):
        """Store metrics for a single turn."""
        total = stt_time + llm_time + tts_time
        metrics = TurnMetrics(
            stt_latency=stt_time,
            llm_latency=llm_time,
            tts_latency=tts_time,
            total_latency=total,
            language=language,
            timestamp=time.time(),
        )
        self.turn_metrics.append(metrics)
        logger.debug(
            f"📈 Metrics recorded - STT: {stt_time:.2f}s, "
            f"LLM: {llm_time:.2f}s, TTS: {tts_time:.2f}s, "
            f"Total: {total:.2f}s, Lang: {language}"
        )

    def get_average_latencies(self) -> Dict[str, float]:
        """Compute average latencies over collected turns."""
        if not self.turn_metrics:
            return {"stt": 0.0, "llm": 0.0, "tts": 0.0, "total": 0.0}

        count = len(self.turn_metrics)
        stt_avg = sum(m.stt_latency for m in self.turn_metrics) / count
        llm_avg = sum(m.llm_latency for m in self.turn_metrics) / count
        tts_avg = sum(m.tts_latency for m in self.turn_metrics) / count
        total_avg = sum(m.total_latency for m in self.turn_metrics) / count

        return {"stt": stt_avg, "llm": llm_avg, "tts": tts_avg, "total": total_avg}

    def generate_report(self) -> str:
        """Create a human-readable summary report."""
        averages = self.get_average_latencies()
        return (
            "Performance Metrics\n"
            f"- STT avg: {averages['stt']:.2f}s\n"
            f"- LLM avg: {averages['llm']:.2f}s\n"
            f"- TTS avg: {averages['tts']:.2f}s\n"
            f"- Total avg: {averages['total']:.2f}s\n"
            f"- Turns counted: {len(self.turn_metrics)}"
        )

    def reset(self):
        """Clear all recorded metrics."""
        self.turn_metrics = []
        logger.debug("📊 MetricsCollector reset")

