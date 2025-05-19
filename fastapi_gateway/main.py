# fastapi_gateway/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_gateway.services.auth_service import verify_api_key_and_jwt
from fastapi_gateway.utils.redis_client import redis_conn
from fastapi_utils.tasks import repeat_every
from fastapi_gateway.cleanup_task import cleanup_expired_api_keys
from fastapi_gateway.routes import key_issuer  # 📌 issue-key 라우터 분리 등록
import requests
import json
import uuid
from datetime import datetime

print("✅ FastAPI main.py 로딩됨")
app = FastAPI()

# 📌 라우터 등록
app.include_router(key_issuer.router)

FLASK_AI_URL = "http://127.0.0.1:5000/analyze"

@app.middleware("http")
async def proxy_auth_middleware(request: Request, call_next):
    body_bytes = await request.body()
    request.state.body = body_bytes
    request.state.body_str = body_bytes.decode("utf-8")  # ✅ 원문 문자열 저장

    path = request.url.path

    if path.startswith("/proxy/"):
        print("🛡️ [미들웨어] 인증 진입:", path)
        print("🔍 [미들웨어] 요청 IP:", request.client.host)
        print("🔍 [미들웨어] 요청 헤더:", dict(request.headers))
        # ✅ request_body에 원문도 포함시켜서 넘김
        try:
            request_body = json.loads(request.state.body_str)
            request_body["__raw_body__"] = request.state.body_str
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"요청 본문 파싱 실패: {str(e)}"})

        is_valid = await verify_api_key_and_jwt(request, request_body)  # ✅ 수정된 시그니처에 맞게 호출
        if not is_valid:
            return JSONResponse(status_code=401, content={"error": "API Key 또는 JWT 인증 실패"})

    return await call_next(request)

@app.post("/proxy/analyze")
async def analyze_proxy(request: Request):
    print("📥 [프록시] 요청 수신: /proxy/analyze")
    print("🔸 요청 헤더:", dict(request.headers))
    print("🔸 요청 IP:", request.client.host)
    try:
        ip = request.client.host
        key = f"ratelimit:{ip}"

        current = redis_conn.incr(key)
        if current == 1:
            redis_conn.expire(key, 60)
        if current > 10:
            return JSONResponse(status_code=429, content={"error": "요청 한도 초과 (1분에 10회)"})

        body = json.loads(request.state.body.decode("utf-8"))
        flask_response = requests.post(FLASK_AI_URL, json=body)
        result = flask_response.json()

        log_payload = {
            "logId": str(uuid.uuid4()),
            "userId": request.headers.get("X-User-Id", "anonymous"),
            "originalText": body.get("text", ""),
            "filteredText": result.get("result", {}).get("rewritten_text", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
        print("📤 [프록시] Redis에 로그 발행 준비:", log_payload)
        redis_conn.publish("filter-log", json.dumps(log_payload))
        print("📤 [프록시] Redis에 발행 완료")

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.on_event("startup")
def on_startup():
    print("✅ FastAPI 서버 시작 이벤트 진입")

@repeat_every(seconds=86400)
def periodic_cleanup():
    print("🧹 API 키 자동 정리 시작")
    cleanup_expired_api_keys()


# uvicorn fastapi_gateway.main:app --reload --port 8001 --host 0.0.0.0 --http h11
# taskkill /f /im python.exe
# python fastapi_gateway/log_consumer.py
#  uvicorn fastapi_gateway.main:app --port 8001 --host 0.0.0.0 --http h11