from fastapi import APIRouter

from app.api.v1.endpoints.monitoring import router_monitoring
from app.api.v1.endpoints.users import router_users
from app.api.v1.endpoints.incidents import router_incident


api_router = APIRouter()

api_router.include_router(router_monitoring, tags=['Monitoring'])
api_router.include_router(router_users, tags=['Users'])
api_router.include_router(router_incident, tags=['Incidents'])
