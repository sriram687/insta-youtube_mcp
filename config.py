"""
Configuration module for the MCP Video Upload Server.
"""

import os
from typing import List
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # YouTube API Credentials
    youtube_client_id: str = ""
    youtube_client_secret: str = ""
    youtube_access_token: str = ""
    youtube_refresh_token: str = ""
    
    # Instagram API Credentials
    instagram_access_token: str = ""
    instagram_app_id: str = ""
    instagram_app_secret: str = ""
    
    # File Upload Configuration
    max_file_size_mb: int = 100
    allowed_video_extensions: str = "mp4,mov,avi,mkv,webm"
    
    # API Rate Limiting
    rate_limit_requests_per_minute: int = 60
    
    # Temporary file settings
    temp_dir: str = "/tmp"
    cleanup_temp_files: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("allowed_video_extensions")
    def validate_extensions(cls, v):
        """Validate and normalize file extensions."""
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        return v
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get list of allowed file extensions."""
        if isinstance(self.allowed_video_extensions, str):
            return [ext.strip().lower() for ext in self.allowed_video_extensions.split(",")]
        return self.allowed_video_extensions


# Global settings instance
settings = Settings()
