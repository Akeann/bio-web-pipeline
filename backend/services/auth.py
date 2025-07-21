# from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from ..models.user import UserCreate, UserInDB, TokenData
from ..data.fake_db import fake_users_db
from ..services.jwt import decode_token
from ..services.password import verify_password, get_password_hash
from ..config import UsersDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

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
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]
    
    fake_users_db[user_data.username] = user_dict
    return UserInDB(**user_dict)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = fake_users_db.get(token_data.username)
    if user is None:
        raise credentials_exception
    return UserInDB(**user)

def get_fake_user() -> UserInDB:
    return UserInDB(
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpass")
    )