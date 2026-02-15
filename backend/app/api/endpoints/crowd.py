import json
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, get_db, require_roles
from app.models.models import AnalyticsEvent, CrowdReport, CrowdSignal, User
from app.schemas.schemas import (
    AnalyticsEventResponse,
    CrowdAggregateResponse,
    CrowdModerationUpdate,
    CrowdReportCreate,
    CrowdReportResponse,
    CrowdSignalResponse,
)
from app.tasks.crowd import aggregate_crowd_signals, geohash_from_coords

router = APIRouter(prefix="/crowd", tags=["crowd"])


@router.post("/reports", response_model=CrowdReportResponse, status_code=201)
def create_report(
    payload: CrowdReportCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    geohash = geohash_from_coords(payload.lat, payload.lng)
    window_start = datetime.utcnow() - timedelta(minutes=5)
    recent = (
        db.query(CrowdReport)
        .filter(
            CrowdReport.user_id == user.id,
            CrowdReport.geohash == geohash,
            CrowdReport.created_at >= window_start,
        )
        .count()
    )
    if recent >= 1:
        raise HTTPException(status_code=429, detail="Too many reports for this area and time window")

    row = CrowdReport(
        id=str(uuid.uuid4()),
        user_id=user.id,
        geohash=geohash,
        lat=payload.lat,
        lng=payload.lng,
        severity=payload.severity,
        note=payload.note,
    )
    db.add(row)

    db.add(
        AnalyticsEvent(
            id=str(uuid.uuid4()),
            event_type="report_submitted",
            user_id=user.id,
            trace_id=request.headers.get("x-trace-id"),
            payload=json.dumps({"geohash": geohash, "severity": payload.severity}),
        )
    )
    db.commit()
    db.refresh(row)
    return row


@router.get("/signals", response_model=list[CrowdSignalResponse])
def list_signals(
    geohash: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(CrowdSignal).order_by(CrowdSignal.bucket_start.desc())
    if geohash:
        query = query.filter(CrowdSignal.geohash == geohash)
    return query.limit(200).all()


@router.post("/aggregate", response_model=CrowdAggregateResponse)
def aggregate_now(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    created = aggregate_crowd_signals(db)
    return CrowdAggregateResponse(created_signals=created)


@router.patch("/reports/{report_id}", response_model=CrowdReportResponse)
def moderate_report(
    report_id: str,
    payload: CrowdModerationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    row = db.query(CrowdReport).filter(CrowdReport.id == report_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Crowd report not found")

    if payload.is_flagged is not None:
        row.is_flagged = payload.is_flagged
    if payload.is_hidden is not None:
        row.is_hidden = payload.is_hidden

    db.commit()
    db.refresh(row)
    return row


@router.get("/analytics", response_model=list[AnalyticsEventResponse])
def list_analytics(
    event_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    query = db.query(AnalyticsEvent).order_by(AnalyticsEvent.created_at.desc())
    if event_type:
        query = query.filter(AnalyticsEvent.event_type == event_type)
    return query.limit(200).all()
