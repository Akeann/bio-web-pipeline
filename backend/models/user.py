from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from uuid import UUID

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None
    country: Optional[str] = None
    role: Optional[str] = None
    institution_type: Optional[str] = None

class UserInDB(UserBase):
    id: UUID
    full_name: Optional[str] = None
    country: Optional[str] = None
    role: Optional[str] = None
    institution_type: Optional[str] = None
    disabled: Optional[bool] = False
    registration_date: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp of registration"
    )

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None