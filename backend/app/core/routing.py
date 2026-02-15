import hashlib
import heapq
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.schemas.schemas import RouteResponse


@dataclass
class Node:
    """Graph node for routing."""

    def __init__(self, id: str, lat: float, lon: float):
        self.id = id
        self.lat = lat
        self.lon = lon

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Edge:
    """Graph edge for routing."""

    def __init__(self, from_node: str, to_node: str, distance: float):
        self.from_node = from_node
        self.to_node = to_node
        self.distance = distance


@dataclass
class RoutingResult:
    polyline: List[List[float]]
    eta_seconds: int
    bulla_score: float
    warnings: List[str]
    explanation: List[str]


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two points using Haversine formula."""
    r = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def create_mock_graph() -> Tuple[Dict[str, Node], List[Edge]]:
    """Create mock graph (10+ nodes) for Seville center MVP."""
    nodes = {
        "catedral": Node("catedral", 37.3862, -5.9926),
        "giralda": Node("giralda", 37.3857, -5.9929),
        "alcazar": Node("alcazar", 37.3839, -5.9914),
        "plaza_espana": Node("plaza_espana", 37.3765, -5.9868),
        "torre_oro": Node("torre_oro", 37.3825, -5.9960),
        "triana": Node("triana", 37.3870, -6.0020),
        "macarena": Node("macarena", 37.4008, -5.9900),
        "maestranza": Node("maestranza", 37.3838, -5.9972),
        "encarnacion": Node("encarnacion", 37.3936, -5.9924),
        "campana": Node("campana", 37.3921, -5.9968),
        "alameda": Node("alameda", 37.3997, -5.9958),
    }

    links = [
        ("catedral", "giralda"),
        ("giralda", "encarnacion"),
        ("encarnacion", "campana"),
        ("campana", "alameda"),
        ("alameda", "macarena"),
        ("catedral", "alcazar"),
        ("alcazar", "plaza_espana"),
        ("catedral", "torre_oro"),
        ("torre_oro", "triana"),
        ("catedral", "maestranza"),
        ("maestranza", "triana"),
        ("campana", "maestranza"),
        ("encarnacion", "catedral"),
    ]

    edges: List[Edge] = []
    for frm, to in links:
        a = nodes[frm]
        b = nodes[to]
        dist = haversine_distance(a.lat, a.lon, b.lat, b.lon)
        edges.append(Edge(frm, to, dist))
        edges.append(Edge(to, frm, dist))
    return nodes, edges


def _build_adjacency(edges: List[Edge]) -> Dict[str, List[Tuple[str, float]]]:
    graph: Dict[str, List[Tuple[str, float]]] = {}
    for edge in edges:
        graph.setdefault(edge.from_node, []).append((edge.to_node, edge.distance))
    return graph


def a_star_search(start: Node, goal: Node, nodes: Dict[str, Node], edges: List[Edge]) -> Optional[List[Node]]:
    graph = _build_adjacency(edges)
    open_set = [(0, 0, start.id)]
    came_from: Dict[str, str] = {}
    g_score = {start.id: 0.0}

    while open_set:
        _, current_g, current_id = heapq.heappop(open_set)
        if current_id == goal.id:
            path = [nodes[current_id]]
            while current_id in came_from:
                current_id = came_from[current_id]
                path.append(nodes[current_id])
            return list(reversed(path))

        for neighbor_id, distance in graph.get(current_id, []):
            tentative_g = current_g + distance
            if neighbor_id not in g_score or tentative_g < g_score[neighbor_id]:
                came_from[neighbor_id] = current_id
                g_score[neighbor_id] = tentative_g
                neighbor = nodes[neighbor_id]
                h = haversine_distance(neighbor.lat, neighbor.lon, goal.lat, goal.lon)
                heapq.heappush(open_set, (tentative_g + h, tentative_g, neighbor_id))

    return None


def find_nearest_node(lat: float, lon: float, nodes: Dict[str, Node]) -> Node:
    return min(nodes.values(), key=lambda n: haversine_distance(lat, lon, n.lat, n.lon))


def _target_node_from_id(target_type: str, target_id: str, nodes: Dict[str, Node]) -> Node:
    if target_id in nodes:
        return nodes[target_id]
    digest = hashlib.sha1(f"{target_type}:{target_id}".encode()).hexdigest()
    idx = int(digest[:4], 16) % len(nodes)
    return list(nodes.values())[idx]


def _bulla_score(dt: datetime, lat: float, lng: float) -> float:
    hour_factor = ((dt.hour + dt.minute / 60) % 24) / 24
    hotspot_lat, hotspot_lng = 37.3891, -5.9845
    dist_m = haversine_distance(lat, lng, hotspot_lat, hotspot_lng)
    hotspot_factor = max(0.0, 1.0 - min(dist_m, 2500) / 2500)
    score = 0.55 * hour_factor + 0.45 * hotspot_factor
    return round(min(max(score, 0.0), 1.0), 3)


def calculate_optimal_route(
    origin: List[float],
    route_datetime: datetime,
    target_type: str,
    target_id: str,
    avoid_bulla: bool = True,
    max_walk_km: float = 10.0,
) -> RoutingResult:
    nodes, edges = create_mock_graph()
    start = find_nearest_node(origin[0], origin[1], nodes)
    goal = _target_node_from_id(target_type, target_id, nodes)

    path = a_star_search(start, goal, nodes, edges)
    if not path:
        poly = [origin, [goal.lat, goal.lon]]
    else:
        poly = [[n.lat, n.lon] for n in path]

    total_distance = 0.0
    for i in range(len(poly) - 1):
        total_distance += haversine_distance(poly[i][0], poly[i][1], poly[i + 1][0], poly[i + 1][1])

    eta_seconds = max(60, int((total_distance / 1000.0) / 4.6 * 3600))  # 4.6km/h
    bulla = _bulla_score(route_datetime, origin[0], origin[1])

    warnings: List[str] = []
    if total_distance / 1000.0 > max_walk_km:
        warnings.append("La distancia supera tu límite máximo de caminata.")
    if avoid_bulla and bulla > 0.7:
        warnings.append("Zona con alta bulla estimada. Considera rutas alternativas.")

    explanation = [
        f"Se calculó ruta con A* sobre grafo mock de {len(nodes)} nodos.",
        f"ETA estimada con velocidad peatonal media y distancia de {int(total_distance)} m.",
        f"Bulla score ({bulla}) combina hora actual y cercanía a hotspot del centro.",
    ]

    return RoutingResult(
        polyline=poly,
        eta_seconds=eta_seconds,
        bulla_score=bulla,
        warnings=warnings,
        explanation=explanation,
    )


def as_route_response(result: RoutingResult) -> RouteResponse:
    return RouteResponse(
        polyline=result.polyline,
        eta_seconds=result.eta_seconds,
        bulla_score=result.bulla_score,
        warnings=result.warnings,
        explanation=result.explanation,
    )
