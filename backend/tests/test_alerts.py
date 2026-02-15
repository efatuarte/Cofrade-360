from datetime import datetime
import uuid

import pytest

from tests.conftest import make_evento, make_hermandad, make_location

try:
    from app.models.models import Procession, RestrictedArea
except ImportError:
    pytest.skip("Operational alert models are not available in this build", allow_module_level=True)


def test_alerts_next_includes_upcoming_items(client, db):
    loc = make_location(db)
    event = make_evento(
        db,
        location_id=loc.id,
        titulo="Traslado",
        fecha_inicio=datetime(2026, 4, 10, 18, 15),
        fecha_fin=datetime(2026, 4, 10, 19, 0),
    )
    brotherhood = make_hermandad(db, church_id=loc.id)

    process = Procession(
        id=str(uuid.uuid4()),
        brotherhood_id=brotherhood.id,
        date=datetime(2026, 4, 10, 18, 30),
        status="scheduled",
    )
    db.add(process)

    restriction = RestrictedArea(
        id=str(uuid.uuid4()),
        name="Corte puntual",
        geom="POLYGON((-5.99 37.39,-5.98 37.39,-5.98 37.38,-5.99 37.38,-5.99 37.39))",
        start_datetime=datetime(2026, 4, 10, 18, 10),
        end_datetime=datetime(2026, 4, 10, 18, 50),
        reason="corte",
    )
    db.add(restriction)
    db.commit()

    response = client.get(
        "/api/v1/alerts/next",
        params={"at": datetime(2026, 4, 10, 18, 0).isoformat(), "minutes_ahead": 120},
    )

    assert response.status_code == 200
    payload = response.json()
    kinds = [item["kind"] for item in payload["items"]]
    assert "event_start" in kinds
    assert "procession_start" in kinds
    assert "restriction_start" in kinds
    assert "restriction_end" in kinds

    starts = [item["starts_at"] for item in payload["items"]]
    assert starts == sorted(starts)

    event_titles = [item["title"] for item in payload["items"] if item["kind"] == "event_start"]
    assert any(event.titulo in title for title in event_titles)


def test_alerts_next_can_skip_restrictions(client, db):
    loc = make_location(db)
    make_evento(
        db,
        location_id=loc.id,
        titulo="Concierto banda",
        fecha_inicio=datetime(2026, 4, 10, 18, 40),
    )
    restriction = RestrictedArea(
        id=str(uuid.uuid4()),
        name="Valla",
        geom="POLYGON((-5.99 37.39,-5.98 37.39,-5.98 37.38,-5.99 37.38,-5.99 37.39))",
        start_datetime=datetime(2026, 4, 10, 18, 35),
        end_datetime=datetime(2026, 4, 10, 19, 10),
        reason="valla",
    )
    db.add(restriction)
    db.commit()

    response = client.get(
        "/api/v1/alerts/next",
        params={
            "at": datetime(2026, 4, 10, 18, 0).isoformat(),
            "minutes_ahead": 120,
            "include_restrictions": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert all(item["kind"] != "restriction_start" for item in payload["items"])
    assert all(item["kind"] != "restriction_end" for item in payload["items"])
