"""Family Tree specific settings."""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel


class FamilyTreeSettings(BaseModel):
    """Settings for family tree project."""
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "data" / "processed"
    
    # Data files
    PEOPLE_CSV: str = "people.csv"
    RELATIONSHIPS_CSV: str = "relationships.csv"
    
    # FalkorDB Settings
    FALKORDB_HOST: str = "localhost"
    FALKORDB_PORT: int = 6379
    GRAPH_NAME: str = "family_tree"
    
    # LLM Settings
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "mixtral-8x7b-32768"
    
    # Logging
    LOG_LEVEL: str = "INFO"


# Global settings instance
ft_settings = FamilyTreeSettings()