from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)

class UserInDB(UserBase):
    full_name: Optional[str]
    hashed_password: str  # Никогда не храним пароли в чистом виде!