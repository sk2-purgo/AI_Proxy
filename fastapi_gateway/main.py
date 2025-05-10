from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer, Enum, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base
from enum import Enum as PyEnum
from jwt_utils import verify_server_jwt
import requests
import datetime
import pymysql  # sqlalchemy + pymysql 조합 시 필요
import json

#  DB 연결 설정
DATABASE_URL = "mysql+pymysql://root:proxy1234@localhost:3307/purgo_proxy"
engine = create_engine(DATABASE_URL, echo=True)  # ← 쿼리 출력 활성화
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

#  ENUM 타입 정의
class StatusEnum(PyEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"

#  DB 테이블 모델
class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(64), unique=True, index=True)
    status = Column(Enum(StatusEnum, native_enum=False))
    memo = Column(String(255))
    created_at = Column(TIMESTAMP)

class UsageLog(Base):
    __tablename__ = "usage_log"
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(64))
    endpoint = Column(String(64))
    req_bytes = Column(Integer)
    res_bytes = Column(Integer)
    called_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

#  Flask 서버 주소
# FLASK_AI_URL = "http://127.0.0.1:5000/analyze"
FLASK_AI_URL = "http://3.34.64.170:5000/analyze"

#  FastAPI 앱
app = FastAPI()

#  요청 바디 모델
class TextRequest(BaseModel):
    text: str

#  /proxy/analyze 라우터
@app.post("/proxy/analyze")
async def relay_to_flask(
        request: Request,
        authorization: Optional[str] = Header(None),
        x_auth_token: Optional[str] = Header(None)
):
    db = SessionLocal()

    try:
        raw_body = await request.body()  # 🔵 raw_body는 bytes
        body_str = raw_body.decode('utf-8')  # 🔵 UTF-8로 decode
        parsed_body = json.loads(body_str)  # 🔵 dict로 변환
        text = parsed_body.get("text")

        print(f"📨 받은 요청: {text}")

        # Authorization 헤더 체크
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        api_key = authorization.replace("Bearer ", "")

        # API 키 유효성 확인
        key_entry = db.query(ApiKey).filter_by(api_key=api_key, status=StatusEnum.ACTIVE).first()
        if not key_entry:
            raise HTTPException(status_code=401, detail="Invalid API key")

        # JWT 검증
        if not x_auth_token:
            raise HTTPException(status_code=401, detail="Missing X-Auth-Token")
        if not verify_server_jwt(x_auth_token, parsed_body):
            raise HTTPException(status_code=401, detail="Invalid or tampered JWT")

        # Flask 서버로 요청
        flask_response = requests.post(FLASK_AI_URL, json={"text": text})
        response_data = flask_response.json()

        # 사용 로그 기록
        db.add(UsageLog(
            api_key=api_key,
            endpoint="/proxy/analyze",
            req_bytes=len(raw_body),
            res_bytes=len(flask_response.content),
        ))
        db.commit()

        return response_data

    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return {"error": f"Flask 서버 통신 실패: {str(e)}"}

    finally:
        db.close()


