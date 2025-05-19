import asyncio
import httpx
import time

async def send_request(text):
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=400.0) as client:
            response = await client.post(
                "http://localhost:5000/analyze",
                json={"text": text}
            )
            duration = round(time.perf_counter() - start, 2)
            print(f"✅ 입력: {text} | 소요 시간: {duration}초")
            print(f"➡️ 응답: {response.json()['result']['rewritten_text']}")
    except Exception as e:
        print(f"❌ 요청 실패: {text} | 오류: {type(e).__name__} - {str(e)}")

async def main():
    await asyncio.gather(
        send_request("씨발 뭐야 이거"),
        send_request("야 너 뭐하냐"),
        send_request("진짜 개열받네"),
        send_request("진짜 개열받네"),
    )

if __name__ == "__main__":
    asyncio.run(main())
