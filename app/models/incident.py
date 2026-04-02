from sqlalchemy import String, Text, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.schemas.incident import IncidentStatus, IncidentPriority
from datetime import datetime
from app.db.base import Base

class Incident(Base):
    __tablename__ = 'incidents'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text(2000), nullable=False)
    status: Mapped[SAEnum] = mapped_column(
        SAEnum(IncidentStatus,names='IncidentStatusEnum'),
        default=IncidentStatus.OPEN, 
        nullable=False
    )
    priority: Mapped[SAEnum] = mapped_column(
        SAEnum(IncidentPriority,names='IncidentPriotityEnum'),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), nullable=False
    ) 