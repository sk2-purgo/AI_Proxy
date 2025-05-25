from fastapi import Request
from fastapi_gateway.database import SessionLocal, ApiKey

def increment_abuse_count(request: Request):
    db = SessionLocal()
    try:
        raw_token = request.headers.get("authorization", "")
        if raw_token.startswith("Bearer "):
            api_key = raw_token.replace("Bearer ", "")
            key_entry = db.query(ApiKey).filter_by(api_key=api_key).first()
            if key_entry:
                key_entry.abuse_count = (key_entry.abuse_count or 0) + 1
                db.commit()
            else:
                print("❌ 해당 API Key로 DB 조회 실패")
    except Exception as e:
        print("❌ abuse_count 증가 실패:", str(e))
        db.rollback()
    finally:
        db.close()