from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.schemas import RouteResponse

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Cofrade 360 API"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_routing_optimal():
    response = client.post(
        "/api/v1/routing/optimal",
        json={
            "origin": [37.3862, -5.9926],
            "datetime": datetime(2026, 4, 10, 19, 30).isoformat(),
            "target": {"type": "event", "id": "macarena"},
            "constraints": {"avoid_bulla": 0.7, "prefer_wide": True, "max_detour": 1.5},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "polyline" in data
    assert "eta_seconds" in data
    assert "total_cost" in data
    assert "bulla_score" in data
    assert "warnings" in data
    assert "explanation" in data
    assert "alternatives" in data
    assert len(data["polyline"]) >= 2
    assert data["eta_seconds"] > 0


def test_mode_calle_ws_route_update_message():
    mock_route = RouteResponse(
        polyline=[[37.3862, -5.9926], [37.4008, -5.9900]],
        eta_seconds=320,
        total_cost=320.0,
        bulla_score=0.5,
        warnings=[],
        explanation=[],
        alternatives=[],
    )
    with patch("app.api.endpoints.routing.crud.list_restrictions", return_value=[]), patch(
        "app.api.endpoints.routing.calculate_optimal_route", return_value=mock_route
    ):
        with client.websocket_connect("/api/v1/routing/ws/mode-calle") as ws:
            ws.send_json(
                {
                    "type": "client_location_update",
                    "plan_id": "plan-1",
                    "location": {"lat": 37.3862, "lng": -5.9926},
                    "datetime": datetime(2026, 4, 10, 22, 15).isoformat(),
                    "target": {"type": "event", "id": "macarena"},
                    "constraints": {"avoid_bulla": 0.8, "prefer_wide": True, "max_detour": 1.5},
                }
            )
            msg = ws.receive_json()
            assert msg["type"] == "server_route_update"
            assert "route" in msg
            assert "eta_seconds" in msg["route"]
