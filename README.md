<div align="center">
    <h1>🍅 Tomato : AI 기반 프로젝트 주제 추천 서비스</h1>
    <p><b>삼성 청년 SW·AI 아카데미 14기</b></p>
    <p><b>특화 프로젝트 서울 5반 A508 </b></p>
</div>

---

![랜딩 페이지](docs/image/Landing.png)

<!-- ## 💡 프로젝트 소개

개발자 협업 파트너를 찾을 때 기술 스택만큼 중요한 것은 **업무 스타일과 개발 성향의 일치**입니다.  
**Handshake**는 단순한 이력 나열에서 벗어나, **DSTI(다차원 개발 성향 지표)** 테스트를 통해 사용자의 개발 스타일을 분석하고 이를 벡터화하여 최적의 동료를 추천합니다.

**스와이프 기반의 직관적인 UX**와 **실시간 사용자 행동 로그 분석**을 결합하여, 유저가 서비스를 이용할수록 더욱 정교하고 개인화된 네트워킹 경험을 제공하는 맞춤형 매칭 플랫폼입니다.

### 🎬 소개 영상 (Google Drive 바로가기)

[![Watch the video](docs/assets/image/thumbnail.png)](https://drive.google.com/file/d/1tUah4i2zK8bNwODaS_OBKnRJs6PDZsWM/view?usp=sharing) -->

---

## 📑 목차

1. [💡 프로젝트 소개](#-프로젝트-소개)
2. [💡 주요 기능 및 플랫폼](#-주요-기능-및-플랫폼)
3. [🗓️ 개발 일정](#️-개발-일정)
4. [📝 산출물](#-산출물)
5. [👨‍👩‍👧‍👦 개발 팀 소개](#-개발-팀-소개)
6. [🛠️ 기술 스택](#️-기술-스택)
7. [🖥️ 서비스 화면](#️-서비스-화면)
8. [📂 아키텍처 구조](#-아키텍처-구조)
9. [🏗️ 프로젝트 구조](#️-프로젝트-구조)

---

## 💡 주요 기능 및 플랫폼

<!-- `Handshake`는 **사용자 행동 로그 기반 실시간 벡터 매칭 엔진**을 활용한 **개발자 스와이프 네트워킹 서비스**입니다.  
기술 스택, 직무, 성향, 행동 데이터를 벡터로 표현해 **“잘 맞는 개발자”를 직관적으로 연결**합니다.

---

### 🤖 AI 기반 추천 · 매칭 엔진

#### 주요 역할

사용자의 **프로필 정보 + 실제 행동 로그**를 기반으로
개발자 간 **친화도 벡터를 실시간으로 계산**하고, 유사도 기반 매칭을 제공합니다.

#### 핵심 기능

- 🧠 **프로필 임베딩**
  - 직무, 기술 스택, 개발 성향, 상태(재직/구직 등)를 임베딩 벡터로 변환
  - Word2Vec 기반 하이브리드 학습 모델 활용

- 📊 **행동 로그 기반 선호도 업데이트**
  - 스와이프, 클릭, 좋아요 등 행동 로그를 수집
  - 행동에 따라 meta feature 가중치(weight) 실시간 조정

- 🔢 **벡터 유사도 매칭**
  - 사용자 선호 벡터 ↔ 상대 프로필 벡터 간 코사인 유사도 계산
  - Top-K 방식으로 추천 사용자 선별

- 📈 **직관적인 매칭 지표 제공**
  - 유사도를 퍼센트 형태로 변환하여 사용자 친화적으로 표현

---

### 📱 모바일 웹앱 (PWA, Next.js)

#### 주요 역할

개발자들이 **직관적으로 탐색·매칭·소통**할 수 있는 핵심 사용자 인터페이스

#### 핵심 기능

- 👉 **스와이프 기반 추천**
  - 추천된 개발자를 카드 형태로 제공
  - 좌/우 스와이프로 관심 표현

- 💬 **매칭 후 1:1 채팅**
  - 상호 관심 시 채팅방 자동 생성

- 🔔 **실시간 알림**
  - 매칭 성공, 채팅 요청, 알림 수신

- 📝 **프로필 관리**
  - 기술 스택, 자기소개, 상태 정보 수정
  - 수정 시 추천 벡터 자동 재계산 -->

---

## 🗓️ 개발 일정

### **개발 기간** : 2026.02.19 ~ 2026.03.30 **(5주)**

- **1주차 (2/23 ~ 3/1)**: 프로젝트 기획 및 기술 스택 선정
- **2주차 (3/2 ~ 3/8)**: 데이터 수집, 시스템 설계 및 와이어프레임 완성
- **3주차 (3/9 ~ 3/15)**: 기본 기능 구현 및 AI 모델 연동, 인프라 구축
- **4주차 (3/16 ~ 3/22)**: 세부 기능 구현 및 데이터 정제
- **5주차 (3/23 ~ 3/29)**: 테스트 및 배포
- **3/30**: 최종 프로젝트 발표

---

## 📝 산출물

<!-- ### 1. 🔗 [기획서](https://www.notion.so/2e9931677a2e80388958e7651e588a12?source=copy_link) -->

<!-- ### 2. 🔗 [기능 명세서](https://www.notion.so/2e9931677a2e800d9b3dd2436e2aea16?source=copy_link) -->

### 3. 🔗 [ERD](docs/image/ERD.png)

<!-- ### 4. 🔗 [API 문서](https://www.notion.so/API-2e3931677a2e81e2811fdd0527662c90?source=copy_link) -->

### 5. 🔗 [발표 자료](/docs/pdf/14기_특화PJT_발표자료_A508.pdf) -->

---

## 👨‍👩‍👧‍👦 개발 팀 소개

<div align="center">

### **😎 멋쟁이**

AI 기반 프로젝트 주제 추천 서비스 `Tomato`를 개발한 팀입니다.

</div>

---

<div align="center">

<table style="width: 100%; table-layout: fixed; border-collapse: collapse;">
  <tbody>
  <tr>

  <td align="center" valign="top" style="border: none; padding: 15px; width: 33.3%; word-break: keep-all;">
  <a href="https://github.com/LSH0707">
  <img src="docs/image/lsh_1.png" width="140px" alt="이승훈"/>
  </a>

  <b><sub>이승훈 (Team Leader)</sub></b>

  <sub><a href="https://github.com/LSH0707">@LSH0707</a></sub>

  <img src="https://img.shields.io/badge/Frontend-41B883?style=flat&logo=react&logoColor=white"/>

  <div align="left">
  <small>
  <ul>
  <li>[FE] </li>
  <li>[FE] </li>
  <li>[FE] </li>
  </ul>
  </small>
  </div>
  </td>

  <td align="center" valign="top" style="border: none; padding: 15px; width: 33.3%; word-break: keep-all;">
  <a href="https://github.com/moonhayun116">
  <img src="docs/image/mhy.png" width="140px" alt="문하윤"/>
  </a>

  <b><sub>문하윤</sub></b>

  <sub><a href="https://github.com/moonhayun116">@moonhayun116</a></sub>

  <img src="https://img.shields.io/badge/Data_Engineering-0A66C2?style=flat"/>

  <div align="left">
  <small>
  <ul>
  <li>[DT] </li>
  <li>[DT] </li>
  <li>[DT] </li>
  </ul>
  </small>
  </div>
  </td>

  <td align="center" valign="top" style="border: none; padding: 15px; width: 33.3%; word-break: keep-all;">
  <a href="https://github.com/nnnnnara">
  <img src="docs/image/snl.png" width="140px" alt="서나라"/>
  </a>

  <b><sub>서나라</sub></b>

  <sub><a href="https://github.com/nnnnnara">@nnnnnara</a></sub>

  <img src="https://img.shields.io/badge/Infra-FF9900?style=flat&logo=amazonaws&logoColor=white"/>

  <div align="left">
  <small>
  <ul>
  <li>[Infra] </li>
  <li>[Infra] </li>
  <li>[Infra] </li>
  </ul>
  </small>
  </div>
  </td>

  </tr>
  <tr>

  <td align="center" valign="top" style="border: none; padding: 15px; width: 33.3%; word-break: keep-all;">
  <a href="https://github.com/hyunjo01">
  <img src="docs/image/yhj.png" width="140px" alt="윤현조"/>
  </a>

  <b><sub>윤현조</sub></b>

  <sub><a href="https://github.com/hyunjo01">@hyunjo01</a></sub>

  <img src="https://img.shields.io/badge/Backend-0771A1?style=flat&logo=springboot&logoColor=white"/>

  <div align="left">
  <small>
  <ul>
  <li>[BE] </li>
  <li>[BE] </li>
  <li>[BE] </li>
  </ul>
  </small>
  </div>
  </td>

  <td align="center" valign="top" style="border: none; padding: 15px; width: 33.3%; word-break: keep-all;">
  <a href="https://github.com/seoliee">
  <img src="docs/image/lsh_2.png" width="140px" alt="이서현"/>
  </a>

  <b><sub>이서현</sub></b>

  <sub><a href="https://github.com/seoliee">@seoliee</a></sub>

  <img src="https://img.shields.io/badge/Data_Engineering-0A66C2?style=flat"/>
  <img src="https://img.shields.io/badge/AI-F78F1E?style=flat&logo=tensorflow&logoColor=white"/>
  <img src="https://img.shields.io/badge/Backend-0771A1?style=flat&logo=springboot&logoColor=white"/>

  <div align="left">
  <small>
  <ul>
  <li>[DE] </li>
  <li>[AI] </li>
  <li>[BE] </li>
  </ul>
  </small>
  </div>
  </td>

<td align="center" valign="top" style="border: none; padding: 15px; width: 33.3%; word-break: keep-all;">
  <a href="https://github.com/SngJuni">
    <img src="docs/image/hsj.png" width="140px" alt="황승준"/>
  </a>

  <b><sub>황승준</sub></b>

  <sub><a href="https://github.com/SngJuni">@SngJuni</a></sub>

  <img src="https://img.shields.io/badge/AI-F78F1E?style=flat&logo=openai&logoColor=white"/>
  <img src="https://img.shields.io/badge/Backend-0771A1?style=flat&logo=springboot&logoColor=white"/>

  <div align="left">
    <small>
      <ul>
        <li>[AI] OpenAI Embedding + pgvector 기반 추천 시스템 설계 및 구현</li>
        <li>[AI] 사용자 행동 로그 가중합 기반 선호 임베딩 생성 로직 설계</li>
        <li>[AI] FastAPI 기반 추천 엔진 구축 및 Kafka 이벤트 기반 실시간 갱신 처리</li>
        <li>[BE] Spring Boot ↔ FastAPI 구조 설계 및 추천 시스템 연동 API 구현</li>
        <li>[PM] 프로젝트 아키텍처 설계 및 전체 개발 일정 관리/기술 스택 선정 주도</li>
      </ul>
    </small>
  </div>
  </td>

  </tr>
  </tbody>
</table>

</div>

---

## 🛠️ 기술 스택

<a name="techStack"></a>

### 🌕 Frontend

<div align="center">

![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![JavaScript](https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E)<br>
![React Router](https://img.shields.io/badge/React_Router-CA4245?style=for-the-badge&logo=react-router&logoColor=white)
![React Markdown](https://img.shields.io/badge/React_Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white)
![ESLint](https://img.shields.io/badge/ESLint-4B3263?style=for-the-badge&logo=eslint&logoColor=white)

</div>

### 🔙 Backend

<div align="center">

![Java](https://img.shields.io/badge/Java-007396?style=for-the-badge&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=for-the-badge&logo=springboot&logoColor=white)
![Spring Data JPA](https://img.shields.io/badge/Spring_Data_JPA-6DB33F?style=for-the-badge&logo=spring&logoColor=white)
![Spring Batch](https://img.shields.io/badge/Spring_Batch-6DB33F?style=for-the-badge&logo=spring&logoColor=white)<br>
![Spring Security](https://img.shields.io/badge/Spring_Security-6DB33F?style=for-the-badge&logo=springsecurity&logoColor=white)
![OAuth2 Client](https://img.shields.io/badge/OAuth2_Client-EB5424?style=for-the-badge&logo=openid&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache_Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)

</div>

### 📦 Data Collection

<div align="center">

![GitHub API](https://img.shields.io/badge/GitHub_API-181717?style=for-the-badge&logo=github&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4B8BBE?style=for-the-badge)
![lxml](https://img.shields.io/badge/lxml-0C7DBE?style=for-the-badge)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)<br>
![undetected--chromedriver](https://img.shields.io/badge/undetected--chromedriver-4A4A4A?style=for-the-badge)
![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![tqdm](https://img.shields.io/badge/tqdm-FFC107?style=for-the-badge)

</div>

### 🤖 AI & Recommendation Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge)<br>
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-336791?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI_API-412991?style=for-the-badge&logo=openai&logoColor=white)

</div>

### ☁️ Infra & DevOps

<div align="center">

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white)<br>
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white)
![EC2](https://img.shields.io/badge/AWS_EC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Certbot](https://img.shields.io/badge/Certbot-003A8F?style=for-the-badge&logo=letsencrypt&logoColor=white)

</div>

### 🗄️ Database

<div align="center">

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

</div>

### 🛠️ Tools

<div align="center">

![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitLab](https://img.shields.io/badge/GitLab-FC6D26?style=for-the-badge&logo=gitlab&logoColor=white)
![Jira](https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=jira&logoColor=white)<br>
![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white)
![MatterMost](https://img.shields.io/badge/MatterMost-0072C6?style=for-the-badge&logo=mattermost&logoColor=white)

</div>

---

## 🖥️ 서비스 화면

<!-- ### 🔥 주요 기능 - 스와이프 및 채팅

<div align="center">
<table style="margin-left: auto; margin-right: auto;">
<tr>
<th align="center">👆 스와이프 매칭</th>
<th align="center">📊 만족도 설문</th>
</tr>
<tr>
<td align="center">
<img src="./docs/assets/gif/recommendation.gif" alt="스와이프 매칭" width="250">
</td>
<td align="center">
<img src="./docs/assets/gif/recommendationServey.gif" alt="만족도 설문" width="250">
</td>
</tr>
<tr>
<th align="center">🔔 실시간 알림</th>
<th align="center">💬 실시간 채팅</th>
</tr>
<tr>
<td align="center">
<img src="./docs/assets/gif/notification.gif" alt="실시간 알림" width="250">
</td>
<td align="center">
<img src="./docs/assets/gif/chat.gif" alt="실시간 채팅" width="250">
</td>
</tr>
</table>

</div>

### 🧭 온보딩 및 프로필

<div align="center">

<table style="margin-left: auto; margin-right: auto;">
<tr>
<th align="center">🔑 로그인</th>
<th align="center">📝 설문조사</th>
<th align="center">🧪 DSTI 테스트</th>
</tr>
<tr>
<td align="center">
<img src="./docs/assets/gif/login.png" alt="로그인" width="200">
</td>
<td align="center">
<img src="./docs/assets/gif/signupServey.gif" alt="설문조사" width="200">
</td>
<td align="center">
<img src="./docs/assets/gif/dstiTest.gif" alt="DSTI 테스트" width="200">
</td>
</tr>
<tr>
<th align="center">🏠 홈</th>
<th align="center">👤 마이페이지</th>
<th align="center">📄 DSTI 상세</th>
</tr>
<tr>
<td align="center">
<img src="./docs/assets/gif/main.gif" alt="메인" width="200">
</td>
<td align="center">
<img src="./docs/assets/gif/mypage.gif" alt="마이페이지" width="200">
</td>
<td align="center">
<img src="./docs/assets/gif/dstiDescription.gif" alt="DSTI 상세" width="200">
</td>
</tr>
</table>

</div> -->

---

## 📂 아키텍처 구조

### 🏗️ System Architecture Flow

![System Architecture](docs/image/architecture.png)

- **Traffic Routing:**  
  User → Nginx (Reverse Proxy) → Frontend (Vite + React) / Backend (Spring Boot)

- **Topic Data Pipeline (GitHub 기반):**  
  GitHub API → 주제 데이터 수집 → LLM(OpenAI) 기반 구조화 →  
  OpenAI Embedding 생성 → PostgreSQL(pgvector) 저장

- **Company Data Pipeline (크롤링 기반):**  
  Web Crawling → Spring Batch → 기업 데이터 정제 및 적재 → PostgreSQL 저장

- **Recommendation Engine (AI):**  
  주제 임베딩은 수집 시 최초 1회 생성하며,  
  사용자 행동 로그 기반 가중치(`w`)를 반영해 프로젝트 선호 임베딩을 가중합 방식으로 갱신합니다.

- **Similarity Search:**  
  프로젝트 선호 임베딩과 주제 임베딩 간 유사도를 계산하여 Top-K 추천 결과를 생성합니다.

- **Event Streaming:**  
  Backend → Kafka → 사용자 행동 로그 비동기 처리 및 선호 임베딩 갱신

- **Data Management:**  
  Backend ↔ PostgreSQL (RDB + pgvector), Redis (Cache)

- **DevOps:**  
  GitLab → Jenkins (CI/CD) → Docker / Docker Compose → AWS EC2 배포  
  Nginx + Certbot 기반 HTTPS 운영 환경 구성

---

### frontend - React 웹

<details>
<summary><strong>frontend/</strong></summary>

```text
frontend/
├── src/
│   ├── assets/                     # 이미지 및 정적 리소스
│   ├── components/
│   │   └── common/                 # 공통 UI 컴포넌트 (Navbar, Modal, Route 등)
│   ├── constants/                  # 전역 상수 정의
│   ├── pages/                      # 페이지 단위 폴더 구조
│   │   ├── Login/                  # 로그인 페이지
│   │   ├── Signup/                 # 회원가입 페이지
│   │   ├── Main/                   # 메인 추천 피드 페이지
│   │   ├── Profile/                # 사용자 프로필 관리
│   │   ├── ProjectCreate/          # 프로젝트 생성
│   │   ├── ProjectDetail/          # 프로젝트 상세 조회
│   │   └── Callback/               # OAuth 로그인 콜백 처리
│   ├── styles/                     # 전역 스타일
│   ├── utils/
│   │   └── fetchInterceptor.js     # API 요청 인터셉터 (토큰 처리, 공통 에러 처리)
│   ├── App.jsx                     # 라우팅 구성 (React Router)
│   └── main.jsx                    # Vite 엔트리 포인트
│
├── dist/                           # 빌드 결과물
├── Dockerfile                      # 프론트엔드 컨테이너 이미지 정의
├── nginx.conf                      # 정적 파일 서빙 및 라우팅 설정
├── Jenkinsfile                     # CI/CD 파이프라인 (빌드 및 배포 자동화)
├── package.json                    # 의존성 및 스크립트 관리
├── vite.config.js                  # Vite 번들링 설정
└── index.html                      # 앱 진입 HTML
```

</details>

### backend - Spring Boot 백엔드

<details>
<summary><strong>backend/</strong></summary>

```text
backend/
├── .gradle/                    # Gradle 캐시
├── .idea/                      # IntelliJ 설정 파일
├── build/                      # 빌드 결과물
├── gradle/                     # Gradle Wrapper
│
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── site/
│   │   │       └── to_mato/
│   │   │           ├── auth/           # 인증 및 소셜 로그인 (JWT, OAuth2)
│   │   │           ├── catalog/        # 직무/기술 스택 메타 정보 관리
│   │   │           ├── common/         # 공통 응답, 예외 처리, 보안 설정
│   │   │           ├── company/        # 기업 데이터 (크롤링 기반 데이터 관리)
│   │   │           ├── llm/            # OpenAI API 연동 및 프롬프트 처리
│   │   │           ├── project/        # 프로젝트 생성, 팀 빌딩, 상태 관리
│   │   │           ├── recommendation/ # Kafka 기반 이벤트 처리 및 추천 시스템 연동
│   │   │           ├── topic/          # 주제 데이터 관리 (임베딩 대상)
│   │   │           ├── user/           # 사용자 정보 및 선호 데이터 관리
│   │   │           └── ToMatoApplication.java
│   │   │
│   │   └── resources/
│   │       └── application.yml         # 환경 설정 (DB, Redis, Kafka 등)
│   │
│   └── test/
│       └── java/
│           └── site/
│               └── to_mato/
│                   └── ToMatoApplicationTests.java
│
├── build.gradle                # 의존성 및 빌드 설정 (JPA, Kafka, Redis 등)
├── settings.gradle             # 프로젝트 설정
├── gradlew                     # Gradle Wrapper (Unix)
├── gradlew.bat                 # Gradle Wrapper (Windows)
├── Dockerfile                  # 백엔드 컨테이너 이미지 정의
├── Jenkinsfile                 # CI/CD 파이프라인 (빌드 및 배포 자동화)
└── README.md
```

</details>

### ai - 사용자 행동 로그 기반 벡터 추천 엔진

<details>
<summary><strong>ai/</strong></summary>

```text
ai/
├── app/
│   ├── common/                 # 공통 설정 및 예외 처리, 로깅
│   ├── consumer/               # Kafka 컨슈머 (행동 로그 기반 선호 임베딩 갱신)
│   ├── repositories/           # DB 접근 계층 (PostgreSQL, Redis)
│   ├── routers/                # FastAPI API 엔드포인트 (추천, 내부 처리)
│   ├── schemas/                # 요청/응답 데이터 모델 (Pydantic)
│   ├── services/               # 추천 로직 및 벡터 연산 (가중합 기반 선호 임베딩)
│   ├── utils/                  # 공용 유틸 (벡터 연산, 거리 계산 등)
│   ├── db.py                   # DB 및 Redis 세션 관리
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   └── settings.py             # 환경 변수 및 설정 관리
│
├── data/                       # 데이터 수집 및 전처리/임베딩 파이프라인
│   ├── collect_repos.py        # GitHub API 기반 주제 데이터 수집
│   ├── preprocess_readme.py    # README 전처리 및 토큰 최적화
│   ├── llm_pipeline.py         # OpenAI 기반 데이터 구조화
│   ├── embed_pipeline.py       # OpenAI Embedding 생성 및 저장
│   ├── enrich_repos.py         # 메타데이터 보강
│   └── collect_nostar_repos.py # 추가 데이터 수집 (조건 기반)
│
├── Dockerfile                  # AI 서버 컨테이너 이미지 정의
├── Jenkinsfile                 # CI/CD 파이프라인 (빌드 및 배포)
├── requirements.txt            # Python 의존성 관리
└── README.md
```

</details>

### crawler - 기업 데이터 수집 및 정제 파이프라인

<details>
<summary><strong>crawler/</strong></summary>

```text
crawler/
├── config/                     # 크롤링 설정 (산업군, 검색 조건 등)
│
├── crawler/                    # 크롤링 및 데이터 처리 로직
│   ├── discover_new_jobs.py    # 신규 데이터 탐색
│   ├── collect_new_job_details.py # 상세 정보 수집
│   ├── preprocess_new_jobs.py  # 신규 데이터 정제
│   ├── preprocess_incremental_jobs.py # 증분 데이터 정제
│   └── common.py               # 공통 유틸 및 HTTP 처리
│
├── data/                       # 크롤링 상태 및 중간 데이터 저장
│
├── db_ready/                   # DB 적재를 위한 최종 가공 데이터 (CSV)
│   ├── companies.csv           # 기업 정보
│   ├── skills.csv              # 기술 스택
│   ├── company_skills.csv      # 기업-기술 매핑
│   ├── company_skill_pairs.csv # 상세 매핑 정보
│   └── domains.csv             # 직무/도메인 정보
│
├── run_all.py                  # 수집 → 정제 → 적재 준비 전체 파이프라인 실행
├── init_preprocess_all.py      # 초기 데이터 일괄 정제
├── rerun_preprocess_yesterday.py # 증분 데이터 재처리
│
├── Dockerfile                  # 크롤러 실행 환경 정의
├── requirements.txt            # Python 의존성
└── README.md
```

</details>

---

<div align="center">
  <p>🍅 <strong>Tomato</strong> - AI 기반 프로젝트 주제 추천 서비스</p>
</div>
