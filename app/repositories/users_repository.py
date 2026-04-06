import logging
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    OperationalError,
)

from app.api.v1.dependencies import CurrentUser, DBSession
from app.core.security import create_token, hash_password, verify_password
from app.models.users_models import User
from app.schemas.user_schema import Token, UserCreate

Form_data = Annotated[OAuth2PasswordRequestForm, Depends()]
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def user_exists(user: UserCreate | str, db: DBSession) -> User | bool:
    """Busca o usuário no banco de dados, no caso de busca para login ele realiza uma busca somente para o email, caso contrário busca pelo email e cpf retornando o objeto do banco de dados ou um bool"""  # noqa

    # Email sendo passado no login como str
    if type(user) is str:
        stmt = select(User).where((User.email == user))

    # criacão de usuário
    elif type(user) is UserCreate:
        stmt = select(User).where(
            (User.email == user.email) | (User.cpf == user.cpf)
        )

    exist = await db.execute(stmt)

    result = exist.scalar_one_or_none()

    if not result:
        return None

    if result.is_active is False:
        raise HTTPException(status_code=409, detail='Usuário desativado')

    return result


async def create_user(user: UserCreate, db: DBSession) -> User:
    user_already_exists = await user_exists(user, db)
    if user_already_exists:
        raise HTTPException(
            status_code=409, detail='Email ou CPF já cadastrado no sistema.'
        )

    new_user = User(
        cpf=user.cpf, email=user.email, password=hash_password(user.password)
    )

    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)

        return new_user
    except IntegrityError as e:  # pragma: no cover
        await db.rollback()  # pragma: no cover
        raise HTTPException(status_code=409, detail=f'{e}')  # pragma: no cover
    except OperationalError as e:  # pragma: no cover
        await db.rollback()  # pragma: no cover
        raise HTTPException(status_code=409, detail=f'{e}')  # pragma: no cover
    except InvalidRequestError as e:  # pragma: no cover
        raise HTTPException(status_code=409, detail=f'{e}')  # pragma: no cover


async def login(user_data: OAuth2PasswordRequestForm, db: DBSession) -> Token:
    user = await user_exists(user_data.username, db)

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail='Credenciais inválidas')

    access_token = create_token(data={'sub': str(user.id)})

    token = Token(access_token=access_token, token_type='Bearer')

    return token


async def disable_account(
    current_user: CurrentUser, db: DBSession
) -> str | None:  # noqa
    user = await user_exists(current_user.email, db)

    if not user:  # pragma: no cover
        return None

    if user.role != 'client':
        raise HTTPException(
            status_code=403,
            detail='Você não possui permissão para realizar essa acão.',
        )

    user.is_active = False

    await db.commit()
    return 'Usuário desabilitado'
