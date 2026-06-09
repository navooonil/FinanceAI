import os
import pytest
from fastapi.testclient import TestClient

# Force testing environment before importing app components
os.environ["ENVIRONMENT"] = "testing"

from main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """
    Returns a standard FastAPI TestClient.
    """
    with TestClient(app) as c:
        yield c
