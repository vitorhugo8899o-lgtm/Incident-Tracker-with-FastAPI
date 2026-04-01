from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from app.schemas.incident import IncidentStatus, IncidentPriority
from enum import Enum
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Incident(Base):
    __table__ = 'incidents'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text(2000), nullable=False)
    status: Mapped[Enum] = mapped_column(
        Enum(IncidentStatus,names='IncidentStatusEnum'), 
        nullable=False
    )
    priority: Mapped[Enum] = mapped_column(
        Enum(IncidentPriority,names='IncidentPriotityEnum'),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), nullable=False
    ) 