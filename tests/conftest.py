from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.v1.dependencies import get_db
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models.incident_models import Incident
from app.models.users_models import User

TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(autouse=True)
def bypass_lifespan_db_check():
    with patch('app.main.check_database_connection') as mock_check:
        mock_check.return_value = None
        yield mock_check


@pytest_asyncio.fixture(scope='function')
async def init_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope='function')
async def db_session(init_test_db):
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope='function')
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope='function')
async def user(db_session):
    raw_password = 'Senha12@#'

    user = User(
        cpf='82965919104',
        email='emailfoda@gmail.com',
        password=hash_password(raw_password),
        role='CLIENT',
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user, raw_password


@pytest_asyncio.fixture(scope='function')
async def tech(db_session):
    raw_password = 'Senha12@#'

    tech = User(
        cpf='03605029116',
        email='emailfodatech@gmail.com',
        password=hash_password(raw_password),
        role='TECHNICIAN',
    )

    db_session.add(tech)
    await db_session.commit()
    await db_session.refresh(tech)

    return tech, raw_password


@pytest_asyncio.fixture(scope='function')
async def supervisor(db_session):

    raw_password = 'Senha12@#'

    tech = User(
        cpf='05209680185',
        email='emailfodatech@gmail.com',
        password=hash_password(raw_password),
        role='supervisor',
    )

    db_session.add(tech)
    await db_session.commit()
    await db_session.refresh(tech)

    return tech, raw_password


@pytest_asyncio.fixture(scope='function')
async def user_disable(db_session):
    raw_password = 'Senha12@#'

    user = User(
        cpf=' 75365731972',
        email='emailfoda2@gmail.com',
        password=hash_password(raw_password),
        is_active=False,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user, raw_password


@pytest_asyncio.fixture(scope='function')
async def token_user(client, user):
    user, raw_password = user

    data = {'username': user.email, 'password': f'{raw_password}'}

    response = await client.post('/api/v1/Login', data=data)

    return response.json()['access_token']


@pytest_asyncio.fixture(scope='function')
async def token_tech(client, tech):
    tech, raw_password = tech

    data = {'username': tech.email, 'password': f'{raw_password}'}

    response = await client.post('/api/v1/Login', data=data)

    return response.json()['access_token']


@pytest_asyncio.fixture(scope='function')
async def token_supervisor(client, supervisor):
    supervisor, raw_password = supervisor

    data = {'username': supervisor.email, 'password': f'{raw_password}'}

    response = await client.post('/api/v1/Login', data=data)

    return response.json()['access_token']


@pytest_asyncio.fixture(scope='function')
async def incident_user(user, db_session):

    user, raw = user

    incident = Incident(
        title='Titulo foda',
        description='descrição elaborada',
        priority='low',
        creator_id=user.id,
    )

    db_session.add(incident)
    await db_session.commit()
    await db_session.refresh(incident)

    return incident


@pytest_asyncio.fixture(scope='function')
async def incident2_user(user, db_session):

    user, raw = user

    incident = Incident(
        title='Titulo foda2',
        description='descrição elaborada2',
        priority='low',
        creator_id=user.id,
    )

    db_session.add(incident)
    await db_session.commit()
    await db_session.refresh(incident)

    return incident


@pytest_asyncio.fixture(scope='function')
async def incident_closed(user, db_session):

    user, raw = user

    incident = Incident(
        title='Titulo foda',
        description='descrição elaborada',
        priority='low',
        creator_id=user.id,
        status='closed',
    )

    db_session.add(incident)
    await db_session.commit()
    await db_session.refresh(incident)

    return incident
