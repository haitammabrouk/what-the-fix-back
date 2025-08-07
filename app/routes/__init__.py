from fastapi import APIRouter

from . import user, fix

API_ROUTER = APIRouter()

API_ROUTER.include_router(user.router)
API_ROUTER.include_router(fix.router)