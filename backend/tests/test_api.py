from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Cofrade 360 API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_routing_optimal():
    """Test optimal routing endpoint"""
    response = client.post(
        "/api/v1/routing/optimal",
        json={
            "origen": [37.3862, -5.9926],  # Catedral
            "destino": [37.4008, -5.9900],  # Macarena
            "evitar_procesiones": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "ruta" in data
    assert "distancia_metros" in data
    assert "duracion_minutos" in data
    assert "instrucciones" in data
    assert len(data["ruta"]) >= 2
    assert data["distancia_metros"] > 0
