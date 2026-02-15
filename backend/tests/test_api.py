from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app

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
            "constraints": {"avoid_bulla": True, "max_walk_km": 5},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "polyline" in data
    assert "eta_seconds" in data
    assert "bulla_score" in data
    assert "warnings" in data
    assert "explanation" in data
    assert len(data["polyline"]) >= 2
    assert data["eta_seconds"] > 0


def test_mode_calle_ws_reroute_message():
    with client.websocket_connect("/api/v1/routing/ws/mode-calle?plan_id=plan-1") as ws:
        ws.send_json(
            {
                "location": {"lat": 37.3862, "lng": -5.9926},
                "datetime": datetime(2026, 4, 10, 22, 15).isoformat(),
                "target": {"type": "event", "id": "macarena"},
                "constraints": {"avoid_bulla": True, "max_walk_km": 2},
            }
        )
        msg = ws.receive_json()
        assert msg["type"] == "reroute"
        assert "route" in msg
        assert "eta_seconds" in msg["route"]
