"""
CSRF Protection middleware for FastAPI applications.
"""

import hmac
import hashlib
import secrets
import time
from typing import Optional, List
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import get_settings
from logging_config import setup_logging

logger = setup_logging(__name__)
settings = get_settings()


class CSRFProtection:
    """CSRF Protection utility class."""
    
    def __init__(self, secret_key: str = None, token_lifetime: int = 3600):
        self.secret_key = secret_key or settings.csrf_secret_key
        self.token_lifetime = token_lifetime
        
    def generate_csrf_token(self, session_id: str = None) -> str:
        """Generate a CSRF token."""
        if not session_id:
            session_id = secrets.token_urlsafe(32)
        
        timestamp = str(int(time.time()))
        data = f"{session_id}:{timestamp}"
        
        # Create HMAC signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"{data}:{signature}"
    
    def verify_csrf_token(self, token: str, session_id: str = None) -> bool:
        """Verify a CSRF token."""
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return False
            
            token_session_id, timestamp, signature = parts
            
            # Check if session ID matches (if provided)
            if session_id and token_session_id != session_id:
                return False
            
            # Check timestamp
            token_time = int(timestamp)
            current_time = int(time.time())
            
            if current_time - token_time > self.token_lifetime:
                return False
            
            # Verify signature
            data = f"{token_session_id}:{timestamp}"
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, TypeError):
            return False


class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF Protection middleware."""
    
    def __init__(self, app,
                 secret_key: str = None,
                 token_lifetime: int = 3600,
                 safe_methods: List[str] = None,
                 exempt_paths: List[str] = None,
                 header_name: str = "X-CSRF-Token",
                 cookie_name: str = "csrftoken"):
        super().__init__(app)
        
        self.csrf_protection = CSRFProtection(secret_key, token_lifetime)
        self.safe_methods = safe_methods or ["GET", "HEAD", "OPTIONS", "TRACE"]
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json"]
        self.header_name = header_name
        self.cookie_name = cookie_name
        
    def get_csrf_token_from_request(self, request: Request) -> Optional[str]:
        """Extract CSRF token from request."""
        # Check header first
        token = request.headers.get(self.header_name)
        if token:
            return token
        
        # Check cookies
        token = request.cookies.get(self.cookie_name)
        if token:
            return token
        
        # Check form data for POST requests
        if request.method == "POST":
            try:
                # This would require reading the body, which is tricky in middleware
                # For now, we'll rely on headers and cookies
                pass
            except Exception:
                pass
        
        return None
    
    def get_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID from request."""
        # Try to get session ID from cookies or headers
        session_id = request.cookies.get("sessionid")
        if not session_id:
            session_id = request.headers.get("X-Session-ID")
        
        return session_id
    
    def should_check_csrf(self, request: Request) -> bool:
        """Determine if CSRF check should be performed."""
        # Skip safe methods
        if request.method in self.safe_methods:
            return False
        
        # Skip exempt paths
        path = request.url.path
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return False
        
        # Skip if not a browser request (no cookies/referer)
        if not request.cookies and not request.headers.get("referer"):
            return False
        
        return True
    
    def check_referer(self, request: Request) -> bool:
        """Check referer header for additional CSRF protection."""
        referer = request.headers.get("referer")
        if not referer:
            return False
        
        # Parse referer URL
        from urllib.parse import urlparse
        
        try:
            referer_parsed = urlparse(referer)
            request_host = request.headers.get("host")
            
            # Allow same-origin requests
            if referer_parsed.hostname == request_host:
                return True
            
            # Allow configured origins
            allowed_origins = settings.cors_origins_list
            referer_origin = f"{referer_parsed.scheme}://{referer_parsed.hostname}"
            if referer_parsed.port:
                referer_origin += f":{referer_parsed.port}"
            
            return referer_origin in allowed_origins
            
        except Exception:
            return False
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and apply CSRF protection."""
        
        # Skip CSRF check if not needed
        if not self.should_check_csrf(request):
            response = await call_next(request)
            
            # Add CSRF token to response for GET requests
            if request.method == "GET" and request.url.path not in self.exempt_paths:
                session_id = self.get_session_id(request)
                csrf_token = self.csrf_protection.generate_csrf_token(session_id)
                
                # Set CSRF token in response header
                response.headers["X-CSRF-Token"] = csrf_token
                
                # Set CSRF token in cookie
                response.set_cookie(
                    key=self.cookie_name,
                    value=csrf_token,
                    httponly=True,
                    secure=settings.is_production,
                    samesite="strict",
                    max_age=self.csrf_protection.token_lifetime
                )
            
            return response
        
        # Get CSRF token from request
        csrf_token = self.get_csrf_token_from_request(request)
        
        if not csrf_token:
            logger.warning("CSRF token missing", extra={
                "path": request.url.path,
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown"
            })
            
            return JSONResponse(
                status_code=403,
                content={
                    "error": "CSRF token missing",
                    "message": "CSRF token is required for this request"
                }
            )
        
        # Verify CSRF token
        session_id = self.get_session_id(request)
        
        if not self.csrf_protection.verify_csrf_token(csrf_token, session_id):
            logger.warning("CSRF token verification failed", extra={
                "path": request.url.path,
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown"
            })
            
            return JSONResponse(
                status_code=403,
                content={
                    "error": "CSRF token invalid",
                    "message": "CSRF token verification failed"
                }
            )
        
        # Additional referer check
        if not self.check_referer(request):
            logger.warning("Referer check failed", extra={
                "path": request.url.path,
                "method": request.method,
                "referer": request.headers.get("referer"),
                "client_ip": request.client.host if request.client else "unknown"
            })
            
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Invalid referer",
                    "message": "Request origin not allowed"
                }
            )
        
        # Process the request
        response = await call_next(request)
        
        # Refresh CSRF token in response
        new_csrf_token = self.csrf_protection.generate_csrf_token(session_id)
        response.headers["X-CSRF-Token"] = new_csrf_token
        
        response.set_cookie(
            key=self.cookie_name,
            value=new_csrf_token,
            httponly=True,
            secure=settings.is_production,
            samesite="strict",
            max_age=self.csrf_protection.token_lifetime
        )
        
        return response


# Convenience functions for manual CSRF handling
def get_csrf_token(session_id: str = None) -> str:
    """Generate a CSRF token for manual use."""
    csrf_protection = CSRFProtection()
    return csrf_protection.generate_csrf_token(session_id)


def verify_csrf_token(token: str, session_id: str = None) -> bool:
    """Verify a CSRF token for manual use."""
    csrf_protection = CSRFProtection()
    return csrf_protection.verify_csrf_token(token, session_id)