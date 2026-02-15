from app.core.routing import _a_star, _create_fallback_graph, _load_graph_from_segments, haversine_distance


class _EmptyQuery:
    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return []


class _DummyDB:
    def query(self, model):
        return _EmptyQuery()


def test_haversine_distance():
    lat1, lon1 = 37.3862, -5.9926
    lat2, lon2 = 37.4008, -5.9900
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    assert 1400 < distance < 1800


def test_create_fallback_graph():
    nodes, edges, _ = _create_fallback_graph()
    assert len(nodes) >= 6
    assert len(edges) > 0
    assert "catedral" in nodes
    assert "macarena" in nodes


def test_a_star_search_with_fallback_graph():
    nodes, edges, _ = _create_fallback_graph()
    start = nodes["catedral"]
    goal = nodes["macarena"]
    path = _a_star(
        nodes,
        edges,
        start,
        goal,
        active_restrictions=[],
        active_occupations={},
        avoid_bulla=0.5,
        prefer_wide=True,
    )
    assert path is not None
    assert len(path.node_ids) >= 2
    assert path.node_ids[0] == start.id
    assert path.node_ids[-1] == goal.id


def test_load_graph_from_segments_uses_fallback_when_empty_db():
    nodes, edges, names = _load_graph_from_segments(_DummyDB())
    assert "catedral" in nodes
    assert len(edges) > 0
    assert len(names) > 0
