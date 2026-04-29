import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text

from app.api.v1.router import api_router
from app.db.session import engine


async def check_database_connection():  # pragma: no cover
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
    except Exception as e:
        raise ConnectionError(f'Falha de conexão com o banco de dados: {e}')


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover

    try:
        await check_database_connection()

    except Exception:
        sys.exit(1)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web-incident-tracker.vercel.app/",
        'https://web-incident-tracker-kxaekfljr-vitor-hugos-projects-411fbd87.vercel.app',"https://web-incident-tracker-git-main-vitor-hugos-projects-411fbd87.vercel.app/"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router, prefix='/api/v1')
