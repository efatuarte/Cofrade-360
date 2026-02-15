from datetime import datetime


def test_ws_persists_last_route_and_can_fetch(client):
    plan_id = "plan-phase13"
    with client.websocket_connect(f"/api/v1/routing/ws/mode-calle?plan_id={plan_id}") as ws:
        ws.receive_json()  # hello
        ws.send_json(
            {
                "type": "location_update",
                "location": {"lat": 37.3862, "lng": -5.9926},
                "datetime": datetime(2026, 4, 10, 22, 15).isoformat(),
                "target": {"type": "event", "id": "macarena"},
                "constraints": {"avoid_bulla": True, "max_walk_km": 2},
            }
        )
        route_update = ws.receive_json()
        assert route_update["type"] == "route_update"

    last = client.get(f"/api/v1/routing/last?plan_id={plan_id}")
    assert last.status_code == 200
    payload = last.json()
    assert payload["plan_id"] == plan_id
    assert payload["route"]["eta_seconds"] > 0


def test_routing_last_returns_404_for_unknown_plan(client):
    response = client.get("/api/v1/routing/last?plan_id=unknown-plan")
    assert response.status_code == 404
