from unittest.mock import patch

import json

import pytest

from tests.conftest import auth_header

try:
    from app.db.ingestion.import_hermandades_dataset import import_dataset
    from app.models.models import DataProvenance, Hermandad, MediaAsset, Procession, ProcessionSchedulePoint
    from tests.conftest import make_admin_user
except ImportError:
    pytest.skip("Ingestion import tests require optional operational models not present in this build", allow_module_level=True)


def test_import_dataset_is_idempotent(db, tmp_path):
    dataset = {
        "items": [
            {
                "name_short": "Gran Poder",
                "name_full": "Hermandad del Gran Poder",
                "web_url": "https://www.gran-poder.es",
                "ss_day": "Madrugada",
                "sede": {
                    "temple_name": "Basílica del Gran Poder",
                    "address": "Plaza de San Lorenzo, 13",
                    "lat": 37.3935,
                    "lng": -5.9995,
                    "needs_geocode": False,
                },
                "titulares": [],
                "media": {
                    "logo_url": "https://example.com/logo.jpg",
                    "images": ["https://example.com/paso1.jpg"],
                },
                "schedule": {
                    "salida": "2026-04-10T01:00:00",
                    "carrera_oficial_start": None,
                    "carrera_oficial_end": None,
                    "recogida": "2026-04-10T07:30:00",
                    "itinerary_text": "San Lorenzo, Campana, Carrera Oficial, San Lorenzo",
                },
                "provenance": [
                    {
                        "url": "https://www.gran-poder.es",
                        "accessed_at": "2026-02-16T10:00:00",
                        "fields_extracted": ["name_short", "name_full", "media.logo_url"],
                        "status_code": 200,
                    }
                ],
            }
        ]
    }

    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(json.dumps(dataset), encoding="utf-8")

    first = import_dataset(db, dataset_path=dataset_path)
    second = import_dataset(db, dataset_path=dataset_path)

    assert first["total_items"] == 1
    assert first["created_hermandades"] == 1
    assert second["created_hermandades"] == 0

    assert db.query(Hermandad).count() == 1
    assert db.query(MediaAsset).count() == 2
    assert db.query(Procession).count() == 1
    assert db.query(ProcessionSchedulePoint).count() == 2
    assert db.query(DataProvenance).count() == 1


def test_import_endpoint_requires_admin_or_editor(client, db):
    admin = make_admin_user(db)

    with patch("app.api.endpoints.ingestion.import_dataset", return_value={
        "total_items": 71,
        "created_hermandades": 10,
        "created_media": 20,
        "created_processions": 8,
        "created_schedule_points": 16,
        "created_provenance": 12,
    }):
        response = client.post("/api/v1/ingestion/hermandades/import", headers=auth_header(admin.id))

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_items"] == 71
    assert payload["created_hermandades"] == 10
