import pytest

@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Mock any environment variables here if needed"""
    monkeypatch.setenv("ARXIV_API_TIMEOUT", "30")