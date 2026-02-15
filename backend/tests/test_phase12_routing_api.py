from datetime import datetime, timedelta

from app.models.models import RouteRestriction, StreetEdge, StreetNode


def _seed_graph(db):
    db.add(StreetNode(id="a", geom="POINT(-5.9968 37.3921)"))
    db.add(StreetNode(id="b", geom="POINT(-5.9990 37.3927)"))
    db.add(StreetNode(id="c", geom="POINT(-5.9924 37.3936)"))

    db.add(
        StreetEdge(
            id="ab",
            source_node="a",
            target_node="b",
            geom="LINESTRING(-5.9968 37.3921, -5.9990 37.3927)",
            length_m=210,
            is_walkable=True,
        )
    )
    db.add(
        StreetEdge(
            id="ac",
            source_node="a",
            target_node="c",
            geom="LINESTRING(-5.9968 37.3921, -5.9924 37.3936)",
            length_m=390,
            is_walkable=True,
        )
    )
    db.add(
        StreetEdge(
            id="cb",
            source_node="c",
            target_node="b",
            geom="LINESTRING(-5.9924 37.3936, -5.9990 37.3927)",
            length_m=410,
            is_walkable=True,
        )
    )
    db.commit()


def test_phase12_optimal_route_returns_alternative(client, db):
    _seed_graph(db)
    res = client.post(
        "/api/v1/routing/optimal",
        json={
            "origin": [37.3921, -5.9968],
            "destination": [37.3927, -5.9990],
            "datetime": datetime.utcnow().isoformat(),
            "constraints": {"avoid_bulla": True, "max_walk_km": 5},
        },
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["eta_seconds"] > 0
    assert len(payload["polyline"]) >= 2
    assert len(payload["alternatives"]) >= 1


def test_phase12_restriction_forces_detour_in_api(client, db):
    _seed_graph(db)
    db.add(
        RouteRestriction(
            id="r1",
            edge_id="ab",
            starts_at=datetime.utcnow() - timedelta(minutes=5),
            ends_at=datetime.utcnow() + timedelta(minutes=30),
            reason="corte",
            severity=2000,
        )
    )
    db.commit()

    res = client.post(
        "/api/v1/routing/optimal",
        json={
            "origin": [37.3921, -5.9968],
            "destination": [37.3927, -5.9990],
            "datetime": datetime.utcnow().isoformat(),
            "constraints": {"avoid_bulla": True, "max_walk_km": 5},
        },
    )
    assert res.status_code == 200
    assert len(res.json()["polyline"]) >= 3
