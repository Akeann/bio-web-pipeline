from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    country = Column(String(50), nullable=True)
    role = Column(String(50), nullable=True)
    institution_type = Column(String(50), nullable=True)
    disabled = Column(Boolean, default=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    
    analysis_jobs = relationship("AnalysisJob", back_populates="user", cascade="all, delete-orphan")

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID как строка
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=False)
    parameters = Column(Text, nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    result_path = Column(String(500), nullable=True)
    
    user = relationship("User", back_populates="analysis_jobs")