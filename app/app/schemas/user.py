from fastapi import Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: int
    username: str
    is_admin: bool
    is_active: bool


class UserCreate(BaseModel):
    username: str = Query(..., max_length=60)
    password: str = Query(..., max_length=20, min_length=8)
    is_admin: Optional[bool] = False
    is_active: Optional[bool]


class UserUpdate(UserCreate):
    username: Optional[str]
    password: Optional[str]


class UserRetrieve(User):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
