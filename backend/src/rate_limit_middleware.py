import time
import json
from typing import Dict, Tuple, Any
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from logging_config import setup_logging

logger = setup_logging(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware using in-memory storage.
    
    For production, consider using Redis or another distributed cache.
    """
    
    def __init__(self, app, requests_per_hour: int = 100, requests_per_minute: int = 10):
        super().__init__(app)
        self.requests_per_hour = requests_per_hour
        self.requests_per_minute = requests_per_minute
        # Store request counts per IP
        self.hour_counts: Dict[str, int] = defaultdict(int)
        self.minute_counts: Dict[str, int] = defaultdict(int)
        # Store reset times
        self.hour_resets: Dict[str, float] = {}
        self.minute_resets: Dict[str, float] = {}
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for X-Forwarded-For header (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        # Check for X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        # Fall back to direct connection
        return request.client.host if request.client else "unknown"
    
    def check_rate_limit(self, client_ip: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if the request should be rate limited.
        
        Returns:
            (is_allowed, headers_dict)
        """
        current_time = time.time()
        
        # Clean up old entries
        self._cleanup_old_entries(current_time)
        
        # Check minute limit
        minute_reset = self.minute_resets.get(client_ip, current_time)
        if current_time > minute_reset:
            self.minute_counts[client_ip] = 0
            self.minute_resets[client_ip] = current_time + 60
        
        # Check hour limit
        hour_reset = self.hour_resets.get(client_ip, current_time)
        if current_time > hour_reset:
            self.hour_counts[client_ip] = 0
            self.hour_resets[client_ip] = current_time + 3600
        
        # Increment counts
        self.minute_counts[client_ip] += 1
        self.hour_counts[client_ip] += 1
        
        # Prepare rate limit headers
        headers = {
            "X-RateLimit-Limit-Minute": str(self.requests_per_minute),
            "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
            "X-RateLimit-Remaining-Minute": str(max(0, self.requests_per_minute - self.minute_counts.get(client_ip, 0))),
            "X-RateLimit-Remaining-Hour": str(max(0, self.requests_per_hour - self.hour_counts.get(client_ip, 0))),
            "X-RateLimit-Reset-Minute": str(int(self.minute_resets.get(client_ip, current_time + 60))),
            "X-RateLimit-Reset-Hour": str(int(self.hour_resets.get(client_ip, current_time + 3600)))
        }
        
        # Check if limits exceeded
        if self.minute_counts[client_ip] > self.requests_per_minute:
            headers["Retry-After"] = str(int(self.minute_resets[client_ip] - current_time))
            return False, headers
        
        if self.hour_counts[client_ip] > self.requests_per_hour:
            headers["Retry-After"] = str(int(self.hour_resets[client_ip] - current_time))
            return False, headers
        
        return True, headers
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove old entries to prevent memory leak."""
        # Clean up entries older than 1 hour
        cutoff_time = current_time - 3600
        
        # Clean hour data
        for ip in list(self.hour_resets.keys()):
            if self.hour_resets[ip] < cutoff_time:
                del self.hour_resets[ip]
                del self.hour_counts[ip]
        
        # Clean minute data
        for ip in list(self.minute_resets.keys()):
            if self.minute_resets[ip] < cutoff_time:
                del self.minute_resets[ip]
                del self.minute_counts[ip]
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and apply rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        client_ip = self.get_client_ip(request)
        is_allowed, headers = self.check_rate_limit(client_ip)
        
        if not is_allowed:
            logger.warning("Rate limit exceeded", extra={
                "client_ip": client_ip,
                "path": request.url.path,
                "method": request.method
            })
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded. Please try again later.",
                    "retry_after": int(headers.get("Retry-After", 60))
                },
                headers=headers
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
        
        return response