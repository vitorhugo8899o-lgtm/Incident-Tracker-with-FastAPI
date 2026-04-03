from typing import Annotated
from http import HTTPStatus
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from app.api.v1.dependencies import CurrentUser, DBSession
from app.repositories.users_repository import create_user,login
from app.schemas.user import UserCreate, UserPublic, Token
from fastapi.security import OAuth2PasswordRequestForm
from app.models.incident import Incident
from sqlalchemy import select

Form_data = Annotated[OAuth2PasswordRequestForm, Depends()]
router_users = APIRouter()


@router_users.post('/users',status_code=HTTPStatus.CREATED)
async def new_user(user: UserCreate,db: DBSession) -> UserPublic:
    return await create_user(user, db)


@router_users.post('/Login',status_code=HTTPStatus.OK, response_model=Token)
async def login_user(user:Form_data,db:DBSession, response: Response):
    token =  await login(user,db)

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