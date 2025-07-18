"""
Redis-based rate limiting middleware for production use.
"""

import time
import json
import redis
import asyncio
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from logging_config import setup_logging
from config import get_settings

logger = setup_logging(__name__)
settings = get_settings()


class RedisRateLimiter:
    """Redis-based rate limiter with sliding window."""
    
    def __init__(self, redis_client: redis.Redis, window_size: int = 3600):
        self.redis = redis_client
        self.window_size = window_size
    
    async def is_allowed(self, key: str, limit: int, window: int = None) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is allowed using sliding window rate limiting.
        
        Args:
            key: Rate limit key (typically IP address)
            limit: Maximum requests allowed
            window: Time window in seconds (defaults to window_size)
            
        Returns:
            (is_allowed, metadata_dict)
        """
        if window is None:
            window = self.window_size
            
        current_time = time.time()
        pipeline = self.redis.pipeline()
        
        # Remove old entries
        pipeline.zremrangebyscore(key, 0, current_time - window)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(current_time): current_time})
        
        # Set expiration
        pipeline.expire(key, window)
        
        # Execute pipeline
        try:
            results = pipeline.execute()
            current_requests = results[1]
            
            # Check if limit exceeded
            if current_requests >= limit:
                return False, {
                    "requests_made": current_requests,
                    "limit": limit,
                    "window": window,
                    "reset_time": current_time + window
                }
            
            return True, {
                "requests_made": current_requests + 1,
                "limit": limit,
                "window": window,
                "reset_time": current_time + window
            }
            
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiter: {e}")
            # Fail open - allow request if Redis is down
            return True, {
                "requests_made": 0,
                "limit": limit,
                "window": window,
                "reset_time": current_time + window,
                "error": "Redis unavailable"
            }


class EnhancedRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Enhanced rate limiting middleware with Redis backend and multiple limits.
    """
    
    def __init__(self, app, 
                 requests_per_minute: int = 10,
                 requests_per_hour: int = 100,
                 requests_per_day: int = 1000,
                 redis_url: str = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        
        # Initialize Redis client
        self.redis_client = None
        if redis_url or settings.is_production:
            try:
                redis_url = redis_url or settings.redis_url or "redis://localhost:6379"
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()  # Test connection
                logger.info("Redis rate limiter initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Redis: {e}")
                self.redis_client = None
        
        # Initialize rate limiters
        if self.redis_client:
            self.minute_limiter = RedisRateLimiter(self.redis_client, 60)
            self.hour_limiter = RedisRateLimiter(self.redis_client, 3600)
            self.day_limiter = RedisRateLimiter(self.redis_client, 86400)
        else:
            # Fallback to in-memory rate limiting
            from rate_limit_middleware import RateLimitMiddleware
            self.fallback_limiter = RateLimitMiddleware(
                app, requests_per_hour, requests_per_minute
            )
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request with enhanced proxy support."""
        # Check for Cloudflare
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip:
            return cf_ip
        
        # Check for X-Forwarded-For header (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Check for X-Forwarded-Proto (AWS ALB)
        forwarded_proto = request.headers.get("X-Forwarded-Proto")
        if forwarded_proto:
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
        
        # Fall back to direct connection
        return request.client.host if request.client else "unknown"
    
    def get_rate_limit_key(self, client_ip: str, request: Request) -> str:
        """Generate rate limit key based on IP and endpoint."""
        endpoint = request.url.path
        return f"rate_limit:{client_ip}:{endpoint}"
    
    async def check_rate_limits(self, key: str) -> Tuple[bool, Dict[str, any]]:
        """Check all rate limits (minute, hour, day)."""
        if not self.redis_client:
            return True, {}
        
        # Check minute limit
        minute_allowed, minute_meta = await self.minute_limiter.is_allowed(
            f"{key}:minute", self.requests_per_minute, 60
        )
        
        if not minute_allowed:
            return False, {
                "limit_type": "minute",
                "retry_after": 60,
                **minute_meta
            }
        
        # Check hour limit
        hour_allowed, hour_meta = await self.hour_limiter.is_allowed(
            f"{key}:hour", self.requests_per_hour, 3600
        )
        
        if not hour_allowed:
            return False, {
                "limit_type": "hour",
                "retry_after": 3600,
                **hour_meta
            }
        
        # Check day limit
        day_allowed, day_meta = await self.day_limiter.is_allowed(
            f"{key}:day", self.requests_per_day, 86400
        )
        
        if not day_allowed:
            return False, {
                "limit_type": "day",
                "retry_after": 86400,
                **day_meta
            }
        
        return True, {
            "minute": minute_meta,
            "hour": hour_meta,
            "day": day_meta
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and apply rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        client_ip = self.get_client_ip(request)
        
        # Use Redis rate limiting if available
        if self.redis_client:
            rate_limit_key = self.get_rate_limit_key(client_ip, request)
            is_allowed, metadata = await self.check_rate_limits(rate_limit_key)
            
            if not is_allowed:
                logger.warning("Rate limit exceeded", extra={
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "method": request.method,
                    "limit_type": metadata.get("limit_type"),
                    "requests_made": metadata.get("requests_made")
                })
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "message": f"Rate limit exceeded for {metadata.get('limit_type', 'requests')}",
                        "retry_after": metadata.get("retry_after", 60),
                        "limit_type": metadata.get("limit_type")
                    },
                    headers={
                        "Retry-After": str(metadata.get("retry_after", 60)),
                        "X-RateLimit-Limit": str(metadata.get("limit", 0)),
                        "X-RateLimit-Remaining": str(max(0, metadata.get("limit", 0) - metadata.get("requests_made", 0))),
                        "X-RateLimit-Reset": str(int(metadata.get("reset_time", time.time() + 60)))
                    }
                )
            
            # Add rate limit headers to successful responses
            response = await call_next(request)
            
            # Add informational headers
            if "minute" in metadata:
                minute_meta = metadata["minute"]
                response.headers["X-RateLimit-Minute-Limit"] = str(self.requests_per_minute)
                response.headers["X-RateLimit-Minute-Remaining"] = str(max(0, self.requests_per_minute - minute_meta.get("requests_made", 0)))
            
            if "hour" in metadata:
                hour_meta = metadata["hour"]
                response.headers["X-RateLimit-Hour-Limit"] = str(self.requests_per_hour)
                response.headers["X-RateLimit-Hour-Remaining"] = str(max(0, self.requests_per_hour - hour_meta.get("requests_made", 0)))
            
            return response
        
        else:
            # Fall back to in-memory rate limiting
            return await self.fallback_limiter.dispatch(request, call_next)