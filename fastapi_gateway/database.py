# fastapi_gateway/database.py

from sqlalchemy import create_engine, Column, String, Integer, Enum, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base
from enum import Enum as PyEnum
import datetime
from sqlalchemy import Enum as SqlEnum , Integer
import os
from dotenv import load_dotenv

load_dotenv()
#  DB 접속 정보
DATABASE_URL = os.getenv("DATABASE_URL")

#  SQLAlchemy 구성
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# API 키 상태 ENUM
class StatusEnum(PyEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


# API 키 테이블
class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(64), unique=True, index=True)
    status = Column(String(10))
    created_at = Column(TIMESTAMP)
    last_used = Column(TIMESTAMP)
    jwt_secret = Column(String(128))
    abuse_count = Column(Integer, default=0)

class BadWord(Base):
    __tablename__ = "badwords"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(64), unique=True, index=True)
    count = Column(Integer, default=1)
