![header](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=header&text=PROXY&fontSize75&animation=fadeIn&fontColor=FFF)
<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688.svg?&style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-000000.svg?&style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C.svg?&style=for-the-badge&logo=pytorch&logoColor=white"/>
  <img src="https://img.shields.io/badge/Transformers-FFBF00.svg?&style=for-the-badge&logo=huggingface&logoColor=black"/>
  <img src="https://img.shields.io/badge/GluonNLP-0F92A1.svg?&style=for-the-badge&logo=mxnet&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastText-005571.svg?&style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenAI-412991.svg?&style=for-the-badge&logo=openai&logoColor=white"/>
  <img src="https://img.shields.io/badge/SentencePiece-3C78D8.svg?&style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Scikit--learn-F7931E.svg?&style=for-the-badge&logo=scikit-learn&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-150458.svg?&style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/matplotlib-11557C.svg?&style=for-the-badge&logo=plotly&logoColor=white"/>
  <img src="https://img.shields.io/badge/pdfkit-333333.svg?&style=for-the-badge&logo=pdf&logoColor=white"/>
</div>

# AI Proxy Server (FastAPI)

##  프로젝트 소개


##### 이 서비스는 외부 요청을 인증하고 분석 요청을 중계하는 SaaS 형태의 욕설 필터링 API 게이트웨이입니다.
##### JWT 해시 서명 + API Key 이중 인증, SHA-256 본문 해시 검증으로 보안성과 무결성을 확보합니다.
##### Redis Pub/Sub을 통해 비속어 횟수와 필터링 로그를 자동으로 발행하며, 통계와 로그 관리 과정을 실시간으로 자동화합니다
##### 요청 대상(chat/community)에 따라 Flask KoBERT AI 서버로 분기하며, 욕설 판단 결과에 따라 로그 후처리까지 수행합니다. ####
---

## 주요 기능

- API Key와 JWT 기반 이중 인증 처리
    - Redis 또는 DB에서 API Key 유효성 확인
    - JWT 서명(HMAC-SHA256) 및 본문 SHA-256 해시값 검증
    - Redis 캐시가 존재할 경우 해시 검증 생략하여 속도 최적화


- 요청 대상(chat / community)에 따라 Flask AI 서버로 비동기 요청 포워딩
    - FastAPI → httpx 기반 비동기 호출
    - AI 서버에서 KoBERT 기반 분석 수행


- 분석 결과 후처리
    - fasttext 기반 욕설 단어 추출
    - KoBERT 기반 최종 판단(`final_decision`: 0=정상, 1=욕설)
    - `result.rewritten_text`에 정제된 문장 포함


- Redis Pub/Sub 로그 발행 (필터링 통계용)
    - `filter-log`: 필터링 요청/결과 기록
    - `badword-log`: 탐지된 욕설 단어 리스트
    - `abuse-log`: 욕설 판정 시 API Key 발행
    - `revoke-log`: REVOKED 키에 대한 캐시 삭제 알림


- `log_consumer.py`를 통한 Redis 로그 수신 및 후처리
    - 욕설 단어 카운트 DB 반영 (`badwords`)
    - abuse 횟수 누적 (`abuse_count`)
    - `revoke-log` 수신 시 Redis 캐시 즉시 삭제


- API Key 자동 정리 기능
    - 30일 이상 경과 또는 7일 이상 미사용 시 DB에서 자동 제거



---

## 기술 스택

| 분류             | 사용 기술                            | 설명 |
|------------------|----------------------------------------|------|
| **API 프레임워크** | FastAPI                              | 비동기 처리에 최적화된 Python 기반 REST API 프레임워크 |
| **인증 처리**      | JWT (pyjwt) + API Key                | API Key와 HMAC-SHA256 기반 JWT 서명을 함께 검증하는 이중 인증 구조 |
| **데이터베이스**   | MySQL + SQLAlchemy + pymysql        | 욕설 탐지 기록 및 abuse 카운트 통계를 저장하는 관계형 DB 및 ORM |
| **HTTP 클라이언트**| httpx                                | Flask AI 서버로 비속어 분석 요청을 비동기로 전송 |
| **캐시/메시징**    | Redis + Pub/Sub (`redis-py`)        | 인증 캐시 관리 및 로그 이벤트(filter-log, abuse-log 등) 실시간 발행 |
| **작업 스케줄링**  | fastapi-utils (`@repeat_every`)      | 미사용 API Key를 정기적으로 정리하는 스케줄러 구성 |
| **환경 변수 관리** | python-dotenv                        | `.env` 파일 기반으로 환경 설정 및 민감 정보 외부화 |
| **언어 및 버전**   | Python 3.10                          | 전체 시스템 구현 및 라이브러리 호환 기준 버전 |


---

##  설치 및 실행 방법

```bash
  # 의존성 설치
pip install -r requirements.txt
```
requirements.txt 기준 주요 패키지:

- fastapi

- uvicorn

- pyjwt

- httpx

- redis

- python-dotenv

- sqlalchemy

- pymysql

- fastapi-utils

## FastAPI 실행
```
uvicorn fastapi_gateway.main:app --port 8001 --host 0.0.0.0 --http h11
```

## Pub/Sub 구독 실행
```
python -m fastapi_gateway.Log_consumer
```
---

  ## 외부 서버 요청 예시
```
curl -X POST http://외부 서버 주소:8001/proxy/analyze/target{community,chat 중 택 1} \
  -H "Authorization: Bearer {API_KEY}" \
  -H "X-Auth-Token: {JWT}" \
  -H "Content-Type: application/json" \
  -d '{"text": "비속어"}'

```


## 외부 서버 응답 예시

```
{
  "result": {
    "original_text": "원본",
    "rewritten_text": "대체 문장"
  },
  "final_decision": 0,1 ( 욕설 여부 )
}

```
---

##  인증 흐름
```text
┌────────────┐
│ 클라이언트  │
└────┬───────┘
     ↓
 Authorization: Bearer <API_KEY>
 X-Auth-Token: <JWT>
     ↓
     
FastAPI 프록시 서버

① API_KEY 추출  
② JWT 추출  
③ Redis 캐시 조회  
   - 있음  → JWT 서명만 검증 (해시 생략)  
   - 없음  → DB 조회 + 해시 검증  
     - status가 ACTIVE인지 확인  
     - JWT 서명 + 본문 SHA256 해시 검증  
     - Redis에 시크릿 키 캐시 (TTL = 5분)

     ↓

Flask AI 서버로 요청 포워딩 (httpx 비동기)

     ↓

AI 응답 수신

     ↓

결과 후처리  
- result 반환
- Redis Pub/Sub 로그 발행
  - filter-log
  - abuse-log (final_decision=1일 경우)
  - badword-log (fasttext 감지 단어)
  - revoke-log (DB에서 상태 변경 감지 시)
```
---
##  디렉토리 구조

```text
fastapi_gateway/
├── main.py
├── routes/
│   ├── key_issuer.py
│   ├── stats_router.py
├── services/
│   ├── analyze_service.py
│   ├── auth_service.py
├── utils/
│   ├── jwt_utils.py
│   ├── log_publisher.py
├── middlewares/
│   ├── auth_middleware.py
├── database.py
├── Log_consumer.py
├── cleanup_task.py
├── .env
├── requirements.txt
