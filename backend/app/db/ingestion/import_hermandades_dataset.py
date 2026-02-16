"""A3: importar dataset normalizado de hermandades a DB de forma idempotente."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import (
    DataProvenance,
    Hermandad,
    Location,
    MediaAsset,
    Procession,
    ProcessionItineraryText,
    ProcessionSchedulePoint,
    Titular,
)

DEFAULT_DATASET_PATH = Path(__file__).resolve().parent / "hermandades_dataset.normalized.json"

DAY_TO_ENUM = {
    "Viernes de Dolores": "viernes_dolores",
    "Sábado de Pasión": "sabado_pasion",
    "Domingo de Ramos": "domingo_ramos",
    "Lunes Santo": "lunes_santo",
    "Martes Santo": "martes_santo",
    "Miércoles Santo": "miercoles_santo",
    "Jueves Santo": "jueves_santo",
    "Madrugada": "madrugada",
    "Viernes Santo": "viernes_santo",
    "Sábado Santo": "sabado_santo",
    "Domingo de Resurrección": "domingo_resurreccion",
}


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _find_or_create_location(db: Session, sede: Dict[str, Any]) -> Optional[Location]:
    temple_name = (sede.get("temple_name") or "").strip()
    address = (sede.get("address") or "").strip()
    if not temple_name and not address:
        return None

    query = db.query(Location)
    if temple_name:
        query = query.filter(Location.name == temple_name)
    if address:
        query = query.filter(Location.address == address)

    location = query.first()
    if location:
        return location

    location = Location(
        id=str(uuid.uuid4()),
        name=temple_name or address,
        address=address or None,
        lat=sede.get("lat"),
        lng=sede.get("lng"),
        kind="church",
    )
    db.add(location)
    db.flush()
    return location


def _upsert_hermandad(db: Session, item: Dict[str, Any], church: Optional[Location]) -> tuple[Hermandad, bool]:
    name_short = item["name_short"].strip()
    hermandad = db.query(Hermandad).filter(Hermandad.name_short == name_short).first()
    created = False
    if hermandad is None:
        hermandad = Hermandad(
            id=str(uuid.uuid4()),
            nombre=item["name_full"],
            name_short=name_short,
            name_full=item.get("name_full") or name_short,
            web_url=item.get("web_url"),
            ss_day=DAY_TO_ENUM.get(item.get("ss_day", ""), None),
            sede=(item.get("sede") or {}).get("temple_name"),
            church_id=church.id if church else None,
            history="",
            highlights="[]",
            stats="{}",
        )
        db.add(hermandad)
        db.flush()
        created = True
    else:
        hermandad.nombre = item.get("name_full") or hermandad.nombre
        hermandad.name_full = item.get("name_full") or hermandad.name_full
        hermandad.web_url = item.get("web_url") or hermandad.web_url
        hermandad.ss_day = DAY_TO_ENUM.get(item.get("ss_day", ""), hermandad.ss_day)
        hermandad.sede = (item.get("sede") or {}).get("temple_name") or hermandad.sede
        if church:
            hermandad.church_id = church.id
    return hermandad, created


def _upsert_titulares(db: Session, hermandad: Hermandad, titulares: list[Dict[str, Any]]) -> int:
    if not titulares:
        return 0
    created = 0
    for idx, t in enumerate(titulares):
        name = (t.get("name") or "").strip()
        if not name:
            continue
        exists = (
            db.query(Titular)
            .filter(Titular.brotherhood_id == hermandad.id, Titular.name == name)
            .first()
        )
        if exists:
            exists.kind = t.get("kind", exists.kind)
            exists.position = idx
            continue
        db.add(
            Titular(
                id=str(uuid.uuid4()),
                brotherhood_id=hermandad.id,
                name=name,
                kind=t.get("kind", "unknown"),
                position=idx,
            )
        )
        created += 1
    return created


def _upsert_media(db: Session, hermandad: Hermandad, media: Dict[str, Any]) -> int:
    created = 0
    urls = []
    logo = media.get("logo_url")
    if logo:
        urls.append(logo)
    for image in media.get("images", []):
        if image and image not in urls:
            urls.append(image)

    for idx, url in enumerate(urls):
        exists = (
            db.query(MediaAsset)
            .filter(MediaAsset.brotherhood_id == hermandad.id, MediaAsset.path == url)
            .first()
        )
        if exists:
            continue
        asset = MediaAsset(
            id=str(uuid.uuid4()),
            kind="image",
            mime="image/jpeg",
            path=url,
            brotherhood_id=hermandad.id,
        )
        db.add(asset)
        db.flush()
        created += 1
        if idx == 0 and hermandad.logo_asset_id is None:
            hermandad.logo_asset_id = asset.id
    return created


def _upsert_procession_data(db: Session, hermandad: Hermandad, schedule: Dict[str, Any], provenance_url: Optional[str]) -> tuple[int, int]:
    parsed_date = _parse_datetime(schedule.get("salida"))
    if parsed_date is None:
        return 0, 0

    procession = (
        db.query(Procession)
        .filter(Procession.brotherhood_id == hermandad.id, Procession.date == parsed_date)
        .first()
    )
    created_procession = 0
    if procession is None:
        procession = Procession(
            id=str(uuid.uuid4()),
            brotherhood_id=hermandad.id,
            date=parsed_date,
            status="scheduled",
        )
        db.add(procession)
        db.flush()
        created_procession = 1

    # Reemplazo completo de puntos para idempotencia.
    db.query(ProcessionSchedulePoint).filter(ProcessionSchedulePoint.procession_id == procession.id).delete()
    point_map = {
        "salida": "salida",
        "carrera_oficial_start": "carrera_oficial_start",
        "carrera_oficial_end": "carrera_oficial_end",
        "recogida": "recogida",
    }
    created_points = 0
    for field, point_type in point_map.items():
        dt = _parse_datetime(schedule.get(field))
        if not dt:
            continue
        db.add(
            ProcessionSchedulePoint(
                id=str(uuid.uuid4()),
                procession_id=procession.id,
                point_type=point_type,
                label=field,
                scheduled_datetime=dt,
            )
        )
        created_points += 1

    itinerary_text = (schedule.get("itinerary_text") or "").strip()
    if itinerary_text:
        itinerary = (
            db.query(ProcessionItineraryText)
            .filter(ProcessionItineraryText.procession_id == procession.id)
            .first()
        )
        if itinerary is None:
            db.add(
                ProcessionItineraryText(
                    id=str(uuid.uuid4()),
                    procession_id=procession.id,
                    raw_text=itinerary_text,
                    source_url=provenance_url,
                    accessed_at=datetime.utcnow(),
                )
            )
        else:
            itinerary.raw_text = itinerary_text
            itinerary.source_url = provenance_url
            itinerary.accessed_at = datetime.utcnow()

    return created_procession, created_points


def _upsert_provenance(db: Session, hermandad_id: str, provenance_rows: list[Dict[str, Any]]) -> int:
    created = 0
    for row in provenance_rows:
        source_url = row.get("url")
        accessed_at = _parse_datetime(row.get("accessed_at")) or datetime.utcnow()
        fields_extracted = row.get("fields_extracted") or []

        exists = (
            db.query(DataProvenance)
            .filter(
                DataProvenance.entity_type == "brotherhood",
                DataProvenance.entity_id == hermandad_id,
                DataProvenance.source_url == source_url,
            )
            .first()
        )
        if exists:
            exists.accessed_at = accessed_at
            exists.fields_extracted = json.dumps(fields_extracted)
            continue

        db.add(
            DataProvenance(
                id=str(uuid.uuid4()),
                entity_type="brotherhood",
                entity_id=hermandad_id,
                source_url=source_url,
                accessed_at=accessed_at,
                fields_extracted=json.dumps(fields_extracted),
            )
        )
        created += 1
    return created


def import_dataset(db: Session, dataset_path: Path = DEFAULT_DATASET_PATH) -> Dict[str, int]:
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    items = payload.get("items", [])

    created_hermandades = 0
    created_titulares = 0
    created_media = 0
    created_processions = 0
    created_schedule_points = 0
    created_provenance = 0

    for item in items:
        sede = item.get("sede") or {}
        media = item.get("media") or {}
        provenance = item.get("provenance") or []
        schedule = item.get("schedule") or {}
        titulares = item.get("titulares") or []

        church = _find_or_create_location(db, sede)
        hermandad, is_created = _upsert_hermandad(db, item, church)
        if is_created:
            created_hermandades += 1

        created_titulares += _upsert_titulares(db, hermandad, titulares)
        created_media += _upsert_media(db, hermandad, media)

        source_url = provenance[0].get("url") if provenance else item.get("web_url")
        proc_created, points_created = _upsert_procession_data(db, hermandad, schedule, source_url)
        created_processions += proc_created
        created_schedule_points += points_created

        created_provenance += _upsert_provenance(db, hermandad.id, provenance)

    db.commit()
    return {
        "total_items": len(items),
        "created_hermandades": created_hermandades,
        "created_titulares": created_titulares,
        "created_media": created_media,
        "created_processions": created_processions,
        "created_schedule_points": created_schedule_points,
        "created_provenance": created_provenance,
    }


def main() -> None:
    db = SessionLocal()
    try:
        summary = import_dataset(db)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    finally:
        db.close()


if __name__ == "__main__":
    main()
