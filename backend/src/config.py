"""
Configuration management for FOCUS Generator backend.
Centralizes all application settings and environment variables.
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # S3 Configuration
    s3_bucket_name: str = Field(default="cur-gen-files", env="S3_BUCKET_NAME")
    s3_public_read: bool = Field(default=False, env="S3_PUBLIC_READ")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"], 
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Frontend URL (for production deployments)
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    
    # Redis Configuration (for rate limiting and caching)
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    
    # Rate Limiting Configuration
    rate_limit_per_minute: int = Field(default=10, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=100, env="RATE_LIMIT_PER_HOUR")
    rate_limit_per_day: int = Field(default=1000, env="RATE_LIMIT_PER_DAY")
    
    # Security Configuration
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    csrf_secret_key: str = Field(default="dev-csrf-secret", env="CSRF_SECRET_KEY")
    
    # File Generation Limits
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    max_generation_timeout: int = Field(default=300, env="MAX_GENERATION_TIMEOUT")
    
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_session_token: Optional[str] = Field(default=None, env="AWS_SESSION_TOKEN")
    
    # Data Generation Settings
    default_row_count: int = Field(default=1000, env="DEFAULT_ROW_COUNT")
    max_row_count: int = Field(default=1000000, env="MAX_ROW_COUNT")
    min_row_count: int = Field(default=1, env="MIN_ROW_COUNT")
    
    # Performance Settings
    enable_compression: bool = Field(default=True, env="ENABLE_COMPRESSION")
    compression_level: int = Field(default=6, env="COMPRESSION_LEVEL")
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # Logging Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Retry Settings
    retry_max_attempts: int = Field(default=3, env="RETRY_MAX_ATTEMPTS")
    retry_backoff_factor: float = Field(default=2.0, env="RETRY_BACKOFF_FACTOR")
    retry_max_delay: int = Field(default=60, env="RETRY_MAX_DELAY")
    
    # Temporary Directory
    temp_dir: str = Field(default="/tmp", env="TEMP_DIR")
    
    @validator('log_level')
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {', '.join(allowed)}")
        return v.upper()
    
    @validator('log_format')
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        allowed = ["json", "text"]
        if v.lower() not in allowed:
            raise ValueError(f"Log format must be one of: {', '.join(allowed)}")
        return v.lower()
    
    @validator('environment')
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of: {', '.join(allowed)}")
        return v.lower()
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list, handling both dev and prod scenarios."""
        if self.is_production:
            # In production, use specific origins
            origins = [self.frontend_url]
            if isinstance(self.cors_origins, list):
                origins.extend(self.cors_origins)
            return origins
        else:
            # In development, allow localhost variants
            return self.cors_origins
    
    def get_aws_config(self) -> Dict[str, Any]:
        """Get AWS configuration dictionary."""
        config = {"region_name": self.aws_region}
        
        if self.aws_access_key_id:
            config["aws_access_key_id"] = self.aws_access_key_id
        if self.aws_secret_access_key:
            config["aws_secret_access_key"] = self.aws_secret_access_key
        if self.aws_session_token:
            config["aws_session_token"] = self.aws_session_token
            
        return config
    
    def get_redis_url(self) -> str:
        """Get Redis URL, handling both simple and complex configurations."""
        return self.redis_url
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


# Configuration presets for different environments
DEVELOPMENT_CONFIG = {
    "debug": True,
    "log_level": "DEBUG",
    "enable_compression": False,
    "enable_caching": False,
}

PRODUCTION_CONFIG = {
    "debug": False,
    "log_level": "INFO",
    "enable_compression": True,
    "enable_caching": True,
    "cors_origins": [],  # Restrict CORS in production
}

TESTING_CONFIG = {
    "debug": True,
    "log_level": "WARNING",
    "enable_compression": False,
    "enable_caching": False,
    "temp_dir": "/tmp/focus_test",
}


def apply_environment_config(settings_instance: Settings) -> Settings:
    """Apply environment-specific configuration overrides."""
    config_map = {
        "development": DEVELOPMENT_CONFIG,
        "production": PRODUCTION_CONFIG,
        "testing": TESTING_CONFIG,
    }
    
    env_config = config_map.get(settings_instance.environment, {})
    
    # Apply overrides
    for key, value in env_config.items():
        if hasattr(settings_instance, key):
            setattr(settings_instance, key, value)
    
    return settings_instance


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings with environment-specific overrides."""
    settings_instance = Settings()
    return apply_environment_config(settings_instance)


# Global settings instance
settings = get_settings()