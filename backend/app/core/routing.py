import heapq
import math
from typing import List, Dict, Tuple, Optional
from app.schemas.schemas import RouteResponse


class Node:
    """Graph node for routing"""
    def __init__(self, id: str, lat: float, lon: float):
        self.id = id
        self.lat = lat
        self.lon = lon
        
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return self.id == other.id


class Edge:
    """Graph edge for routing"""
    def __init__(self, from_node: str, to_node: str, distance: float, blocked: bool = False):
        self.from_node = from_node
        self.to_node = to_node
        self.distance = distance
        self.blocked = blocked


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two points using Haversine formula"""
    R = 6371000  # Earth's radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def create_mock_graph() -> Tuple[Dict[str, Node], List[Edge]]:
    """Create a mock graph for Seville city center"""
    # Mock nodes (key landmarks in Seville)
    nodes = {
        "catedral": Node("catedral", 37.3862, -5.9926),
        "giralda": Node("giralda", 37.3857, -5.9929),
        "alcazar": Node("alcazar", 37.3839, -5.9914),
        "plaza_españa": Node("plaza_españa", 37.3765, -5.9868),
        "torre_oro": Node("torre_oro", 37.3825, -5.9960),
        "triana": Node("triana", 37.3870, -6.0020),
        "macarena": Node("macarena", 37.4008, -5.9900),
        "maestranza": Node("maestranza", 37.3838, -5.9972),
    }
    
    # Mock edges (streets between landmarks)
    edges = [
        Edge("catedral", "giralda", 50, False),
        Edge("giralda", "catedral", 50, False),
        Edge("catedral", "alcazar", 150, False),
        Edge("alcazar", "catedral", 150, False),
        Edge("alcazar", "plaza_españa", 800, False),
        Edge("plaza_españa", "alcazar", 800, False),
        Edge("catedral", "torre_oro", 400, False),
        Edge("torre_oro", "catedral", 400, False),
        Edge("torre_oro", "triana", 350, False),
        Edge("triana", "torre_oro", 350, False),
        Edge("catedral", "maestranza", 300, False),
        Edge("maestranza", "catedral", 300, False),
        Edge("catedral", "macarena", 1200, False),
        Edge("macarena", "catedral", 1200, False),
        Edge("triana", "maestranza", 500, False),
        Edge("maestranza", "triana", 500, False),
    ]
    
    return nodes, edges


def a_star_search(
    start: Node, 
    goal: Node, 
    nodes: Dict[str, Node], 
    edges: List[Edge],
    evitar_procesiones: bool = True
) -> Optional[List[Node]]:
    """
    A* pathfinding algorithm
    
    Args:
        start: Starting node
        goal: Goal node
        nodes: Dictionary of all nodes
        edges: List of all edges
        evitar_procesiones: Whether to avoid blocked streets
    
    Returns:
        List of nodes representing the path, or None if no path found
    """
    # Build adjacency list
    graph = {}
    for edge in edges:
        if evitar_procesiones and edge.blocked:
            continue  # Skip blocked edges
        
        if edge.from_node not in graph:
            graph[edge.from_node] = []
        graph[edge.from_node].append((edge.to_node, edge.distance))
    
    # Priority queue: (f_score, g_score, node_id)
    open_set = [(0, 0, start.id)]
    came_from = {}
    g_score = {start.id: 0}
    
    while open_set:
        _, current_g, current_id = heapq.heappop(open_set)
        
        if current_id == goal.id:
            # Reconstruct path
            path = []
            while current_id in came_from:
                path.append(nodes[current_id])
                current_id = came_from[current_id]
            path.append(start)
            return list(reversed(path))
        
        if current_id not in graph:
            continue
        
        for neighbor_id, distance in graph[current_id]:
            tentative_g = current_g + distance
            
            if neighbor_id not in g_score or tentative_g < g_score[neighbor_id]:
                came_from[neighbor_id] = current_id
                g_score[neighbor_id] = tentative_g
                
                # Heuristic: straight-line distance to goal
                neighbor_node = nodes[neighbor_id]
                h_score = haversine_distance(
                    neighbor_node.lat, neighbor_node.lon,
                    goal.lat, goal.lon
                )
                f_score = tentative_g + h_score
                
                heapq.heappush(open_set, (f_score, tentative_g, neighbor_id))
    
    return None  # No path found


def find_nearest_node(lat: float, lon: float, nodes: Dict[str, Node]) -> Node:
    """Find the nearest node to the given coordinates"""
    min_dist = float('inf')
    nearest = None
    
    for node in nodes.values():
        dist = haversine_distance(lat, lon, node.lat, node.lon)
        if dist < min_dist:
            min_dist = dist
            nearest = node
    
    return nearest


def calculate_optimal_route(
    origen: List[float],
    destino: List[float],
    evitar_procesiones: bool = True
) -> RouteResponse:
    """
    Calculate optimal route using A* algorithm
    
    Args:
        origen: [lat, lon] of starting point
        destino: [lat, lon] of destination
        evitar_procesiones: Whether to avoid streets with processions
    
    Returns:
        RouteResponse with route details
    """
    # Create mock graph
    nodes, edges = create_mock_graph()
    
    # Find nearest nodes to origin and destination
    start_node = find_nearest_node(origen[0], origen[1], nodes)
    goal_node = find_nearest_node(destino[0], destino[1], nodes)
    
    # Run A* algorithm
    path = a_star_search(start_node, goal_node, nodes, edges, evitar_procesiones)
    
    if not path:
        # If no path found, return direct route
        return RouteResponse(
            ruta=[origen, destino],
            distancia_metros=int(haversine_distance(origen[0], origen[1], destino[0], destino[1])),
            duracion_minutos=15,
            instrucciones=["No se encontró una ruta óptima. Ruta directa mostrada."]
        )
    
    # Convert path to coordinates
    ruta_coords = [[node.lat, node.lon] for node in path]
    
    # Calculate total distance
    total_distance = 0
    for i in range(len(path) - 1):
        total_distance += haversine_distance(
            path[i].lat, path[i].lon,
            path[i+1].lat, path[i+1].lon
        )
    
    # Estimate duration (assume 5 km/h walking speed)
    duracion = int(total_distance / 5000 * 60)
    
    # Generate instructions
    instrucciones = [
        f"Inicia en {start_node.id}",
        *[f"Continúa hacia {node.id}" for node in path[1:-1]],
        f"Llegarás a {goal_node.id}"
    ]
    
    return RouteResponse(
        ruta=ruta_coords,
        distancia_metros=int(total_distance),
        duracion_minutos=max(1, duracion),
        instrucciones=instrucciones
    )
