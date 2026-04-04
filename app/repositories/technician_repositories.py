from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    OperationalError,
)
from sqlalchemy.orm import joinedload

from app.api.v1.dependencies import CurrentUser, DBSession
from app.models.incident_history_models import IncidentHistory
from app.models.incident_models import Incident
from app.models.users_models import User
from app.schemas.incident_schema import IncidentStatus, IncidentUpdate


async def is_technician(techinician_id: int, db: DBSession) -> User:
    stmt = select(User).where(User.id == techinician_id)

    result = await db.execute(stmt)

    user = result.scalar_one_or_none()

    if user.role == 'client':
        raise HTTPException(
            status_code=403,
            detail='Você não possui permisão para realizar essa acão'
        )

    return user


async def update_incident(
    technician: CurrentUser,
    db: DBSession,
    id_incident: int,
    update_data: IncidentUpdate
) -> Incident:
    stmt = (
        select(Incident)
        .options(
            joinedload(Incident.creator).load_only(User.id, User.email, User.role),
            joinedload(Incident.history)
        )
        .where(Incident.id == id_incident)
    )

    result = await db.execute(stmt)
    incident = result.unique().scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail="Incidente não encontrado")

    if incident.status in [IncidentStatus.resolved, IncidentStatus.closed]:
        raise HTTPException(status_code=400, detail="Chamado já finalizado")

    await is_technician(technician.id, db)

    changes = []
    if update_data.status and update_data.status != incident.status:
        changes.append(f"Status: {incident.status} -> {update_data.status}")
        incident.status = update_data.status

    if update_data.priority and update_data.priority != incident.priority:
        changes.append(f"Prioridade: {incident.priority} -> {update_data.priority}")
        incident.priority = update_data.priority

    if not changes and not update_data.comment:
        return incident

    incident.technician_id = technician.id

    new_history = IncidentHistory(
        incident_id=incident.id,
        user_id=technician.id,
        action=" | ".join(changes) if changes else "Atualização de dados/comentário",
        comment=update_data.comment
    )

    db.add(new_history)

    try:
        await db.commit()
        await db.refresh(incident)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar alterações: {e}")

    return incident


async def disable_worker(id_user: int, db: DBSession) -> User | None:
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
