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

    # Legacy fields
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    escudo = Column(String)
    sede = Column(String)
    fecha_fundacion = Column(DateTime)

    # Phase 3 fields
    name_short = Column(String, nullable=True)
    name_full = Column(String, nullable=True)
    logo_asset_id = Column(String, ForeignKey("media_assets.id"), nullable=True)
    church_id = Column(String, ForeignKey("locations.id"), nullable=True)
    ss_day = Column(String, nullable=True)  # domingo_ramos ... domingo_resurreccion
    history = Column(Text, nullable=True)
    highlights = Column(Text, nullable=True)  # JSON serialized string
    stats = Column(Text, nullable=True)  # JSON serialized string

    web_url = Column(String, nullable=True)

    ubicacion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eventos = relationship("Evento", back_populates="hermandad")
    church = relationship("Location")
    media_assets = relationship("MediaAsset", back_populates="brotherhood", foreign_keys="MediaAsset.brotherhood_id")
    titulares = relationship("Titular", back_populates="brotherhood", cascade="all, delete-orphan")


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(String, primary_key=True, index=True)
    kind = Column(String, nullable=False)  # image/video
    mime = Column(String, nullable=False)
    path = Column(String, nullable=False)
    brotherhood_id = Column(String, ForeignKey("hermandades.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    brotherhood = relationship("Hermandad", back_populates="media_assets", foreign_keys=[brotherhood_id])


class Titular(Base):
    __tablename__ = "titulares"

    id = Column(String, primary_key=True, index=True)
    brotherhood_id = Column(String, ForeignKey("hermandades.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    kind = Column(String, nullable=False, default="unknown")  # cristo | virgen | misterio | unknown
    position = Column(Integer, nullable=False, default=0)  # display order
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    brotherhood = relationship("Hermandad", back_populates="titulares")


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
    item_type = Column(String, nullable=False)  # event | brotherhood
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


class Procession(Base):
    __tablename__ = "processions"

    id = Column(String, primary_key=True, index=True)
    brotherhood_id = Column(String, ForeignKey("hermandades.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    status = Column(String, nullable=False, default="scheduled")
    confidence = Column(Float, nullable=False, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    brotherhood = relationship("Hermandad")
    schedule_points = relationship("ProcessionSchedulePoint", cascade="all, delete-orphan")
    itinerary = relationship("ProcessionItineraryText", uselist=False, cascade="all, delete-orphan")


class ProcessionSchedulePoint(Base):
    __tablename__ = "procession_schedule_points"

    id = Column(String, primary_key=True, index=True)
    procession_id = Column(String, ForeignKey("processions.id"), nullable=False, index=True)
    point_type = Column(String, nullable=False)
    label = Column(String, nullable=True)
    scheduled_datetime = Column(DateTime, nullable=False)


class ProcessionItineraryText(Base):
    __tablename__ = "procession_itinerary_texts"

    id = Column(String, primary_key=True, index=True)
    procession_id = Column(String, ForeignKey("processions.id"), nullable=False, unique=True, index=True)
    raw_text = Column(Text, nullable=False)
    source_url = Column(String, nullable=True)
    accessed_at = Column(DateTime, nullable=True)


class DataProvenance(Base):
    __tablename__ = "data_provenance"

    id = Column(String, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False, index=True)
    source_url = Column(String, nullable=False)
    accessed_at = Column(DateTime, nullable=False)
    fields_extracted = Column(Text, nullable=False, default="[]")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)
    changed_fields = Column(Text, nullable=False, default="{}")
    actor_user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)



class StreetNode(Base):
    __tablename__ = "street_nodes"

    id = Column(String, primary_key=True, index=True)
    geom = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class StreetEdge(Base):
    __tablename__ = "street_edges"

    id = Column(String, primary_key=True, index=True)
    source_node = Column(String, ForeignKey("street_nodes.id"), nullable=False, index=True)
    target_node = Column(String, ForeignKey("street_nodes.id"), nullable=False, index=True)
    geom = Column(Text, nullable=False)
    length_m = Column(Float, nullable=False)
    width_estimate = Column(Float, nullable=True)
    highway_type = Column(String, nullable=True)
    is_walkable = Column(Boolean, nullable=False, default=True)
    tags = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RouteRestriction(Base):
    __tablename__ = "route_restrictions"

    id = Column(String, primary_key=True, index=True)
    edge_id = Column(String, ForeignKey("street_edges.id"), nullable=False, index=True)
    starts_at = Column(DateTime, nullable=False, index=True)
    ends_at = Column(DateTime, nullable=False, index=True)
    reason = Column(String, nullable=False)
    severity = Column(Float, nullable=False, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)



class NotificationEvent(Base):
    __tablename__ = "notification_events"

    id = Column(String, primary_key=True, index=True)
    plan_id = Column(String, nullable=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    kind = Column(String, nullable=False, index=True)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)



class CrowdReport(Base):
    __tablename__ = "crowd_reports"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    geohash = Column(String, nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    severity = Column(Integer, nullable=False, default=3)
    note = Column(Text, nullable=True)
    is_flagged = Column(Boolean, nullable=False, default=False)
    is_hidden = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class CrowdSignal(Base):
    __tablename__ = "crowd_signals"

    id = Column(String, primary_key=True, index=True)
    geohash = Column(String, nullable=False, index=True)
    bucket_start = Column(DateTime, nullable=False, index=True)
    bucket_end = Column(DateTime, nullable=False, index=True)
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    reports_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(String, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    trace_id = Column(String, nullable=True, index=True)
    payload = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
