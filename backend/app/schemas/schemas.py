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


class SemanaSantaDay(str, Enum):
    domingo_ramos = "domingo_ramos"
    lunes_santo = "lunes_santo"
    martes_santo = "martes_santo"
    miercoles_santo = "miercoles_santo"
    jueves_santo = "jueves_santo"
    madrugada = "madrugada"
    viernes_santo = "viernes_santo"
    sabado_santo = "sabado_santo"
    domingo_resurreccion = "domingo_resurreccion"


class MediaKind(str, Enum):
    image = "image"
    video = "video"


class PlanItemType(str, Enum):
    event = "event"
    brotherhood = "brotherhood"


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
    role: str = "user"
    is_active: bool
    notifications_processions: bool = True
    notifications_restrictions: bool = True
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


class NotificationSettingsUpdate(BaseModel):
    notifications_processions: Optional[bool] = None
    notifications_restrictions: Optional[bool] = None

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.notifications_processions is None and self.notifications_restrictions is None:
            raise ValueError("At least one notification field must be provided")
        return self


class NotificationSettingsResponse(BaseModel):
    notifications_processions: bool
    notifications_restrictions: bool


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


# ============= Hermandad & Media Schemas =============

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


class BrotherhoodResponse(BaseModel):
    id: str
    name_short: str
    name_full: str
    logo_asset_id: Optional[str] = None
    church_id: Optional[str] = None
    ss_day: Optional[SemanaSantaDay] = None
    history: Optional[str] = None
    highlights: Optional[str] = None
    stats: Optional[str] = None
    created_at: datetime
    church: Optional[LocationResponse] = None

    model_config = ConfigDict(from_attributes=True)


class MediaAssetResponse(BaseModel):
    id: str
    kind: MediaKind
    mime: str
    path: str
    brotherhood_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SignedMediaResponse(BaseModel):
    asset_id: str
    url: str


class MediaUploadRequest(BaseModel):
    kind: MediaKind
    mime: str
    extension: str = Field(default="jpg", min_length=2, max_length=10)
    brotherhood_id: Optional[str] = None


class MediaUploadSignedUrlResponse(BaseModel):
    asset_id: str
    path: str
    put_url: str


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


# ============= Itinerario Schemas =============

class PlanConflictWarning(BaseModel):
    item_id: str
    conflict_with_item_id: str
    detail: str


class PlanItemBase(BaseModel):
    item_type: PlanItemType
    event_id: Optional[str] = None
    brotherhood_id: Optional[str] = None
    desired_time_start: datetime
    desired_time_end: datetime
    lat: Optional[float] = None
    lng: Optional[float] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_window_and_target(self):
        if self.desired_time_start > self.desired_time_end:
            raise ValueError("desired_time_start must be <= desired_time_end")
        if self.item_type == PlanItemType.event and not self.event_id:
            raise ValueError("event_id is required for event item")
        if self.item_type == PlanItemType.brotherhood and not self.brotherhood_id:
            raise ValueError("brotherhood_id is required for brotherhood item")
        return self


class PlanItemCreate(PlanItemBase):
    pass


class PlanItemUpdate(BaseModel):
    desired_time_start: Optional[datetime] = None
    desired_time_end: Optional[datetime] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    notes: Optional[str] = None


class PlanItemResponse(PlanItemBase):
    id: str
    plan_id: str
    position: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPlanCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    plan_date: datetime


class UserPlanUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=120)
    plan_date: Optional[datetime] = None


class UserPlanResponse(BaseModel):
    id: str
    user_id: str
    title: str
    plan_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[PlanItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class AddPlanItemResponse(BaseModel):
    item: PlanItemResponse
    warnings: List[PlanConflictWarning] = []


class OptimizePlanResponse(BaseModel):
    items: List[PlanItemResponse]
    warnings: List[PlanConflictWarning] = []



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

class RoutingTarget(BaseModel):
    type: str = Field(..., pattern='^(event|brotherhood)$')
    id: str


class RoutingConstraints(BaseModel):
    avoid_bulla: bool = True
    max_walk_km: float = Field(10.0, gt=0)


class RouteRequest(BaseModel):
    origin: List[float] = Field(..., min_length=2, max_length=2)  # [lat, lng]
    datetime: datetime
    target: RoutingTarget
    constraints: RoutingConstraints = RoutingConstraints()


class RouteResponse(BaseModel):
    polyline: List[List[float]]
    eta_seconds: int
    bulla_score: float
    warnings: List[str]
    explanation: List[str]


class ModeCalleWsLocation(BaseModel):
    lat: float
    lng: float


class ModeCalleWsRequest(BaseModel):
    location: ModeCalleWsLocation
    datetime: datetime
    target: RoutingTarget
    constraints: RoutingConstraints = RoutingConstraints()


class ModeCalleWsResponse(BaseModel):
    type: str = "reroute"
    route: RouteResponse


# ============= Error Schemas =============

class ErrorDetail(BaseModel):
    detail: str
    code: Optional[str] = None
    trace_id: Optional[str] = None
