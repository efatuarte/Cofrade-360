from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.models import Hermandad, Evento, User, Location
from app.schemas.schemas import (
    HermandadCreate, EventoCreate, EventoUpdate, UserCreate, LocationCreate
)
from app.core.security import get_password_hash
from datetime import datetime
from typing import List, Optional, Tuple
import uuid


# ============= User CRUD =============

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ============= Location CRUD =============

def get_location(db: Session, location_id: str) -> Optional[Location]:
    return db.query(Location).filter(Location.id == location_id).first()


def create_location(db: Session, location: LocationCreate) -> Location:
    db_location = Location(
        id=str(uuid.uuid4()),
        **location.model_dump()
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


# ============= Hermandad CRUD =============

def get_hermandad(db: Session, hermandad_id: str) -> Optional[Hermandad]:
    return db.query(Hermandad).filter(Hermandad.id == hermandad_id).first()


def get_hermandades(db: Session, skip: int = 0, limit: int = 100) -> List[Hermandad]:
    return db.query(Hermandad).offset(skip).limit(limit).all()


def create_hermandad(db: Session, hermandad: HermandadCreate) -> Hermandad:
    db_hermandad = Hermandad(
        id=str(uuid.uuid4()),
        **hermandad.model_dump()
    )
    db.add(db_hermandad)
    db.commit()
    db.refresh(db_hermandad)
    return db_hermandad


# ============= Evento CRUD =============

def get_evento(db: Session, evento_id: str) -> Optional[Evento]:
    return (
        db.query(Evento)
        .options(joinedload(Evento.location))
        .filter(Evento.id == evento_id)
        .first()
    )


def get_eventos_paginated(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    q: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    has_poster: Optional[bool] = None,
) -> Tuple[List[Evento], int]:
    query = db.query(Evento).options(joinedload(Evento.location))

    if tipo:
        query = query.filter(Evento.tipo == tipo)
    if estado:
        query = query.filter(Evento.estado == estado)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(Evento.titulo.ilike(pattern), Evento.descripcion.ilike(pattern))
        )
    if from_date:
        query = query.filter(Evento.fecha_inicio >= from_date)
    if to_date:
        query = query.filter(Evento.fecha_inicio <= to_date)
    if min_price is not None:
        query = query.filter(Evento.precio >= min_price)
    if max_price is not None:
        query = query.filter(Evento.precio <= max_price)
    if has_poster is True:
        query = query.filter(Evento.poster_asset_id.isnot(None))
    elif has_poster is False:
        query = query.filter(Evento.poster_asset_id.is_(None))

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Evento.fecha_inicio).offset(offset).limit(page_size).all()
    return items, total


def create_evento(db: Session, evento: EventoCreate) -> Evento:
    db_evento = Evento(
        id=str(uuid.uuid4()),
        **evento.model_dump()
    )
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento


def update_evento(db: Session, evento_id: str, update: EventoUpdate) -> Optional[Evento]:
    db_evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not db_evento:
        return None
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_evento, field, value)
    db.commit()
    db.refresh(db_evento)
    return db_evento
