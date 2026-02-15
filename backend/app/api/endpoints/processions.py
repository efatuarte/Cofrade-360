import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.crud import crud
from app.models.models import User
from app.schemas.schemas import (
    ProcessionItineraryTextResponse,
    ProcessionItineraryTextUpsert,
    ProcessionOccupationCreate,
    ProcessionOccupationResponse,
    ProcessionOccupationUpdate,
    ProcessionResponse,
    ProcessionSchedulePointCreate,
    ProcessionSchedulePointResponse,
    ProcessionStatus,
    ProvenanceCreate,
    ProvenanceResponse,
    RestrictedAreaCreate,
    RestrictedAreaResponse,
    RestrictedAreaUpdate,
)

router = APIRouter()


@router.get("/processions", response_model=list[ProcessionResponse])
def list_processions(
    date: Optional[datetime] = None,
    status: Optional[ProcessionStatus] = None,
    db: Session = Depends(get_db),
):
    return crud.list_processions(db, date=date, status=status.value if status else None)


@router.get("/processions/{procession_id}", response_model=ProcessionResponse)
def get_procession(procession_id: str, db: Session = Depends(get_db)):
    item = crud.get_procession(db, procession_id)
    if not item:
        raise HTTPException(status_code=404, detail="Procession not found")
    return item


@router.get("/processions/{procession_id}/occupations", response_model=list[ProcessionOccupationResponse])
def list_occupations(
    procession_id: str,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=422, detail="'from' must be <= 'to'")
    if not crud.get_procession(db, procession_id):
        raise HTTPException(status_code=404, detail="Procession not found")
    return crud.list_procession_occupations(db, procession_id=procession_id, from_date=from_date, to_date=to_date)


@router.get("/restrictions", response_model=list[RestrictedAreaResponse])
def list_restrictions(
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=422, detail="'from' must be <= 'to'")
    return crud.list_restrictions(db, from_date=from_date, to_date=to_date)


@router.post("/restrictions", response_model=RestrictedAreaResponse, status_code=201)
def create_restriction(
    payload: RestrictedAreaCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "editor")),
):
    return crud.create_restriction(db, payload=payload)


@router.patch("/restrictions/{restriction_id}", response_model=RestrictedAreaResponse)
def patch_restriction(
    restriction_id: str,
    payload: RestrictedAreaUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "editor")),
):
    current = crud.get_restriction(db, restriction_id)
    if not current:
        raise HTTPException(status_code=404, detail="Restriction not found")

    start = payload.start_datetime or current.start_datetime
    end = payload.end_datetime or current.end_datetime
    if start > end:
        raise HTTPException(status_code=422, detail="start_datetime must be <= end_datetime")

    return crud.update_restriction(db, item=current, payload=payload)


@router.post("/processions/occupations", response_model=ProcessionOccupationResponse, status_code=201)
def create_occupation(
    payload: ProcessionOccupationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "editor")),
):
    if not crud.get_procession(db, payload.procession_id):
        raise HTTPException(status_code=404, detail="Procession not found")
    if not crud.get_street_segment(db, payload.street_segment_id):
        raise HTTPException(status_code=404, detail="Street segment not found")
    if crud.has_occupation_overlap(
        db,
        street_segment_id=payload.street_segment_id,
        start_datetime=payload.start_datetime,
        end_datetime=payload.end_datetime,
    ):
        raise HTTPException(status_code=409, detail="Occupation overlaps existing segment window")
    return crud.create_occupation(db, payload=payload)


@router.patch("/processions/occupations/{occupation_id}", response_model=ProcessionOccupationResponse)
def patch_occupation(
    occupation_id: str,
    payload: ProcessionOccupationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "editor")),
):
    current = crud.get_occupation(db, occupation_id)
    if not current:
        raise HTTPException(status_code=404, detail="Occupation not found")

    start = payload.start_datetime or current.start_datetime
    end = payload.end_datetime or current.end_datetime
    if start > end:
        raise HTTPException(status_code=422, detail="start_datetime must be <= end_datetime")

    if crud.has_occupation_overlap(
        db,
        street_segment_id=current.street_segment_id,
        start_datetime=start,
        end_datetime=end,
        exclude_id=current.id,
    ):
        raise HTTPException(status_code=409, detail="Occupation overlaps existing segment window")

    return crud.update_occupation(db, item=current, payload=payload)


@router.get("/processions/{procession_id}/schedule", response_model=list[ProcessionSchedulePointResponse])
def list_procession_schedule(procession_id: str, db: Session = Depends(get_db)):
    if not crud.get_procession(db, procession_id):
        raise HTTPException(status_code=404, detail="Procession not found")
    return crud.list_procession_schedule_points(db, procession_id=procession_id)


@router.put("/processions/{procession_id}/schedule", response_model=list[ProcessionSchedulePointResponse])
def put_procession_schedule(
    procession_id: str,
    payload: list[ProcessionSchedulePointCreate],
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "editor")),
):
    if not crud.get_procession(db, procession_id):
        raise HTTPException(status_code=404, detail="Procession not found")
    return crud.replace_procession_schedule_points(db, procession_id=procession_id, points=payload)


@router.get("/processions/{procession_id}/itinerary", response_model=ProcessionItineraryTextResponse | None)
def get_procession_itinerary(procession_id: str, db: Session = Depends(get_db)):
    if not crud.get_procession(db, procession_id):
        raise HTTPException(status_code=404, detail="Procession not found")
    return crud.get_procession_itinerary_text(db, procession_id=procession_id)


@router.put("/processions/{procession_id}/itinerary", response_model=ProcessionItineraryTextResponse)
def put_procession_itinerary(
    procession_id: str,
    payload: ProcessionItineraryTextUpsert,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "editor")),
):
    if not crud.get_procession(db, procession_id):
        raise HTTPException(status_code=404, detail="Procession not found")
    return crud.upsert_procession_itinerary_text(db, procession_id=procession_id, payload=payload)


@router.post("/provenance", response_model=ProvenanceResponse, status_code=201)
def create_provenance(
    payload: ProvenanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "editor")),
):
    row = crud.create_provenance(db, payload=payload)
    return ProvenanceResponse(
        id=row.id,
        entity_type=row.entity_type,
        entity_id=row.entity_id,
        source_url=row.source_url,
        accessed_at=row.accessed_at,
        fields_extracted=json.loads(row.fields_extracted),
        created_at=row.created_at,
    )


@router.get("/provenance", response_model=list[ProvenanceResponse])
def list_provenance(entity_type: Optional[str] = None, entity_id: Optional[str] = None, db: Session = Depends(get_db)):
    rows = crud.list_provenance(db, entity_type=entity_type, entity_id=entity_id)
    return [
        ProvenanceResponse(
            id=row.id,
            entity_type=row.entity_type,
            entity_id=row.entity_id,
            source_url=row.source_url,
            accessed_at=row.accessed_at,
            fields_extracted=json.loads(row.fields_extracted),
            created_at=row.created_at,
        )
        for row in rows
    ]
