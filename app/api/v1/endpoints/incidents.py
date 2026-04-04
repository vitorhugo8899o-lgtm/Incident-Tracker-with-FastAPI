from fastapi import APIRouter, Query
from http import HTTPStatus
from typing import Annotated
from app.api.v1.dependencies import CurrentUser, DBSession
from app.repositories.incident_repository import create_incident
from app.schemas.incident import IncidentCreate
from app.schemas.incident import IncidentUpdate, FilterIncidents
from app.repositories.incident_repository import get_all_incident

router_incident = APIRouter()


@router_incident.post('/incidents')
async def incident_create(
    current_user: CurrentUser,
    db: DBSession,
    incident: IncidentCreate
):
    return await create_incident(current_user, db, incident)


@router_incident.get('/incidents',status_code=HTTPStatus.OK)
async def fields_incides(
    current_user: CurrentUser,
    db: DBSession,
    filter: Annotated[FilterIncidents, Query()]
):
    return await get_all_incident(db,filter)
