"""Example unit tests."""

import pytest
from src.config.settings import settings


def test_settings_loaded():
    """Test that settings are loaded correctly."""
    assert settings.APP_NAME is not None
    assert settings.VERSION == "0.1.0"


def test_sample_function(sample_data):
    """Example test using fixture."""
    assert sample_data["name"] == "Test Item"
    assert sample_data["value"] == 42
    assert sample_data["active"] is True


class TestExampleClass:
    """Example test class."""
    
    def test_something(self):
        """Test something."""
        assert True
    
    def test_with_fixture(self, app_settings):
        """Test using app settings fixture."""
        assert app_settings.APP_NAME is not None
