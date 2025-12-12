"""Example integration tests."""

import pytest


@pytest.mark.integration
def test_integration_example():
    """Example integration test."""
    # This would test multiple components working together
    assert True


@pytest.mark.slow
def test_slow_operation():
    """Example of a slow test."""
    # Mark slow tests so they can be skipped during development
    import time
    time.sleep(0.1)  # Simulate slow operation
    assert True
