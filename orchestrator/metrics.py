"""
Metrics Collector - Tracks performance metrics for the orchestrator
"""

import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class TurnMetrics:
    """Metrics for a single conversation turn"""
    stt_latency: float
    llm_latency: float
    tts_latency: float
    total_latency: float
    language: str
    timestamp: float = field(default_factory=time.time)
    success: bool = True
    error_type: Optional[str] = None


class MetricsCollector:
    """
    Collects and aggregates performance metrics for the orchestrator
    """
    
    def __init__(self, max_metrics: int = 1000):
        """
        Initialize metrics collector
        
        Args:
            max_metrics: Maximum number of metrics to keep in memory (default: 1000)
        """
        self.turn_metrics: List[TurnMetrics] = []
        self.max_metrics = max_metrics
    
    def record_turn(
        self,
        stt_time: float,
        llm_time: float,
        tts_time: float,
        language: str,
        success: bool = True,
        error_type: Optional[str] = None
    ):
        """
        Record metrics for a conversation turn
        
        Args:
            stt_time: STT processing time in seconds
            llm_time: LLM processing time in seconds
            tts_time: TTS processing time in seconds
            language: Language code used
            success: Whether the turn was successful
            error_type: Type of error if unsuccessful
        """
        total = stt_time + llm_time + tts_time
        
        metrics = TurnMetrics(
            stt_latency=stt_time,
            llm_latency=llm_time,
            tts_latency=tts_time,
            total_latency=total,
            language=language,
            timestamp=time.time(),
            success=success,
            error_type=error_type
        )
        
        self.turn_metrics.append(metrics)
        
        # Maintain max_metrics limit
        if len(self.turn_metrics) > self.max_metrics:
            self.turn_metrics = self.turn_metrics[-self.max_metrics:]
        
        logger.debug(f"📈 Metrics recorded - STT: {stt_time:.2f}s, LLM: {llm_time:.2f}s, TTS: {tts_time:.2f}s, Total: {total:.2f}s")
    
    def get_average_latencies(self) -> Dict[str, float]:
        """
        Get average latencies across all recorded turns
        
        Returns:
            Dictionary with average latencies for STT, LLM, TTS, and total
        """
        if not self.turn_metrics:
            return {
                "stt": 0.0,
                "llm": 0.0,
                "tts": 0.0,
                "total": 0.0
            }
        
        count = len(self.turn_metrics)
        return {
            "stt": sum(m.stt_latency for m in self.turn_metrics) / count,
            "llm": sum(m.llm_latency for m in self.turn_metrics) / count,
            "tts": sum(m.tts_latency for m in self.turn_metrics) / count,
            "total": sum(m.total_latency for m in self.turn_metrics) / count
        }
    
    def get_language_statistics(self) -> Dict[str, Dict[str, float]]:
        """
        Get statistics grouped by language
        
        Returns:
            Dictionary mapping language codes to their average latencies
        """
        language_stats = {}
        
        for metric in self.turn_metrics:
            lang = metric.language
            if lang not in language_stats:
                language_stats[lang] = {
                    "count": 0,
                    "stt_sum": 0.0,
                    "llm_sum": 0.0,
                    "tts_sum": 0.0,
                    "total_sum": 0.0
                }
            
            stats = language_stats[lang]
            stats["count"] += 1
            stats["stt_sum"] += metric.stt_latency
            stats["llm_sum"] += metric.llm_latency
            stats["tts_sum"] += metric.tts_latency
            stats["total_sum"] += metric.total_latency
        
        # Calculate averages
        result = {}
        for lang, stats in language_stats.items():
            count = stats["count"]
            result[lang] = {
                "count": count,
                "stt_avg": stats["stt_sum"] / count,
                "llm_avg": stats["llm_sum"] / count,
                "tts_avg": stats["tts_sum"] / count,
                "total_avg": stats["total_sum"] / count
            }
        
        return result
    
    def get_success_rate(self) -> float:
        """
        Get success rate (percentage of successful turns)
        
        Returns:
            Success rate as a float between 0.0 and 1.0
        """
        if not self.turn_metrics:
            return 1.0
        
        successful = sum(1 for m in self.turn_metrics if m.success)
        return successful / len(self.turn_metrics)
    
    def get_error_statistics(self) -> Dict[str, int]:
        """
        Get error statistics by error type
        
        Returns:
            Dictionary mapping error types to their counts
        """
        error_counts = {}
        for metric in self.turn_metrics:
            if not metric.success and metric.error_type:
                error_counts[metric.error_type] = error_counts.get(metric.error_type, 0) + 1
        return error_counts
    
    def generate_report(self) -> str:
        """
        Generate a formatted performance report
        
        Returns:
            Formatted report string
        """
        if not self.turn_metrics:
            return "No metrics recorded yet."
        
        averages = self.get_average_latencies()
        success_rate = self.get_success_rate()
        lang_stats = self.get_language_statistics()
        error_stats = self.get_error_statistics()
        
        report = f"""
📊 Performance Metrics Report
{'=' * 50}
Total Turns: {len(self.turn_metrics)}
Success Rate: {success_rate * 100:.1f}%

Average Latencies:
  - STT: {averages['stt']:.2f}s
  - LLM: {averages['llm']:.2f}s
  - TTS: {averages['tts']:.2f}s
  - Total: {averages['total']:.2f}s

Language Statistics:
"""
        for lang, stats in lang_stats.items():
            report += f"  {lang} ({stats['count']} turns):\n"
            report += f"    - STT: {stats['stt_avg']:.2f}s\n"
            report += f"    - LLM: {stats['llm_avg']:.2f}s\n"
            report += f"    - TTS: {stats['tts_avg']:.2f}s\n"
            report += f"    - Total: {stats['total_avg']:.2f}s\n"
        
        if error_stats:
            report += "\nError Statistics:\n"
            for error_type, count in error_stats.items():
                report += f"  - {error_type}: {count}\n"
        
        return report
    
    def reset(self):
        """Clear all metrics"""
        self.turn_metrics.clear()
        logger.info("📊 Metrics reset")
