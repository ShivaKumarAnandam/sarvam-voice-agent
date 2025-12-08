"""
Circuit Breaker - Protects against cascading failures
"""

import time
from typing import Callable, Any, Optional
from loguru import logger


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for protecting against cascading failures.
    Opens circuit after failure_threshold failures, closes after timeout.
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit (default: 5)
            timeout: Time in seconds before attempting to close circuit (default: 60)
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.state = "closed"  # closed, open, half_open
        self.last_failure_time = 0.0
        self.success_count = 0
        self.half_open_success_threshold = 2  # Need 2 successes to close from half-open
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call a function with circuit breaker protection
        
        Args:
            func: Async function to call
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func
            
        Raises:
            CircuitBreakerOpen: If circuit is open
        """
        # Check circuit state
        if self.state == "open":
            # Check if timeout has passed
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
                self.success_count = 0
                logger.info("🔄 Circuit breaker: OPEN → HALF_OPEN (timeout passed)")
            else:
                raise CircuitBreakerOpen(
                    f"Circuit breaker is OPEN. Retry after {self.timeout - (time.time() - self.last_failure_time):.0f} seconds"
                )
        
        # Try to execute function
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == "half_open":
                self.success_count += 1
                if self.success_count >= self.half_open_success_threshold:
                    self.state = "closed"
                    self.failure_count = 0
                    logger.info("✅ Circuit breaker: HALF_OPEN → CLOSED (success threshold reached)")
            elif self.state == "closed":
                self.failure_count = 0  # Reset on success
            
            return result
            
        except Exception as e:
            # Failure - increment failure count
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.warning(f"⚠️ Circuit breaker: CLOSED → OPEN (failure threshold reached: {self.failure_count})")
            elif self.state == "half_open":
                self.state = "open"
                logger.warning(f"⚠️ Circuit breaker: HALF_OPEN → OPEN (failure occurred)")
            
            # Re-raise the original exception
            raise
    
    def get_state(self) -> dict:
        """
        Get current circuit breaker state
        
        Returns:
            Dictionary with state information
        """
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout,
            "last_failure_time": self.last_failure_time,
            "time_until_retry": max(0, self.timeout - (time.time() - self.last_failure_time)) if self.state == "open" else 0
        }
    
    def reset(self):
        """Manually reset circuit breaker to closed state"""
        self.state = "closed"
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        logger.info("🔄 Circuit breaker manually reset to CLOSED")
