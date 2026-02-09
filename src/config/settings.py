"""Application settings and configuration."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Family Tree Knowledge Graph"
    VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DIR : Path = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed" 

    # NEW: Data file names - Add this section
    PEOPLE_CSV: str = "people.csv"
    RELATIONSHIPS_CSV: str = "relationships.csv"

    # NEW: FalkorDB Settings - Add this entire section
    FALKORDB_HOST: str = "localhost"
    FALKORDB_PORT: int = 6379
    GRAPH_NAME: str = "family_tree"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    
    # Database (optional)
    DATABASE_URL: Optional[str] = None
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None

    # NEW: LLM Settings - Add this section
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "mixtral-8x7b-32768"
    
    # External APIs (optional)
    API_KEY: Optional[str] = None
    
    @field_validator("DATA_DIR")
    @classmethod
    def create_data_dir(cls, v):
        """Create data directory if it doesn't exist."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"  # This allows extra fields from .env
    }



# Global settings instance
settings = Settings()
