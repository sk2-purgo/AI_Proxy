import jwt
import hashlib
import json
from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = "hG7dF!2$jd91Qz@uE4vw32T8pK9bX1A0"
ALGORITHM = "HS256"

def verify_server_jwt(token: str, request_body: dict) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("🔵 디코딩한 JWT Payload:", payload)

        expected_hash = payload.get("hash")

        # ✅ JSON 직렬화 시 공백 제거 (Java 방식 맞춤)
        text_json = json.dumps(request_body, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        text_hash = hashlib.sha256(text_json.encode('utf-8')).hexdigest()

        print(f"✅ expected_hash (JWT 안): {expected_hash}")
        print(f"✅ actual_hash (요청 본문으로 재계산): {text_hash}")
        print(f"✅ 요청 본문 직렬화 결과 text_json: {text_json}")

        if expected_hash != text_hash:
            print("❌ 해시 불일치 발생!! 요청 본문과 JWT 본문이 다름")
            return False

        return True

    except ExpiredSignatureError:
        print("❌ JWT 만료됨 (ExpiredSignatureError)")
        return False
    except InvalidTokenError as e:
        print(f"❌ JWT 유효성 실패 (InvalidTokenError): {str(e)}")
        return False
