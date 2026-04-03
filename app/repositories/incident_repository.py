from fastapi import HTTPException
from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    OperationalError,
)

from app.api.v1.dependencies import CurrentUser, DBSession
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentPublic


async def create_incident(
        user: CurrentUser,
        db: DBSession,
        incident: IncidentCreate
) -> IncidentPublic:
    new_incident = Incident(
        title=incident.title,
        description=incident.description,
        priority=incident.priority,
        status=incident.status,
        creator=user
    )

    db.add(new_incident)

    try:
        await db.commit()
        await db.refresh(new_incident)

        return IncidentPublic(
            id=new_incident.id,
            title=new_incident.title,
            description=new_incident.description,
            status=new_incident.status,
            priority=new_incident.priority,
            created_at=new_incident.created_at
        )

    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f'{e}')
    except OperationalError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f'{e}')
    except InvalidRequestError as e:
        raise HTTPException(status_code=409, detail=f'{e}')
