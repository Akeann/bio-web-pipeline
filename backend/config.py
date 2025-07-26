from datetime import timedelta
from typing import Dict, Any
import os

# Безопасность
SECRET_KEY = "your-secret-key" # нужно будет заменить на случайную строку + HTTPS
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Типы для аннотаций
UserDict = Dict[str, Any]
UsersDB = Dict[str, UserDict]