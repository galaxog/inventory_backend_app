from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True
