from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas import schemas
from app.crud import crud

router = APIRouter()


@router.get("/hermandades", response_model=List[schemas.Hermandad])
def read_hermandades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all hermandades"""
    hermandades = crud.get_hermandades(db, skip=skip, limit=limit)
    return hermandades


@router.get("/hermandades/{hermandad_id}", response_model=schemas.Hermandad)
def read_hermandad(hermandad_id: str, db: Session = Depends(get_db)):
    """Get hermandad by ID"""
    hermandad = crud.get_hermandad(db, hermandad_id=hermandad_id)
    if hermandad is None:
        raise HTTPException(status_code=404, detail="Hermandad not found")
    return hermandad


@router.post("/hermandades", response_model=schemas.Hermandad)
def create_hermandad(hermandad: schemas.HermandadCreate, db: Session = Depends(get_db)):
    """Create a new hermandad"""
    return crud.create_hermandad(db=db, hermandad=hermandad)
