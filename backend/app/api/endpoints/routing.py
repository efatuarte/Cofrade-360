from fastapi import APIRouter
from app.schemas.schemas import RouteRequest, RouteResponse
from app.core.routing import calculate_optimal_route

router = APIRouter()


@router.post("/optimal", response_model=RouteResponse)
async def get_optimal_route(request: RouteRequest):
    """
    Calculate optimal route between two points using A* algorithm.
    
    Avoids blocked streets (e.g., due to processions) if evitar_procesiones is True.
    """
    route = calculate_optimal_route(
        origen=request.origen,
        destino=request.destino,
        evitar_procesiones=request.evitar_procesiones
    )
    return route
