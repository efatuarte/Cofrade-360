from datetime import datetime

from app.models.models import CrowdReport, User
from app.tasks.crowd import aggregate_crowd_signals
from tests.conftest import auth_header, make_admin_user, make_user


def test_phase14_rate_limit_per_user_geohash_window(client, db):
    user = make_user(db)
    body = {"lat": 37.3921, "lng": -5.9968, "severity": 5, "note": "Bulla alta"}

    first = client.post("/api/v1/crowd/reports", json=body, headers=auth_header(user.id))
    second = client.post("/api/v1/crowd/reports", json=body, headers=auth_header(user.id))

    assert first.status_code == 201
    assert second.status_code == 429


def test_phase14_aggregation_creates_signals(client, db):
    user = make_user(db)
    for sev in [3, 4, 5]:
        db.add(
            CrowdReport(
                id=f"r-{sev}",
                user_id=user.id,
                geohash="37.392:-5.997",
                lat=37.3921,
                lng=-5.9968,
                severity=sev,
            )
        )
    db.commit()

    created = aggregate_crowd_signals(db, now=datetime.utcnow(), bucket_minutes=10)
    assert created >= 1

    res = client.get("/api/v1/crowd/signals?geohash=37.392:-5.997")
    assert res.status_code == 200
    payload = res.json()
    assert len(payload) >= 1
    assert payload[0]["confidence"] > 0


def test_phase14_routing_penalizes_bulla(db):
    from app.core.routing import calculate_optimal_route
    from app.models.models import CrowdSignal, StreetEdge, StreetNode

    db.add(StreetNode(id="a", geom="POINT(-5.9968 37.3921)"))
    db.add(StreetNode(id="b", geom="POINT(-5.9990 37.3927)"))
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
        CrowdSignal(
            id="cs1",
            geohash="37.393:-5.999",
            bucket_start=datetime(2026, 4, 10, 19, 0),
            bucket_end=datetime(2026, 4, 10, 19, 30),
            score=0.9,
            confidence=0.9,
            reports_count=8,
        )
    )
    db.commit()

    no_penalty = calculate_optimal_route(
        db,
        origin=[37.3921, -5.9968],
        destination=[37.3927, -5.9990],
        route_datetime=datetime(2026, 4, 10, 19, 15),
        target_type=None,
        target_id=None,
        avoid_bulla=False,
    )
    penalty = calculate_optimal_route(
        db,
        origin=[37.3921, -5.9968],
        destination=[37.3927, -5.9990],
        route_datetime=datetime(2026, 4, 10, 19, 15),
        target_type=None,
        target_id=None,
        avoid_bulla=True,
    )

    assert penalty.eta_seconds >= no_penalty.eta_seconds
    assert any("Penalty bulla" in e for e in penalty.explanation)


def test_phase14_rbac_for_moderation(client, db):
    user = make_user(db)
    admin = make_admin_user(db)

    report = CrowdReport(
        id="rep-1",
        user_id=user.id,
        geohash="37.392:-5.997",
        lat=37.3921,
        lng=-5.9968,
        severity=4,
    )
    db.add(report)
    db.commit()

    denied = client.patch("/api/v1/crowd/reports/rep-1", json={"is_hidden": True}, headers=auth_header(user.id))
    allowed = client.patch("/api/v1/crowd/reports/rep-1", json={"is_hidden": True}, headers=auth_header(admin.id))

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["is_hidden"] is True
