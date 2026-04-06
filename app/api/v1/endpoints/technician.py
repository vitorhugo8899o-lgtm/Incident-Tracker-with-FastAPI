from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.api.v1.dependencies import CurrentUser, DBSession
from app.models.users_models import User
from app.repositories.technician_repositories import (
    disable_worker,
    generate_metrics_chart,
    get_tech_history,
    get_technician_metrics_data,
    update_incident,
)
from app.repositories.users_repository import user_exists
from app.schemas.incident_schema import IncidentPublic, IncidentUpdate
from app.schemas.user_schema import UserPublic

router_technician = APIRouter()


@router_technician.put(
    '/incident/{id_incident}',
    status_code=HTTPStatus.OK,
    response_model=IncidentPublic,
)
async def resolve_incident(
    user: CurrentUser, db: DBSession, id_incident: int, update: IncidentUpdate
):

    return await update_incident(user, db, id_incident, update)


@router_technician.put(
    '/disable/user/or/worker/{id_user}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic | None,
)
async def supervisor_disable_users(
    current_user: CurrentUser, db: DBSession, id_user: int
):
    user = await user_exists(current_user.email, db)

    if user.role != 'supervisor':
        raise HTTPException(
            status_code=403,
            detail='Você não possui permissão para realizar essa acão.',
        )

    return await disable_worker(id_user, db)


@router_technician.get(
    '/users/{id_user}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic | None,
)
async def supervisor_get_user(
    id_user: int, db: DBSession, current_user: CurrentUser
):
    if current_user.role != 'supervisor':
        raise HTTPException(
            status_code=403,
            detail='Você não possui permissão para realizar essa acão',
        )
    stmt = select(User).where(User.id == id_user)

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return None

    return user


@router_technician.get('/metrics/{tech_id}')
async def technical_metrics_resolved(tech_id: int, db: DBSession):
    incidents = await get_technician_metrics_data(db, tech_id)
    chart_buffer = generate_metrics_chart(incidents)

    if not chart_buffer:
        return {'detail': 'Nenhum dado encontrado para o período.'}

    return StreamingResponse(chart_buffer, media_type='image/png')


@router_technician.get('/tech/history_incident/', status_code=HTTPStatus.OK)
async def history_tech_incidents(user: CurrentUser, db: DBSession):
    return await get_tech_history(user.id, db)
