from fastapi_gateway.database import SessionLocal, ApiKey
from datetime import datetime, timedelta

def cleanup_expired_api_keys():
    db = SessionLocal()
    now = datetime.utcnow()
    deleted_count = 0

    try:
        # 1. 24시간 내 미사용된 키 삭제
        threshold_1day = now - timedelta(days=1)
        expired_never_used = db.query(ApiKey).filter(
            ApiKey.last_used == None,
            ApiKey.created_at < threshold_1day
        ).all()

        # 2. 마지막 사용이 30일 전인 키 삭제
        threshold_30days = now - timedelta(days=30)
        expired_long_unused = db.query(ApiKey).filter(
            ApiKey.last_used != None,
            ApiKey.last_used < threshold_30days
        ).all()

        # 삭제 처리
        for entry in expired_never_used + expired_long_unused:
            print(f"🗑️ 삭제 대상: {entry.api_key} (사용자: {entry.user_name})")
            db.delete(entry)
            deleted_count += 1

        db.commit()
        print(f"✅ 총 {deleted_count}개의 API 키 삭제 완료")
    except Exception as e:
        db.rollback()
        print("❌ 정리 중 오류:", str(e))
    finally:
        db.close()

# 직접 실행 시
if __name__ == "__main__":
    cleanup_expired_api_keys()
