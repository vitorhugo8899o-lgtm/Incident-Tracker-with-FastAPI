from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.schemas.custom_schema import IncidentPriority, IncidentStatus

if TYPE_CHECKING:
    from app.models.incident_history_models import IncidentHistory
    from app.models.users_models import User


class Incident(Base):
    __tablename__ = 'incidents'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[IncidentStatus] = mapped_column(
        SAEnum(IncidentStatus, name='incident,status,enum'),
        default=IncidentStatus.open,
        nullable=False,
    )
    priority: Mapped[IncidentPriority] = mapped_column(
        SAEnum(IncidentPriority, name='incident,priority,enum'), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    creator_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False
    )

    technician_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id'), nullable=True
    )

    creator: Mapped["User"] = relationship(
        foreign_keys=[creator_id],
        back_populates="created_incidents"
    )

    technician: Mapped["User"] = relationship(
        foreign_keys=[technician_id],
        back_populates="assigned_incidents"
    )

    history: Mapped[list["IncidentHistory"]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan"
    )
