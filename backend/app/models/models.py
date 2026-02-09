from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.session import Base
from datetime import datetime


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
    fecha_hora = Column(DateTime, nullable=False)
    hermandad_id = Column(String, nullable=False)
    ubicacion = Column(String)
    ubicacion_geo = Column(Geometry('POINT', srid=4326))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hermandad = relationship("Hermandad", back_populates="eventos")


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
    tipo = Column(String)  # intersection, landmark, etc.
    created_at = Column(DateTime, default=datetime.utcnow)


class Arista(Base):
    __tablename__ = "aristas"

    id = Column(String, primary_key=True, index=True)
    nodo_origen = Column(String, nullable=False)
    nodo_destino = Column(String, nullable=False)
    geometria = Column(Geometry('LINESTRING', srid=4326))
    distancia_metros = Column(Integer)
    costo = Column(Integer)  # For A* algorithm
    bloqueada = Column(Integer, default=0)  # 0 = open, 1 = blocked
    created_at = Column(DateTime, default=datetime.utcnow)
