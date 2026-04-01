from fastapi import APIRouter

from app.api.v1.endpoints.monitoring import router_monitoring

api_router = APIRouter()

api_router.include_router(router_monitoring, tags=['monitoring'])
