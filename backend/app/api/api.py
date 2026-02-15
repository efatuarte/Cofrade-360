from fastapi import APIRouter
from app.api.endpoints import admin, auth, crowd, eventos, hermandades, ingestion, itinerario, media, routing

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(hermandades.router, tags=["hermandades"])
api_router.include_router(eventos.router, tags=["eventos"])
api_router.include_router(routing.router, prefix="/routing", tags=["routing"])

api_router.include_router(media.router, tags=["media"])
api_router.include_router(ingestion.router, tags=["ingestion"])
api_router.include_router(itinerario.router, tags=["itinerario"])

api_router.include_router(admin.router)

api_router.include_router(crowd.router)
