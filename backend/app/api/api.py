from fastapi import APIRouter
from app.api.endpoints import hermandades, routing

api_router = APIRouter()

api_router.include_router(hermandades.router, prefix="/hermandades", tags=["hermandades"])
api_router.include_router(hermandades.router, prefix="/eventos", tags=["eventos"])
api_router.include_router(routing.router, prefix="/routing", tags=["routing"])
