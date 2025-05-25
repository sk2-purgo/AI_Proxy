# fastapi_gateway/middlewares/auth_middleware.py

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi_gateway.services.auth_service import verify_api_key_and_jwt
import json

async def proxy_auth_middleware(request: Request, call_next):
    body_bytes = await request.body()
    request.state.body = body_bytes
    request.state.body_str = body_bytes.decode("utf-8")

    path = request.url.path

    if path.startswith("/proxy/"):
        print("🛡️ [미들웨어] 인증 진입:", path)
        print("🔍 [미들웨어] 요청 IP:", request.client.host)
        print("🔍 [미들웨어] 요청 헤더:", dict(request.headers))
        try:
            request_body = json.loads(request.state.body_str)
            request_body["__raw_body__"] = request.state.body_str
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"요청 본문 파싱 실패: {str(e)}"})

        is_valid = await verify_api_key_and_jwt(request, request_body)
        if not is_valid:
            return JSONResponse(status_code=401, content={"error": "API Key 또는 JWT 인증 실패"})

    return await call_next(request)
