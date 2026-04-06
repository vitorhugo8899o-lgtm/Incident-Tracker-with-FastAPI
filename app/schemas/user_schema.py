import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from validate_docbr import CPF

from app.schemas.custom_schema import IncidentPriority, IncidentStatus

cpf_validator = CPF()


class UserCreate(BaseModel):
    email: EmailStr = Field(max_length=40)
    password: str = Field(min_length=8, max_length=128)
    cpf: str = Field(pattern=r'^\d{11}$')

    @field_validator('password')
    def validate_password(cls, v: str):
        num = 8
        if len(v) < num:
            raise ValueError('Senha deve ter no mínimo 8 caracteres')

        if not re.search(r'[a-z]', v):
            raise ValueError('Deve conter letra minúscula')

        if not re.search(r'[A-Z]', v):
            raise ValueError('Deve conter letra maiúscula')

        if not re.search(r'\d', v):
            raise ValueError('Deve conter número')

        if not re.search(r'[@$!%*?&]', v):
            raise ValueError('Deve conter caractere especial')

        return v

    @field_validator('cpf')
    def validate_cpf(cls, v):
        if not cpf_validator.validate(v):
            raise ValueError('CPF inválido')
        return v


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    cpf: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=40)
    password: str

    @field_validator('password')
    def validate_password(cls, v: str):
        num = 8
        if len(v) < num:
            raise ValueError('Senha deve ter no mínimo 8 caracteres')

        if not re.search(r'[a-z]', v):
            raise ValueError('Deve conter letra minúscula')

        if not re.search(r'[A-Z]', v):
            raise ValueError('Deve conter letra maiúscula')

        if not re.search(r'\d', v):
            raise ValueError('Deve conter número')

        if not re.search(r'[@$!%*?&]', v):
            raise ValueError('Deve conter caractere especial')

        return v


class Token(BaseModel):
    access_token: str
    token_type: str


class UserIncidentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=10, max_length=150)
    description: Optional[str] = Field(
        default=None, min_length=15, max_length=2000
    )
    status: Optional[IncidentStatus] = None
    priority: Optional[IncidentPriority] = None
