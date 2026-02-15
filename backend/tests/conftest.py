"""
Shared test fixtures.
Uses a single SQLite database and creates only non-PostGIS tables.
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.deps import get_db
from app.core.security import get_password_hash, create_access_token
from app.models.models import User, Location, Hermandad, MediaAsset, Evento, UserPlan, PlanItem

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture(autouse=True)
def setup_tables():
    """Create tables needed for tests (no PostGIS dependency)."""
    User.__table__.create(bind=engine, checkfirst=True)
    Location.__table__.create(bind=engine, checkfirst=True)
    Hermandad.__table__.create(bind=engine, checkfirst=True)
    MediaAsset.__table__.create(bind=engine, checkfirst=True)
    Evento.__table__.create(bind=engine, checkfirst=True)
    UserPlan.__table__.create(bind=engine, checkfirst=True)
    PlanItem.__table__.create(bind=engine, checkfirst=True)
    yield
    PlanItem.__table__.drop(bind=engine, checkfirst=True)
    UserPlan.__table__.drop(bind=engine, checkfirst=True)
    Evento.__table__.drop(bind=engine, checkfirst=True)
    MediaAsset.__table__.drop(bind=engine, checkfirst=True)
    Hermandad.__table__.drop(bind=engine, checkfirst=True)
    Location.__table__.drop(bind=engine, checkfirst=True)
    User.__table__.drop(bind=engine, checkfirst=True)


# -------- shared helpers --------

def make_user(db) -> User:
    uid = str(uuid.uuid4())
    u = User(
        id=uid,
        email=f"u-{uid[:8]}@test.com",
        hashed_password=get_password_hash("test1234"),
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def auth_header(user_id: str) -> dict:
    token = create_access_token(data={"sub": user_id})
    return {"Authorization": f"Bearer {token}"}


def make_location(db, name: str = "Plaza Test") -> Location:
    loc = Location(
        id=str(uuid.uuid4()),
        name=name,
        address="Addr",
        lat=37.39,
        lng=-5.99,
        kind="plaza",
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


def make_evento(db, location_id: str, **kw) -> Evento:
    from datetime import datetime
    defaults = dict(
        id=str(uuid.uuid4()),
        titulo="Evento Test",
        tipo="otro",
        fecha_inicio=datetime(2026, 4, 5, 18, 0),
        fecha_fin=datetime(2026, 4, 5, 20, 0),
        location_id=location_id,
        es_gratuito=True,
        precio=0,
        estado="programado",
    )
    defaults.update(kw)
    ev = Evento(**defaults)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


def make_hermandad(db, church_id: str, **kw) -> Hermandad:
    defaults = dict(
        id=str(uuid.uuid4()),
        nombre="Hermandad Test",
        descripcion="Desc",
        name_short="Test",
        name_full="Hermandad Test Full",
        church_id=church_id,
        ss_day="viernes_santo",
        history="Historia",
        highlights='["h1"]',
        stats='{"nazarenos": 100}',
    )
    defaults.update(kw)
    h = Hermandad(**defaults)
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


def make_media_asset(db, brotherhood_id: str, **kw) -> MediaAsset:
    defaults = dict(
        id=str(uuid.uuid4()),
        kind="image",
        mime="image/jpeg",
        path=f"brotherhoods/{uuid.uuid4()}.jpg",
        brotherhood_id=brotherhood_id,
    )
    defaults.update(kw)
    asset = MediaAsset(**defaults)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset
