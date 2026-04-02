from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IncidentStatus(str, Enum):
    open = 'open'
    in_progress = 'in_progress'
    resolved = 'resolved'
    closed = 'closed'


class IncidentPriority(str, Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'


class IncidentBase(BaseModel):
    title: str = Field(min_length=10, max_length=150)
    description: str = Field(min_length=15, max_length=2000)
    priority: IncidentPriority

    @field_validator('title', 'description')
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError(
                'O campo não pode conter apenas espaços em branco.'
            )
        return v.strip()


class IncidentCreate(IncidentBase):
    status: IncidentStatus = IncidentStatus.open


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=10, max_length=150)
    description: Optional[str] = Field(
        default=None, min_length=15, max_length=2000
    )
    status: Optional[IncidentStatus] = None
    priority: Optional[IncidentPriority] = None


class IncidentPublic(IncidentBase):
    id: int
    status: IncidentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
