from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.db.ingestion.hermandades_sources import DAY_BLOCKS, HERMANDADES_SEVILLA_WEBS
from app.db.ingestion.import_hermandades_dataset import import_dataset
from app.models.models import User
from app.schemas.schemas import IngestionBrotherhoodSource, IngestionImportSummary

router = APIRouter()


@router.get("/ingestion/hermandades/sources", response_model=list[IngestionBrotherhoodSource])
def list_hermandades_sources():
    rows: list[IngestionBrotherhoodSource] = []
    for day, brotherhood_names in DAY_BLOCKS.items():
        for name in brotherhood_names:
            rows.append(
                IngestionBrotherhoodSource(
                    ss_day=day,
                    name=name,
                    web_url=HERMANDADES_SEVILLA_WEBS[name],
                )
            )
    return rows


@router.post("/ingestion/hermandades/import", response_model=IngestionImportSummary)
def import_hermandades(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "editor")),
):
    summary = import_dataset(db)
    return IngestionImportSummary(**summary)
