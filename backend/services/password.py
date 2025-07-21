from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import bcrypt
import passlib

# Обход для ошибки чтения версии bcrypt
if not hasattr(bcrypt, '__about__'):
    bcrypt.__about__ = type('obj', (object,), {'__version__': '4.3.0'})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


