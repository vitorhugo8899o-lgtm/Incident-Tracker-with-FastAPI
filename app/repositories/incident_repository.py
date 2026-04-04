from fastapi import HTTPException
from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    OperationalError,
)
from sqlalchemy import select

from app.api.v1.dependencies import CurrentUser, DBSession
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentPublic, FilterIncidents


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
    

async def get_all_incident(db: DBSession, filter: FilterIncidents):
    q = select(Incident)

    filter_data = filter.model_dump(
        exclude={'limit', 'offset'},
        exclude_none=True 
    )

    for field, value in filter_data.items():
        if field == 'creator':
            q = q.filter(Incident.creator_id == value)
            
        elif field in ['status', 'priority', 'created_at']:
            db_attribute = getattr(Incident, field)
            q = q.filter(db_attribute == value)

    if filter.limit > 0:
        q = q.limit(filter.limit)
        
    q = q.offset(filter.offset)

    result = await db.scalars(q)
    return result.all()