from passlib.context import CryptContext
from ..models.user import UserCreate, UserInDB
from fastapi import HTTPException

# Пока нет БД
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "testuser@example.com",
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def register_user(user_data: UserCreate) -> UserInDB:
    # Проверка, что пользователь не существует
    if user_data.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user_data.password)
    
    user_dict = user_data.dict()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]
    
    fake_users_db[user_data.username] = user_dict
    return UserInDB(**user_dict)

# Фейковый пользователь для разработки
def get_fake_user() -> UserInDB:
    return UserInDB(
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpass")
    )