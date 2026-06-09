from unittest.mock import patch


def test_health_check_healthy(client):
    """
    Asserts health endpoint returns 200 and healthy metadata when all services are online.
    """
    with patch("app.api.v1.endpoints.check_db_health") as mock_db, \
         patch("app.api.v1.endpoints.chroma_client.check_health") as mock_chroma:
        
        mock_db.return_value = True
        mock_chroma.return_value = True

        response = client.get("/api/v1/v1/health")  # Routed under /api/v1/v1/health since master prefix is /api and route prefix is /v1. Let's verify our routing in main.py: app.include_router(api_router, prefix="/api") and api_router.include_router(v1_router, prefix="/v1") -> /api/v1/health
        # Wait, router.py says: api_router.include_router(v1_router, prefix="/v1")
        # endpoints.py says: router = APIRouter() and @router.get("/health")
        # So request path is indeed: /api/v1/health
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["services"]["postgres"] == "online"
        assert data["services"]["chroma"] == "online"


def test_health_check_unhealthy(client):
    """
    Asserts health endpoint returns 503 and unhealthy status if postgres is offline.
    """
    with patch("app.api.v1.endpoints.check_db_health") as mock_db, \
         patch("app.api.v1.endpoints.chroma_client.check_health") as mock_chroma:
        
        mock_db.return_value = False
        mock_chroma.return_value = True

        response = client.get("/api/v1/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["services"]["postgres"] == "offline"
        assert data["services"]["chroma"] == "online"


def test_info(client):
    """
    Asserts basic application configuration and docs references are returned.
    """
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert data["docs_url"] == "/docs"
