"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config.settings import settings


@pytest.fixture
def app_settings():
    """Provide application settings for tests."""
    return settings


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        "name": "Test Item",
        "value": 42,
        "active": True
    }
