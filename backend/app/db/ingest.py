from __future__ import annotations

import argparse
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from .session import SessionLocal
from ..models.models import DataProvenance, Hermandad, MediaAsset, Procession, ProcessionItineraryText, ProcessionSchedulePoint

DATASET_ROOT = Path(__file__).resolve().parent / "datasets"


class ProvenanceEntry(BaseModel):
    url: HttpUrl
    accessed_at: datetime
    fields_extracted: list[str] = Field(default_factory=list)
    notes: str | None = None


class BrotherhoodData(BaseModel):
    type: str = "brotherhood"
    year: int = Field(ge=2020, le=2100)
    name_short: str
    name_full: str
    web: HttpUrl
    ss_day: str
    sede: str | None = None
    titulares: list[str] = Field(default_factory=list)
    media_links: list[HttpUrl] = Field(default_factory=list)
    notes: str | None = None
    provenance: list[ProvenanceEntry] = Field(default_factory=list)

    @field_validator("type")
    @classmethod
    def must_be_brotherhood(cls, value: str) -> str:
        if value != "brotherhood":
            raise ValueError("type must be 'brotherhood'")
        return value


class ProcessionSchedulePointData(BaseModel):
    point_type: str
    label: str | None = None
    scheduled_datetime: datetime


class ProcessionData(BaseModel):
    type: str = "procession"
    year: int = Field(ge=2020, le=2100)
    brotherhood: str
    date: datetime
    schedule_points: list[ProcessionSchedulePointData] = Field(default_factory=list)
    itinerary_text: str
    confidence: float = Field(ge=0, le=1)
    provenance: list[ProvenanceEntry] = Field(default_factory=list)

    @field_validator("type")
    @classmethod
    def must_be_procession(cls, value: str) -> str:
        if value != "procession":
            raise ValueError("type must be 'procession'")
        return value


class IngestionReport(BaseModel):
    created: int = 0
    updated: int = 0
    skipped: int = 0
    warnings: list[str] = Field(default_factory=list)


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return normalized.strip("-")


def _upsert_provenance(db: Session, *, entity_type: str, entity_id: str, rows: list[ProvenanceEntry]) -> None:
    for row in rows:
        current = (
            db.query(DataProvenance)
            .filter(
                DataProvenance.entity_type == entity_type,
                DataProvenance.entity_id == entity_id,
                DataProvenance.source_url == str(row.url),
            )
            .first()
        )
        if current:
            current.accessed_at = row.accessed_at
            current.fields_extracted = json.dumps(row.fields_extracted)
            current.notes = row.notes
            continue
        db.add(
            DataProvenance(
                id=str(uuid.uuid4()),
                entity_type=entity_type,
                entity_id=entity_id,
                source_url=str(row.url),
                accessed_at=row.accessed_at,
                fields_extracted=json.dumps(row.fields_extracted),
                notes=row.notes,
            )
        )


def _upsert_brotherhood(db: Session, payload: BrotherhoodData, report: IngestionReport) -> Hermandad:
    slug = _slugify(payload.name_short)
    existing = (
        db.query(Hermandad)
        .filter(func.lower(Hermandad.name_short) == payload.name_short.lower())
        .first()
    )
    if existing is None:
        existing = Hermandad(
            id=str(uuid.uuid4()),
            nombre=payload.name_full,
            name_short=payload.name_short,
            name_full=payload.name_full,
            sede=payload.sede,
            ss_day=payload.ss_day,
            history=payload.notes,
        )
        db.add(existing)
        db.flush()
        report.created += 1
    else:
        existing.nombre = payload.name_full
        existing.name_full = payload.name_full
        existing.sede = payload.sede
        existing.ss_day = payload.ss_day
        existing.history = payload.notes
        report.updated += 1

    for media_link in payload.media_links:
        present = (
            db.query(MediaAsset)
            .filter(MediaAsset.brotherhood_id == existing.id, MediaAsset.path == str(media_link))
            .first()
        )
        if not present:
            db.add(
                MediaAsset(
                    id=str(uuid.uuid4()),
                    kind="image",
                    mime="image/jpeg",
                    path=str(media_link),
                    brotherhood_id=existing.id,
                )
            )

    _upsert_provenance(db, entity_type="brotherhood", entity_id=existing.id, rows=payload.provenance)
    if not slug:
        report.warnings.append(f"Brotherhood without slug: {payload.name_short}")
    return existing


def _upsert_procession(db: Session, payload: ProcessionData, report: IngestionReport) -> None:
    brotherhood = None
    candidate_slug = _slugify(payload.brotherhood)
    for candidate in db.query(Hermandad).all():
        if _slugify(candidate.name_short or "") == candidate_slug:
            brotherhood = candidate
            break
    if not brotherhood:
        report.skipped += 1
        report.warnings.append(f"Missing brotherhood for procession key '{payload.brotherhood}'")
        return

    year_start = datetime(payload.year, 1, 1)
    year_end = datetime(payload.year, 12, 31, 23, 59, 59)
    current = (
        db.query(Procession)
        .filter(
            Procession.brotherhood_id == brotherhood.id,
            Procession.date >= year_start,
            Procession.date <= year_end,
        )
        .first()
    )
    if current is None:
        current = Procession(
            id=str(uuid.uuid4()),
            brotherhood_id=brotherhood.id,
            date=payload.date,
            status="scheduled",
            confidence=payload.confidence,
        )
        db.add(current)
        db.flush()
        report.created += 1
    else:
        current.date = payload.date
        current.confidence = payload.confidence
        report.updated += 1

    db.query(ProcessionSchedulePoint).filter(ProcessionSchedulePoint.procession_id == current.id).delete()
    for point in payload.schedule_points:
        db.add(
            ProcessionSchedulePoint(
                id=str(uuid.uuid4()),
                procession_id=current.id,
                point_type=point.point_type,
                label=point.label,
                scheduled_datetime=point.scheduled_datetime,
            )
        )

    itinerary = db.query(ProcessionItineraryText).filter(ProcessionItineraryText.procession_id == current.id).first()
    if itinerary is None:
        db.add(
            ProcessionItineraryText(
                id=str(uuid.uuid4()),
                procession_id=current.id,
                raw_text=payload.itinerary_text,
                source_url=str(payload.provenance[0].url) if payload.provenance else None,
                accessed_at=datetime.utcnow(),
            )
        )
    else:
        itinerary.raw_text = payload.itinerary_text
        itinerary.source_url = str(payload.provenance[0].url) if payload.provenance else itinerary.source_url
        itinerary.accessed_at = datetime.utcnow()

    _upsert_provenance(db, entity_type="procession", entity_id=current.id, rows=payload.provenance)


def run_ingestion(*, year: int, dry_run: bool, db: Session | None = None) -> dict[str, Any]:
    report = IngestionReport()
    year_root = DATASET_ROOT / str(year)
    brotherhood_file = year_root / "brotherhoods.json"
    procession_file = year_root / "processions.json"

    owns_session = db is None
    db = db or SessionLocal()
    try:
        brotherhood_rows = json.loads(brotherhood_file.read_text(encoding="utf-8"))
        procession_rows = json.loads(procession_file.read_text(encoding="utf-8"))

        for row in brotherhood_rows:
            payload = BrotherhoodData.model_validate(row)
            _upsert_brotherhood(db, payload, report)

        for row in procession_rows:
            payload = ProcessionData.model_validate(row)
            _upsert_procession(db, payload, report)

        if dry_run:
            db.rollback()
        else:
            db.commit()

        return report.model_dump()
    finally:
        if owns_session:
            db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Versioned dataset ingestion")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    dry_run = True if args.dry_run else not args.apply
    summary = run_ingestion(year=args.year, dry_run=dry_run)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
