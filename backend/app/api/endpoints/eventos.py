"""
Eventos (Events) endpoints with pagination, filtering, and CRUD.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, get_db
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
    estado: Optional[EstadoEvento] = None,
    q: Optional[str] = None,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    has_poster: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List events with pagination and filters."""
    items, total = crud.get_eventos_paginated(
        db,
        page=page,
        page_size=page_size,
        tipo=tipo.value if tipo else None,
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
    updated = crud.update_evento(db, evento_id=event_id, update=update)
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated


@router.get("/events/{event_id}/poster")
def get_event_poster(event_id: str, db: Session = Depends(get_db)):
    """Get signed URL for event poster (placeholder until MinIO FASE 3)."""
    evento = crud.get_evento(db, evento_id=event_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Event not found")
    if not evento.poster_asset_id:
        raise HTTPException(status_code=404, detail="Event has no poster")

    # Placeholder — will return signed URL from MinIO in FASE 3
    return {"poster_url": None, "asset_id": evento.poster_asset_id}
