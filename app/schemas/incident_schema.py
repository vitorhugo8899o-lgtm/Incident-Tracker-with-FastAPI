from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.custom_schema import IncidentPriority, IncidentStatus


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
    status: Optional[IncidentStatus] = None
    priority: Optional[IncidentPriority] = None


class IncidentPublic(IncidentBase):
    id: int
    status: IncidentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreatorSchema(BaseModel):
    id: int
    email: EmailStr
    role: str


class IncidentDeleteReturn(IncidentBase):
    id: int
    creator: CreatorSchema


class FilterIncidents(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=0, default=0)
    status: IncidentStatus | None = Field(default=None)
    priority: IncidentPriority | None = Field(default=None)
    created_at: datetime | None = Field(default=None)
    creator: int | None = Field(default=None)


class IncidentList(BaseModel):
    incidents: list[IncidentPublic]
