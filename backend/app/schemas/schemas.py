from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class HermandadBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    escudo: Optional[str] = None
    sede: Optional[str] = None
    fecha_fundacion: Optional[datetime] = None


class HermandadCreate(HermandadBase):
    pass


class Hermandad(HermandadBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventoBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_hora: datetime
    hermandad_id: str
    ubicacion: Optional[str] = None


class EventoCreate(EventoBase):
    pass


class Evento(EventoBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RutaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    distancia_metros: Optional[int] = None
    duracion_minutos: Optional[int] = None


class RutaCreate(RutaBase):
    pass


class Ruta(RutaBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RouteRequest(BaseModel):
    origen: List[float]  # [lat, lon]
    destino: List[float]  # [lat, lon]
    evitar_procesiones: bool = True


class RouteResponse(BaseModel):
    ruta: List[List[float]]  # List of [lat, lon] coordinates
    distancia_metros: int
    duracion_minutos: int
    instrucciones: List[str]
