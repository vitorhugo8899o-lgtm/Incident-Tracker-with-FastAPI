
from fastapi import APIRouter

from app.api.v1.dependencies import CurrentUser, DBSession
from app.repositories.technician import uptade_incident
from app.schemas.incident import IncidentUpdate

router_technician = APIRouter()


@router_technician.put('/incident/{id_incident}')
async def resolve_incident(
    user: CurrentUser,
    db: DBSession,
    id_incident: int,
    update: IncidentUpdate
):

    return await uptade_incident(user, db, id_incident, update)
