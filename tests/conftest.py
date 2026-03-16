import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    """FastAPI TestClient fixture for testing endpoints."""
    return TestClient(app)