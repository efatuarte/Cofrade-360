from datetime import datetime

from app.core.routing import (
    Edge,
    Node,
    a_star_search,
    calculate_optimal_route,
    create_mock_graph,
    haversine_distance,
)


def test_haversine_distance():
    lat1, lon1 = 37.3862, -5.9926
    lat2, lon2 = 37.4008, -5.9900
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    assert 1400 < distance < 1800


def test_create_mock_graph():
    nodes, edges = create_mock_graph()
    assert len(nodes) >= 10
    assert len(edges) > 0
    assert "catedral" in nodes
    assert "macarena" in nodes


def test_a_star_search():
    nodes, edges = create_mock_graph()
    start = nodes["catedral"]
    goal = nodes["macarena"]
    path = a_star_search(start, goal, nodes, edges)
    assert path is not None
    assert len(path.node_ids) >= 2
    assert path.node_ids[0] == start.id
    assert path.node_ids[-1] == goal.id


def test_calculate_optimal_route():
    result = calculate_optimal_route(
        origin=[37.3862, -5.9926],
        route_datetime=datetime(2026, 4, 10, 19, 30),
        target_type="event",
        target_id="macarena",
        avoid_bulla=True,
        max_walk_km=6,
    )
    assert result.eta_seconds > 0
    assert len(result.polyline) >= 2
    assert 0 <= result.bulla_score <= 1
    assert len(result.explanation) == 3
