from fastapi import APIRouter

from app.api.routes import demo, events, health


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(demo.router, prefix="/api/v1")
api_router.include_router(events.router, prefix="/api/v1")
