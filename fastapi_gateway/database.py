# fastapi_gateway/database.py

from sqlalchemy import create_engine, Column, String, Integer, Enum, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base
from enum import Enum as PyEnum
import datetime
from sqlalchemy import Enum as SqlEnum , Integer
import os
from dotenv import load_dotenv
from sqlalchemy import event
from fastapi_gateway.utils.redis_client import redis_conn

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

# 상태가 변경된 ApiKey를 감지하고 publish
@event.listens_for(SessionLocal, "after_flush")
def after_flush(session, flush_context):
    for instance in session.dirty:
        if isinstance(instance, ApiKey):
            if instance.status == "REVOKED":
                redis_conn.publish("revoke-log", instance.api_key)
                print(f"📡 [Hook] status='REVOKED' 감지됨 → Redis 발행 완료: {instance.api_key}")
