import hashlib
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.models import CrowdSignal, Hermandad, RouteRestriction, StreetEdge, StreetNode
from app.schemas.schemas import RouteAlternative, RouteResponse

WALKING_SPEED_MPS = 1.28
_CACHE: Dict[str, dict] = {}


@dataclass
class RoutingResult:
    polyline: List[List[float]]
    eta_seconds: int
    bulla_score: float
    warnings: List[str]
    explanation: List[str]
    alternatives: List[RouteAlternative]


def _parse_point_wkt(wkt: str) -> Tuple[float, float]:
    raw = wkt.strip().replace("POINT(", "").replace(")", "")
    lng, lat = raw.split()
    return float(lat), float(lng)


def _parse_line_wkt(wkt: str) -> List[List[float]]:
    inner = wkt.strip().replace("LINESTRING(", "").replace(")", "")
    coords = []
    for pair in inner.split(","):
        lng, lat = pair.strip().split()
        coords.append([float(lat), float(lng)])
    return coords


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _target_coords(db: Session, target_type: str, target_id: str) -> Optional[List[float]]:
    if target_type == "brotherhood":
        hermandad = db.query(Hermandad).filter(Hermandad.id == target_id).first()
        if hermandad and hermandad.church and hermandad.church.lat and hermandad.church.lng:
            return [hermandad.church.lat, hermandad.church.lng]
    digest = hashlib.sha1(f"{target_type}:{target_id}".encode()).hexdigest()
    jitter = int(digest[:6], 16) / 0xFFFFFF
    return [37.389 + jitter * 0.02, -5.995 + jitter * 0.02]


def _find_nearest_node(nodes: dict[str, tuple[float, float]], point: List[float]) -> str:
    return min(nodes, key=lambda nid: haversine_distance(point[0], point[1], nodes[nid][0], nodes[nid][1]))


def _build_graph(db: Session, route_datetime: datetime) -> tuple[dict[str, tuple[float, float]], dict[str, list[tuple[str, float, str]]], str]:
    nodes_rows = db.query(StreetNode).all()
    edge_rows = db.query(StreetEdge).filter(StreetEdge.is_walkable.is_(True)).all()
    restrictions = (
        db.query(RouteRestriction)
        .filter(RouteRestriction.starts_at <= route_datetime, RouteRestriction.ends_at >= route_datetime)
        .all()
    )
    penalties = {r.edge_id: r.severity for r in restrictions}
    restriction_signature = "|".join(sorted(f"{r.edge_id}:{r.severity}" for r in restrictions))

    nodes = {row.id: _parse_point_wkt(str(row.geom)) for row in nodes_rows}
    graph: dict[str, list[tuple[str, float, str]]] = {nid: [] for nid in nodes}
    for edge in edge_rows:
        cost = edge.length_m / WALKING_SPEED_MPS
        if edge.id in penalties:
            cost += penalties[edge.id]
        graph[edge.source_node].append((edge.target_node, cost, edge.id))
    return nodes, graph, restriction_signature


def _reconstruct_path(came_from: dict[str, tuple[str, str]], current: str) -> tuple[list[str], list[str]]:
    nodes = [current]
    edges: list[str] = []
    while current in came_from:
        prev, edge_id = came_from[current]
        edges.append(edge_id)
        current = prev
        nodes.append(current)
    nodes.reverse()
    edges.reverse()
    return nodes, edges


def _astar(
    nodes: dict[str, tuple[float, float]],
    graph: dict[str, list[tuple[str, float, str]]],
    start: str,
    goal: str,
) -> tuple[list[str], list[str], float]:
    import heapq

    queue = [(0.0, start)]
    g_score = {start: 0.0}
    came_from: dict[str, tuple[str, str]] = {}

    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            node_path, edge_path = _reconstruct_path(came_from, current)
            return node_path, edge_path, g_score[current]

        for neighbor, cost, edge_id in graph.get(current, []):
            tentative = g_score[current] + cost
            if tentative < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = (current, edge_id)
                g_score[neighbor] = tentative
                h = haversine_distance(nodes[neighbor][0], nodes[neighbor][1], nodes[goal][0], nodes[goal][1]) / WALKING_SPEED_MPS
                heapq.heappush(queue, (tentative + h, neighbor))

    return [start, goal], [], float("inf")


def _polyline_from_edges(db: Session, edge_ids: list[str], start: List[float], goal: List[float]) -> List[List[float]]:
    if not edge_ids:
        return [start, goal]
    rows = db.query(StreetEdge).filter(StreetEdge.id.in_(edge_ids)).all()
    by_id = {r.id: r for r in rows}
    poly: List[List[float]] = []
    for edge_id in edge_ids:
        coords = _parse_line_wkt(str(by_id[edge_id].geom))
        if poly and coords:
            coords = coords[1:]
        poly.extend(coords)
    return _simplify_polyline(poly)


def _simplify_polyline(poly: List[List[float]]) -> List[List[float]]:
    if len(poly) <= 8:
        return poly
    step = max(1, len(poly) // 8)
    simplified = [poly[0]] + [poly[i] for i in range(step, len(poly) - 1, step)] + [poly[-1]]
    return simplified


def _bulla_score(dt: datetime, polyline: List[List[float]]) -> float:
    if not polyline:
        return 0.0
    center = polyline[len(polyline) // 2]
    hotspot = [37.3921, -5.9968]
    dist = haversine_distance(center[0], center[1], hotspot[0], hotspot[1])
    hour_factor = (dt.hour / 24)
    return round(min(1.0, 0.65 * max(0.0, 1.0 - dist / 2500.0) + 0.35 * hour_factor), 3)




def _crowd_penalty(db: Session, route_datetime: datetime, polyline: List[List[float]], avoid_bulla: bool) -> tuple[float, list[str]]:
    if not polyline:
        return 0.0, []
    mid = polyline[len(polyline) // 2]
    geohash = f"{round(mid[0], 3)}:{round(mid[1], 3)}"
    signal = (
        db.query(CrowdSignal)
        .filter(
            CrowdSignal.geohash == geohash,
            CrowdSignal.bucket_start <= route_datetime,
            CrowdSignal.bucket_end >= route_datetime,
        )
        .order_by(CrowdSignal.bucket_start.desc())
        .first()
    )
    if not signal:
        return 0.0, []

    penalty = (signal.score * signal.confidence * 240.0) if avoid_bulla else 0.0
    explanation = [f"Penalty bulla aplicado: score={signal.score:.2f}, confidence={signal.confidence:.2f}."] if penalty > 0 else []
    return penalty, explanation

def _cache_key(origin: List[float], destination: List[float], route_datetime: datetime, avoid_bulla: bool, max_walk_km: float, restriction_signature: str) -> str:
    bucket = route_datetime.replace(minute=(route_datetime.minute // 10) * 10, second=0, microsecond=0)
    raw = f"{origin}-{destination}-{bucket.isoformat()}-{avoid_bulla}-{max_walk_km}-{restriction_signature}"
    return hashlib.sha1(raw.encode()).hexdigest()


def calculate_optimal_route(
    db: Session,
    *,
    origin: List[float],
    destination: Optional[List[float]],
    route_datetime: datetime,
    target_type: Optional[str],
    target_id: Optional[str],
    avoid_bulla: bool = True,
    max_walk_km: float = 10.0,
) -> RoutingResult:
    if destination is None and target_type and target_id:
        destination = _target_coords(db, target_type, target_id)
    if destination is None:
        destination = origin

    nodes, graph, restriction_signature = _build_graph(db, route_datetime)
    key = _cache_key(origin, destination, route_datetime, avoid_bulla, max_walk_km, restriction_signature)
    if key in _CACHE:
        payload = _CACHE[key]
        return RoutingResult(**payload)
    if not nodes:
        # fallback mínima
        straight_eta = int(max(60, haversine_distance(origin[0], origin[1], destination[0], destination[1]) / WALKING_SPEED_MPS))
        return RoutingResult(
            polyline=[origin, destination],
            eta_seconds=straight_eta,
            bulla_score=_bulla_score(route_datetime, [origin, destination]),
            warnings=["No street graph loaded. Using straight-line fallback."],
            explanation=["Fallback route because street graph is empty."],
            alternatives=[],
        )

    start = _find_nearest_node(nodes, origin)
    goal = _find_nearest_node(nodes, destination)
    node_path, edge_path, total_cost = _astar(nodes, graph, start, goal)
    polyline = _polyline_from_edges(db, edge_path, origin, destination)

    total_distance = 0.0
    for i in range(len(polyline) - 1):
        total_distance += haversine_distance(polyline[i][0], polyline[i][1], polyline[i + 1][0], polyline[i + 1][1])
    eta_seconds = int(max(60, total_cost if total_cost != float("inf") else total_distance / WALKING_SPEED_MPS))

    crowd_penalty_seconds, crowd_explanation = _crowd_penalty(db, route_datetime, polyline, avoid_bulla)
    eta_seconds += int(crowd_penalty_seconds)

    warnings: List[str] = []
    if total_distance > max_walk_km * 1000:
        warnings.append("La distancia supera tu límite máximo de caminata.")

    bulla = _bulla_score(route_datetime, polyline)
    if avoid_bulla and bulla > 0.75:
        warnings.append("Ruta con bulla alta estimada")

    # simple alternative: direct destination through nearest origin edge (no restrictions)
    alt_eta = int(max(60, total_distance / WALKING_SPEED_MPS * 1.1))
    alternatives = [
        RouteAlternative(
            polyline=[origin, destination],
            eta_seconds=alt_eta,
            explanation=["Alternativa directa (menos puntos, puede ignorar cortes)."],
        )
    ]

    explanation = [
        f"Ruta calculada con A* sobre grafo real cargado en DB ({len(nodes)} nodos).",
        f"Costo peatonal base = length / {WALKING_SPEED_MPS:.2f} m/s.",
        "Se aplicaron penalizaciones por restricciones activas en ventana temporal.",
        *crowd_explanation,
    ]

    result = RoutingResult(
        polyline=polyline,
        eta_seconds=eta_seconds,
        bulla_score=bulla,
        warnings=warnings,
        explanation=explanation,
        alternatives=alternatives,
    )
    _CACHE[key] = {
        "polyline": result.polyline,
        "eta_seconds": result.eta_seconds,
        "bulla_score": result.bulla_score,
        "warnings": result.warnings,
        "explanation": result.explanation,
        "alternatives": result.alternatives,
    }
    return result


def as_route_response(result: RoutingResult) -> RouteResponse:
    return RouteResponse(
        polyline=result.polyline,
        eta_seconds=result.eta_seconds,
        bulla_score=result.bulla_score,
        warnings=result.warnings,
        explanation=result.explanation,
        alternatives=result.alternatives,
    )
