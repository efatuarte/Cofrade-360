from fastapi import APIRouter
from app.api.endpoints import hermandades, eventos, routing, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(hermandades.router, tags=["hermandades"])
api_router.include_router(eventos.router, tags=["eventos"])
api_router.include_router(routing.router, prefix="/routing", tags=["routing"])
