from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.v1.dependencies import CurrentUser, DBSession
from app.repositories.incident_repository import (
    create_incident,
    delete_incident,
    get_all_incident,
)
from app.schemas.incident_schema import (
    FilterIncidents,
    IncidentCreate,
    IncidentDeleteReturn,
)

router_incident = APIRouter()


@router_incident.post('/incidents', status_code=HTTPStatus.CREATED)
async def incident_create(
    current_user: CurrentUser,
    db: DBSession,
    incident: IncidentCreate
):
    return await create_incident(current_user, db, incident)


@router_incident.delete(
        '/incidents/{id_incident}',
        status_code=HTTPStatus.OK,
        response_model=IncidentDeleteReturn | str
)
async def user_delete_incident(
    user: CurrentUser,
    db: DBSession,
    id_incident: int
):
    return await delete_incident(db, id_incident, user.id)


@router_incident.get('/incidents', status_code=HTTPStatus.OK)
async def fields_incides(
    current_user: CurrentUser,
    db: DBSession,
    filter: Annotated[FilterIncidents, Query()]
):
    return await get_all_incident(current_user.role, db, filter)
