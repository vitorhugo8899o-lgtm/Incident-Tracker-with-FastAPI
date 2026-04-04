from fastapi import APIRouter

from app.api.v1.endpoints.incidents import router_incident
from app.api.v1.endpoints.monitoring import router_monitoring
from app.api.v1.endpoints.technician import router_technician
from app.api.v1.endpoints.users import router_users

api_router = APIRouter()

api_router.include_router(router_monitoring, tags=['Monitoring'])
api_router.include_router(router_users, tags=['Users'])
api_router.include_router(router_incident, tags=['Incidents'])
api_router.include_router(router_technician, tags=['Technicians'])
