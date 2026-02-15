"""
Tests for Eventos (Events) endpoints.
Uses shared conftest.py fixtures (SQLite, no PostGIS).
"""
from tests.conftest import make_user, auth_header, make_location, make_evento


def test_list_events_empty(client):
    r = client.get("/api/v1/events")
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_events_paginated(client, db):
    loc = make_location(db)
    for i in range(5):
        make_evento(db, loc.id, titulo=f"Ev {i}")

    r = client.get("/api/v1/events?page=1&page_size=2")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_get_event_by_id(client, db):
    loc = make_location(db)
    ev = make_evento(db, loc.id, titulo="Detalle")

    r = client.get(f"/api/v1/events/{ev.id}")
    assert r.status_code == 200
    assert r.json()["titulo"] == "Detalle"
    assert r.json()["location"]["name"] == "Plaza Test"


def test_get_event_not_found(client):
    r = client.get("/api/v1/events/nonexistent")
    assert r.status_code == 404


def test_create_event_auth_required(client):
    r = client.post(
        "/api/v1/events",
        json={"titulo": "New", "fecha_inicio": "2026-04-05T18:00:00"},
    )
    assert r.status_code == 403


def test_create_event_success(client, db):
    user = make_user(db)
    loc = make_location(db)
    user_id, loc_id = user.id, loc.id

    r = client.post(
        "/api/v1/events",
        json={
            "titulo": "Nuevo Evento",
            "tipo": "procesion",
            "fecha_inicio": "2026-04-05T18:00:00",
            "fecha_fin": "2026-04-05T22:00:00",
            "location_id": loc_id,
            "es_gratuito": True,
            "precio": 0,
        },
        headers=auth_header(user_id),
    )
    assert r.status_code == 201
    assert r.json()["titulo"] == "Nuevo Evento"
    assert r.json()["tipo"] == "procesion"


def test_create_event_validation_dates(client, db):
    """End before start should fail validation."""
    user = make_user(db)
    user_id = user.id

    r = client.post(
        "/api/v1/events",
        json={
            "titulo": "Bad dates",
            "fecha_inicio": "2026-04-10T18:00:00",
            "fecha_fin": "2026-04-05T18:00:00",
            "es_gratuito": True,
            "precio": 0,
        },
        headers=auth_header(user_id),
    )
    assert r.status_code == 422


def test_create_event_validation_price(client, db):
    """Free event with price > 0 should fail."""
    user = make_user(db)
    user_id = user.id

    r = client.post(
        "/api/v1/events",
        json={
            "titulo": "Bad price",
            "fecha_inicio": "2026-04-10T18:00:00",
            "es_gratuito": True,
            "precio": 25.0,
        },
        headers=auth_header(user_id),
    )
    assert r.status_code == 422


def test_update_event(client, db):
    user = make_user(db)
    loc = make_location(db)
    ev = make_evento(db, loc.id, titulo="Original")
    user_id, ev_id = user.id, ev.id

    r = client.patch(
        f"/api/v1/events/{ev_id}",
        json={"titulo": "Updated"},
        headers=auth_header(user_id),
    )
    assert r.status_code == 200
    assert r.json()["titulo"] == "Updated"


def test_filter_by_tipo(client, db):
    loc = make_location(db)
    make_evento(db, loc.id, titulo="Procesion 1", tipo="procesion")
    make_evento(db, loc.id, titulo="Concierto 1", tipo="concierto")

    r = client.get("/api/v1/events?tipo=procesion")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["titulo"] == "Procesion 1"


def test_filter_by_search_query(client, db):
    loc = make_location(db)
    make_evento(db, loc.id, titulo="Procesion Gran Poder")
    make_evento(db, loc.id, titulo="Concierto Marchas")

    r = client.get("/api/v1/events?q=Gran Poder")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert "Gran Poder" in data["items"][0]["titulo"]


def test_filter_by_type_alias(client, db):
    loc = make_location(db)
    make_evento(db, loc.id, titulo="Procesion alias", tipo="procesion")
    make_evento(db, loc.id, titulo="Concierto alias", tipo="concierto")

    r = client.get("/api/v1/events?type=procesion")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["tipo"] == "procesion"


def test_filter_by_price_and_has_poster(client, db):
    loc = make_location(db)
    make_evento(db, loc.id, titulo="Free no poster", precio=0, es_gratuito=True)
    make_evento(
        db,
        loc.id,
        titulo="Paid poster",
        precio=20,
        es_gratuito=False,
        poster_asset_id="events/paid.jpg",
    )

    r = client.get("/api/v1/events?min_price=10&max_price=30&has_poster=true")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["titulo"] == "Paid poster"


def test_list_events_invalid_ranges(client):
    r = client.get(
        "/api/v1/events?from=2026-04-10T10:00:00&to=2026-04-01T10:00:00"
    )
    assert r.status_code == 422

    r2 = client.get("/api/v1/events?min_price=20&max_price=5")
    assert r2.status_code == 422


def test_get_event_poster_signed_url(client, db, monkeypatch):
    loc = make_location(db)
    ev = make_evento(db, loc.id, poster_asset_id="events/my-poster.jpg")

    def fake_signed(asset_id: str, bucket_name=None):
        assert asset_id == "events/my-poster.jpg"
        return "https://minio.local/signed/events/my-poster.jpg"

    monkeypatch.setattr(
        "app.api.endpoints.eventos.get_presigned_get_url",
        fake_signed,
    )

    r = client.get(f"/api/v1/events/{ev.id}/poster")
    assert r.status_code == 200
    assert r.json()["asset_id"] == "events/my-poster.jpg"
    assert "signed" in r.json()["url"]


def test_get_event_poster_without_asset_returns_404(client, db):
    loc = make_location(db)
    ev = make_evento(db, loc.id, poster_asset_id=None)

    r = client.get(f"/api/v1/events/{ev.id}/poster")
    assert r.status_code == 404
