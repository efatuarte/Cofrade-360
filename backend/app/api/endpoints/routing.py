from dataclasses import dataclass
from typing import Dict, Tuple

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.routing import as_route_response, calculate_optimal_route
from app.schemas.schemas import ModeCalleWsRequest, ModeCalleWsResponse, RouteRequest, RouteResponse

router = APIRouter()


@dataclass
class WsPlanState:
    last_eta_seconds: int


_ws_state: Dict[Tuple[str, str], WsPlanState] = {}


@router.post("/optimal", response_model=RouteResponse)
async def get_optimal_route(request: RouteRequest):
    result = calculate_optimal_route(
        origin=request.origin,
        route_datetime=request.datetime,
        target_type=request.target.type,
        target_id=request.target.id,
        avoid_bulla=request.constraints.avoid_bulla,
        max_walk_km=request.constraints.max_walk_km,
    )
    return as_route_response(result)


@router.websocket("/ws/mode-calle")
async def mode_calle_ws(websocket: WebSocket):
    plan_id = websocket.query_params.get("plan_id", "unknown")
    await websocket.accept()

    try:
        while True:
            payload = await websocket.receive_json()
            request = ModeCalleWsRequest.model_validate(payload)
            result = calculate_optimal_route(
                origin=[request.location.lat, request.location.lng],
                route_datetime=request.datetime,
                target_type=request.target.type,
                target_id=request.target.id,
                avoid_bulla=request.constraints.avoid_bulla,
                max_walk_km=request.constraints.max_walk_km,
            )

            key = (plan_id, websocket.client.host if websocket.client else "anon")
            current = _ws_state.get(key)
            eta_changed = current is None or abs(current.last_eta_seconds - result.eta_seconds) >= 60
            has_warning = len(result.warnings) > 0

            if eta_changed or has_warning:
                _ws_state[key] = WsPlanState(last_eta_seconds=result.eta_seconds)
                response = ModeCalleWsResponse(route=as_route_response(result))
                await websocket.send_json(response.model_dump())
    except WebSocketDisconnect:
        pass
