"""
Configuration management for FOCUS Generator backend.
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


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


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings