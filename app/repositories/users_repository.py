from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    OperationalError,
    
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.api.v1.dependencies import get_db
from app.models.users import User
from app.schemas.user import UserCreate, UserPublic, UserLogin, Token
from app.core.security import hash_password, verify_password, create_token


DBSession = Annotated[AsyncSession, Depends(get_db)]
Form_data = Annotated[OAuth2PasswordRequestForm, Depends()]

async def user_exists(user: UserCreate, db: DBSession) -> User | bool:
    """Busca o usuário no banco de dados, no caso de busca para login ele realiza uma busca somente para o email, caso contrário busca pelo email e cpf retornando o objeto do banco de dados ou um bool"""
    
    if type(user) == str:
        stmt = select(User).where((User.email == user)) 


    elif type(user) == UserCreate:
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



async def login(user_data:OAuth2PasswordRequestForm, db:DBSession):
    user = await user_exists(user_data.username,db)

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    access_token = create_token(data={'sub': user.id})

    token = Token(access_token=access_token, token_type='Bearer')

    return token