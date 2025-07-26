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
    return UserInDB(**user)

def register_user(user_data: UserCreate) -> UserInDB:
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    
    user_dict = {
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
    credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
    
    await clean_blacklist()
    
    if token is None:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        token = token.strip('"').strip("'")
    
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        
        if token in TOKEN_BLACKLIST:
            return None
            
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        return None
    
    user = fake_users_db.get(token_data.username)
    if user is None:
        return None
        
    return UserInDB(**user)

def get_fake_user() -> UserInDB:
    return UserInDB(
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpass")
    )