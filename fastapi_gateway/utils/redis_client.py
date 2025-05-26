# fastapi_gateway/utils/redis_client.py

import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_conn = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=0,
    decode_responses=True
)

# ✅ 연결 확인용 (선택적)
print(" Redis 연결 성공:", redis_conn.ping())
