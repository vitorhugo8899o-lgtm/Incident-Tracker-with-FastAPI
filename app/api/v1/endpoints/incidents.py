from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db

router_incident = APIRouter()
db = Annotated[AsyncSession, Depends(get_db)]


@router_incident.post('')
async def incident_create():
    pass
