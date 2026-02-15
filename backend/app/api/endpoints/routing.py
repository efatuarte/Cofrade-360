import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.routing import as_route_response, calculate_optimal_route
from app.models.models import AnalyticsEvent, NotificationEvent
from app.schemas.schemas import (
    ModeCalleWsHeartbeat,
    ModeCalleWsHello,
    ModeCalleWsLocationUpdate,
    ModeCalleWsRouteUpdate,
    ModeCalleWsWarning,
    RouteRequest,
    RouteResponse,
    RoutingLastResponse,
)

router = APIRouter()


@dataclass
class WsPlanState:
    last_eta_seconds: int


_ws_state: Dict[Tuple[str, str], WsPlanState] = {}


@router.post("/optimal", response_model=RouteResponse)
async def get_optimal_route(request: RouteRequest, http_request: Request, db: Session = Depends(get_db)):
    result = calculate_optimal_route(
        db,
        origin=request.origin,
        destination=request.destination,
        route_datetime=request.datetime,
        target_type=request.target.type if request.target else None,
        target_id=request.target.id if request.target else None,
        avoid_bulla=request.constraints.avoid_bulla,
        max_walk_km=request.constraints.max_walk_km,
    )
    db.add(
        AnalyticsEvent(
            id=str(uuid.uuid4()),
            event_type="route_requested",
            trace_id=http_request.headers.get("x-trace-id"),
            payload=json.dumps({"has_destination": request.destination is not None, "has_target": request.target is not None}),
        )
    )
    db.commit()
    return as_route_response(result)


@router.get("/last", response_model=RoutingLastResponse)
def get_last_route(plan_id: str, db: Session = Depends(get_db)):
    row = (
        db.query(NotificationEvent)
        .filter(NotificationEvent.plan_id == plan_id, NotificationEvent.kind == "route_update")
        .order_by(NotificationEvent.created_at.desc())
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Last route not found")

    payload = json.loads(row.payload)
    return RoutingLastResponse(
        plan_id=plan_id,
        route=RouteResponse(**payload["route"]),
        generated_at=row.created_at,
    )


@router.websocket("/ws/mode-calle")
async def mode_calle_ws(websocket: WebSocket, db: Session = Depends(get_db)):
    plan_id = websocket.query_params.get("plan_id", "unknown")
    await websocket.accept()

    await websocket.send_json(
        {
            "type": "hello",
            "protocol_version": "1.0",
            "server_time": datetime.utcnow().isoformat(),
        }
    )

    try:
        while True:
            payload = await websocket.receive_json()
            msg_type = payload.get("type", "location_update")

            if msg_type == "hello":
                ModeCalleWsHello.model_validate(payload)
                continue

            if msg_type == "heartbeat":
                hb = ModeCalleWsHeartbeat.model_validate(payload)
                await websocket.send_json({"type": "heartbeat", "sent_at": hb.sent_at.isoformat()})
                continue

            if msg_type != "location_update":
                continue

            request = ModeCalleWsLocationUpdate.model_validate(payload)
            result = calculate_optimal_route(
                db,
                origin=[request.location.lat, request.location.lng],
                destination=None,
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
                route_payload = ModeCalleWsRouteUpdate(route=as_route_response(result)).model_dump(mode="json")
                await websocket.send_json(route_payload)

                db.add(
                    NotificationEvent(
                        id=str(uuid.uuid4()),
                        plan_id=plan_id,
                        kind="route_update",
                        payload=json.dumps(route_payload),
                    )
                )
                db.add(
                    AnalyticsEvent(
                        id=str(uuid.uuid4()),
                        event_type="reroute",
                        trace_id=None,
                        payload=json.dumps({"plan_id": plan_id, "eta_seconds": result.eta_seconds}),
                    )
                )

                # Fase 13 warning rules
                warning_codes: list[tuple[str, str]] = []
                if result.eta_seconds > 20 * 60:
                    warning_codes.append(("ETA_MISS", "No llegas a la ventana prevista"))
                if result.bulla_score > 0.75:
                    warning_codes.append(("HIGH_BULLA", "Bulla alta en la ruta actual"))
                if any("restricciones" in e.lower() for e in result.explanation):
                    warning_codes.append(("ROUTE_CUT", "Corte detectado en ruta, se aplicó desvío"))

                for code, detail in warning_codes:
                    warning_payload = ModeCalleWsWarning(
                        code=code,
                        detail=detail,
                        created_at=datetime.utcnow(),
                    ).model_dump(mode="json")
                    await websocket.send_json(warning_payload)
                    db.add(
                        NotificationEvent(
                            id=str(uuid.uuid4()),
                            plan_id=plan_id,
                            kind="warning",
                            payload=json.dumps(warning_payload),
                        )
                    )
                    db.add(
                        AnalyticsEvent(
                            id=str(uuid.uuid4()),
                            event_type="warning_shown",
                            trace_id=None,
                            payload=json.dumps({"plan_id": plan_id, "code": code}),
                        )
                    )
                db.commit()
    except WebSocketDisconnect:
        pass
