from dataclasses import dataclass
from typing import Dict, Optional, Set, Tuple

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.routing import calculate_optimal_route, haversine_distance
from app.crud import crud
from app.schemas.schemas import (
    ModeCalleWsRequest,
    ModeCalleWsRouteUpdate,
    ModeCalleWsWarning,
    RouteRequest,
    RouteResponse,
)

router = APIRouter()


@dataclass
class WsClientState:
    last_eta_seconds: Optional[int] = None
    last_location: Optional[Tuple[float, float]] = None
    last_restriction_ids: Optional[Set[str]] = None


_ws_state: Dict[Tuple[str, str], WsClientState] = {}


@router.post("/optimal", response_model=RouteResponse)
def get_optimal_route(request: RouteRequest, db: Session = Depends(get_db)):
    return calculate_optimal_route(
        db,
        origin=request.origin,
        destination=request.destination,
        route_datetime=request.datetime,
        target_type=request.target.type if request.target else None,
        target_id=request.target.id if request.target else None,
        avoid_bulla=request.constraints.avoid_bulla,
        prefer_wide=request.constraints.prefer_wide,
        max_detour=request.constraints.max_detour,
    )


@router.websocket("/ws/mode-calle")
async def mode_calle_ws(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            request = ModeCalleWsRequest.model_validate(payload)

            key = (request.plan_id, websocket.client.host if websocket.client else "anon")
            state = _ws_state.get(key, WsClientState())

            current_location = (request.location.lat, request.location.lng)
            moved_far = False
            if state.last_location is not None:
                moved_far = haversine_distance(
                    state.last_location[0], state.last_location[1], current_location[0], current_location[1]
                ) > 80

            active_restrictions = crud.list_restrictions(db, from_date=request.datetime, to_date=request.datetime)
            active_ids = {r.id for r in active_restrictions}
            restriction_changed = state.last_restriction_ids is None or active_ids != state.last_restriction_ids

            if not moved_far and not restriction_changed and state.last_eta_seconds is not None:
                continue

            route = calculate_optimal_route(
                db,
                origin=[request.location.lat, request.location.lng],
                destination=request.destination,
                route_datetime=request.datetime,
                target_type=request.target.type if request.target else None,
                target_id=request.target.id if request.target else None,
                avoid_bulla=request.constraints.avoid_bulla,
                prefer_wide=request.constraints.prefer_wide,
                max_detour=request.constraints.max_detour,
            )

            state.last_eta_seconds = route.eta_seconds
            state.last_location = current_location
            state.last_restriction_ids = active_ids
            _ws_state[key] = state

            await websocket.send_json(ModeCalleWsRouteUpdate(route=route).model_dump())
            if restriction_changed:
                await websocket.send_json(
                    ModeCalleWsWarning(message="Cambio en restricciones activas, ruta recalculada.").model_dump()
                )
    except WebSocketDisconnect:
        pass
