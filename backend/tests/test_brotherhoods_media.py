from tests.conftest import auth_header, make_hermandad, make_location, make_media_asset, make_user


def test_list_brotherhoods_paginated(client, db):
    church = make_location(db, name="Iglesia Test")
    make_hermandad(db, church_id=church.id, name_short="Macarena", ss_day="madrugada")
    make_hermandad(db, church_id=church.id, name_short="Cachorro", ss_day="viernes_santo")

    response = client.get("/api/v1/brotherhoods?page=1&page_size=1")
    assert response.status_code == 200
    data = response.json()
    assert data["page_size"] == 1
    assert data["total"] == 2
    assert len(data["items"]) == 1


def test_filter_brotherhoods_by_day_and_media(client, db):
    church = make_location(db, name="Basílica Test")
    h1 = make_hermandad(db, church_id=church.id, name_short="Con media", ss_day="madrugada")
    make_hermandad(db, church_id=church.id, name_short="Sin media", ss_day="madrugada")
    make_media_asset(db, brotherhood_id=h1.id)

    response = client.get("/api/v1/brotherhoods?day=madrugada&has_media=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name_short"] == "Con media"


def test_get_brotherhood_media_signed(client, db, monkeypatch):
    church = make_location(db)
    h = make_hermandad(db, church_id=church.id)
    asset = make_media_asset(db, brotherhood_id=h.id, path="brotherhoods/test.jpg")

    monkeypatch.setattr(
        "app.api.endpoints.hermandades.get_presigned_get_url",
        lambda object_name: f"https://signed.local/{object_name}",
    )

    response = client.get(f"/api/v1/brotherhoods/{h.id}/media")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["asset_id"] == asset.id
    assert payload[0]["url"].startswith("https://signed.local/")


def test_media_upload_url_requires_auth(client):
    response = client.post(
        "/api/v1/media/upload-url",
        json={"kind": "image", "mime": "image/jpeg", "extension": "jpg"},
    )
    assert response.status_code == 403


def test_media_upload_and_get_media(client, db, monkeypatch):
    user = make_user(db)

    monkeypatch.setattr(
        "app.api.endpoints.media.get_presigned_put_url",
        lambda object_name: f"https://signed.local/put/{object_name}",
    )
    monkeypatch.setattr(
        "app.api.endpoints.media.get_presigned_get_url",
        lambda object_name: f"https://signed.local/get/{object_name}",
    )

    create_response = client.post(
        "/api/v1/media/upload-url",
        headers=auth_header(user.id),
        json={"kind": "image", "mime": "image/jpeg", "extension": "jpg"},
    )
    assert create_response.status_code == 200
    payload = create_response.json()
    assert payload["put_url"].startswith("https://signed.local/put/")

    get_response = client.get(f"/api/v1/media/{payload['asset_id']}")
    assert get_response.status_code == 200
    get_payload = get_response.json()
    assert get_payload["url"].startswith("https://signed.local/get/")
