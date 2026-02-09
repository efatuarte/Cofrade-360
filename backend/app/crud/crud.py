from sqlalchemy.orm import Session
from app.models.models import Hermandad, Evento
from app.schemas.schemas import HermandadCreate, EventoCreate
from typing import List, Optional
import uuid


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


def get_evento(db: Session, evento_id: str) -> Optional[Evento]:
    return db.query(Evento).filter(Evento.id == evento_id).first()


def get_eventos(db: Session, skip: int = 0, limit: int = 100) -> List[Evento]:
    return db.query(Evento).offset(skip).limit(limit).all()


def create_evento(db: Session, evento: EventoCreate) -> Evento:
    db_evento = Evento(
        id=str(uuid.uuid4()),
        **evento.model_dump()
    )
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento
