from app.api.v1.dependencies import CurrentUser, DBSession
from app.schemas.incident import IncidentCreate, IncidentPublic
from app.models.incident import Incident
from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    OperationalError,
    
)
from fastapi import HTTPException

async def create_incident(
        id_user: int, 
        db: DBSession,
        incident: IncidentCreate
) -> IncidentPublic:
    new_incident = Incident(
        title = incident.title,
        description = incident.description,
        priority = incident.priority,
        status = incident.status,
        creator_id = id_user
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
