from typing import Annotated
from http import HTTPStatus
from typing import Optional
from fastapi import APIRouter, Depends, Cookie, Header
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db
from app.repositories.users_repository import create_user,login
from app.schemas.user import UserCreate, UserPublic, Token
from fastapi.security import OAuth2PasswordRequestForm

db = Annotated[AsyncSession, Depends(get_db)]
Form_data = Annotated[OAuth2PasswordRequestForm, Depends()]
router_users = APIRouter()


@router_users.post('/users',status_code=HTTPStatus.CREATED)
async def new_user(user: UserCreate,db: db) -> UserPublic:
    return await create_user(user, db)


@router_users.post('/Login',status_code=HTTPStatus.OK, response_model=Token)
async def login_user(user:Form_data,db:db, response: Response):
    token =  await login(user,db)

    response.set_cookie(
        key='Login_info',
        value=token,
        max_age=60 * 60,
        httponly=True,
        secure=False,
    )

    response.headers["Cache-Control"] = "no-store"

    return token
