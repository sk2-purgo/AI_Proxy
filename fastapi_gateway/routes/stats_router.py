# fastapi_gateway/routes/stats_router.py

from fastapi import APIRouter
from fastapi_gateway.database import SessionLocal, BadWord, ApiKey

router = APIRouter()


# 1. 욕 종류별 count 목록 조회 API
@router.get("/badwords")
def get_badword_list():
    db = SessionLocal()
    try:
        badwords = db.query(BadWord).all()
        result = [{"word": bw.word, "count": bw.count} for bw in badwords]
        return {"badwords": result}
    finally:
        db.close()


# 2. abuse_count 총합 조회 API
@router.get("/abuse-total")
def get_abuse_total():
    db = SessionLocal()
    try:
        abuse_counts = db.query(ApiKey.abuse_count).all()
        abuse_sum = sum(a.abuse_count or 0 for a in abuse_counts)
        return {"total_abuse_count": abuse_sum}
    finally:
        db.close()
