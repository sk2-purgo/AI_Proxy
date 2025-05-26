from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from fastapi_gateway.routes import key_issuer
from fastapi_gateway.routes import stats_router
from fastapi_gateway.middlewares.auth_middleware import proxy_auth_middleware
from fastapi_gateway.services.analyze_service import handle_analyze
from fastapi_gateway.cleanup_task import cleanup_expired_api_keys
from dotenv import load_dotenv
import os

print(" FastAPI main.py 로딩됨")
app = FastAPI()

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONT_ORIGIN")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(key_issuer.router)
app.include_router(stats_router.router)

# 인증 미들웨어 수동 적용
app.middleware("http")(proxy_auth_middleware)

# 분석 라우터 직접 등록
@app.post("/proxy/analyze/{target}")
async def analyze_entry(request: Request, target: str):
    return await handle_analyze(request, target)

@app.on_event("startup")
def on_startup():
    print(" FastAPI 서버 시작 이벤트 진입")

@repeat_every(seconds=86400)
def periodic_cleanup():
    print("\U0001f9f9 API 키 자동 정리 시작")
    cleanup_expired_api_keys()

# 테스트용
# uvicorn fastapi_gateway.main:app --reload --port 8001 --host 0.0.0.0 --http h11

# ctrl + c 해도 안 되면 실행하기기
# taskkill /f /im python.exe

# 로그 받아오기
# python -m fastapi_gateway.Log_consumer

# 실행
#  uvicorn fastapi_gateway.main:app --port 8001 --host 0.0.0.0 --http h11