from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi_gateway.utils.log_publisher import publish_filter_log
from fastapi_gateway.utils.log_publisher import publish_abuse_count
from fastapi_gateway.utils.log_publisher import publish_badwords
import httpx, json
from dotenv import load_dotenv
import os

load_dotenv()

async def handle_analyze(request: Request, target: str):
    print("📥 [프록시] 요청 수신: /proxy/analyze")
    print("🔸 요청 헤더:", dict(request.headers))
    print("🔸 요청 IP:", request.client.host)

    if target == "community":
        ai_url = os.getenv("AI_COMMUNITY_URL")
    elif target == "chat":
        ai_url = os.getenv("AI_CHAT_URL")
    else:
        return JSONResponse(status_code=404, content={"error": f"지원하지 않는 분석 대상: {target}"})

    try:
        body = json.loads(request.state.body.decode("utf-8"))
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            flask_response = await client.post(ai_url, json=body)
            result = flask_response.json()

        # ✅ 1. 로그 발행 (fasttext_result 저장 포함)
        fasttext_words = result.get("result", {}).get("fasttext_result", [])
        publish_badwords(fasttext_words)

        # ✅ 2. abuse_count 발행 (비속어 판단 시)
        is_abusive = result.get("final_decision", 0) == 1
        if is_abusive:
            raw_token = request.headers.get("authorization", "")
            if raw_token.startswith("Bearer "):
                api_key = raw_token.replace("Bearer ", "")
                publish_abuse_count(api_key)

        # ✅ 3. 로그 저장
        publish_filter_log(
            user_id=request.headers.get("X-User-Id", "anonymous"),
            original_text=body.get("text", ""),
            filtered_text=result.get("result", {}).get("rewritten_text", "")
        )

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
