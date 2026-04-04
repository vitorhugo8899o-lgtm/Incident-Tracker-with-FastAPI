from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.schemas.custom_schema import UserRole

if TYPE_CHECKING:
    from app.models.incident_models import Incident


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name='user=role=enum'),
        default=UserRole.CLIENT,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    created_incidents: Mapped[list["Incident"]] = relationship(
        foreign_keys="[Incident.creator_id]",
        back_populates="creator"
    )

    assigned_incidents: Mapped[list["Incident"]] = relationship(
        foreign_keys="[Incident.technician_id]",
        back_populates="technician"
    )
