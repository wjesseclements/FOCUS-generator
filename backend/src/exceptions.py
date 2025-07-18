"""
Custom exception classes for the FOCUS Generator application.

This module provides a hierarchy of domain-specific exceptions that provide
better error context and enable more precise error handling throughout the application.
"""

from typing import Dict, Any, Optional, List


class FocusGeneratorError(Exception):
    """Base exception for all FOCUS Generator errors.
    
    All custom exceptions in the application should inherit from this base class.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class ValidationError(FocusGeneratorError):
    """Raised when data validation fails.
    
    This exception should be used for all validation-related errors,
    including schema validation, data type validation, and constraint validation.
    """
    
    def __init__(self, message: str, column: Optional[str] = None, 
                 value: Optional[Any] = None, constraint: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.column = column
        self.value = value
        self.constraint = constraint
        
        validation_details = {
            "column": column,
            "value": value,
            "constraint": constraint,
            **(details or {})
        }
        
        super().__init__(message, validation_details)


class DataGenerationError(FocusGeneratorError):
    """Raised when data generation fails.
    
    This includes errors during FOCUS data generation, profile processing,
    and data transformation operations.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None,
                 parameters: Optional[Dict[str, Any]] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.operation = operation
        self.parameters = parameters
        
        generation_details = {
            "operation": operation,
            "parameters": parameters,
            **(details or {})
        }
        
        super().__init__(message, generation_details)


class FileOperationError(FocusGeneratorError):
    """Raised when file operations fail.
    
    This includes errors during file creation, reading, writing, compression,
    and cleanup operations.
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 operation: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.file_path = file_path
        self.operation = operation
        
        file_details = {
            "file_path": file_path,
            "operation": operation,
            **(details or {})
        }
        
        super().__init__(message, file_details)


class ConfigurationError(FocusGeneratorError):
    """Raised when configuration is invalid or missing.
    
    This includes errors related to settings, environment variables,
    and application configuration.
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_value: Optional[Any] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.config_key = config_key
        self.config_value = config_value
        
        config_details = {
            "config_key": config_key,
            "config_value": config_value,
            **(details or {})
        }
        
        super().__init__(message, config_details)


class ResourceLimitError(FocusGeneratorError):
    """Raised when resource limits are exceeded.
    
    This includes errors related to file size limits, memory limits,
    processing time limits, and rate limits.
    """
    
    def __init__(self, message: str, resource_type: Optional[str] = None,
                 current_value: Optional[Any] = None, 
                 limit_value: Optional[Any] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.resource_type = resource_type
        self.current_value = current_value
        self.limit_value = limit_value
        
        resource_details = {
            "resource_type": resource_type,
            "current_value": current_value,
            "limit_value": limit_value,
            **(details or {})
        }
        
        super().__init__(message, resource_details)


class StreamingError(FocusGeneratorError):
    """Raised when streaming operations fail.
    
    This includes errors during CSV streaming, data buffering,
    and streaming-related I/O operations.
    """
    
    def __init__(self, message: str, stream_position: Optional[int] = None,
                 operation: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.stream_position = stream_position
        self.operation = operation
        
        streaming_details = {
            "stream_position": stream_position,
            "operation": operation,
            **(details or {})
        }
        
        super().__init__(message, streaming_details)


class SecurityError(FocusGeneratorError):
    """Raised when security violations are detected.
    
    This includes errors related to input sanitization, CSRF protection,
    and security policy violations.
    """
    
    def __init__(self, message: str, security_type: Optional[str] = None,
                 violation_details: Optional[Dict[str, Any]] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.security_type = security_type
        self.violation_details = violation_details
        
        security_details = {
            "security_type": security_type,
            "violation_details": violation_details,
            **(details or {})
        }
        
        super().__init__(message, security_details)


class RateLimitError(FocusGeneratorError):
    """Raised when rate limits are exceeded.
    
    This is a specialized resource limit error for rate limiting scenarios.
    """
    
    def __init__(self, message: str, limit_type: str, 
                 current_count: int, limit_count: int,
                 reset_time: Optional[float] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.limit_type = limit_type
        self.current_count = current_count
        self.limit_count = limit_count
        self.reset_time = reset_time
        
        rate_limit_details = {
            "limit_type": limit_type,
            "current_count": current_count,
            "limit_count": limit_count,
            "reset_time": reset_time,
            **(details or {})
        }
        
        super().__init__(message, rate_limit_details)


class ExternalServiceError(FocusGeneratorError):
    """Raised when external service calls fail.
    
    This includes errors when communicating with AWS S3, Redis,
    or other external dependencies.
    """
    
    def __init__(self, message: str, service_name: Optional[str] = None,
                 operation: Optional[str] = None, 
                 status_code: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.service_name = service_name
        self.operation = operation
        self.status_code = status_code
        
        service_details = {
            "service_name": service_name,
            "operation": operation,
            "status_code": status_code,
            **(details or {})
        }
        
        super().__init__(message, service_details)


# Convenience functions for common error scenarios
def validation_error(message: str, column: str, value: Any, constraint: str) -> ValidationError:
    """Create a validation error with standard formatting."""
    return ValidationError(
        f"Validation failed for column '{column}': {message}",
        column=column,
        value=value,
        constraint=constraint
    )


def file_operation_error(message: str, file_path: str, operation: str) -> FileOperationError:
    """Create a file operation error with standard formatting."""
    return FileOperationError(
        f"File operation '{operation}' failed: {message}",
        file_path=file_path,
        operation=operation
    )


def resource_limit_error(resource_type: str, current: Any, limit: Any) -> ResourceLimitError:
    """Create a resource limit error with standard formatting."""
    return ResourceLimitError(
        f"Resource limit exceeded for {resource_type}: {current} > {limit}",
        resource_type=resource_type,
        current_value=current,
        limit_value=limit
    )