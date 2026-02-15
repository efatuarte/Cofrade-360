"""
Eventos (Events) endpoints with pagination, filtering, and CRUD.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, get_db
from app.core.storage import get_presigned_get_url
from app.crud import crud
from app.models.models import User
from app.schemas.schemas import (
    EstadoEvento,
    EventoCreate,
    EventoResponse,
    EventoUpdate,
    PaginatedResponse,
    TipoEvento,
)

router = APIRouter()


@router.get("/events", response_model=PaginatedResponse[EventoResponse])
def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tipo: Optional[TipoEvento] = None,
    event_type: Optional[TipoEvento] = Query(None, alias="type"),
    estado: Optional[EstadoEvento] = None,
    q: Optional[str] = None,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    has_poster: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List events with pagination and filters."""
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=422, detail="'from' must be <= 'to'")
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=422, detail="'min_price' must be <= 'max_price'")

    selected_type = event_type or tipo

    items, total = crud.get_eventos_paginated(
        db,
        page=page,
        page_size=page_size,
        tipo=selected_type.value if selected_type else None,
        estado=estado.value if estado else None,
        q=q,
        from_date=from_date,
        to_date=to_date,
        min_price=min_price,
        max_price=max_price,
        has_poster=has_poster,
    )
    return PaginatedResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/events/{event_id}", response_model=EventoResponse)
def get_event(event_id: str, db: Session = Depends(get_db)):
    """Get a single event by ID."""
    evento = crud.get_evento(db, evento_id=event_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Event not found")
    return evento


@router.post("/events", response_model=EventoResponse, status_code=201)
def create_event(
    evento: EventoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new event (authenticated)."""
    if evento.location_id:
        loc = crud.get_location(db, evento.location_id)
        if not loc:
            raise HTTPException(status_code=400, detail="Location not found")
    return crud.create_evento(db=db, evento=evento)


@router.patch("/events/{event_id}", response_model=EventoResponse)
def update_event(
    event_id: str,
    update: EventoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an event (authenticated)."""
    existing = crud.get_evento(db, evento_id=event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = update.model_dump(exclude_unset=True)
    start = update_data.get("fecha_inicio", existing.fecha_inicio)
    end = update_data.get("fecha_fin", existing.fecha_fin)
    is_free = update_data.get("es_gratuito", existing.es_gratuito)
    price = update_data.get("precio", existing.precio)

    if end and start > end:
        raise HTTPException(status_code=422, detail="fecha_inicio must be before fecha_fin")
    if is_free and price > 0:
        raise HTTPException(status_code=422, detail="Free events cannot have a price > 0")
    if (not is_free) and price <= 0:
        raise HTTPException(status_code=422, detail="Non-free events must have a price > 0")

    updated = crud.update_evento(db, evento_id=event_id, update=update)
    return updated


@router.get("/events/{event_id}/poster")
def get_event_poster(event_id: str, db: Session = Depends(get_db)):
    """Get signed URL for event poster in MinIO bucket."""
    evento = crud.get_evento(db, evento_id=event_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Event not found")
    if not evento.poster_asset_id:
        raise HTTPException(status_code=404, detail="Event has no poster")

    try:
        signed_url = get_presigned_get_url(evento.poster_asset_id)
    except Exception:
        raise HTTPException(status_code=503, detail="Media storage unavailable")

    return {
        "asset_id": evento.poster_asset_id,
        "url": signed_url,
    }
