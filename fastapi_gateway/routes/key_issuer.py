# fastapi_gateway/routes/key_issuer.py

from fastapi import APIRouter, HTTPException
from fastapi_gateway.database import SessionLocal, ApiKey
from pydantic import BaseModel
import uuid
import secrets
from sqlalchemy.exc import IntegrityError
from datetime import datetime

router = APIRouter()

#  요청 스키마
class KeyIssueRequest(BaseModel): # Pydantic 기반 모델로 FastAPI가 자동으로 JSON body → 객체로 변환
    user_name: str

#  응답 스키마
class KeyIssueResponse(BaseModel):
    api_key: str
    jwt_secret: str

@router.post("/issue-key", response_model=KeyIssueResponse)
def issue_api_key(request: KeyIssueRequest):
    db = SessionLocal()

    new_api_key = str(uuid.uuid4()) # 랜덤 기반 uuid 생성
    new_jwt_secret = secrets.token_urlsafe(64)

    api_key_entry = ApiKey(
        api_key=new_api_key,
        jwt_secret=new_jwt_secret,
        status="ACTIVE",                      # 상태 명시
        created_at=datetime.utcnow()          # 생성 시간 명시
    )

    try:
        db.add(api_key_entry)
        db.commit()
        return KeyIssueResponse(api_key=new_api_key, jwt_secret=new_jwt_secret)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="이미 동일한 API 키가 존재합니다.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
