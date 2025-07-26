from .services.auth import get_current_user
from typing import Optional
from .models.user import UserInDB
from fastapi import Depends

# Для совместимости со старым кодом
__all__ = ['get_current_user']

# Добавьте эту функцию для необязательной аутентификации
async def get_optional_user(current_user: Optional[UserInDB] = Depends(get_current_user)):
    return current_user