"""Application settings and configuration."""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Your Project"
    VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    
    # Database (optional)
    DATABASE_URL: Optional[str] = None
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # External APIs (optional)
    API_KEY: Optional[str] = None
    
    @validator("DATA_DIR", pre=True)
    def create_data_dir(cls, v):
        """Create data directory if it doesn't exist."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
