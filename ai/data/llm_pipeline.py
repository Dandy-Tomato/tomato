"""
llm_pipeline.py
repo_embeddings 테이블의 readme를 LLM으로 분석해서
topics + topic_skills 테이블에 저장하는 파이프라인

처리 방식: 레포 1개씩 LLM 호출 + 레포 단위 커밋
- 1개 실패해도 나머지에 영향 없음
- 중단 후 재실행 시 source_repo_id UNIQUE로 이어서 처리
"""

import os
import json
import time
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── 설정 ──────────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME", "tomato"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

TEST_MODE  = False   # True: 20개만 테스트, False: 전체 실행
BATCH_SIZE = 20     # DB fetch 단위 (LLM은 1개씩 호출)
SLEEP_SEC  = 0.5    # API 호출 간격 (GMS 크레딧 보호)
MODEL       = "gpt-4.1-nano"
EMBED_MODEL = "text-embedding-3-small"

# domain 텍스트 → domain_id 매핑 (domains 테이블 기준)
DOMAIN_MAP = {
    "service":      1,
    "finance":      2,
    "it":           3,
    "retail":       4,
    "manufacturing":5,
    "construction": 6,
    "healthcare":   7,
    "education":    8,
    "media":        9,
    "culture":      10,
    "institution":  11,
}

# ── OpenAI 클라이언트 ──────────────────────────────────────────────────────────
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1/",
)

# ── Skills 목록 (DB의 skills 테이블과 1:1 대응) ────────────────────────────────
# LLM이 이 목록에서만 기술을 선택하도록 프롬프트에 직접 주입
# skills 테이블 변경 시 이 목록도 함께 업데이트할 것
SKILLS_LIST = [
    "API", "ASP.NET", "AWS", "Ajax", "Android", "Android Studio", "Angular",
    "Ansible", "Azure", "C", "C#", "C/C++", "CAN", "CSS", "DBMS", "Django",
    "Docker", "Embedded", "Embedded Linux", "FastAPI", "Flask", "Flutter",
    "GCP", "Git", "GitHub", "GitLab", "Google Analytics", "Google Optimize",
    "HTML", "JPA", "JSP", "Java", "JavaScript", "Jenkins", "Kafka", "Kotlin",
    "Kubernetes", "LLM", "Laravel", "Linux", "MQTT", "MSA", "MSSQL", "MariaDB",
    "MongoDB", "MyBatis", "MySQL", "NestJS", "Nexacro", "Next.js", "NoSQL",
    "Node.js", "NumPy", "OpenCV", "Oracle", "PHP", "Pandas", "PostgreSQL",
    "PyTorch", "Python", "R", "RAG", "RDBMS", "REST API", "ROS", "ROS2",
    "RTOS", "Raspberry Pi", "React", "React Native", "Redis", "SPSS", "SQL",
    "SaaS", "Scikit-learn", "Spring", "Spring Batch", "Spring Boot",
    "Spring MVC", "Spring Security", "Swift", "Tableau", "TensorFlow",
    "Terraform", "Tibero", "TypeScript", "Unix", "VMware", "Vue.js", "WAS",
    "WebSquare", "iOS", "jQuery", "Nuxt.js", "Svelte", "Tailwind CSS",
    "Express.js", "Go", "Rust", "Ruby on Rails", "Elasticsearch", "Firebase",
    "Supabase", "GraphQL", "gRPC", "GitHub Actions", "Nginx", "RabbitMQ",
    "WebSocket", "OAuth2", "JWT", "LangChain", "OpenAI API", "Spark",
    "Airflow", "Prometheus", "Grafana", "Arduino",
]
_SKILLS_LIST_STR = ", ".join(f'"{s}"' for s in SKILLS_LIST)

# ── LLM 프롬프트 ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""
You are an expert software project analyst.
Given a GitHub repository README, extract structured information for a project topic recommendation system.

Return ONLY a valid JSON object with exactly these fields:
{{
  "title": "concise project title in Korean (max 50 chars)",
  "description": "project description in Korean (2~4 sentences, what it does and what technologies are used)",
  "difficulty": <integer 1~5, 1=very easy, 5=very hard>,
  "expected_duration_week": <integer, estimated weeks to complete>,
  "recommended_team_size": <integer, recommended number of team members>,
  "tech_stack": ["tech1", "tech2", ...]
}}

Rules:
- title and description MUST be in Korean
- difficulty: 1=간단한 CRUD, 5=AI/분산시스템/복잡한 아키텍처
- expected_duration_week: 1~24 범위
- recommended_team_size: 1~6 범위
- tech_stack: 아래 허용 목록에서만 선택 (목록에 없는 기술은 절대 사용 금지), 최대 10개
  허용 목록: {_SKILLS_LIST_STR}
- Return ONLY the JSON object, no markdown, no explanation
""".strip()


# ── DB 유틸 ───────────────────────────────────────────────────────────────────

def load_done_ids(cur) -> set:
    """이미 topics에 저장된 source_repo_id 로드"""
    cur.execute("SELECT source_repo_id FROM topics WHERE source_repo_id IS NOT NULL")
    return {row[0] for row in cur.fetchall()}


def fetch_repos(cur, done_ids: set, batch_size: int) -> list:
    """아직 처리 안 된 repo_embeddings 가져오기"""
    if done_ids:
        cur.execute("""
            SELECT repo_embeddings_id, repo_full_name, domain, readme
            FROM repo_embeddings
            WHERE repo_embeddings_id != ALL(%s)
              AND readme IS NOT NULL
              AND domain IS NOT NULL
            ORDER BY repo_embeddings_id
            LIMIT %s
        """, (list(done_ids), batch_size))
    else:
        cur.execute("""
            SELECT repo_embeddings_id, repo_full_name, domain, readme
            FROM repo_embeddings
            WHERE readme IS NOT NULL
              AND domain IS NOT NULL
            ORDER BY repo_embeddings_id
            LIMIT %s
        """, (batch_size,))
    return cur.fetchall()


def load_skills(cur) -> dict:
    """skills 테이블 전체 로드 → {소문자 name: skill_id}"""
    cur.execute("SELECT skill_id, name FROM skills ORDER BY skill_id")
    rows = cur.fetchall()
    skill_map = {name.lower(): skill_id for skill_id, name in rows}
    print(f"📚 skills 로드 완료: {len(skill_map)}개")
    return skill_map


# ── LLM / 임베딩 호출 ─────────────────────────────────────────────────────────

def analyze_with_llm(readme: str) -> dict | None:
    """README → LLM → JSON 반환"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"README:\n{readme[:3000]}"},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        print(f"  ❌ LLM 분석 실패: {e}")
        return None


def get_embedding(text: str) -> list | None:
    """description 임베딩 생성"""
    try:
        response = client.embeddings.create(model=EMBED_MODEL, input=text)
        return response.data[0].embedding
    except Exception as e:
        print(f"  ❌ 임베딩 생성 실패: {e}")
        return None


# ── 유효성 검사 ───────────────────────────────────────────────────────────────

def validate_result(result: dict) -> bool:
    """LLM 결과 유효성 검사 및 범위 클램핑"""
    required = ["title", "description", "difficulty", "expected_duration_week", "recommended_team_size"]
    for key in required:
        if key not in result:
            print(f"  ⚠️ 누락된 필드: {key}")
            return False

    result["difficulty"]             = max(1, min(5,  result["difficulty"]))
    result["expected_duration_week"] = max(1, min(24, result["expected_duration_week"]))
    result["recommended_team_size"]  = max(1, min(6,  result["recommended_team_size"]))

    if "tech_stack" not in result or not isinstance(result["tech_stack"], list):
        result["tech_stack"] = []

    return True


# ── DB 저장 ───────────────────────────────────────────────────────────────────

def save_topic(cur, repo_id: int, domain: str, result: dict, embedding: list | None) -> int | None:
    """topics 테이블에 저장 → topic_id 반환"""
    domain_id = DOMAIN_MAP.get(domain, 3)
    if domain not in DOMAIN_MAP:
        print(f"  ⚠️ 알 수 없는 domain: {domain} → it(3) 기본값 사용")

    embedding_str = ("[" + ",".join(map(str, embedding)) + "]") if embedding else None

    cur.execute("""
        INSERT INTO topics
            (title, description, difficulty, expected_duration_week,
             recommended_team_size, topic_embedding, domain_id, source_repo_id)
        VALUES (%s, %s, %s, %s, %s, %s::vector, %s, %s)
        ON CONFLICT (source_repo_id) DO UPDATE SET
            title                  = EXCLUDED.title,
            description            = EXCLUDED.description,
            difficulty             = EXCLUDED.difficulty,
            expected_duration_week = EXCLUDED.expected_duration_week,
            recommended_team_size  = EXCLUDED.recommended_team_size,
            topic_embedding        = EXCLUDED.topic_embedding,
            domain_id              = EXCLUDED.domain_id
        RETURNING topic_id
    """, (
        result["title"], result["description"], result["difficulty"],
        result["expected_duration_week"], result["recommended_team_size"],
        embedding_str, domain_id, repo_id,
    ))
    row = cur.fetchone()
    return row[0] if row else None


def save_topic_skills(cur, topic_id: int, tech_stack: list, skill_map: dict):
    """topic_skills 테이블에 기술스택 저장"""
    if not tech_stack:
        return

    matched, unmatched = [], []
    for tech in tech_stack:
        skill_id = skill_map.get(tech.lower())
        if skill_id:
            matched.append(skill_id)
        else:
            unmatched.append(tech)

    if unmatched:
        print(f"    ⚠️ 매칭 실패 기술: {unmatched}")

    for skill_id in matched:
        cur.execute("""
            INSERT INTO topic_skills (topic_id, skill_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (topic_id, skill_id))

    print(f"    🔗 topic_skills: {len(matched)}개 저장 / {len(tech_stack)}개 추출")


# ── 메인 ──────────────────────────────────────────────────────────────────────

def main():
    print("🚀 llm_pipeline 시작")

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()

    # topics 테이블에 source_repo_id 컬럼 없으면 추가
    cur.execute("ALTER TABLE topics ADD COLUMN IF NOT EXISTS source_repo_id BIGINT UNIQUE")
    conn.commit()

    skill_map = load_skills(cur)

    total_success = 0
    total_fail    = 0

    while True:
        done_ids = load_done_ids(cur)
        repos    = fetch_repos(cur, done_ids, BATCH_SIZE)

        if not repos:
            print("✅ 모든 레포 처리 완료!")
            break

        print(f"\n📦 {len(repos)}개 처리 시작 (누적 완료: {len(done_ids)}개)")

        for repo_id, repo_name, domain, readme in repos:
            print(f"  🔍 [{repo_id}] {repo_name} (domain: {domain})")

            # 1. LLM 분석
            result = analyze_with_llm(readme)
            time.sleep(SLEEP_SEC)

            if not result or not validate_result(result):
                print(f"  ⏭️ 스킵")
                total_fail += 1
                continue

            # 2. 임베딩
            embedding = get_embedding(result["description"])
            time.sleep(SLEEP_SEC)

            # 3. DB 저장 — 레포 단위 커밋 (1개 실패가 다른 레포에 영향 없음)
            try:
                topic_id = save_topic(cur, repo_id, domain, result, embedding)
                if topic_id and result.get("tech_stack"):
                    save_topic_skills(cur, topic_id, result["tech_stack"], skill_map)
                conn.commit()
                total_success += 1
                print(
                    f"  ✅ {result['title']} "
                    f"(난이도:{result['difficulty']}, "
                    f"{result['expected_duration_week']}주, "
                    f"{result['recommended_team_size']}명)"
                )
            except Exception as e:
                conn.rollback()
                print(f"  ❌ DB 저장 실패: {e}")
                total_fail += 1

        if TEST_MODE:
            print(f"\n🧪 TEST_MODE 완료. 전체 실행하려면 TEST_MODE = False")
            break

    cur.close()
    conn.close()
    print(f"\n🎉 완료! 성공: {total_success}개, 실패: {total_fail}개")


if __name__ == "__main__":
    main()