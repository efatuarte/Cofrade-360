from tests.conftest import auth_header, make_user


def test_plan_crud_and_items_flow(client, db):
    user = make_user(db)

    create_plan = client.post(
        "/api/v1/me/plans",
        headers=auth_header(user.id),
        json={"title": "Viernes Santo", "plan_date": "2026-04-10T00:00:00"},
    )
    assert create_plan.status_code == 201
    plan_id = create_plan.json()["id"]

    list_plans = client.get("/api/v1/me/plans", headers=auth_header(user.id))
    assert list_plans.status_code == 200
    assert len(list_plans.json()) == 1

    add_item_1 = client.post(
        f"/api/v1/me/plans/{plan_id}/items",
        headers=auth_header(user.id),
        json={
            "item_type": "event",
            "event_id": "evt-1",
            "desired_time_start": "2026-04-10T10:00:00",
            "desired_time_end": "2026-04-10T11:00:00",
            "lat": 37.39,
            "lng": -5.99,
        },
    )
    assert add_item_1.status_code == 201
    assert add_item_1.json()["warnings"] == []
    item_1_id = add_item_1.json()["item"]["id"]

    add_item_2 = client.post(
        f"/api/v1/me/plans/{plan_id}/items",
        headers=auth_header(user.id),
        json={
            "item_type": "brotherhood",
            "brotherhood_id": "bro-1",
            "desired_time_start": "2026-04-10T10:30:00",
            "desired_time_end": "2026-04-10T11:30:00",
            "lat": 37.40,
            "lng": -6.00,
        },
    )
    assert add_item_2.status_code == 201
    assert len(add_item_2.json()["warnings"]) == 1
    item_2_id = add_item_2.json()["item"]["id"]

    patch_item = client.patch(
        f"/api/v1/me/plans/{plan_id}/items/{item_2_id}",
        headers=auth_header(user.id),
        json={"desired_time_start": "2026-04-10T12:00:00", "desired_time_end": "2026-04-10T13:00:00"},
    )
    assert patch_item.status_code == 200
    assert patch_item.json()["warnings"] == []

    optimize = client.post(f"/api/v1/me/plans/{plan_id}/optimize", headers=auth_header(user.id))
    assert optimize.status_code == 200
    assert len(optimize.json()["items"]) == 2

    delete_item = client.delete(
        f"/api/v1/me/plans/{plan_id}/items/{item_1_id}",
        headers=auth_header(user.id),
    )
    assert delete_item.status_code == 204


def test_itinerary_requires_auth(client):
    response = client.get("/api/v1/me/plans")
    assert response.status_code == 403
