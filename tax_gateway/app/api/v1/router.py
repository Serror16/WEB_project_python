from fastapi import APIRouter
from .endpoints.auth import router as auth_router
from .endpoints.tax import router as tax_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(tax_router, prefix="/tax")