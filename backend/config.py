import os
from datetime import timedelta
from typing import Dict, Any
from uuid import UUID

# Безопасность
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Типы для аннотаций
UserDict = Dict[str, Any]
UsersDB = Dict[str, UserDict]