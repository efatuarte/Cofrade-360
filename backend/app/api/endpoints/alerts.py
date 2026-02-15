from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.models import Evento, Procession, RestrictedArea
from app.schemas.schemas import AlertItem, AlertsResponse

router = APIRouter()


def _event_detail(evento: Evento) -> str:
    parts = [evento.tipo]
    if evento.location_id:
        parts.append(f"location_id={evento.location_id}")
    return " · ".join(parts)


@router.get("/alerts/next", response_model=AlertsResponse)
def get_next_alerts(
    at: datetime | None = None,
    minutes_ahead: int = Query(120, ge=15, le=1440),
    include_events: bool = True,
    include_processions: bool = True,
    include_restrictions: bool = True,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    now = at or datetime.utcnow()
    until = now + timedelta(minutes=minutes_ahead)

    items: list[AlertItem] = []

    if include_events:
        eventos = (
            db.query(Evento)
            .filter(Evento.fecha_inicio >= now, Evento.fecha_inicio <= until)
            .order_by(Evento.fecha_inicio.asc())
            .all()
        )
        for ev in eventos:
            items.append(
                AlertItem(
                    id=f"event-start:{ev.id}",
                    kind="event_start",
                    severity="info",
                    title=f"Próximo evento: {ev.titulo}",
                    detail=_event_detail(ev),
                    starts_at=ev.fecha_inicio,
                    ends_at=ev.fecha_fin,
                    source_id=ev.id,
                )
            )

    if include_processions:
        processions = (
            db.query(Procession)
            .filter(Procession.date >= now, Procession.date <= until)
            .order_by(Procession.date.asc())
            .all()
        )
        for proc in processions:
            severity = "warning" if proc.status == "in_progress" else "info"
            items.append(
                AlertItem(
                    id=f"procession-start:{proc.id}",
                    kind="procession_start",
                    severity=severity,
                    title="Procesión próxima",
                    detail=f"brotherhood_id={proc.brotherhood_id} · status={proc.status}",
                    starts_at=proc.date,
                    ends_at=None,
                    source_id=proc.id,
                )
            )

    if include_restrictions:
        restrictions = (
            db.query(RestrictedArea)
            .filter(RestrictedArea.end_datetime >= now, RestrictedArea.start_datetime <= until)
            .order_by(RestrictedArea.start_datetime.asc())
            .all()
        )
        for area in restrictions:
            if now <= area.start_datetime <= until:
                items.append(
                    AlertItem(
                        id=f"restriction-start:{area.id}",
                        kind="restriction_start",
                        severity="critical",
                        title=f"Inicio de restricción: {area.name}",
                        detail=area.reason,
                        starts_at=area.start_datetime,
                        ends_at=area.end_datetime,
                        source_id=area.id,
                    )
                )
            if now <= area.end_datetime <= until:
                items.append(
                    AlertItem(
                        id=f"restriction-end:{area.id}",
                        kind="restriction_end",
                        severity="info",
                        title=f"Fin de restricción: {area.name}",
                        detail=area.reason,
                        starts_at=area.end_datetime,
                        ends_at=None,
                        source_id=area.id,
                    )
                )

    severity_rank = {"critical": 0, "warning": 1, "info": 2}
    items.sort(key=lambda item: (item.starts_at, severity_rank.get(item.severity, 3), item.title))

    return AlertsResponse(
        generated_at=datetime.utcnow(),
        window_start=now,
        window_end=until,
        items=items[:limit],
    )
