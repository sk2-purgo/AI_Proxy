# fastapi_gateway/database.py

from sqlalchemy import create_engine, Column, String, Integer, Enum, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base
from enum import Enum as PyEnum
import datetime
from sqlalchemy import Enum as SqlEnum

#  DB 접속 정보
DATABASE_URL = "mysql+pymysql://root:proxy1234@localhost:3307/purgo_proxy"

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
    user_name = Column(String(64))
    api_key = Column(String(64), unique=True, index=True)
    status = Column(String(10))
    memo = Column(String(255))
    created_at = Column(TIMESTAMP)
    jwt_secret = Column(String(128))

# 사용 로그 테이블
class UsageLog(Base):
    __tablename__ = "usage_log"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(64))
    endpoint = Column(String(64))
    req_bytes = Column(Integer)
    res_bytes = Column(Integer)
    called_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
