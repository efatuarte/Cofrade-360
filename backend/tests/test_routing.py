import json
from datetime import datetime, timedelta

from app.core.routing import calculate_optimal_route, haversine_distance
from app.models.models import RouteRestriction, StreetEdge, StreetNode


def _seed_graph(db):
    nodes = [
        StreetNode(id="a", geom="POINT(-5.9968 37.3921)"),
        StreetNode(id="b", geom="POINT(-5.9990 37.3927)"),
        StreetNode(id="c", geom="POINT(-5.9924 37.3936)"),
    ]
    for node in nodes:
        db.add(node)

    edges = [
        StreetEdge(
            id="ab",
            source_node="a",
            target_node="b",
            geom="LINESTRING(-5.9968 37.3921, -5.9990 37.3927)",
            length_m=210,
            is_walkable=True,
            tags=json.dumps({}),
        ),
        StreetEdge(
            id="ac",
            source_node="a",
            target_node="c",
            geom="LINESTRING(-5.9968 37.3921, -5.9924 37.3936)",
            length_m=390,
            is_walkable=True,
            tags=json.dumps({}),
        ),
        StreetEdge(
            id="cb",
            source_node="c",
            target_node="b",
            geom="LINESTRING(-5.9924 37.3936, -5.9990 37.3927)",
            length_m=410,
            is_walkable=True,
            tags=json.dumps({}),
        ),
    ]
    for edge in edges:
        db.add(edge)
    db.commit()


def test_haversine_distance():
    distance = haversine_distance(37.3862, -5.9926, 37.4008, -5.9900)
    assert 1400 < distance < 1800


def test_route_between_two_points_in_seville(db):
    _seed_graph(db)
    result = calculate_optimal_route(
        db,
        origin=[37.3921, -5.9968],
        destination=[37.3927, -5.9990],
        route_datetime=datetime(2026, 4, 10, 19, 30),
        target_type=None,
        target_id=None,
        avoid_bulla=True,
        max_walk_km=6,
    )
    assert result.eta_seconds > 0
    assert len(result.polyline) >= 2
    assert result.explanation[0].startswith("Ruta calculada con A*")


def test_active_restriction_forces_detour(db):
    _seed_graph(db)
    db.add(
        RouteRestriction(
            id="r1",
            edge_id="ab",
            starts_at=datetime.utcnow() - timedelta(minutes=10),
            ends_at=datetime.utcnow() + timedelta(minutes=10),
            reason="corte",
            severity=2000,
        )
    )
    db.commit()

    result = calculate_optimal_route(
        db,
        origin=[37.3921, -5.9968],
        destination=[37.3927, -5.9990],
        route_datetime=datetime.utcnow(),
        target_type=None,
        target_id=None,
        avoid_bulla=True,
        max_walk_km=6,
    )
    # con restricción en AB, la ruta debe pasar por C (3 puntos)
    assert len(result.polyline) >= 3
