from fastapi import APIRouter
from app.repositories.incident_repository import create_incident
from app.api.v1.dependencies import DBSession, CurrentUser
from app.schemas.incident import IncidentCreate

router_incident = APIRouter()


@router_incident.post('/incidents')
async def incident_create(current_user:CurrentUser, db: DBSession, incident: IncidentCreate):
    return await create_incident(current_user.id,db,incident)
