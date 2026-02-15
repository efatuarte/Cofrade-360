import json
from pathlib import Path

from app.db.ingest import BrotherhoodData, ProcessionData, run_ingestion
from app.models.models import AuditLog, Hermandad, Procession
from tests.conftest import auth_header, make_admin_user, make_user


def test_phase11_schema_validation():
    brotherhood = BrotherhoodData.model_validate(
        {
            "type": "brotherhood",
            "year": 2026,
            "name_short": "Macarena",
            "name_full": "Hermandad de la Macarena",
            "web": "https://www.hermandaddelamacarena.es",
            "ss_day": "madrugada",
            "sede": "Basílica de la Macarena",
            "provenance": [
                {
                    "url": "https://www.hermandaddelamacarena.es",
                    "accessed_at": "2026-02-15T10:00:00",
                    "fields_extracted": ["name_short"],
                }
            ],
        }
    )
    procession = ProcessionData.model_validate(
        {
            "type": "procession",
            "year": 2026,
            "brotherhood": "macarena",
            "date": "2026-04-03T00:00:00",
            "schedule_points": [
                {
                    "point_type": "salida",
                    "label": "Salida",
                    "scheduled_datetime": "2026-04-03T00:00:00",
                }
            ],
            "itinerary_text": "Basílica, Campana, Catedral",
            "confidence": 0.9,
        }
    )

    assert brotherhood.name_short == "Macarena"
    assert procession.confidence == 0.9


def test_phase11_upsert_is_idempotent(tmp_path, db):
    base = tmp_path / "datasets" / "2026"
    base.mkdir(parents=True)
    (base / "brotherhoods.json").write_text(
        json.dumps(
            [
                {
                    "type": "brotherhood",
                    "year": 2026,
                    "name_short": "Macarena",
                    "name_full": "Hermandad de la Macarena",
                    "web": "https://www.hermandaddelamacarena.es",
                    "ss_day": "madrugada",
                    "sede": "Basílica de la Macarena",
                }
            ]
        ),
        encoding="utf-8",
    )
    (base / "processions.json").write_text(
        json.dumps(
            [
                {
                    "type": "procession",
                    "year": 2026,
                    "brotherhood": "macarena",
                    "date": "2026-04-03T00:00:00",
                    "schedule_points": [
                        {
                            "point_type": "salida",
                            "label": "Salida",
                            "scheduled_datetime": "2026-04-03T00:00:00",
                        }
                    ],
                    "itinerary_text": "Basílica, Campana, Catedral",
                    "confidence": 0.7,
                }
            ]
        ),
        encoding="utf-8",
    )

    from app.db import ingest

    original_root = ingest.DATASET_ROOT
    ingest.DATASET_ROOT = tmp_path / "datasets"
    try:
        first = run_ingestion(year=2026, dry_run=False, db=db)
        second = run_ingestion(year=2026, dry_run=False, db=db)
    finally:
        ingest.DATASET_ROOT = original_root

    assert first["created"] >= 1
    assert second["created"] == 0
    assert db.query(Hermandad).count() == 1
    assert db.query(Procession).count() == 1


def test_phase11_admin_endpoints_enforce_rbac(client, db):
    user = make_user(db)
    admin = make_admin_user(db)

    h = Hermandad(
        id="h-1",
        nombre="Macarena",
        name_short="Macarena",
        name_full="Hermandad de la Macarena",
        ss_day="madrugada",
    )
    db.add(h)
    db.commit()

    denied = client.patch(
        "/api/v1/admin/brotherhoods/h-1",
        json={"sede": "Nueva sede"},
        headers=auth_header(user.id),
    )
    assert denied.status_code == 403

    allowed = client.patch(
        "/api/v1/admin/brotherhoods/h-1",
        json={"sede": "Nueva sede"},
        headers=auth_header(admin.id),
    )
    assert allowed.status_code == 200
    assert allowed.json()["sede"] == "Nueva sede"
    assert db.query(AuditLog).count() == 1
