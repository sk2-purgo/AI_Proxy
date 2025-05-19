# fastapi_gateway/log_consumer.py

import redis
import json
import traceback

redis_conn = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def run_consumer():
    print("🟢 [log_consumer] filter-log 채널 구독 시작")

    try:
        pubsub = redis_conn.pubsub()
        pubsub.subscribe("filter-log")
        print("📡 Redis PubSub 구독 완료: filter-log")

        for message in pubsub.listen():
            print("📨 [RAW] 수신된 메시지:", message)

            if message["type"] != "message":
                print("❕ [무시] 메시지 타입:", message["type"])
                continue

            try:
                data = json.loads(message["data"])
                print("📩 필터링 로그 수신:", data)
                redis_conn.incr("filter:count")
            except Exception as e:
                print("❌ 로그 처리 실패:", str(e))
                traceback.print_exc()

    except KeyboardInterrupt:
        print("🛑 [log_consumer] Ctrl+C 감지됨. 안전하게 종료합니다.")
        pubsub.close()
        exit(0)

    except Exception as e:
        print("❌ Redis 연결 실패:", str(e))
        traceback.print_exc()

# ✅ 반드시 분리 실행만 가능하도록
if __name__ == "__main__":
    run_consumer()
