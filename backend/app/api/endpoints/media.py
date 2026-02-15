import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, get_db
from app.core.storage import get_presigned_get_url, get_presigned_put_url
from app.crud import crud
from app.models.models import User
from app.schemas.schemas import MediaUploadRequest, MediaUploadSignedUrlResponse, SignedMediaResponse

router = APIRouter()


@router.post("/media/upload-url", response_model=MediaUploadSignedUrlResponse)
def create_upload_url(
    payload: MediaUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    object_path = f"media/{payload.kind.value}/{uuid.uuid4()}.{payload.extension.strip('.')}"
    asset = crud.create_media_asset(
        db,
        kind=payload.kind.value,
        mime=payload.mime,
        path=object_path,
        brotherhood_id=payload.brotherhood_id,
    )

    put_url = get_presigned_put_url(object_path)
    return MediaUploadSignedUrlResponse(asset_id=asset.id, path=object_path, put_url=put_url)


@router.get("/media/{asset_id}", response_model=SignedMediaResponse)
def get_media(asset_id: str, db: Session = Depends(get_db)):
    asset = crud.get_media_asset(db, asset_id=asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Media asset not found")

    return SignedMediaResponse(asset_id=asset.id, url=get_presigned_get_url(asset.path))
