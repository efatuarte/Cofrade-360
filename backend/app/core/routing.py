import hashlib
import heapq
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.models import ProcessionSegmentOccupation, RestrictedArea, StreetSegment
from app.schemas.schemas import RouteAlternative, RouteExplanationItem, RouteResponse


@dataclass
class Node:
    id: str
    lat: float
    lng: float


@dataclass
class SegmentEdge:
    id: str
    from_node: str
    to_node: str
    base_distance_m: float
    width_estimate: float


@dataclass
class PathResult:
    node_ids: List[str]
    segment_ids: List[str]
    total_cost: float
    eta_seconds: int
    warnings: List[str]
    explanation: Dict[str, Tuple[float, int]]


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _parse_linestring(geom: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    body = geom.replace("LINESTRING(", "").replace(")", "")
    p1_raw, p2_raw = [p.strip() for p in body.split(",")[:2]]
    x1, y1 = [float(v) for v in p1_raw.split()]
    x2, y2 = [float(v) for v in p2_raw.split()]
    return (y1, x1), (y2, x2)


def _parse_polygon_bbox(geom: str) -> Tuple[float, float, float, float]:
    clean = geom.replace("POLYGON((", "").replace("MULTIPOLYGON(((", "").replace(")", "")
    pairs = [p.strip() for p in clean.split(",") if p.strip()]
    lats = []
    lngs = []
    for p in pairs:
        vals = p.split()
        if len(vals) < 2:
            continue
        lngs.append(float(vals[0]))
        lats.append(float(vals[1]))
    if not lats:
        return -90, -180, 90, 180
    return min(lats), min(lngs), max(lats), max(lngs)


def _point_in_bbox(lat: float, lng: float, bbox: Tuple[float, float, float, float]) -> bool:
    min_lat, min_lng, max_lat, max_lng = bbox
    return min_lat <= lat <= max_lat and min_lng <= lng <= max_lng


def _load_graph_from_segments(db: Session) -> Tuple[Dict[str, Node], List[SegmentEdge], Dict[str, str]]:
    segments = db.query(StreetSegment).filter(StreetSegment.is_walkable.is_(True)).all()
    if not segments:
        return _create_fallback_graph()

    nodes: Dict[str, Node] = {}
    edges: List[SegmentEdge] = []
    segment_to_name: Dict[str, str] = {}

    def node_key(lat: float, lng: float) -> str:
        return f"{round(lat,6)}:{round(lng,6)}"

    for seg in segments:
        (lat1, lng1), (lat2, lng2) = _parse_linestring(seg.geom)
        k1 = node_key(lat1, lng1)
        k2 = node_key(lat2, lng2)
        nodes.setdefault(k1, Node(id=k1, lat=lat1, lng=lng1))
        nodes.setdefault(k2, Node(id=k2, lat=lat2, lng=lng2))
        dist = haversine_distance(lat1, lng1, lat2, lng2)
        width = seg.width_estimate if seg.width_estimate is not None else 3.0
        edges.append(SegmentEdge(id=seg.id, from_node=k1, to_node=k2, base_distance_m=dist, width_estimate=width))
        edges.append(SegmentEdge(id=seg.id, from_node=k2, to_node=k1, base_distance_m=dist, width_estimate=width))
        segment_to_name[seg.id] = seg.name

    return nodes, edges, segment_to_name


def _create_fallback_graph() -> Tuple[Dict[str, Node], List[SegmentEdge], Dict[str, str]]:
    raw_nodes = {
        "catedral": (37.3862, -5.9926),
        "giralda": (37.3857, -5.9929),
        "campana": (37.3921, -5.9968),
        "alameda": (37.3997, -5.9958),
        "macarena": (37.4008, -5.9900),
        "triana": (37.3870, -6.0020),
    }
    nodes = {k: Node(id=k, lat=v[0], lng=v[1]) for k, v in raw_nodes.items()}
    links = [("catedral", "giralda"), ("giralda", "campana"), ("campana", "alameda"), ("alameda", "macarena"), ("catedral", "triana"), ("triana", "campana")]
    edges: List[SegmentEdge] = []
    seg_names: Dict[str, str] = {}
    for idx, (a, b) in enumerate(links):
        seg_id = f"fallback-{idx}"
        dist = haversine_distance(nodes[a].lat, nodes[a].lng, nodes[b].lat, nodes[b].lng)
        edges.append(SegmentEdge(id=seg_id, from_node=a, to_node=b, base_distance_m=dist, width_estimate=4.0))
        edges.append(SegmentEdge(id=seg_id, from_node=b, to_node=a, base_distance_m=dist, width_estimate=4.0))
        seg_names[seg_id] = f"Fallback {idx}"
    return nodes, edges, seg_names


def _nearest_node(nodes: Dict[str, Node], lat: float, lng: float) -> Node:
    return min(nodes.values(), key=lambda n: haversine_distance(lat, lng, n.lat, n.lng))


def _target_point(db: Session, target_type: str, target_id: str) -> Optional[Tuple[float, float]]:
    digest = hashlib.sha1(f"{target_type}:{target_id}".encode()).hexdigest()
    return 37.38 + (int(digest[:4], 16) % 300) / 10000.0, -6.01 + (int(digest[4:8], 16) % 300) / 10000.0


def _active_restrictions(db: Session, route_datetime: datetime) -> List[RestrictedArea]:
    return db.query(RestrictedArea).filter(RestrictedArea.start_datetime <= route_datetime, RestrictedArea.end_datetime >= route_datetime).all()


def _active_occupations(db: Session, route_datetime: datetime) -> Dict[str, float]:
    rows = db.query(ProcessionSegmentOccupation).filter(
        ProcessionSegmentOccupation.start_datetime <= route_datetime,
        ProcessionSegmentOccupation.end_datetime >= route_datetime,
    ).all()
    return {row.street_segment_id: row.crowd_factor for row in rows}


def _segment_midpoint(nodes: Dict[str, Node], edge: SegmentEdge) -> Tuple[float, float]:
    a = nodes[edge.from_node]
    b = nodes[edge.to_node]
    return (a.lat + b.lat) / 2.0, (a.lng + b.lng) / 2.0


def _cost_for_edge(
    edge: SegmentEdge,
    nodes: Dict[str, Node],
    active_restrictions: List[RestrictedArea],
    active_occupations: Dict[str, float],
    avoid_bulla: float,
    prefer_wide: bool,
) -> Tuple[float, Dict[str, float], bool]:
    penalties = {"base_time": edge.base_distance_m / 1.35, "restriction": 0.0, "occupation": 0.0, "width": 0.0, "bulla": 0.0}
    blocked = False

    mid_lat, mid_lng = _segment_midpoint(nodes, edge)
    for area in active_restrictions:
        bbox = _parse_polygon_bbox(area.geom)
        if _point_in_bbox(mid_lat, mid_lng, bbox):
            blocked = True
            penalties["restriction"] = float("inf")
            break

    if not blocked and edge.id in active_occupations:
        occ_factor = active_occupations[edge.id]
        penalties["occupation"] = 140 * occ_factor
        penalties["bulla"] = 90 * occ_factor * avoid_bulla

    if not blocked and prefer_wide and edge.width_estimate < 3.5:
        penalties["width"] = (3.5 - edge.width_estimate) * 80

    total = sum(v for v in penalties.values() if v != float("inf"))
    if blocked:
        total = float("inf")
    return total, penalties, blocked


def _a_star(
    nodes: Dict[str, Node],
    edges: List[SegmentEdge],
    start_node: Node,
    end_node: Node,
    active_restrictions: List[RestrictedArea],
    active_occupations: Dict[str, float],
    avoid_bulla: float,
    prefer_wide: bool,
) -> Optional[PathResult]:
    adjacency: Dict[str, List[SegmentEdge]] = {}
    for edge in edges:
        adjacency.setdefault(edge.from_node, []).append(edge)

    open_set = [(0.0, start_node.id)]
    came_from: Dict[str, str] = {}
    came_edge: Dict[str, str] = {}
    g_score = {start_node.id: 0.0}
    penalty_acc: Dict[str, Dict[str, float]] = {start_node.id: {"base_time": 0.0, "restriction": 0.0, "occupation": 0.0, "width": 0.0, "bulla": 0.0}}

    while open_set:
        _, current_id = heapq.heappop(open_set)
        if current_id == end_node.id:
            node_path = [current_id]
            seg_path: List[str] = []
            while current_id in came_from:
                seg_path.append(came_edge[current_id])
                current_id = came_from[current_id]
                node_path.append(current_id)
            node_path.reverse()
            seg_path.reverse()

            total_cost = g_score[end_node.id]
            eta_seconds = max(60, int(total_cost))
            penalties = penalty_acc[end_node.id]
            explanation = {
                "base_time": (penalties["base_time"], len(seg_path)),
                "occupation": (penalties["occupation"], len([s for s in seg_path if s in active_occupations])),
                "width": (penalties["width"], len(seg_path)),
                "bulla": (penalties["bulla"], len([s for s in seg_path if s in active_occupations])),
                "restriction": (penalties["restriction"], 0),
            }
            warnings = []
            if penalties["occupation"] > 0:
                warnings.append("Se detectaron tramos ocupados por cortejo con penalización.")
            if penalties["width"] > 0:
                warnings.append("Se penalizaron calles estrechas para priorizar seguridad peatonal.")
            return PathResult(node_ids=node_path, segment_ids=seg_path, total_cost=total_cost, eta_seconds=eta_seconds, warnings=warnings, explanation=explanation)

        for edge in adjacency.get(current_id, []):
            cost, penalties, blocked = _cost_for_edge(edge, nodes, active_restrictions, active_occupations, avoid_bulla, prefer_wide)
            if blocked or cost == float("inf"):
                continue
            tentative = g_score[current_id] + cost
            if tentative < g_score.get(edge.to_node, float("inf")):
                came_from[edge.to_node] = current_id
                came_edge[edge.to_node] = edge.id
                g_score[edge.to_node] = tentative

                current_pen = penalty_acc[current_id]
                penalty_acc[edge.to_node] = {k: current_pen.get(k, 0.0) + penalties.get(k, 0.0) for k in current_pen.keys()}

                heuristic = haversine_distance(nodes[edge.to_node].lat, nodes[edge.to_node].lng, end_node.lat, end_node.lng) / 1.35
                heapq.heappush(open_set, (tentative + heuristic, edge.to_node))

    return None


def _build_response(
    nodes: Dict[str, Node],
    path: PathResult,
    bulla_score: float,
    alternatives: List[RouteAlternative],
) -> RouteResponse:
    poly = [[nodes[n].lat, nodes[n].lng] for n in path.node_ids]
    explanation_items = [
        RouteExplanationItem(reason=reason, weight=round(weight, 2), segments_count=count)
        for reason, (weight, count) in sorted(path.explanation.items(), key=lambda kv: kv[1][0], reverse=True)
        if weight > 0
    ][:3]
    return RouteResponse(
        polyline=poly,
        eta_seconds=path.eta_seconds,
        total_cost=round(path.total_cost, 2),
        bulla_score=round(bulla_score, 3),
        warnings=path.warnings,
        explanation=explanation_items,
        alternatives=alternatives,
    )


def _bulla_score(route_datetime: datetime, avoid_bulla: float, active_occupations_count: int) -> float:
    hour_factor = ((route_datetime.hour + route_datetime.minute / 60) % 24) / 24.0
    occ_factor = min(active_occupations_count / 20.0, 1.0)
    return min(1.0, 0.5 * hour_factor + 0.4 * occ_factor + 0.1 * avoid_bulla)


def calculate_optimal_route(
    db: Session,
    *,
    origin: List[float],
    destination: Optional[List[float]],
    route_datetime: datetime,
    target_type: Optional[str],
    target_id: Optional[str],
    avoid_bulla: float,
    prefer_wide: bool,
    max_detour: float,
) -> RouteResponse:
    nodes, edges, _ = _load_graph_from_segments(db)

    target_coords: Optional[Tuple[float, float]] = None
    if destination is not None:
        target_coords = (destination[0], destination[1])
    elif target_type and target_id:
        target_coords = _target_point(db, target_type, target_id)

    if target_coords is None:
        raise ValueError("destination or target is required")

    start = _nearest_node(nodes, origin[0], origin[1])
    end = _nearest_node(nodes, target_coords[0], target_coords[1])

    active_restrictions = _active_restrictions(db, route_datetime)
    active_occupations = _active_occupations(db, route_datetime)

    best = _a_star(nodes, edges, start, end, active_restrictions, active_occupations, avoid_bulla, prefer_wide)
    if best is None:
        direct_distance = haversine_distance(origin[0], origin[1], target_coords[0], target_coords[1])
        eta = max(60, int(direct_distance / 1.2))
        return RouteResponse(
            polyline=[origin, [target_coords[0], target_coords[1]]],
            eta_seconds=eta,
            total_cost=round(direct_distance, 2),
            bulla_score=_bulla_score(route_datetime, avoid_bulla, len(active_occupations)),
            warnings=["No se encontró ruta en grafo: se muestra ruta directa."],
            explanation=[RouteExplanationItem(reason="fallback", weight=1.0, segments_count=1)],
            alternatives=[],
        )

    alternatives: List[RouteAlternative] = []
    alt_wide = _a_star(nodes, edges, start, end, active_restrictions, active_occupations, avoid_bulla, True)
    if alt_wide and abs(alt_wide.total_cost - best.total_cost) / max(best.total_cost, 1.0) <= max_detour:
        alternatives.append(
            RouteAlternative(
                label="tranquila",
                polyline=[[nodes[n].lat, nodes[n].lng] for n in alt_wide.node_ids],
                eta_seconds=alt_wide.eta_seconds,
                total_cost=round(alt_wide.total_cost, 2),
            )
        )

    alt_fast = _a_star(nodes, edges, start, end, active_restrictions, active_occupations, 0.0, False)
    if alt_fast and abs(alt_fast.total_cost - best.total_cost) / max(best.total_cost, 1.0) <= max_detour:
        alternatives.append(
            RouteAlternative(
                label="rapida",
                polyline=[[nodes[n].lat, nodes[n].lng] for n in alt_fast.node_ids],
                eta_seconds=alt_fast.eta_seconds,
                total_cost=round(alt_fast.total_cost, 2),
            )
        )

    bulla_score = _bulla_score(route_datetime, avoid_bulla, len(active_occupations))
    return _build_response(nodes, best, bulla_score, alternatives[:2])
