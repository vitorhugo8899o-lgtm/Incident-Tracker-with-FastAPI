
from fastapi import APIRouter, HTTPException
from http import HTTPStatus

from app.api.v1.dependencies import CurrentUser, DBSession
from app.repositories.technician import uptade_incident, disable_worker
from app.repositories.users_repository import user_exists

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


@router_technician.post('/disable/{id_user}',status_code=HTTPStatus.OK)
async def supervisor_disable_users(current_user: CurrentUser, db:DBSession, id_user:int):
    user = await user_exists(current_user.email,db)

    if user.role != 'supervisor':
        raise HTTPException(
            status_code=403,
            detail='Você não possui permissão para realizar essa acão.'
        )
    
    return await disable_worker(id_user,db)

