import io
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from fastapi import HTTPException
from sqlalchemy import and_, select
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


async def is_technician(techinician_id: int, db: DBSession) -> User | None:
    stmt = select(User).where(User.id == techinician_id)

    result = await db.execute(stmt)

    user = result.scalar_one_or_none()

    if user.role == 'client':
        raise HTTPException(
            status_code=403,
            detail='Você não possui permisão para realizar essa acão',
        )

    return user


async def update_incident(
    technician: CurrentUser,
    db: DBSession,
    id_incident: int,
    update_data: IncidentUpdate,
) -> Incident:
    stmt = (
        select(Incident)
        .options(
            joinedload(Incident.creator).load_only(
                User.id, User.email, User.role
            ),
            joinedload(Incident.history),
        )
        .where(Incident.id == id_incident)
    )

    result = await db.execute(stmt)
    incident = result.unique().scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail='Incidente não encontrado')

    if incident.status in [IncidentStatus.resolved, IncidentStatus.closed]:  # noqa
        raise HTTPException(status_code=409, detail='Chamado já finalizado')

    await is_technician(technician.id, db)

    changes = []
    if update_data.status and update_data.status != incident.status:
        changes.append(f'Status: {incident.status} -> {update_data.status}')
        incident.status = update_data.status

    if update_data.priority and update_data.priority != incident.priority:
        changes.append(
            f'Prioridade: {incident.priority} -> {update_data.priority}'
        )
        incident.priority = update_data.priority

    if not changes and not update_data.comment:
        return incident

    incident.technician_id = technician.id

    new_history = IncidentHistory(
        incident_id=incident.id,
        user_id=technician.id,
        action=' | '.join(changes)
        if changes
        else 'Atualização de dados/comentário',  # noqa
        comment=update_data.comment,
    )

    db.add(new_history)

    try:
        await db.commit()
        await db.refresh(incident)
    except Exception as e:  # pragma: no cover
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f'Erro ao salvar alterações: {e}'
        )

    return incident


async def disable_worker(id_user: int, db: DBSession) -> User | None:
    try:
        stmt = select(User).where(User.id == id_user)

        result = await db.execute(stmt)

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado, verifique o ID se digitou um ID valído."
            )
        elif user.is_active is False:
            raise HTTPException(
                status_code=409,
                detail="Esse usuário já está desabilitado"
            )

        user.is_active = False

        await db.commit()

        return user
    except IntegrityError as e:  # pragma: no cover
        await db.rollback()
        raise HTTPException(status_code=409, detail=f'{e}')
    except OperationalError as e:  # pragma: no cover
        await db.rollback()
        raise HTTPException(status_code=409, detail=f'{e}')
    except InvalidRequestError as e:  # pragma: no cover
        raise HTTPException(status_code=409, detail=f'{e}')


async def get_history(id_incident: int, db: DBSession) -> IncidentHistory:
    stmt = select(Incident).where(Incident.id == id_incident)

    result = await db.execute(stmt)

    incident = result.scalar_one_or_none()

    if not incident:
        return None

    return incident


async def get_technician_metrics_data(db: DBSession, technician_id: int):
    thirty_days_ago = datetime.now() - timedelta(days=30)

    stmt = select(Incident).where(
        and_(
            Incident.technician_id == technician_id,
            Incident.status.in_([
                IncidentStatus.resolved,
                IncidentStatus.closed,
            ]),
            Incident.created_at >= thirty_days_ago,
        )
    )

    result = await db.execute(stmt)
    return result.scalars().all()


def generate_metrics_chart(incidents):
    if not incidents:
        return None

    data = [{'priority': i.priority.value} for i in incidents]
    df = pd.DataFrame(data)
    priority_counts = df['priority'].value_counts()

    colors_map = {'high': '#ef4444', 'medium': '#f59e0b', 'low': '#10b981'}
    current_colors = [colors_map.get(p, '#3b82f6') for p in priority_counts.index]

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#11141d') # Cor do card no React
    ax.set_facecolor('#11141d')

    bars = priority_counts.plot(kind='bar', color=current_colors, ax=ax, width=0.6)

    plt.title('Chamados Resolvidos (Últimos 30 dias)', fontsize=14, pad=20, color='#ffffff')
    plt.xticks(rotation=0, color='#9ca3af') 
    plt.yticks(color='#9ca3af')
    
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    ax.grid(axis='y', linestyle='--', alpha=0.1)

    for bar in bars.patches:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.1,
            int(bar.get_height()),
            ha='center', va='bottom', color='white', fontweight='bold'
        )

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()
    return buf


async def get_tech_history(user_id: int, db: DBSession):
    tech = await is_technician(user_id, db)

    stmt = select(IncidentHistory).where(IncidentHistory.user_id == tech.id)

    result = await db.execute(stmt)

    history = result.scalars().all()

    if not history:
        return None

    return history
