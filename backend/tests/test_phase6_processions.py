from datetime import datetime

from tests.conftest import (
    auth_header,
    make_admin_user,
    make_hermandad,
    make_location,
    make_procession,
    make_street_segment,
    make_user,
)


def test_list_processions_by_date(client, db):
    church = make_location(db)
    h = make_hermandad(db, church_id=church.id)
    make_procession(db, brotherhood_id=h.id, date=datetime(2026, 4, 10, 18, 0))
    make_procession(db, brotherhood_id=h.id, date=datetime(2026, 4, 11, 18, 0))

    response = client.get("/api/v1/processions?date=2026-04-10T08:00:00")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_restrictions_admin_rbac(client, db):
    user = make_user(db)
    admin = make_admin_user(db)

    payload = {
        "name": "Corte test",
        "geom": "POLYGON((-5.99 37.39,-5.98 37.39,-5.98 37.38,-5.99 37.38,-5.99 37.39))",
        "start_datetime": "2026-04-10T17:00:00",
        "end_datetime": "2026-04-10T20:00:00",
        "reason": "corte",
    }

    forbidden = client.post("/api/v1/restrictions", json=payload, headers=auth_header(user.id))
    assert forbidden.status_code == 403

    allowed = client.post("/api/v1/restrictions", json=payload, headers=auth_header(admin.id))
    assert allowed.status_code == 201


def test_occupation_overlap_validation(client, db):
    admin = make_admin_user(db)
    church = make_location(db)
    h = make_hermandad(db, church_id=church.id)
    seg = make_street_segment(db)
    proc = make_procession(db, brotherhood_id=h.id)

    payload = {
        "procession_id": proc.id,
        "street_segment_id": seg.id,
        "start_datetime": "2026-04-10T18:00:00",
        "end_datetime": "2026-04-10T18:20:00",
        "direction": "parallel",
        "crowd_factor": 1.4,
    }
    first = client.post("/api/v1/processions/occupations", json=payload, headers=auth_header(admin.id))
    assert first.status_code == 201

    second = client.post(
        "/api/v1/processions/occupations",
        json={
            **payload,
            "start_datetime": "2026-04-10T18:10:00",
            "end_datetime": "2026-04-10T18:30:00",
        },
        headers=auth_header(admin.id),
    )
    assert second.status_code == 409


def test_list_restrictions_window_validation(client):
    bad = client.get("/api/v1/restrictions?from=2026-04-10T19:00:00&to=2026-04-10T18:00:00")
    assert bad.status_code == 422


def test_upsert_and_list_procession_schedule_and_itinerary(client, db):
    admin = make_admin_user(db)
    church = make_location(db)
    h = make_hermandad(db, church_id=church.id)
    proc = make_procession(db, brotherhood_id=h.id, date=datetime(2026, 4, 10, 18, 0))

    schedule_payload = [
        {
            "point_type": "salida",
            "label": "Cruz de Guía",
            "scheduled_datetime": "2026-04-10T18:00:00",
        },
        {
            "point_type": "recogida",
            "label": "Entrada",
            "scheduled_datetime": "2026-04-11T00:30:00",
        },
    ]
    put_schedule = client.put(
        f"/api/v1/processions/{proc.id}/schedule",
        json=schedule_payload,
        headers=auth_header(admin.id),
    )
    assert put_schedule.status_code == 200
    assert len(put_schedule.json()) == 2

    get_schedule = client.get(f"/api/v1/processions/{proc.id}/schedule")
    assert get_schedule.status_code == 200
    assert get_schedule.json()[0]["point_type"] == "salida"

    itinerary_payload = {
        "raw_text": "Templo, Calle A, Carrera Oficial, Calle B, Templo",
        "source_url": "https://example.org/hdad",
        "accessed_at": "2026-02-16T10:00:00",
    }
    put_itinerary = client.put(
        f"/api/v1/processions/{proc.id}/itinerary",
        json=itinerary_payload,
        headers=auth_header(admin.id),
    )
    assert put_itinerary.status_code == 200
    assert "Carrera Oficial" in put_itinerary.json()["raw_text"]

    get_itinerary = client.get(f"/api/v1/processions/{proc.id}/itinerary")
    assert get_itinerary.status_code == 200
    assert get_itinerary.json()["source_url"] == "https://example.org/hdad"


def test_provenance_create_and_list(client, db):
    admin = make_admin_user(db)

    create = client.post(
        "/api/v1/provenance",
        headers=auth_header(admin.id),
        json={
            "entity_type": "brotherhood",
            "entity_id": "entity-1",
            "source_url": "https://example.com/source",
            "accessed_at": "2026-02-16T11:00:00",
            "fields_extracted": ["name_short", "ss_day"],
        },
    )
    assert create.status_code == 201

    listed = client.get("/api/v1/provenance?entity_type=brotherhood&entity_id=entity-1")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["source_url"] == "https://example.com/source"
