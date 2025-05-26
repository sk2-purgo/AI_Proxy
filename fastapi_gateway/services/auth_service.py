from fastapi_gateway.utils.redis_client import redis_conn
from fastapi_gateway.database import SessionLocal, ApiKey, StatusEnum
from fastapi_gateway.utils.jwt_utils import verify_server_jwt
from fastapi import Request
import jwt
from datetime import datetime

async def verify_api_key_and_jwt(request: Request, request_body: dict) -> bool:
    db = SessionLocal()
    try:
        headers = request.headers
        raw_token = headers.get("authorization", "")
        jwt_token = headers.get("x-auth-token", "")
        if not raw_token.startswith("Bearer "):
            print("[DEBUG] Authorization 헤더 형식 오류")
            return False
        api_key = raw_token.replace("Bearer ", "")

        # 1. Redis에서 시크릿 키 먼저 확인
        cached_secret = redis_conn.get(f"jwt:secret:{api_key}")
        if cached_secret:
            try:
                jwt.decode(jwt_token, cached_secret, algorithms=["HS256"])
                print("✅ [Redis 캐시] 시크릿 키 기반 JWT 검증 통과")
                return True
            except Exception as e:
                print("❌ [Redis 캐시] JWT 서명 검증 실패:", str(e))
                return False

        # 2. Redis에 없으면 DB 확인
        key_entry = db.query(ApiKey).filter_by(api_key=api_key, status=StatusEnum.ACTIVE.value).first()
        if not key_entry:
            print("❌ DB에 API Key 없음")
            return False

        user_secret = key_entry.jwt_secret
        print(f"🔓 DB 조회된 시크릿 키: {user_secret}")

        # 3. 본문 + 해시 검증 수행 (최초 요청)
        is_valid = verify_server_jwt(jwt_token, request_body, api_key)
        if not is_valid:
            print("❌ verify_server_jwt 검증 실패")
            return False

        # 4. Redis에 캐시 등록
        redis_conn.setex(f"jwt:secret:{api_key}", 600, user_secret)
        redis_conn.setex(f"api_key:{api_key}", 600, "ACTIVE")
        print("✅ Redis 캐시에 시크릿 키 저장 완료")

        # 5. DB 마지막 사용 시각 업데이트
        key_entry.last_used = datetime.utcnow()
        db.commit()

        return True

    except Exception as e:
        print("❌ 인증 처리 실패:", str(e))
        return False
    finally:
        db.close()
