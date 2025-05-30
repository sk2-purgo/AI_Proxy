import redis
import json
import traceback
from fastapi_gateway.database import SessionLocal, BadWord, ApiKey

# Redis 연결
redis_conn = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def run_consumer():
    print("🟢 [log_consumer] filter-log, badword-log, abuse-log, revoke-log 채널 구독 시작")

    try:
        pubsub = redis_conn.pubsub()
        pubsub.subscribe("filter-log", "badword-log", "abuse-log", "revoke-log")
        print("📡 Redis PubSub 구독 완료: filter-log, badword-log, abuse-log, revoke-log")

        for message in pubsub.listen():
            if message["type"] != "message":
                print("❕ [무시] 메시지 타입:", message["type"])
                continue

            channel = message["channel"]
            data = message["data"]

            try:
                # ✅ 필터링 로그 카운터 증가
                if channel == "filter-log":
                    log = json.loads(data)
                    print("📩 필터링 로그 수신:", log)
                    redis_conn.incr("filter:count")

                # ✅ 욕설 단어 리스트 DB 저장
                elif channel == "badword-log":
                    word_list = json.loads(data)
                    print("📩 욕설 단어 수신:", word_list)

                    db = SessionLocal()
                    try:
                        for word in word_list:
                            existing = db.query(BadWord).filter_by(word=word).first()
                            if existing:
                                existing.count += 1
                            else:
                                db.add(BadWord(word=word, count=1))
                        db.commit()
                        print("✅ badwords 테이블 갱신 완료")
                    except Exception as e:
                        db.rollback()
                        print("❌ badwords 처리 실패:", str(e))
                        traceback.print_exc()
                    finally:
                        db.close()

                # ✅ abuse count 증가
                elif channel == "abuse-log":
                    api_key = data.strip()
                    print("📩 abuse-log 수신:", api_key)

                    db = SessionLocal()
                    try:
                        entry = db.query(ApiKey).filter_by(api_key=api_key).first()
                        if entry:
                            entry.abuse_count = (entry.abuse_count or 0) + 1
                            db.commit()
                            print("✅ abuse_count 증가 완료")
                        else:
                            print("❌ API Key 조회 실패:", api_key)
                    except Exception as e:
                        db.rollback()
                        print("❌ abuse_count 처리 실패:", str(e))
                        traceback.print_exc()
                    finally:
                        db.close()

                # ✅ REVOKED 감지 시 Redis 캐시 삭제
                elif channel == "revoke-log":
                    api_key = data.strip()
                    print(f"📩 revoke-log 수신: {api_key}")
                    redis_conn.delete(f"jwt:secret:{api_key}")
                    redis_conn.delete(f"api_key:{api_key}")
                    print(f"🧯 Redis 캐시 삭제 완료: {api_key}")

            except Exception as e:
                print("❌ 메시지 처리 실패:", str(e))
                traceback.print_exc()

    except KeyboardInterrupt:
        print("🛑 [log_consumer] Ctrl+C 감지됨. 안전하게 종료합니다.")
        pubsub.close()
        exit(0)

    except Exception as e:
        print("❌ Redis 연결 실패:", str(e))
        traceback.print_exc()

# ✅ 반드시 단독 실행만 가능
if __name__ == "__main__":
    run_consumer()
