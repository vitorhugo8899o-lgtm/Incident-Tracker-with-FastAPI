from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    OperationalError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db
from app.models.users import User
from app.schemas.user import UserCreate, UserPublic
from app.core.security import hash_password

DBSession = Annotated[AsyncSession, Depends(get_db)]


async def user_exists(user: UserCreate, db: DBSession) -> User | bool:
    stmt = select(User).where(
    (User.email == user.email) | (User.cpf == user.cpf)
)

    exist = await db.execute(stmt)

    result = exist.scalar_one_or_none()

    if not result:
        return False

    return result


async def create_user(
    user: UserCreate, db: DBSession
) -> UserPublic:
    user_already_exists = await user_exists(user, db)
    if user_already_exists:
        raise HTTPException(status_code=409, detail="Email ou CPF já cadastrado no sistema.")

    new_user = User(cpf=user.cpf, email=user.email, password=hash_password(user.password))


    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)

        return UserPublic(
            id=new_user.id,
            email=new_user.email,
            creat_at=new_user.created_at
        )
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f'{e}')
    except OperationalError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f'{e}')
    except InvalidRequestError as e:
        raise HTTPException(status_code=409, detail=f'{e}')
