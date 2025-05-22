# fastapi_gateway/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_gateway.services.auth_service import verify_api_key_and_jwt
from fastapi_gateway.utils.redis_client import redis_conn
from fastapi_utils.tasks import repeat_every
from fastapi_gateway.cleanup_task import cleanup_expired_api_keys
from fastapi_gateway.routes import key_issuer
import requests
import json
import uuid
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import httpx

print(" FastAPI main.py 로딩됨")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 또는 ["*"] 임시 허용
    allow_credentials=True, # cors 요처에 대해 쿠키, Authorization 헤더, TLS 클라이언트 인증서 등 허용 여부
    allow_methods=["*"], # GET, POST, PUT, DELETE, OPTIONS 등
    allow_headers=["*"], # Authorization, Content-Type, X-Auth-Token 등
)

#  라우터 등록
app.include_router(key_issuer.router) # 내부는 이것과 같음 app.add_api_route("/issue-key", issue_api_key, methods=["POST"])


FLASK_AI_URL = "http://127.0.0.1:5000/analyze"

@app.middleware("http") # 모든 http 요청을 가로챔
async def proxy_auth_middleware(request: Request, call_next): # call_next는 내부적인 코드가 있는 함수
    body_bytes = await request.body()
    request.state.body = body_bytes
    request.state.body_str = body_bytes.decode("utf-8")  # ✅ 원문 문자열 저장(string으로 저장)

    path = request.url.path # path가 경로만 추출함 즉 이후 조건문에서 해당 경로가 /proxy인지 검사 하기 위해 필요

    if path.startswith("/proxy/"):
        print("🛡️ [미들웨어] 인증 진입:", path)
        print("🔍 [미들웨어] 요청 IP:", request.client.host)
        print("🔍 [미들웨어] 요청 헤더:", dict(request.headers))
        #  request_body에 원문도 포함시켜서 넘김
        try:
            request_body = json.loads(request.state.body_str) # utf-8 디코딩된 본문 문자열 파이썬 dict로 파싱
            request_body["__raw_body__"] = request.state.body_str
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"요청 본문 파싱 실패: {str(e)}"})

        is_valid = await verify_api_key_and_jwt(request, request_body)  # 수정된 시그니처에 맞게 호출
        if not is_valid:
            return JSONResponse(status_code=401, content={"error": "API Key 또는 JWT 인증 실패"})

    return await call_next(request) # 다음 미들웨어 또는 라우터 함수로 요청 전달

@app.post("/proxy/analyze/{target}")
async def analyze_proxy(request: Request, target: str):
    print("📥 [프록시] 요청 수신: /proxy/analyze")
    print("🔸 요청 헤더:", dict(request.headers))
    print("🔸 요청 IP:", request.client.host)
    try:
        ip = request.client.host # 클라이언트 ip 주소를 변수에 저잦ㅇ
        key = f"ratelimit:{ip}" # redis에서 사용할 키 이름 생성

        current = redis_conn.incr(key)
        if current == 1:
            redis_conn.expire(key, 60) # 유효시간 60초
        if current > 10:
            return JSONResponse(status_code=429, content={"error": "요청 한도 초과 (1분에 10회)"})

        # 대상 서버 포트 결정
        if target == "community":
            ai_url = "http://127.0.0.1:5000/analyze"
        elif target == "chat":
            ai_url = "http://127.0.0.1:5001/analyze"
        else:
            return JSONResponse(status_code=404, content={"error": f"지원하지 않는 분석 대상: {target}"})

        body = json.loads(request.state.body.decode("utf-8")) # 문자열로 디코딩
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            flask_response = await client.post(ai_url, json=body) # HTTP Header에는 Content-Type: application/json 자동 포함
            result = flask_response.json()

        log_payload = {
            "logId": str(uuid.uuid4()), # 로그 구분을 위한 유일 식별자 생성
            "userId": request.headers.get("X-User-Id", "anonymous"), # 사용자 추적용 아이디
            "originalText": body.get("text", ""), # 사용자가 보낸 원문 메시지 저장
            "filteredText": result.get("result", {}).get("rewritten_text", ""), # ai 모델이 수정한 최종 메시지 저장
            "timestamp": datetime.utcnow().isoformat() # 로그 발생 시각 기록 (표준 형식)
        }
        print("📤 [프록시] Redis에 로그 발행 준비:", log_payload)
        # log_consumer.py에서 filter-log 채널을 구독 중
        # 이 데이터를 Redis를 통해 비동기 로그 소비기로 전달
        redis_conn.publish("filter-log", json.dumps(log_payload))
        print("📤 [프록시] Redis에 발행 완료")

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.on_event("startup")
def on_startup():
    print(" FastAPI 서버 시작 이벤트 진입")

@repeat_every(seconds=86400)
def periodic_cleanup():
    print("🧹 API 키 자동 정리 시작")
    cleanup_expired_api_keys() # 상단에 import문에 cleaup_task파일이 연결된게 있음


# 테스트용
# uvicorn fastapi_gateway.main:app --reload --port 8001 --host 0.0.0.0 --http h11

# ctrl + c 해도 안 되면 실행하기기
# taskkill /f /im python.exe

# 로그 받아오기
# python fastapi_gateway/log_consumer.py

# 실행
#  uvicorn fastapi_gateway.main:app --port 8001 --host 0.0.0.0 --http h11