"""
Simple circuit breaker implementation to guard external API calls.
Currently not wired in by default; provided for future enhanced error handling.
"""

import time
from typing import Callable, Any


class CircuitBreakerOpen(Exception):
    """Raised when the circuit breaker is open."""


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Args:
            failure_threshold: Number of failures before opening the circuit
            timeout: Cooldown in seconds before allowing half-open attempts
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.state = "closed"  # closed, open, half_open
        self.last_failure_time = 0.0

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with circuit breaker protection."""
        now = time.time()

        if self.state == "open":
            if now - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpen("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            # Success path: reset on success
            self.failure_count = 0
            if self.state == "half_open":
                self.state = "closed"
            return result
        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise

