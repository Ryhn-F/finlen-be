from fastapi import APIRouter

from finlen_be.api.v1.auth import router as auth_router
from finlen_be.api.v1.scenarios import router as scenarios_router
from finlen_be.api.v1.roleplay import router as roleplay_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(scenarios_router)
api_v1_router.include_router(roleplay_router)

__all__ = ["api_v1_router"]
