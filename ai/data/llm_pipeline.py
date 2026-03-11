"""
llm_pipeline.py
repo_embeddings 테이블의 readme를 LLM으로 분석해서 topics 테이블에 저장하는 파이프라인
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

TEST_MODE  = True   # True: 10개만 테스트, False: 전체 실행
BATCH_SIZE = 10 if TEST_MODE else 20
SLEEP_SEC  = 0.5    # API 호출 간격
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

# ── LLM 프롬프트 ───────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an expert software project analyst.
Given a GitHub repository README, extract structured information for a project topic recommendation system.

Return ONLY a valid JSON object with exactly these fields:
{
  "title": "concise project title in Korean (max 50 chars)",
  "description": "project description in Korean (2~4 sentences, what it does and what technologies are used)",
  "difficulty": <integer 1~5, 1=very easy, 5=very hard>,
  "expected_duration_week": <integer, estimated weeks to complete>,
  "recommended_team_size": <integer, recommended number of team members>
}

Rules:
- title and description MUST be in Korean
- difficulty: 1=간단한 CRUD, 5=AI/분산시스템/복잡한 아키텍처
- expected_duration_week: 1~24 범위
- recommended_team_size: 1~6 범위
- Return ONLY the JSON object, no markdown, no explanation
""".strip()


def load_done_ids(cur):
    """이미 topics에 저장된 repo_embeddings_id 로드 (source_repo_id 컬럼 기준)"""
    # topics 테이블에 source_repo_id가 없으면 title 중복 방지만 함
    # 처리 이력은 별도 processed_repos 세트로 관리
    cur.execute("SELECT source_repo_id FROM topics WHERE source_repo_id IS NOT NULL")
    return {row[0] for row in cur.fetchall()}


def fetch_repos(cur, done_ids, batch_size):
    """아직 처리 안 된 repo_embeddings 배치 가져오기"""
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


def analyze_with_llm(readme: str) -> dict | None:
    """LLM으로 README 분석 → JSON 반환"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"README:\n{readme[:3000]}"},  # 토큰 절약
            ],
            temperature=0.3,
            max_tokens=500,
        )
        text = response.choices[0].message.content.strip()
        # 혹시 ```json 블록으로 감싸진 경우 처리
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        print(f"  ❌ LLM 분석 실패: {e}")
        return None


def get_embedding(text: str) -> list | None:
    """description 임베딩 생성"""
    try:
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"  ❌ 임베딩 생성 실패: {e}")
        return None


def validate_result(result: dict) -> bool:
    """LLM 결과 유효성 검사"""
    required = ["title", "description", "difficulty", "expected_duration_week", "recommended_team_size"]
    for key in required:
        if key not in result:
            print(f"  ⚠️ 누락된 필드: {key}")
            return False

    if not (1 <= result["difficulty"] <= 5):
        result["difficulty"] = max(1, min(5, result["difficulty"]))
    if not (1 <= result["expected_duration_week"] <= 24):
        result["expected_duration_week"] = max(1, min(24, result["expected_duration_week"]))
    if not (1 <= result["recommended_team_size"] <= 6):
        result["recommended_team_size"] = max(1, min(6, result["recommended_team_size"]))

    return True


def save_topic(cur, repo_id: int, domain: str, result: dict, embedding: list | None):
    """topics 테이블에 저장"""
    domain_id = DOMAIN_MAP.get(domain)
    if domain_id is None:
        print(f"  ⚠️ 알 수 없는 domain: {domain} → it(3)으로 기본값 설정")
        domain_id = 3  # fallback: IT

    embedding_str = None
    if embedding:
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

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
    """, (
        result["title"],
        result["description"],
        result["difficulty"],
        result["expected_duration_week"],
        result["recommended_team_size"],
        embedding_str,
        domain_id,
        repo_id,
    ))


def main():
    print("🚀 llm_pipeline 시작")

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()

    # topics 테이블에 source_repo_id 컬럼 없으면 추가
    cur.execute("""
        ALTER TABLE topics
        ADD COLUMN IF NOT EXISTS source_repo_id BIGINT UNIQUE
    """)
    conn.commit()

    total_success = 0
    total_fail    = 0

    while True:
        done_ids = load_done_ids(cur)
        repos    = fetch_repos(cur, done_ids, BATCH_SIZE)

        if not repos:
            print("✅ 모든 레포 처리 완료!")
            break

        print(f"\n📦 배치 처리: {len(repos)}개 (완료: {len(done_ids)}개)")

        for repo_id, repo_name, domain, readme in repos:
            print(f"  🔍 [{repo_id}] {repo_name} (domain: {domain})")

            # 1. LLM 분석
            result = analyze_with_llm(readme)
            time.sleep(SLEEP_SEC)

            if not result or not validate_result(result):
                print(f"  ⏭️ 스킵")
                total_fail += 1
                continue

            # 2. description 임베딩
            embedding = get_embedding(result["description"])
            time.sleep(SLEEP_SEC)

            # 3. DB 저장
            try:
                save_topic(cur, repo_id, domain, result, embedding)
                conn.commit()
                total_success += 1
                print(f"  ✅ 저장 완료: {result['title']} (난이도: {result['difficulty']}, {result['expected_duration_week']}주, {result['recommended_team_size']}명)")
            except Exception as e:
                conn.rollback()
                print(f"  ❌ DB 저장 실패: {e}")
                total_fail += 1

        if TEST_MODE:
            print("\n🧪 TEST_MODE: 1배치만 실행 완료. 전체 실행하려면 TEST_MODE = False로 변경하세요.")
            break

    cur.close()
    conn.close()

    print(f"\n🎉 완료! 성공: {total_success}개, 실패: {total_fail}개")


if __name__ == "__main__":
    main()