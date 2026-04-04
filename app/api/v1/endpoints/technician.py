
from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.v1.dependencies import CurrentUser, DBSession
from app.models.users_models import User
from app.repositories.technician_repositories import (
    disable_worker,
    uptade_incident,
)
from app.repositories.users_repository import user_exists
from app.schemas.incident_schema import IncidentUpdate
from app.schemas.user_schema import UserPublic

router_technician = APIRouter()


@router_technician.put('/incident/{id_incident}')
async def resolve_incident(
    user: CurrentUser,
    db: DBSession,
    id_incident: int,
    update: IncidentUpdate
):

    return await uptade_incident(user, db, id_incident, update)


@router_technician.post('/disable/{id_user}', status_code=HTTPStatus.OK)
async def supervisor_disable_users(
    current_user: CurrentUser,
    db: DBSession,
    id_user: int
):
    user = await user_exists(current_user.email, db)

    if user.role != 'supervisor':
        raise HTTPException(
            status_code=403,
            detail='Você não possui permissão para realizar essa acão.'
        )

    return await disable_worker(id_user, db)


@router_technician.get(
        '/users/{id_user}',
        status_code=HTTPStatus.OK,
        response_model=UserPublic
)
async def supervisor_get_user(
    id_user: int,
    db: DBSession,
    current_user: CurrentUser
):
    stmt = select(User).where(User.id == id_user)

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return 'Usuário não encontrado'

    if current_user.role != 'supervisor':
        raise HTTPException(
            status_code=403,
            detail='Você não possui permissão para realizar essa acão'
        )

    return user
