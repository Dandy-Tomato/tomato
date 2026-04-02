# 📦 프로젝트 인수인계 / 실행 가이드

## 1. GitLab 소스 클론 이후 빌드 및 배포 가이드

### 1-1. 기술 스택 및 환경 정보

| 구분            | 내용                                   |
| ------------- | ------------------------------------ |
| Language      | Java (Spring Boot), Python (FastAPI) |
| DB            | PostgreSQL (pgvector)                |
| Cache         | Redis                                |
| Message Queue | Kafka                                |
| Infra         | Docker, Docker Compose               |
| 인증            | OAuth (Google, GitHub)               |
| AI            | OpenAI API (embedding, GPT)          |

---

### 1-2. 실행 환경

```bash
# 필수
Docker
Docker Compose
```

---

### 1-3. 프로젝트 실행 방법

```bash
# 1. 레포 클론
git clone {REPO_URL}
cd {PROJECT_NAME}

# 2. 환경 변수 설정
cp .env.example .env

# 3. 컨테이너 실행
docker-compose -f compose.dev.yml up --build
```

---

### 1-4. 주요 서비스 포트

| 서비스                 | 포트   |
| ------------------- | ---- |
| Backend (Spring)    | 8080 |
| AI Server (FastAPI) | 8000 |
| PostgreSQL          | 5432 |
| Redis               | 6379 |
| Kafka               | 9092 |

---

### 1-5. JVM / WAS 정보

| 항목  | 값                           |
| --- | --------------------------- |
| JVM | OpenJDK 17                  |
| WAS | Spring Boot Embedded Tomcat |

---

## 2. 환경 변수 (Environment Variables)

### 2-1. Frontend

```env
VITE_API_BASE_URL=https://api.to-mato.site/
```

---

### 2-2. Backend (.env)

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tomato

KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_ACTION_LOG_TOPIC=recommendation.action-log
KAFKA_CONSUMER_GROUP=recommendation-consumer
```

---

### 2-3. AI Server

```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=tomato
DB_USER=postgres
DB_PASSWORD=postgres
```

## 3. 배포 시 특이사항

* Docker 기반 실행 필수
* Kafka / Redis / DB 선기동 필요
* `.env` 파일 반드시 설정 필요
* OpenAI API Key 없으면 추천 기능 동작 안함
* DB 초기 데이터 필요 (덤프 파일 참고)

---

## 4. 주요 설정 파일

| 파일                 | 설명                    |
| ------------------ | --------------------- |
| `.env`             | 환경 변수                 |
| `compose.dev.yml`  | 로컬 개발용 Docker Compose |
| `application.yml`  | Spring 설정             |
| `requirements.txt` | FastAPI 의존성           |

---

## 5. 외부 서비스 정보

### 5-1. OAuth

| 서비스    | 용도  |
| ------ | --- |
| Google | 로그인 |
| GitHub | 로그인 |

---

### 5-2. OpenAI

| 항목 | 내용                     |
| -- | ---------------------- |
| 모델 | text-embedding-3-small |
| 용도 | 주제 임베딩 생성              |

---

### 5-3. GitHub API

* 프로젝트 데이터 수집용

---

## 6. DB 정보

### 6-1. 주요 테이블

* users
* projects
* project_members
* recommendations
* action_logs

---

### 6-2. DB 덤프

```bash
# 복원
psql -U postgres -d tomato < dump.sql
```

---

## 7. 시연 시나리오

### 7-1. 회원가입 / 로그인

1. Google / GitHub 로그인
2. 사용자 정보 저장

---

### 7-2. 프로젝트 생성

1. 원하는 기업 선택
2. 기술 스택 선택
3. 팀 구성

---

### 7-3. 추천 기능

1. 프로젝트 정보 기반 추천 요청
2. AI 서버에서 임베딩 기반 추천 수행
3. 추천 결과 반환

---

### 7-4. 주제 구체화

1. 추천 주제 선택
2. 상세 설명 생성 (GPT 활용)

---

### 7-5. 사용자 행동 반영

* LIKE / DISLIKE / BOOKMARK 로그 저장
* Kafka → AI 서버 전달 → 추천 반영

---

## 8. 아키텍처 개요

```
[Frontend]
     ↓
[Spring Backend] ── Kafka ──> [FastAPI AI]
     ↓                          ↓
 PostgreSQL               Embedding / 추천
     ↓
 Redis
```