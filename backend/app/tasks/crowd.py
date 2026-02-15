import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.models import CrowdReport, CrowdSignal


def geohash_from_coords(lat: float, lng: float, precision: int = 3) -> str:
    return f"{round(lat, precision)}:{round(lng, precision)}"


def aggregate_crowd_signals(db: Session, *, now: datetime | None = None, bucket_minutes: int = 10) -> int:
    now = now or datetime.utcnow()
    bucket_start = now.replace(minute=(now.minute // bucket_minutes) * bucket_minutes, second=0, microsecond=0)
    bucket_end = bucket_start + timedelta(minutes=bucket_minutes)

    rows = (
        db.query(CrowdReport)
        .filter(
            CrowdReport.created_at >= bucket_start,
            CrowdReport.created_at < bucket_end,
            CrowdReport.is_hidden.is_(False),
        )
        .all()
    )

    by_geohash: dict[str, list[CrowdReport]] = {}
    for row in rows:
        by_geohash.setdefault(row.geohash, []).append(row)

    created = 0
    for geohash, reports in by_geohash.items():
        avg_severity = sum(r.severity for r in reports) / len(reports)
        score = min(1.0, avg_severity / 5.0)
        confidence = min(1.0, 0.25 + len(reports) * 0.15)

        current = (
            db.query(CrowdSignal)
            .filter(CrowdSignal.geohash == geohash, CrowdSignal.bucket_start == bucket_start)
            .first()
        )
        if current:
            current.score = score
            current.confidence = confidence
            current.reports_count = len(reports)
            continue

        db.add(
            CrowdSignal(
                id=str(uuid.uuid4()),
                geohash=geohash,
                bucket_start=bucket_start,
                bucket_end=bucket_end,
                score=score,
                confidence=confidence,
                reports_count=len(reports),
            )
        )
        created += 1

    db.commit()
    return created
