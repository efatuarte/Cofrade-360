from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")  # user | editor | admin
    is_active = Column(Boolean, default=True, nullable=False)
    notifications_processions = Column(Boolean, default=True, nullable=False)
    notifications_restrictions = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Location(Base):
    __tablename__ = "locations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    kind = Column(String, default="other")
    created_at = Column(DateTime, default=datetime.utcnow)

    eventos = relationship("Evento", back_populates="location")


class Hermandad(Base):
    __tablename__ = "hermandades"

    id = Column(String, primary_key=True, index=True)

    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    escudo = Column(String)
    sede = Column(String)
    fecha_fundacion = Column(DateTime)

    name_short = Column(String, nullable=True)
    name_full = Column(String, nullable=True)
    logo_asset_id = Column(String, ForeignKey("media_assets.id"), nullable=True)
    church_id = Column(String, ForeignKey("locations.id"), nullable=True)
    ss_day = Column(String, nullable=True)
    history = Column(Text, nullable=True)
    highlights = Column(Text, nullable=True)
    stats = Column(Text, nullable=True)

    ubicacion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eventos = relationship("Evento", back_populates="hermandad")
    church = relationship("Location")
    media_assets = relationship("MediaAsset", back_populates="brotherhood", foreign_keys="MediaAsset.brotherhood_id")


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(String, primary_key=True, index=True)
    kind = Column(String, nullable=False)
    mime = Column(String, nullable=False)
    path = Column(String, nullable=False)
    brotherhood_id = Column(String, ForeignKey("hermandades.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    brotherhood = relationship("Hermandad", back_populates="media_assets", foreign_keys=[brotherhood_id])


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(String, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text)
    tipo = Column(String, default="otro")
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime)
    location_id = Column(String, ForeignKey("locations.id"), nullable=True)
    hermandad_id = Column(String, ForeignKey("hermandades.id"), nullable=True)
    precio = Column(Float, default=0)
    moneda = Column(String, default="EUR")
    es_gratuito = Column(Boolean, default=True)
    poster_asset_id = Column(String, nullable=True)
    estado = Column(String, default="programado")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hermandad = relationship("Hermandad", back_populates="eventos")
    location = relationship("Location", back_populates="eventos")


class UserPlan(Base):
    __tablename__ = "user_plans"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    plan_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("PlanItem", back_populates="plan", cascade="all, delete-orphan")


class PlanItem(Base):
    __tablename__ = "plan_items"

    id = Column(String, primary_key=True, index=True)
    plan_id = Column(String, ForeignKey("user_plans.id"), nullable=False, index=True)
    item_type = Column(String, nullable=False)
    event_id = Column(String, ForeignKey("eventos.id"), nullable=True)
    brotherhood_id = Column(String, ForeignKey("hermandades.id"), nullable=True)
    desired_time_start = Column(DateTime, nullable=False)
    desired_time_end = Column(DateTime, nullable=False)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    plan = relationship("UserPlan", back_populates="items")


# ===== FASE 6 =====

class StreetSegment(Base):
    __tablename__ = "street_segments"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    geom = Column(Text, nullable=False)  # WKT LINESTRING (SRID 4326)
    width_estimate = Column(Float, nullable=True)
    kind = Column(String, nullable=False, default="street")
    is_walkable = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RestrictedArea(Base):
    __tablename__ = "restricted_areas"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    geom = Column(Text, nullable=False)  # WKT POLYGON/MULTIPOLYGON
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    reason = Column(String, nullable=False)  # carrera_oficial | corte | valla | otro
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Procession(Base):
    __tablename__ = "processions"

    id = Column(String, primary_key=True, index=True)
    brotherhood_id = Column(String, ForeignKey("hermandades.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    status = Column(String, nullable=False, default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    occupations = relationship("ProcessionSegmentOccupation", back_populates="procession", cascade="all, delete-orphan")
    schedule_points = relationship("ProcessionSchedulePoint", back_populates="procession", cascade="all, delete-orphan")
    itinerary_text = relationship("ProcessionItineraryText", back_populates="procession", uselist=False, cascade="all, delete-orphan")


class ProcessionSegmentOccupation(Base):
    __tablename__ = "procession_segment_occupations"

    id = Column(String, primary_key=True, index=True)
    procession_id = Column(String, ForeignKey("processions.id"), nullable=False, index=True)
    street_segment_id = Column(String, ForeignKey("street_segments.id"), nullable=False, index=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    direction = Column(String, nullable=False, default="unknown")
    crowd_factor = Column(Float, nullable=False, default=1.0)

    procession = relationship("Procession", back_populates="occupations")




class ProcessionSchedulePoint(Base):
    __tablename__ = "procession_schedule_points"

    id = Column(String, primary_key=True, index=True)
    procession_id = Column(String, ForeignKey("processions.id"), nullable=False, index=True)
    point_type = Column(String, nullable=False)  # salida | carrera_oficial_start | carrera_oficial_end | recogida
    label = Column(String, nullable=True)
    scheduled_datetime = Column(DateTime, nullable=False)

    procession = relationship("Procession", back_populates="schedule_points")


class ProcessionItineraryText(Base):
    __tablename__ = "procession_itinerary_texts"

    id = Column(String, primary_key=True, index=True)
    procession_id = Column(String, ForeignKey("processions.id"), nullable=False, unique=True, index=True)
    raw_text = Column(Text, nullable=False)
    source_url = Column(String, nullable=True)
    accessed_at = Column(DateTime, nullable=True)

    procession = relationship("Procession", back_populates="itinerary_text")


class DataProvenance(Base):
    __tablename__ = "data_provenance"

    id = Column(String, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # brotherhood | procession | location | media
    entity_id = Column(String, nullable=False, index=True)
    source_url = Column(String, nullable=False)
    accessed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    fields_extracted = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    puntos = Column(Geometry("LINESTRING", srid=4326))
    distancia_metros = Column(Integer)
    duracion_minutos = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Nodo(Base):
    __tablename__ = "nodos"

    id = Column(String, primary_key=True, index=True)
    ubicacion = Column(Geometry("POINT", srid=4326), nullable=False)
    tipo = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Arista(Base):
    __tablename__ = "aristas"

    id = Column(String, primary_key=True, index=True)
    nodo_origen = Column(String, nullable=False)
    nodo_destino = Column(String, nullable=False)
    geometria = Column(Geometry("LINESTRING", srid=4326))
    distancia_metros = Column(Integer)
    costo = Column(Integer)
    bloqueada = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
