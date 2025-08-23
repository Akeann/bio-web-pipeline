from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from ..models.db_models import Base
import os
from contextlib import contextmanager
from typing import Generator

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Настройка engine с pool_pre_ping для проверки соединений
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    echo=True  # Для отладки SQL запросов
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Таблицы БД созданы")

def get_db() -> Generator[Session, None, None]:
    """
    Генератор сессий БД для использования в зависимостях FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()