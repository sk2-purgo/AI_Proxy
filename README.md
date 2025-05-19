# AI Proxy Server (FastAPI)

##  프로젝트 소개
- FastAPI 기반 인증 프록시 서버
- JWT 서명 및 API Key를 함께 검증
- Flask 기반 AI 서버로 요청 안전 전달

---

## 주요 기능

- 서버 간 JWT 서명 검증 (`X-Auth-Token`)
- API Key 인증 (`Authorization: Bearer {key}`)
- 요청 본문 해시 기반 위변조 검증
- 요청/응답 바이트 수 기록 (MySQL)
- Flask AI 서버로 요청 포워딩
- 비속어 분석 결과 전달

---

## 기술 스택

| 분류             | 사용 기술                   | 설명 |
|------------------|------------------------------|------|
| **API 프레임워크** | FastAPI                     | 비동기 처리에 최적화된 Python 기반 웹 프레임워크 |
| **인증 처리**      | HMAC 서명 기반 JWT + API Key | JWT와 API 키를 함께 사용해 보안성과 유연성 확보 |
| **데이터베이스**   | MySQL + SQLAlchemy          | ORM 기반 관계형 저장소로 API 사용 이력 관리에 적합 |
| **HTTP 클라이언트**| requests                    | FastAPI에서 Flask 서버로 요청 전달을 위한 HTTP 라이브러리 |
| **실행 환경**      | Python 3.10 이상             | FastAPI 등 주요 의존성과 호환되는 최소 실행 환경 |

---

##  설치 및 실행 방법

```bash
  # 의존성 설치
pip install fastapi,uvicorn,sqlalchemy,requests,pymysql,pyjwt,redis,typing-inspect,fastapi-utils
pip install sqlalchemy
pip install requests
pip install pymysql
pip install pyjwt
pip install redis
pip install typing-inspect
pip install fastapi-utils

  # FastAPI 실행
uvicorn fastapi_gateway.main:app --port 8001 --host 0.0.0.0 --http h11
```
---
```bash
  # 요청 예시
curl -X POST http://localhost:8001/proxy/analyze \
  -H "Authorization: Bearer dev-api-key" \
  -H "X-Auth-Token: <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"text": "비속어"}'

```
---

##  인증 흐름
```text
┌────────────┐
│클라이언트   │
└────┬───────┘
     ↓
Authorization: Bearer <API_KEY>
X-Auth-Token: <JWT>
     ↓
[FastAPI 프록시 서버]
     └→ API Key 유효성 확인
     └→ JWT 서명 검증
     └→ 해시 비교 (본문 무결성 확인)
     ↓
Flask AI 서버로 요청 전달
     ↓
응답 반환 및 usage_log 기록
```
---
## 사용 테이블 요약

api_keys: 등록된 API 키 목록 및 상태 (ACTIVE / REVOKED)

usage_log: 요청 이력, 엔드포인트, 바이트 크기 등 기록

---
##  디렉토리 구조

```text
fastapi_gateway/
├── main.py              # FastAPI 엔트리포인트
├── jwt_utils.py         # JWT 해시 검증 로직
├── models.py            # SQLAlchemy ORM 모델 정의
├── requirements.txt     # 의존성 목록
