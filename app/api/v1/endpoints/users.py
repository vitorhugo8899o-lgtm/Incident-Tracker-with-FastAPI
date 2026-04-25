from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.v1.dependencies import CurrentUser, DBSession
from app.models.incident_models import Incident
from app.repositories.users_repository import (
    create_user,
    disable_account,
    login,
)
from app.schemas.user_schema import Token, UserCreate, UserPublic

Form_data = Annotated[OAuth2PasswordRequestForm, Depends()]
router_users = APIRouter()


@router_users.post(
    '/users', status_code=HTTPStatus.CREATED, response_model=UserPublic
)
async def new_user(user: UserCreate, db: DBSession):
    return await create_user(user, db)


@router_users.post('/Login', status_code=HTTPStatus.OK, response_model=Token)
async def login_user(user: Form_data, db: DBSession, response: Response):
    token, info = await login(user, db)

    response.set_cookie(
        key='Login_info',
        value=token.access_token,
        max_age=60 * 60,
        httponly=True,
        secure=False,
    )

    response.set_cookie(
        key='Info_Role',
        value=info,
        max_age=60 * 60,
        httponly=True,
        secure=False,
    )

    response.headers['Cache-Control'] = 'no-store'

    return token


@router_users.get('/user_incidents', status_code=HTTPStatus.OK)
async def get_all_user_incidents(current_user: CurrentUser, db: DBSession):
    stmt = select(Incident).where(Incident.creator_id == current_user.id)
    result = await db.execute(stmt)
    incidents = result.scalars().all()

    return incidents


@router_users.post('/users/disable', status_code=HTTPStatus.OK)
async def disable_user(current_user: CurrentUser, db: DBSession) -> str:
    return await disable_account(current_user, db)
