import json
import uuid
from datetime import datetime
from fastapi_gateway.utils.redis_client import redis_conn


# ✅ 1. 필터링 로그 발행 (기존과 동일)
def publish_filter_log(user_id: str, original_text: str, filtered_text: str):
    log_payload = {
        "logId": str(uuid.uuid4()),
        "userId": user_id or "anonymous",
        "originalText": original_text,
        "filteredText": filtered_text,
        "timestamp": datetime.utcnow().isoformat()
    }
    print("📤 [프록시] Redis에 로그 발행 준비:", log_payload)
    redis_conn.publish("filter-log", json.dumps(log_payload))
    print("📤 [프록시] Redis에 발행 완료")


# ✅ 2. abuse 카운트 증가 요청 발행
def publish_abuse_count(api_key: str):
    print(f"📤 [프록시] abuse-log 채널에 API 키 발행: {api_key}")
    redis_conn.publish("abuse-log", api_key)


# ✅ 3. 욕설 단어 리스트 발행
def publish_badwords(word_list: list[str]):
    if not word_list:
        return
    print(f"📤 [프록시] badword-log 채널에 욕설 단어 발행: {word_list}")
    redis_conn.publish("badword-log", json.dumps(word_list))
