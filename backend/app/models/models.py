from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.session import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Location(Base):
    __tablename__ = "locations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    kind = Column(String, default="other")  # church, plaza, theater, street, other
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
    ubicacion = Column(Geometry('POINT', srid=4326))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eventos = relationship("Evento", back_populates="hermandad")


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


class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    puntos = Column(Geometry('LINESTRING', srid=4326))
    distancia_metros = Column(Integer)
    duracion_minutos = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Nodo(Base):
    __tablename__ = "nodos"

    id = Column(String, primary_key=True, index=True)
    ubicacion = Column(Geometry('POINT', srid=4326), nullable=False)
    tipo = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Arista(Base):
    __tablename__ = "aristas"

    id = Column(String, primary_key=True, index=True)
    nodo_origen = Column(String, nullable=False)
    nodo_destino = Column(String, nullable=False)
    geometria = Column(Geometry('LINESTRING', srid=4326))
    distancia_metros = Column(Integer)
    costo = Column(Integer)
    bloqueada = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
