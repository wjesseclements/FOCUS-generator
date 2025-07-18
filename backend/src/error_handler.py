"""
Centralized error handling for the FOCUS Generator application.

This module provides a consistent way to handle, log, and respond to errors
throughout the application, with proper correlation IDs and structured error responses.
"""

import uuid
import logging
from typing import Dict, Any, Optional, Tuple
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from exceptions import (
    FocusGeneratorError, ValidationError, DataGenerationError, 
    FileOperationError, ConfigurationError, ResourceLimitError,
    StreamingError, SecurityError, RateLimitError, ExternalServiceError
)
from logging_config import setup_logging

logger = setup_logging(__name__)


class ErrorHandler:
    """Centralized error handler for the FOCUS Generator application."""
    
    @staticmethod
    def generate_error_id() -> str:
        """Generate a unique error ID for correlation."""
        return str(uuid.uuid4())[:8]
    
    @staticmethod
    def log_error(error: Exception, error_id: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an error with standardized format and correlation ID."""
        log_context = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        # Add specific details for custom exceptions
        if isinstance(error, FocusGeneratorError):
            log_context["error_details"] = error.details
        
        logger.error(f"Error {error_id}: {str(error)}", extra=log_context)
    
    @staticmethod
    def create_error_response(
        error: Exception, 
        error_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """Create a standardized error response."""
        
        # Base error response
        error_response = {
            "error": True,
            "error_id": error_id,
            "message": str(error),
            "type": type(error).__name__
        }
        
        # Add context if provided
        if context:
            error_response["context"] = context
            
        # Add specific details for custom exceptions
        if isinstance(error, FocusGeneratorError):
            error_response["details"] = error.details
        
        # Map exception types to HTTP status codes
        status_code = ErrorHandler._get_status_code(error)
        
        return status_code, error_response
    
    @staticmethod
    def _get_status_code(error: Exception) -> int:
        """Map exception types to appropriate HTTP status codes."""
        
        if isinstance(error, ValidationError):
            return 400  # Bad Request
        elif isinstance(error, SecurityError):
            return 403  # Forbidden
        elif isinstance(error, RateLimitError):
            return 429  # Too Many Requests
        elif isinstance(error, ResourceLimitError):
            return 413  # Payload Too Large
        elif isinstance(error, ConfigurationError):
            return 500  # Internal Server Error
        elif isinstance(error, FileOperationError):
            return 500  # Internal Server Error
        elif isinstance(error, StreamingError):
            return 500  # Internal Server Error
        elif isinstance(error, DataGenerationError):
            return 500  # Internal Server Error
        elif isinstance(error, ExternalServiceError):
            return 502  # Bad Gateway
        else:
            return 500  # Internal Server Error
    
    @staticmethod
    def handle_error(
        error: Exception, 
        context: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """Handle an error and return an appropriate HTTPException."""
        
        error_id = ErrorHandler.generate_error_id()
        
        # Log the error
        ErrorHandler.log_error(error, error_id, context)
        
        # Create error response
        status_code, error_response = ErrorHandler.create_error_response(
            error, error_id, context
        )
        
        return HTTPException(status_code=status_code, detail=error_response)
    
    @staticmethod
    def handle_error_response(
        error: Exception, 
        context: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Handle an error and return a JSONResponse directly."""
        
        error_id = ErrorHandler.generate_error_id()
        
        # Log the error
        ErrorHandler.log_error(error, error_id, context)
        
        # Create error response
        status_code, error_response = ErrorHandler.create_error_response(
            error, error_id, context
        )
        
        return JSONResponse(
            status_code=status_code, 
            content=error_response
        )


def handle_validation_error(
    message: str, 
    column: Optional[str] = None, 
    value: Optional[Any] = None,
    constraint: Optional[str] = None
) -> HTTPException:
    """Convenience function for handling validation errors."""
    
    error = ValidationError(
        message=message,
        column=column,
        value=value,
        constraint=constraint
    )
    
    return ErrorHandler.handle_error(error)


def handle_resource_limit_error(
    resource_type: str, 
    current_value: Any, 
    limit_value: Any
) -> HTTPException:
    """Convenience function for handling resource limit errors."""
    
    error = ResourceLimitError(
        message=f"Resource limit exceeded for {resource_type}",
        resource_type=resource_type,
        current_value=current_value,
        limit_value=limit_value
    )
    
    return ErrorHandler.handle_error(error)


def handle_file_operation_error(
    message: str, 
    file_path: str, 
    operation: str
) -> HTTPException:
    """Convenience function for handling file operation errors."""
    
    error = FileOperationError(
        message=message,
        file_path=file_path,
        operation=operation
    )
    
    return ErrorHandler.handle_error(error)


def handle_data_generation_error(
    message: str, 
    operation: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Convenience function for handling data generation errors."""
    
    error = DataGenerationError(
        message=message,
        operation=operation,
        parameters=parameters
    )
    
    return ErrorHandler.handle_error(error)


# Context manager for error handling
class ErrorContext:
    """Context manager for consistent error handling."""
    
    def __init__(self, operation: str, context: Optional[Dict[str, Any]] = None):
        self.operation = operation
        self.context = context or {}
        self.error_id = ErrorHandler.generate_error_id()
    
    def __enter__(self):
        logger.info(f"Starting operation: {self.operation}", extra={
            "operation": self.operation,
            "context": self.context,
            "error_id": self.error_id
        })
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the error with context
            ErrorHandler.log_error(
                exc_val, 
                self.error_id, 
                {**self.context, "operation": self.operation}
            )
        else:
            logger.info(f"Completed operation: {self.operation}", extra={
                "operation": self.operation,
                "context": self.context,
                "error_id": self.error_id
            })
        
        # Don't suppress exceptions
        return False


# Decorator for automatic error handling
def handle_errors(operation: str, context: Optional[Dict[str, Any]] = None):
    """Decorator for automatic error handling in functions."""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                with ErrorContext(operation, context):
                    return func(*args, **kwargs)
            except Exception as e:
                # Re-raise as HTTPException for FastAPI endpoints
                if hasattr(e, 'status_code'):
                    raise e
                raise ErrorHandler.handle_error(e, context)
        return wrapper
    return decorator