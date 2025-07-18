"""
Enhanced input validation and sanitization utilities for FOCUS Generator.
"""

import re
import html
import bleach
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, validator, Field
from datetime import datetime, date

# Security constants
MAX_STRING_LENGTH = 1000
MAX_ARRAY_LENGTH = 100
ALLOWED_HTML_TAGS = []  # No HTML tags allowed
ALLOWED_FILENAME_CHARS = re.compile(r'^[a-zA-Z0-9._-]+$')


class ValidationError(Exception):
    """Custom validation error for security-related validation failures."""
    pass


def sanitize_string(value: str, max_length: int = MAX_STRING_LENGTH) -> str:
    """
    Sanitize string input to prevent XSS and injection attacks.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
        
    Raises:
        ValidationError: If string is too long or contains dangerous content
    """
    if not isinstance(value, str):
        raise ValidationError(f"Expected string, got {type(value)}")
    
    if len(value) > max_length:
        raise ValidationError(f"String too long: {len(value)} > {max_length}")
    
    # Remove/escape HTML
    sanitized = html.escape(value)
    
    # Use bleach for additional sanitization
    sanitized = bleach.clean(sanitized, tags=ALLOWED_HTML_TAGS, strip=True)
    
    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
    
    return sanitized.strip()


def validate_filename(filename: str) -> str:
    """
    Validate and sanitize filename to prevent path traversal attacks.
    
    Args:
        filename: Filename to validate
        
    Returns:
        Sanitized filename
        
    Raises:
        ValidationError: If filename is invalid
    """
    if not filename:
        raise ValidationError("Filename cannot be empty")
    
    if len(filename) > 255:
        raise ValidationError("Filename too long")
    
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        raise ValidationError("Filename contains invalid characters")
    
    # Check for allowed characters only
    if not ALLOWED_FILENAME_CHARS.match(filename):
        raise ValidationError("Filename contains invalid characters")
    
    return filename


def validate_numeric_range(value: Union[int, float], 
                          min_val: Union[int, float], 
                          max_val: Union[int, float],
                          field_name: str = "value") -> Union[int, float]:
    """
    Validate numeric value is within allowed range.
    
    Args:
        value: Numeric value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        field_name: Name of field for error messages
        
    Returns:
        Validated value
        
    Raises:
        ValidationError: If value is out of range
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{field_name} must be a number")
    
    if value < min_val or value > max_val:
        raise ValidationError(f"{field_name} must be between {min_val} and {max_val}")
    
    return value


def validate_array_length(array: List[Any], 
                         max_length: int = MAX_ARRAY_LENGTH,
                         field_name: str = "array") -> List[Any]:
    """
    Validate array length to prevent DoS attacks.
    
    Args:
        array: Array to validate
        max_length: Maximum allowed length
        field_name: Name of field for error messages
        
    Returns:
        Validated array
        
    Raises:
        ValidationError: If array is too long
    """
    if not isinstance(array, list):
        raise ValidationError(f"{field_name} must be an array")
    
    if len(array) > max_length:
        raise ValidationError(f"{field_name} too long: {len(array)} > {max_length}")
    
    return array


def validate_enum_value(value: str, 
                       allowed_values: List[str], 
                       field_name: str = "value") -> str:
    """
    Validate enum value against allowed list.
    
    Args:
        value: Value to validate
        allowed_values: List of allowed values
        field_name: Name of field for error messages
        
    Returns:
        Validated value
        
    Raises:
        ValidationError: If value is not in allowed list
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    # Sanitize first
    sanitized_value = sanitize_string(value)
    
    if sanitized_value not in allowed_values:
        raise ValidationError(f"{field_name} must be one of: {allowed_values}")
    
    return sanitized_value


def validate_json_object(obj: Dict[str, Any], 
                        max_depth: int = 5,
                        max_keys: int = 100) -> Dict[str, Any]:
    """
    Validate JSON object to prevent DoS attacks.
    
    Args:
        obj: JSON object to validate
        max_depth: Maximum nesting depth
        max_keys: Maximum number of keys
        
    Returns:
        Validated object
        
    Raises:
        ValidationError: If object is invalid
    """
    if not isinstance(obj, dict):
        raise ValidationError("Must be a JSON object")
    
    def count_keys(d: Dict[str, Any], depth: int = 0) -> int:
        if depth > max_depth:
            raise ValidationError(f"JSON object too deeply nested (max depth: {max_depth})")
        
        key_count = len(d)
        for value in d.values():
            if isinstance(value, dict):
                key_count += count_keys(value, depth + 1)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        key_count += count_keys(item, depth + 1)
        
        return key_count
    
    total_keys = count_keys(obj)
    if total_keys > max_keys:
        raise ValidationError(f"JSON object too large: {total_keys} keys > {max_keys}")
    
    return obj


class SecurityValidationMixin:
    """Mixin class for enhanced security validation."""
    
    @validator('*', pre=True)
    def sanitize_strings(cls, v):
        """Sanitize all string inputs."""
        if isinstance(v, str):
            return sanitize_string(v)
        return v