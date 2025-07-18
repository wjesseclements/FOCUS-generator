"""
Retry utilities for handling transient failures in the FOCUS Generator.

This module provides decorators and functions for implementing retry logic
with exponential backoff for operations that may fail temporarily.
"""

import time
import random
import logging
from typing import TypeVar, Callable, Any, Optional, Type, Tuple
from functools import wraps

from exceptions import FocusGeneratorError, ExternalServiceError, FileOperationError
from logging_config import setup_logging

logger = setup_logging(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (
            FileOperationError,
            ExternalServiceError,
            ConnectionError,
            TimeoutError
        )
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt with exponential backoff."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add random jitter to prevent thundering herd
            delay += random.uniform(0, delay * 0.1)
        
        return delay
    
    def is_retryable(self, exception: Exception) -> bool:
        """Check if an exception is retryable."""
        return isinstance(exception, self.retryable_exceptions)


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    operation_name: Optional[str] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying functions with exponential backoff."""
    
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            op_name = operation_name or func.__name__
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    if attempt > 0:
                        logger.info(f"Retrying {op_name} (attempt {attempt + 1}/{config.max_attempts})")
                    
                    result = func(*args, **kwargs)
                    
                    if attempt > 0:
                        logger.info(f"Success on retry for {op_name} (attempt {attempt + 1})")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if not config.is_retryable(e):
                        logger.error(f"Non-retryable error in {op_name}: {str(e)}")
                        raise
                    
                    if attempt == config.max_attempts - 1:
                        logger.error(f"Max retries exceeded for {op_name}: {str(e)}")
                        raise
                    
                    delay = config.calculate_delay(attempt)
                    logger.warning(
                        f"Retryable error in {op_name} (attempt {attempt + 1}/{config.max_attempts}): "
                        f"{str(e)}, retrying in {delay:.2f}s"
                    )
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def retry_async_with_backoff(
    config: Optional[RetryConfig] = None,
    operation_name: Optional[str] = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for retrying async functions with exponential backoff."""
    
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            import asyncio
            
            op_name = operation_name or func.__name__
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    if attempt > 0:
                        logger.info(f"Retrying {op_name} (attempt {attempt + 1}/{config.max_attempts})")
                    
                    result = await func(*args, **kwargs)
                    
                    if attempt > 0:
                        logger.info(f"Success on retry for {op_name} (attempt {attempt + 1})")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if not config.is_retryable(e):
                        logger.error(f"Non-retryable error in {op_name}: {str(e)}")
                        raise
                    
                    if attempt == config.max_attempts - 1:
                        logger.error(f"Max retries exceeded for {op_name}: {str(e)}")
                        raise
                    
                    delay = config.calculate_delay(attempt)
                    logger.warning(
                        f"Retryable error in {op_name} (attempt {attempt + 1}/{config.max_attempts}): "
                        f"{str(e)}, retrying in {delay:.2f}s"
                    )
                    
                    await asyncio.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def execute_with_retry(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    operation_name: Optional[str] = None,
    *args,
    **kwargs
) -> T:
    """Execute a function with retry logic without using a decorator."""
    
    if config is None:
        config = RetryConfig()
    
    op_name = operation_name or func.__name__
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            if attempt > 0:
                logger.info(f"Retrying {op_name} (attempt {attempt + 1}/{config.max_attempts})")
            
            result = func(*args, **kwargs)
            
            if attempt > 0:
                logger.info(f"Success on retry for {op_name} (attempt {attempt + 1})")
            
            return result
            
        except Exception as e:
            last_exception = e
            
            if not config.is_retryable(e):
                logger.error(f"Non-retryable error in {op_name}: {str(e)}")
                raise
            
            if attempt == config.max_attempts - 1:
                logger.error(f"Max retries exceeded for {op_name}: {str(e)}")
                raise
            
            delay = config.calculate_delay(attempt)
            logger.warning(
                f"Retryable error in {op_name} (attempt {attempt + 1}/{config.max_attempts}): "
                f"{str(e)}, retrying in {delay:.2f}s"
            )
            
            time.sleep(delay)
    
    # This should never be reached, but just in case
    raise last_exception


# Predefined retry configurations for common scenarios
FILE_OPERATION_RETRY = RetryConfig(
    max_attempts=3,
    base_delay=0.5,
    max_delay=5.0,
    retryable_exceptions=(FileOperationError, OSError, IOError)
)

EXTERNAL_SERVICE_RETRY = RetryConfig(
    max_attempts=5,
    base_delay=1.0,
    max_delay=30.0,
    retryable_exceptions=(ExternalServiceError, ConnectionError, TimeoutError)
)

FAST_RETRY = RetryConfig(
    max_attempts=2,
    base_delay=0.1,
    max_delay=1.0
)

SLOW_RETRY = RetryConfig(
    max_attempts=5,
    base_delay=2.0,
    max_delay=120.0
)


# Circuit breaker pattern for preventing cascading failures
class CircuitBreaker:
    """Circuit breaker for preventing cascading failures."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "HALF_OPEN"
                    logger.info(f"Circuit breaker for {func.__name__} is now HALF_OPEN")
                else:
                    raise ExternalServiceError(
                        f"Circuit breaker is OPEN for {func.__name__}",
                        service_name=func.__name__,
                        operation="circuit_breaker_check"
                    )
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise
        
        return wrapper
    
    def _on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            logger.info("Circuit breaker is now CLOSED")
    
    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker is now OPEN (failures: {self.failure_count})")