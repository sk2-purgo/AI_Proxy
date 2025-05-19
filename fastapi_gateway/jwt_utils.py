import jwt
import hashlib
import json
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi_gateway.database import SessionLocal, ApiKey
from fastapi import Request

def verify_server_jwt(token: str, request_body: dict, api_key: str) -> bool:
    print("🟡 [JWT] 사용자별 시크릿 키 검증 진입")

    db = SessionLocal()
    try:
        # 1. 해당 API Key에 연결된 사용자 시크릿 키 가져오기
        key_entry = db.query(ApiKey).filter_by(api_key=api_key).first()
        if not key_entry:
            print("❌ API Key가 존재하지 않음")
            return False

        user_secret = key_entry.jwt_secret

        # 2. JWT 디코딩
        payload = jwt.decode(token, user_secret, algorithms=["HS256"])
        print("🔵 Payload:", payload)

        # 3. 요청 본문 해시 검증 (📌 수정됨: raw body 기준)
        expected_hash = payload.get("hash")

        body_raw = request_body["__raw_body__"]  # 📌 미들웨어에서 추가된 raw 저장 방식
        actual_hash = hashlib.sha256(body_raw.encode("utf-8")).hexdigest()

        print("✅ expected_hash:", expected_hash)
        print("✅ actual_hash:", actual_hash)

        return expected_hash == actual_hash

    except ExpiredSignatureError:
        print("❌ JWT 만료됨")
        return False
    except InvalidTokenError as e:
        print("❌ JWT 구조 오류:", str(e))
        return False
    except Exception as e:
        print("❌ 기타 예외:", str(e))
        return False
    finally:
        db.close()
