from fastapi import APIRouter
from app.api.v1.endpoints import auth, domains

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(domains.router, prefix="/domains", tags=["Domains"])

__all__ = ["router"]
