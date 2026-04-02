from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db

db = Annotated[AsyncSession, Depends(get_db)]


async def create_incident():
    pass
