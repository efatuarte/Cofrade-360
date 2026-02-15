import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_password_hash
from app.models.models import Evento, Hermandad, Location, MediaAsset, PlanItem, User, UserPlan
from app.schemas.schemas import EventoCreate, EventoUpdate, HermandadCreate, LocationCreate, UserCreate


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
        is_active=True,
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
        **location.model_dump(),
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


# ============= Hermandad / Brotherhood CRUD =============

def get_hermandad(db: Session, hermandad_id: str) -> Optional[Hermandad]:
    return (
        db.query(Hermandad)
        .options(joinedload(Hermandad.church))
        .filter(Hermandad.id == hermandad_id)
        .first()
    )


def get_hermandades(db: Session, skip: int = 0, limit: int = 100) -> List[Hermandad]:
    return db.query(Hermandad).offset(skip).limit(limit).all()


def get_brotherhoods_paginated(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = None,
    day: Optional[str] = None,
    church_id: Optional[str] = None,
    has_media: Optional[bool] = None,
) -> Tuple[List[Hermandad], int]:
    query = db.query(Hermandad).options(joinedload(Hermandad.church))

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Hermandad.name_short.ilike(pattern),
                Hermandad.name_full.ilike(pattern),
                Hermandad.nombre.ilike(pattern),
            )
        )
    if day:
        query = query.filter(Hermandad.ss_day == day)
    if church_id:
        query = query.filter(Hermandad.church_id == church_id)

    if has_media is True:
        query = query.join(MediaAsset, MediaAsset.brotherhood_id == Hermandad.id).distinct()
    elif has_media is False:
        query = query.outerjoin(MediaAsset, MediaAsset.brotherhood_id == Hermandad.id).filter(
            MediaAsset.id.is_(None)
        )

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Hermandad.name_short.asc().nulls_last(), Hermandad.nombre.asc()).offset(offset).limit(page_size).all()
    return items, total


def create_hermandad(db: Session, hermandad: HermandadCreate) -> Hermandad:
    db_hermandad = Hermandad(
        id=str(uuid.uuid4()),
        **hermandad.model_dump(),
    )
    db.add(db_hermandad)
    db.commit()
    db.refresh(db_hermandad)
    return db_hermandad


# ============= Media CRUD =============

def create_media_asset(
    db: Session,
    *,
    kind: str,
    mime: str,
    path: str,
    brotherhood_id: Optional[str] = None,
) -> MediaAsset:
    asset = MediaAsset(
        id=str(uuid.uuid4()),
        kind=kind,
        mime=mime,
        path=path,
        brotherhood_id=brotherhood_id,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get_media_asset(db: Session, asset_id: str) -> Optional[MediaAsset]:
    return db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()


def get_brotherhood_media(db: Session, brotherhood_id: str) -> List[MediaAsset]:
    return (
        db.query(MediaAsset)
        .filter(MediaAsset.brotherhood_id == brotherhood_id)
        .order_by(MediaAsset.created_at.desc())
        .all()
    )


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
        query = query.filter(or_(Evento.titulo.ilike(pattern), Evento.descripcion.ilike(pattern)))
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
        **evento.model_dump(),
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


# ============= Itinerario CRUD =============

def list_user_plans(
    db: Session,
    *,
    user_id: str,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> List[UserPlan]:
    query = db.query(UserPlan).options(joinedload(UserPlan.items)).filter(UserPlan.user_id == user_id)
    if from_date:
        query = query.filter(UserPlan.plan_date >= from_date)
    if to_date:
        query = query.filter(UserPlan.plan_date <= to_date)
    return query.order_by(UserPlan.plan_date.asc()).all()


def get_user_plan(db: Session, *, user_id: str, plan_id: str) -> Optional[UserPlan]:
    return (
        db.query(UserPlan)
        .options(joinedload(UserPlan.items))
        .filter(UserPlan.id == plan_id, UserPlan.user_id == user_id)
        .first()
    )


def create_user_plan(db: Session, *, user_id: str, title: str, plan_date: datetime) -> UserPlan:
    plan = UserPlan(id=str(uuid.uuid4()), user_id=user_id, title=title, plan_date=plan_date)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update_user_plan(db: Session, *, plan: UserPlan, title: Optional[str], plan_date: Optional[datetime]) -> UserPlan:
    if title is not None:
        plan.title = title
    if plan_date is not None:
        plan.plan_date = plan_date
    db.commit()
    db.refresh(plan)
    return plan


def create_plan_item(
    db: Session,
    *,
    plan_id: str,
    item_type: str,
    event_id: Optional[str],
    brotherhood_id: Optional[str],
    desired_time_start: datetime,
    desired_time_end: datetime,
    lat: Optional[float],
    lng: Optional[float],
    notes: Optional[str],
) -> PlanItem:
    max_pos = db.query(PlanItem).filter(PlanItem.plan_id == plan_id).count()
    item = PlanItem(
        id=str(uuid.uuid4()),
        plan_id=plan_id,
        item_type=item_type,
        event_id=event_id,
        brotherhood_id=brotherhood_id,
        desired_time_start=desired_time_start,
        desired_time_end=desired_time_end,
        lat=lat,
        lng=lng,
        notes=notes,
        position=max_pos,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_plan_item(db: Session, *, plan_id: str, item_id: str) -> Optional[PlanItem]:
    return db.query(PlanItem).filter(PlanItem.id == item_id, PlanItem.plan_id == plan_id).first()


def update_plan_item(
    db: Session,
    *,
    item: PlanItem,
    desired_time_start: Optional[datetime],
    desired_time_end: Optional[datetime],
    lat: Optional[float],
    lng: Optional[float],
    notes: Optional[str],
) -> PlanItem:
    if desired_time_start is not None:
        item.desired_time_start = desired_time_start
    if desired_time_end is not None:
        item.desired_time_end = desired_time_end
    if lat is not None:
        item.lat = lat
    if lng is not None:
        item.lng = lng
    if notes is not None:
        item.notes = notes
    db.commit()
    db.refresh(item)
    return item


def delete_plan_item(db: Session, *, item: PlanItem) -> None:
    plan_id = item.plan_id
    db.delete(item)
    db.commit()
    remaining = db.query(PlanItem).filter(PlanItem.plan_id == plan_id).order_by(PlanItem.position.asc()).all()
    for idx, rem in enumerate(remaining):
        rem.position = idx
    db.commit()


def reorder_plan_items(db: Session, *, plan_id: str, ordered_ids: List[str]) -> List[PlanItem]:
    for idx, item_id in enumerate(ordered_ids):
        db.query(PlanItem).filter(PlanItem.plan_id == plan_id, PlanItem.id == item_id).update({"position": idx})
    db.commit()
    return db.query(PlanItem).filter(PlanItem.plan_id == plan_id).order_by(PlanItem.position.asc()).all()
