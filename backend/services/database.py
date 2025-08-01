from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from ..models.db_models import Base
import os
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Настройка engine с pool_pre_ping для проверки соединений
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ScopedSession = scoped_session(SessionLocal)  # Для thread-safe сессий

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Таблицы БД созданы")

@contextmanager
def get_db():
    db = ScopedSession()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        ScopedSession.remove()