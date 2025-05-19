from fastapi_gateway.utils.redis_client import redis_conn
from fastapi_gateway.database import SessionLocal, ApiKey, StatusEnum
from fastapi_gateway.jwt_utils import verify_server_jwt
from fastapi import Request
import json
import hashlib
from datetime import datetime

async def verify_api_key_and_jwt(request: Request, request_body: dict) -> bool:
    db = SessionLocal()
    try:
        headers = request.headers
        raw_token = headers.get("authorization", "")
        jwt_token = headers.get("x-auth-token", "")

        # 1. API Key 형식 확인
        if not raw_token.startswith("Bearer "):
            print("[DEBUG] Authorization 헤더 형식 오류")
            return False
        api_key = raw_token.replace("Bearer ", "")

        key_entry = None

        # 2. Redis 캐시 확인
        cached_status = redis_conn.get(f"api_key:{api_key}")
        if cached_status != "ACTIVE":
            key_entry = db.query(ApiKey).filter_by(
                api_key=api_key, status=StatusEnum.ACTIVE.value
            ).first()
            if key_entry:
                redis_conn.setex(f"api_key:{api_key}", 600, "ACTIVE")
            else:
                print(f"❌ [인증 실패] Redis 캐시 미스 후 DB에 존재하지 않는 API Key: {api_key}")
                return False
        else:
            key_entry = db.query(ApiKey).filter_by(api_key=api_key).first()
            if not key_entry:
                print(f"❌ [인증 실패] Redis에는 ACTIVE이나 DB에는 없는 API Key: {api_key}")
                return False

        #  로그: 어떤 API 키와 시크릿 키가 조회되었는지 확인
        print(f"🔐 [DEBUG] API Key: {api_key}")
        print(f"🔐 [DEBUG] 연결된 JWT 시크릿 키: {key_entry.jwt_secret}")

        # 3. 사용 시각 갱신
        key_entry.last_used = datetime.utcnow()
        db.commit()

        # 4. 요청 바디 해시 생성
        body_bytes = await request.body()
        body_json = json.loads(body_bytes.decode("utf-8"))

        #  재직렬화된 문자열을 로그로 출력
        re_serialized = json.dumps(body_json, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        print(f"🧾 [프록시] 재직렬화된 JSON 본문: {re_serialized}")
        print(f"📜 [DEBUG] 재직렬화 대상 객체: {body_json}")

        body_hash = hashlib.sha256(re_serialized.encode()).hexdigest()
        key = f"jwt:hash:{body_hash}"

        print(f"🧮 [DEBUG] 본문 해시값 (actual_hash): {body_hash}")

        # 5. JWT 해시 캐시가 이미 존재하면 통과
        if redis_conn.exists(key):
            print("[DEBUG] JWT 해시 캐시 검증 성공 (Redis)")
            return True

        # 6. 서버-프록시용 JWT 검증
        print("🛡️ [DEBUG] JWT 서명 검증 수행 시작")
        if verify_server_jwt(jwt_token, request_body , api_key):
            redis_conn.setex(key, 30, "1")
            print("[DEBUG] JWT 해시 저장 완료 (Redis 캐시 등록)")
            return True

        print("❌ [인증 실패] JWT 서명 또는 해시 검증 실패")
        return False

    except Exception as e:
        print("[ERROR] 인증 처리 실패:", str(e))
        return False

    finally:
        db.close()
