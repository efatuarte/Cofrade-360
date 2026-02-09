import pytest
from app.core.routing import (
    haversine_distance,
    Node,
    Edge,
    a_star_search,
    create_mock_graph,
    calculate_optimal_route
)


def test_haversine_distance():
    """Test distance calculation"""
    # Distance between two known points in Seville
    lat1, lon1 = 37.3862, -5.9926  # Catedral
    lat2, lon2 = 37.4008, -5.9900  # Macarena
    
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    
    # Should be approximately 1.6 km
    assert 1400 < distance < 1800


def test_create_mock_graph():
    """Test mock graph creation"""
    nodes, edges = create_mock_graph()
    
    assert len(nodes) > 0
    assert len(edges) > 0
    assert "catedral" in nodes
    assert "macarena" in nodes


def test_a_star_search():
    """Test A* algorithm"""
    nodes, edges = create_mock_graph()
    
    start = nodes["catedral"]
    goal = nodes["macarena"]
    
    path = a_star_search(start, goal, nodes, edges, evitar_procesiones=False)
    
    assert path is not None
    assert len(path) >= 2
    assert path[0].id == start.id
    assert path[-1].id == goal.id


def test_calculate_optimal_route():
    """Test route calculation"""
    result = calculate_optimal_route(
        origen=[37.3862, -5.9926],  # Catedral
        destino=[37.4008, -5.9900],  # Macarena
        evitar_procesiones=True
    )
    
    assert result.distancia_metros > 0
    assert result.duracion_minutos > 0
    assert len(result.ruta) >= 2
    assert len(result.instrucciones) > 0
