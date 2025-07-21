from datetime import timedelta
from typing import Dict, Any
import os

# Безопасность
# SECRET_KEY = "your-secret-key"  # В продакшене замените на os.getenv("SECRET_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Типы для аннотаций
UserDict = Dict[str, Any]
UsersDB = Dict[str, UserDict]