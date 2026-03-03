from .routers.auth import router as auth_router
from .routers.health import router as health_router
from .routers.users import router as user_router
from fastapi import APIRouter

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(health_router)
router.include_router(user_router)
