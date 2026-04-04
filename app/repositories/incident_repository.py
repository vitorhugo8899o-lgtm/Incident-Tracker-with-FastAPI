from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    OperationalError,
)

from app.api.v1.dependencies import CurrentUser, DBSession
from app.models.incident_models import Incident
from app.schemas.incident_schema import (
    FilterIncidents,
    IncidentCreate,
    IncidentPublic,
)


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


async def get_all_incident(user_role: str, db: DBSession, filter: FilterIncidents):

    if user_role == 'client':
        raise HTTPException(
            status_code=403,
            detail='Você não possui permisão para realizar essa acão'
        )

    q = select(Incident)

    filter_data = filter.model_dump(
        exclude={'limit', 'offset'},
        exclude_none=True
    )

    for field, value in filter_data.items():
        if field == 'creator':
            q = q.filter(Incident.creator_id == value)

        elif field in ['status', 'priority', 'created_at']: # noqa
            db_attribute = getattr(Incident, field)
            q = q.filter(db_attribute == value)

    if filter.limit > 0:
        q = q.limit(filter.limit)

    q = q.offset(filter.offset)

    result = await db.scalars(q)
    return result.all()


async def delete_incident(db: DBSession, id_incident: int, user_id: int):
    stmt = select(Incident).where(Incident.id == id_incident)

    result = await db.execute(stmt)

    incident = result.scalar_one_or_none()

    if not incident:
        return 'Chamdo não encontrado!'

    if incident.creator_id != user_id:
        raise HTTPException(
            status_code=403,
            detail='Você não possui permisão para realizar essa acão.'
        )

    try:
        await db.delete(incident)
        await db.commit()

        return incident
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f'{e}')
    except OperationalError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f'{e}')
    except InvalidRequestError as e:
        raise HTTPException(status_code=409, detail=f'{e}')
