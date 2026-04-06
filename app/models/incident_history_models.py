# app/models/incident_history_models.py
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.incident_models import Incident
    from app.models.users_models import User


class IncidentHistory(Base):
    __tablename__ = 'incident_history'

    id: Mapped[int] = mapped_column(primary_key=True)

    incident_id: Mapped[int] = mapped_column(
        ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False
    )

    action: Mapped[str] = mapped_column(String(255), nullable=False)

    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    incident: Mapped['Incident'] = relationship(back_populates='history')
    user: Mapped['User'] = relationship()
