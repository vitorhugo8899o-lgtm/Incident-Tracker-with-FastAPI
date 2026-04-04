from fastapi import HTTPException
from sqlalchemy import select

from app.api.v1.dependencies import CurrentUser, DBSession
from app.models.incident import Incident
from app.models.users import User
from app.schemas.incident import IncidentUpdate
from sqlalchemy.exc import IntegrityError, OperationalError, InvalidRequestError

async def is_technician(techinician_id: int, db: DBSession):
    stmt = select(User).where(User.id == techinician_id)

    result = await db.execute(stmt)

    user = result.scalar_one_or_none()

    if user.role == 'client':
        raise HTTPException(
            status_code=409,
            detail='Você não possui permisão para realizar essa acão'
        )

    return user


async def uptade_incident(
        techinician: CurrentUser,
        db: DBSession,
        id_incident: int,
        uptade_incident: IncidentUpdate
):
    stmt = select(Incident).where(Incident.id == id_incident)

    result = await db.execute(stmt)

    incident = result.scalar_one_or_none()

    if not incident:
        return None

    elif (incident.status == 'resolved') | (incident.status == 'closed'):
        return 'Chamado já foi resolvido'

    await is_technician(techinician.id, db)

    incident.status = uptade_incident.status
    incident.priority = uptade_incident.priority
    incident.technician_id = techinician.id

    await db.commit()
    await db.refresh(incident)

    return incident


async def disable_worker(id_user:int,db: DBSession):
    try:
        stmt = select(User).where(User.id == id_user)

        result = await db.execute(stmt)

        user = result.scalar_one_or_none()

        if not user:
            return None
        
        user.is_active = False

        await db.commit()

        return user
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f'{e}')
    except OperationalError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f'{e}')
    except InvalidRequestError as e:
        raise HTTPException(status_code=409, detail=f'{e}')

