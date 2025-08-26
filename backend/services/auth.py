from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from ..models.user import UserCreate, UserInDB, TokenData
from ..services.database import get_db
from ..models.db_models import User as DBUser
from ..services.jwt import decode_token
from ..services.password import verify_password, get_password_hash
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from typing import Optional
import re
from pprint import pprint

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

def authenticate_user(username: str, password: str, db: Session) -> UserInDB:
    """
    Аутентификация пользователя через PostgreSQL
    """
    user = db.query(DBUser).filter(DBUser.username == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return UserInDB(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        country=user.country,
        role=user.role,
        institution_type=user.institution_type,
        disabled=user.disabled,
        registration_date=user.registration_date.isoformat() if user.registration_date else None
    )

def register_user(user_data: UserCreate, db: Session) -> UserInDB:
    """
    Регистрация нового пользователя в PostgreSQL
    """
    # Проверяем существующего пользователя
    existing_user = db.query(DBUser).filter(
        (DBUser.username == user_data.username) | 
        (DBUser.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    
    # Создаем нового пользователя в БД
    db_user = DBUser(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        country=user_data.country,
        role=user_data.role,
        institution_type=user_data.institution_type
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserInDB(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        country=db_user.country,
        role=db_user.role,
        institution_type=db_user.institution_type,
        disabled=db_user.disabled,
        registration_date=db_user.registration_date.isoformat() if db_user.registration_date else None
    )

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[UserInDB]:
    """
    Получение текущего пользователя из JWT токена через PostgreSQL
    """
    await clean_blacklist()
    
    # Получаем токен из куки, если не передан в заголовке
    if token is None:
        token = request.cookies.get("access_token")
        if token is None:
            print("DEBUG: No token found")
            return None

    try:
        if isinstance(token, str):
            # Нормализация токена
            token = token.replace('"', '').replace("'", "")
            token = re.sub(r'^Bearer\s+', '', token).strip()
            
            print(f"DEBUG: Normalized token: {token[:10]}...")

            # Проверка черного списка
            if token in TOKEN_BLACKLIST:
                print("DEBUG: Token is blacklisted")
                return None
                
            # Декодирование JWT
            payload = decode_token(token)
            username = payload.get("sub")
            if not username:
                print("DEBUG: No username in payload")
                return None
                
            # Поиск пользователя в PostgreSQL
            user = db.query(DBUser).filter(DBUser.username == username).first()
            if not user:
                print(f"DEBUG: User {username} not found in database")
                return None
                
            if user.disabled:
                print(f"DEBUG: User {username} is disabled")
                return None
                
            print(f"DEBUG: Authenticated user: {username}")
            
            return UserInDB(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                country=user.country,
                role=user.role,
                institution_type=user.institution_type,
                disabled=user.disabled,
                registration_date=user.registration_date.isoformat() if user.registration_date else None
            )
            
    except JWTError as e:
        print(f"DEBUG: JWT Error: {str(e)}")
    except Exception as e:
        print(f"DEBUG: Unexpected error: {str(e)}")
    
    return None

# Функция для тестирования (может быть удалена после перехода на реальную БД)
def get_test_user(db: Session) -> Optional[UserInDB]:
    """
    Получение тестового пользователя для разработки
    """
    user = db.query(DBUser).filter(DBUser.username == "testuser").first()
    if user:
        return UserInDB(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            country=user.country,
            role=user.role,
            institution_type=user.institution_type,
            disabled=user.disabled,
            registration_date=user.registration_date.isoformat() if user.registration_date else None
        )
    return None