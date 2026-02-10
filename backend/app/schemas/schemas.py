from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


# ============= Enums =============

class TipoEvento(str, Enum):
    procesion = "procesion"
    culto = "culto"
    concierto = "concierto"
    exposicion = "exposicion"
    ensayo = "ensayo"
    otro = "otro"


class EstadoEvento(str, Enum):
    programado = "programado"
    en_curso = "en_curso"
    finalizado = "finalizado"
    cancelado = "cancelado"


class LocationKind(str, Enum):
    church = "church"
    plaza = "plaza"
    theater = "theater"
    street = "street"
    other = "other"


# ============= Pagination =============

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page: int
    page_size: int
    total: int


# ============= User & Auth Schemas =============

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ============= Location Schemas =============

class LocationBase(BaseModel):
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    kind: LocationKind = LocationKind.other


class LocationCreate(LocationBase):
    pass


class LocationResponse(LocationBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============= Hermandad Schemas =============

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

    model_config = ConfigDict(from_attributes=True)


# ============= Evento Schemas =============

class EventoBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    tipo: TipoEvento = TipoEvento.otro
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    location_id: Optional[str] = None
    hermandad_id: Optional[str] = None
    precio: float = 0
    moneda: str = "EUR"
    es_gratuito: bool = True
    poster_asset_id: Optional[str] = None
    estado: EstadoEvento = EstadoEvento.programado


class EventoCreate(EventoBase):
    @model_validator(mode="after")
    def validate_dates_and_price(self):
        if self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValueError("fecha_inicio must be before fecha_fin")

        # Coherencia precio vs es_gratuito
        if self.es_gratuito and self.precio > 0:
            raise ValueError("Free events cannot have a price > 0")

        if (not self.es_gratuito) and self.precio <= 0:
            raise ValueError("Non-free events must have a price > 0")

        return self


class EventoUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[TipoEvento] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    location_id: Optional[str] = None
    hermandad_id: Optional[str] = None
    precio: Optional[float] = None
    moneda: Optional[str] = None
    es_gratuito: Optional[bool] = None
    poster_asset_id: Optional[str] = None
    estado: Optional[EstadoEvento] = None


class EventoResponse(EventoBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    location: Optional[LocationResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ============= Ruta Schemas =============

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

    model_config = ConfigDict(from_attributes=True)


# ============= Routing Schemas =============

class RouteRequest(BaseModel):
    origen: List[float] = Field(..., min_length=2, max_length=2)   # [lat, lon]
    destino: List[float] = Field(..., min_length=2, max_length=2)  # [lat, lon]
    evitar_procesiones: bool = True


class RouteResponse(BaseModel):
    ruta: List[List[float]]
    distancia_metros: int
    duracion_minutos: int
    instrucciones: List[str]


# ============= Error Schemas =============

class ErrorDetail(BaseModel):
    detail: str
    code: Optional[str] = None
    trace_id: Optional[str] = None
