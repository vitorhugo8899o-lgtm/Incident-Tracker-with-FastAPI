from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.v1.dependencies import CurrentUser, DBSession
from app.models.incident import Incident
from app.models.users import User
from app.repositories.users_repository import create_user, login
from app.schemas.user import Token, UserCreate, UserPublic

Form_data = Annotated[OAuth2PasswordRequestForm, Depends()]
router_users = APIRouter()


@router_users.post('/users', status_code=HTTPStatus.CREATED)
async def new_user(user: UserCreate, db: DBSession) -> UserPublic:
    return await create_user(user, db)


@router_users.post('/Login', status_code=HTTPStatus.OK, response_model=Token)
async def login_user(user: Form_data, db: DBSession, response: Response):
    token = await login(user, db)

    response.set_cookie(
        key='Login_info',
        value=token.access_token,
        max_age=60 * 60,
        httponly=True,
        secure=False,
    )

    response.headers["Cache-Control"] = "no-store"

    return token


@router_users.get('/user_incidents')
async def get_all_user_incidents(current_user: CurrentUser, db: DBSession):
    stmt = select(Incident).where(Incident.creator_id == current_user.id)
    result = await db.execute(stmt)
    incidents = result.scalars().all()

    return incidents


@router_users.get('/users/{id_user}')
async def get_user(id_user: int, db: DBSession):
    stmt = select(User).where(User.id == id_user)

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return 'Usuário não encontrado'

    if user.role != 'supervisor':
        raise HTTPException(
            status_code=409,
            detail='Você não possui permissão para realizar essa acão'
        )

    return UserPublic(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        creat_at=user.created_at
    )
