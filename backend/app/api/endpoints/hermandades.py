from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.crud import crud
from app.schemas.schemas import BrotherhoodResponse, PaginatedResponse, SemanaSantaDay, SignedMediaResponse
from app.core.storage import get_presigned_get_url

router = APIRouter()


@router.get("/brotherhoods", response_model=PaginatedResponse[BrotherhoodResponse])
def read_brotherhoods(
    q: Optional[str] = None,
    day: Optional[SemanaSantaDay] = None,
    church_id: Optional[str] = None,
    has_media: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = crud.get_brotherhoods_paginated(
        db,
        page=page,
        page_size=page_size,
        q=q,
        day=day.value if day else None,
        church_id=church_id,
        has_media=has_media,
    )
    return PaginatedResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/brotherhoods/{brotherhood_id}", response_model=BrotherhoodResponse)
def read_brotherhood(brotherhood_id: str, db: Session = Depends(get_db)):
    brotherhood = crud.get_hermandad(db, hermandad_id=brotherhood_id)
    if brotherhood is None:
        raise HTTPException(status_code=404, detail="Brotherhood not found")
    return brotherhood


@router.get("/brotherhoods/{brotherhood_id}/media", response_model=list[SignedMediaResponse])
def read_brotherhood_media(brotherhood_id: str, db: Session = Depends(get_db)):
    brotherhood = crud.get_hermandad(db, hermandad_id=brotherhood_id)
    if brotherhood is None:
        raise HTTPException(status_code=404, detail="Brotherhood not found")

    assets = crud.get_brotherhood_media(db, brotherhood_id=brotherhood_id)
    return [
        SignedMediaResponse(asset_id=asset.id, url=get_presigned_get_url(asset.path))
        for asset in assets
    ]


# Backward-compatible legacy routes
@router.get("/hermandades", response_model=PaginatedResponse[BrotherhoodResponse])
def read_hermandades_legacy(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    page = (skip // max(limit, 1)) + 1
    items, total = crud.get_brotherhoods_paginated(db, page=page, page_size=limit)
    return PaginatedResponse(items=items, page=page, page_size=limit, total=total)


@router.get("/hermandades/{hermandad_id}", response_model=BrotherhoodResponse)
def read_hermandad_legacy(hermandad_id: str, db: Session = Depends(get_db)):
    brotherhood = crud.get_hermandad(db, hermandad_id=hermandad_id)
    if brotherhood is None:
        raise HTTPException(status_code=404, detail="Brotherhood not found")
    return brotherhood
