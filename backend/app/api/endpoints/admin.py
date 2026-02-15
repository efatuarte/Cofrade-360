import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.crud import crud
from app.models.models import AuditLog, Hermandad, MediaAsset, Procession, ProcessionItineraryText, ProcessionSchedulePoint, User
from app.schemas.schemas import (
    AdminBrotherhoodUpdate,
    AdminProcessionUpdate,
    AuditLogResponse,
    BrotherhoodResponse,
    PaginatedResponse,
    ProcessionResponse,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/brotherhoods", response_model=PaginatedResponse[BrotherhoodResponse])
def list_brotherhoods(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    items, total = crud.get_brotherhoods_paginated(db, page=page, page_size=page_size)
    return PaginatedResponse(items=items, page=page, page_size=page_size, total=total)


@router.patch("/brotherhoods/{brotherhood_id}", response_model=BrotherhoodResponse)
def patch_brotherhood(
    brotherhood_id: str,
    payload: AdminBrotherhoodUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    brotherhood = db.query(Hermandad).filter(Hermandad.id == brotherhood_id).first()
    if not brotherhood:
        raise HTTPException(status_code=404, detail="Brotherhood not found")

    changes: dict[str, dict[str, str | None]] = {}

    if payload.sede is not None and payload.sede != brotherhood.sede:
        changes["sede"] = {"from": brotherhood.sede, "to": payload.sede}
        brotherhood.sede = payload.sede
    if payload.ss_day is not None and payload.ss_day.value != brotherhood.ss_day:
        changes["ss_day"] = {"from": brotherhood.ss_day, "to": payload.ss_day.value}
        brotherhood.ss_day = payload.ss_day.value
    if payload.logo_asset_id is not None and payload.logo_asset_id != brotherhood.logo_asset_id:
        changes["logo_asset_id"] = {"from": brotherhood.logo_asset_id, "to": payload.logo_asset_id}
        brotherhood.logo_asset_id = payload.logo_asset_id

    for media_link in payload.media_links:
        exists = (
            db.query(MediaAsset)
            .filter(MediaAsset.brotherhood_id == brotherhood.id, MediaAsset.path == media_link)
            .first()
        )
        if not exists:
            db.add(
                MediaAsset(
                    id=str(uuid.uuid4()),
                    kind="image",
                    mime="image/jpeg",
                    path=media_link,
                    brotherhood_id=brotherhood.id,
                )
            )

    if changes:
        db.add(
            AuditLog(
                id=str(uuid.uuid4()),
                entity_type="brotherhood",
                entity_id=brotherhood.id,
                action="manual_update",
                changed_fields=json.dumps(changes),
                actor_user_id=user.id,
            )
        )

    db.commit()
    db.refresh(brotherhood)
    return brotherhood




@router.get("/processions", response_model=PaginatedResponse[ProcessionResponse])
def list_processions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    query = db.query(Procession).order_by(Procession.date.asc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(items=items, page=page, page_size=page_size, total=total)


@router.patch("/processions/{procession_id}", response_model=ProcessionResponse)
def patch_procession(
    procession_id: str,
    payload: AdminProcessionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    procession = db.query(Procession).filter(Procession.id == procession_id).first()
    if not procession:
        raise HTTPException(status_code=404, detail="Procession not found")

    itinerary = db.query(ProcessionItineraryText).filter(ProcessionItineraryText.procession_id == procession.id).first()
    previous_itinerary = itinerary.raw_text if itinerary else None

    schedule_before = (
        db.query(ProcessionSchedulePoint)
        .filter(ProcessionSchedulePoint.procession_id == procession.id)
        .order_by(ProcessionSchedulePoint.scheduled_datetime.asc())
        .all()
    )

    previous_confidence = procession.confidence
    procession.confidence = payload.confidence

    if itinerary is None:
        itinerary = ProcessionItineraryText(
            id=str(uuid.uuid4()),
            procession_id=procession.id,
            raw_text=payload.itinerary_text,
            accessed_at=datetime.utcnow(),
        )
        db.add(itinerary)
    else:
        itinerary.raw_text = payload.itinerary_text
        itinerary.accessed_at = datetime.utcnow()

    db.query(ProcessionSchedulePoint).filter(ProcessionSchedulePoint.procession_id == procession.id).delete()
    for point in payload.schedule_points:
        db.add(
            ProcessionSchedulePoint(
                id=str(uuid.uuid4()),
                procession_id=procession.id,
                point_type=point.point_type,
                label=point.label,
                scheduled_datetime=point.scheduled_datetime,
            )
        )

    db.add(
        AuditLog(
            id=str(uuid.uuid4()),
            entity_type="procession",
            entity_id=procession.id,
            action="manual_update",
            changed_fields=json.dumps(
                {
                    "confidence": {"from": previous_confidence, "to": payload.confidence},
                    "itinerary_text": {"from": previous_itinerary, "to": payload.itinerary_text},
                    "schedule_points_count": {
                        "from": len(schedule_before),
                        "to": len(payload.schedule_points),
                    },
                }
            ),
            actor_user_id=user.id,
        )
    )

    db.commit()
    db.refresh(procession)
    return procession


@router.get("/audit-logs", response_model=PaginatedResponse[AuditLogResponse])
def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    query = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(items=items, page=page, page_size=page_size, total=total)
