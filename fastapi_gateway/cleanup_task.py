from fastapi_gateway.database import SessionLocal, ApiKey
from datetime import datetime, timedelta

def cleanup_expired_api_keys():
    db = SessionLocal()
    now = datetime.utcnow()
    deleted_count = 0

    try:
        # 1. 24시간 내 미사용된 키 삭제
        threshold_7days = now - timedelta(days=7)
        expired_unused = db.query(ApiKey).filter(
            ApiKey.last_used == None,
            ApiKey.created_at < threshold_7days
        ).all()

        # 2. 발급일 기준 30일이 지난 키 (last_used 여부와 관계 없음)
        threshold_created_30days = now - timedelta(days=30)
        expired_created = db.query(ApiKey).filter(
            ApiKey.created_at < threshold_created_30days
        ).all()

        # 중복 제거 및 삭제 처리
        all_expired = set(expired_unused + expired_created)
        for entry in all_expired:
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