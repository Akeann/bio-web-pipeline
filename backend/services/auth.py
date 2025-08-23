from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from ..models.user import UserCreate, UserInDB, TokenData
from ..data.fake_db import fake_users_db
from ..services.jwt import decode_token
from ..services.password import verify_password, get_password_hash
from ..config import UsersDB, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from typing import Optional
import re
from pprint import pprint
from uuid import uuid4

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

# Хранилище для черного списка токенов
TOKEN_BLACKLIST = {}

def add_to_blacklist(token: str):
    """Добавляет токен в черный список с временем экспирации из самого токена"""
    try:
        # Декодируем токен без проверки подписи, чтобы получить expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            expire_time = datetime.fromtimestamp(exp_timestamp, timezone.utc)
            TOKEN_BLACKLIST[token] = expire_time
        else:
            # Если нет exp, используем стандартное время
            expires_in = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            TOKEN_BLACKLIST[token] = datetime.now(timezone.utc) + expires_in
    except JWTError:
        # Если токен невалидный, всё равно добавляем в чёрный список
        expires_in = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        TOKEN_BLACKLIST[token] = datetime.now(timezone.utc) + expires_in

async def clean_blacklist():
    """Очищает истекшие токены из черного списка"""
    now = datetime.now(timezone.utc)
    global TOKEN_BLACKLIST
    TOKEN_BLACKLIST = {k: v for k, v in TOKEN_BLACKLIST.items() if v > now}

def authenticate_user(username: str, password: str) -> UserInDB:
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.get("id"):
        raise ValueError(f"User {username} has no ID")
        
    return UserInDB(**user)

def register_user(user_data: UserCreate) -> UserInDB:
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    
    user_dict = {
        "id": str(uuid4()),  # Генерируем новый UUID
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "country": user_data.country,
        "role": user_data.role,
        "institution_type": user_data.institution_type,
        "disabled": False,
        "registration_date": datetime.now(timezone.utc).isoformat()
    }
    
    fake_users_db[user_data.username] = user_dict
    return UserInDB(**user_dict)

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme)
) -> Optional[UserInDB]:
    await clean_blacklist()  # Ваша оригинальная очистка чёрного списка
    
    # Оригинальная логика получения токена
    if token is None:
        token = request.cookies.get("access_token")
        if token is None:
            print("DEBUG: No token found")
            return None

    try:
        if isinstance(token, str):
            # Улучшенная нормализация
            token = token.replace('"', '').replace("'", "")
            token = re.sub(r'^Bearer\s+', '', token).strip()
            
            print(f"DEBUG: Normalized token: {token[:10]}...")

            # Ваша проверка чёрного списка
            if token in TOKEN_BLACKLIST:
                print("DEBUG: Token is blacklisted")
                return None
                
            # Ваше оригинальное декодирование JWT
            payload = decode_token(token)
            username = payload.get("sub")
            if not username:
                print("DEBUG: No username in payload")
                return None
                
            # Ваш поиск пользователя
            user = fake_users_db.get(username)
            if not user:
                print(f"DEBUG: User {username} not found")
                return None
                
            print(f"DEBUG: Authenticated user: {username}")
            return UserInDB(**user)
            
    except JWTError as e:
        # Ваша оригинальная обработка ошибок JWT
        print(f"DEBUG: JWT Error: {str(e)}")
    except Exception as e:
        # Ваша обработка прочих ошибок
        print(f"DEBUG: Unexpected error: {str(e)}")
    
    return None

def get_fake_user() -> UserInDB:
    return UserInDB(
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpass")
    )