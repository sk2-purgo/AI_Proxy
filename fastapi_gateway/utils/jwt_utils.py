import time
import jwt
import hashlib
import json
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi_gateway.database import SessionLocal, ApiKey
from fastapi import Request

# ✅ 기존 본문 해시 + 시그니처 검증용 함수
def verify_server_jwt(token: str, request_body: dict, api_key: str) -> bool:
    print("🟡 [JWT] 사용자별 시크릿 키 검증 진입")

    db = SessionLocal()
    try:
        key_entry = db.query(ApiKey).filter_by(api_key=api_key).first()
        if not key_entry:
            print("❌ API Key가 존재하지 않음")
            return False

        user_secret = key_entry.jwt_secret
        payload = jwt.decode(token, user_secret, algorithms=["HS256"])
        print("🔵 Payload:", payload)

        iat = payload.get("iat")
        now = time.time()
        if iat is not None and abs(iat - now) > 10:
            print(f"❌ 시간 오차 초과: 서버 시간 {now}, 토큰 iat {iat}")
            return False

        expected_hash = payload.get("hash")
        body_raw = request_body["__raw_body__"]
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

# ✅ 추가된 시그니처 검증 전용 함수 (본문 무시)
def verify_signature_only(token: str, secret: str) -> bool:
    try:
        jwt.decode(token, secret, algorithms=["HS256"])
        return True
    except ExpiredSignatureError:
        print("❌ JWT 만료됨")
    except InvalidTokenError as e:
        print("❌ JWT 구조 오류:", str(e))
    except Exception as e:
        print("❌ 기타 JWT 오류:", str(e))
    return False
