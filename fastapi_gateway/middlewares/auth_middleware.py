# fastapi_gateway/middlewares/auth_middleware.py
'''
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi_gateway.services.auth_service import verify_api_key_and_jwt

class ProxyAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        request.state.body = await request.body()

        path = request.url.path

        # /proxy/로 시작하는 모든 요청에 대해 인증 수행
        if path.startswith("/proxy/"):
            is_valid = await verify_api_key_and_jwt(request)
            if not is_valid:
                return JSONResponse(status_code=401, content={"error": "API Key 또는 JWT 인증 실패"})

        return await call_next(request)
'''