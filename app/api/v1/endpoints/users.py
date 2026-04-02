from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db
from app.repositories.users_repository import create_user
from app.schemas.user import UserCreate, UserPublic

db = Annotated[AsyncSession, Depends(get_db)]

router_users = APIRouter()


@router_users.post('/users')
async def new_user(
    user: UserCreate,
    db: db
) -> UserPublic:
    return await create_user(user, db)
