"""
토매토 - GitHub 데이터 임베딩 파이프라인
실행 순서: 도메인 분류 → 임베딩 생성 → PostgreSQL 저장

실행 방법:
    python data/embed_pipeline.py
"""

import json
import time
import os
import psycopg2
from datetime import timedelta
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ================================
# 설정값 — .env에서 자동으로 읽어옴
# ================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_HOST        = os.getenv("DB_HOST", "localhost")
DB_PORT        = int(os.getenv("DB_PORT", 5432))
DB_NAME        = os.getenv("DB_NAME", "tomato")
DB_USER        = os.getenv("DB_USER", "postgres")
DB_PASSWORD    = os.getenv("DB_PASSWORD")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE     = os.path.join(BASE_DIR, "repos_preprocessed.jsonl")
EMBED_MODEL    = "text-embedding-3-small"

# ================================
# 도메인 목록 (DB 값 기준)
# ================================
DOMAIN_LIST = [
    "service",       # 서비스
    "finance",       # 금융·은행
    "it",            # IT·정보통신
    "retail",        # 판매·유통
    "manufacturing", # 제조·생산·화학
    "construction",  # 건설
    "healthcare",    # 의료·제약
    "education",     # 교육
    "media",         # 미디어·광고
    "culture",       # 문화·예술·디자인
    "institution",   # 기관·협회
]

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1/"
    )


# ================================
# STEP 1. 도메인 분류 (LLM 호출)
# ================================
def classify_domain(repo: dict) -> str:
    prompt = f"""You are a classifier that assigns GitHub repositories to industry domains.

Given a repository description, respond with ONLY one domain value from this list:
{", ".join(DOMAIN_LIST)}

Rules:
- service: general web services, SaaS, productivity tools, APIs
- finance: banking, payment, investment, fintech, accounting
- it: developer tools, DevOps, infrastructure, networking, security
- retail: e-commerce, shopping, inventory, logistics, supply chain
- manufacturing: factory, IoT sensors, production, chemical, industrial
- construction: architecture, real estate, building management
- healthcare: medical, pharma, health monitoring, patient management
- education: learning platforms, school management, tutoring, EdTech
- media: news, advertising, content management, streaming, marketing
- culture: art, design, music, entertainment, gaming, museum
- institution: government, NGO, association, public service

Repository info:
{repo['llm_input'][:2000]}

Respond with ONLY the domain value. Example: finance"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0,
        )
        result = response.choices[0].message.content.strip().lower()
        if result in DOMAIN_LIST:
            return result
        return "service"
    except Exception as e:
        print(f"도메인 분류 실패 ({repo['full_name']}): {e}")
        return "service"


# ================================
# STEP 2. 임베딩 생성 (1개씩 호출)
# ================================
def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text,
    )
    return response.data[0].embedding


# ================================
# STEP 3. PostgreSQL 저장
# ================================
def save_to_db(cur, repo: dict, domain: str, embedding: list):
    # embedding을 문자열로 변환
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    cur.execute("""
        INSERT INTO repo_embeddings
            (repo_embeddings_id, repo_full_name, domain, language, topics, html_url, repo_embedding, readme)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s::vector, %s)
        ON CONFLICT (repo_embeddings_id) DO UPDATE SET
            domain    = EXCLUDED.domain,
            repo_embedding = EXCLUDED.repo_embedding,
            readme    = EXCLUDED.readme
    """, (
        repo["id"],
        repo["full_name"],
        domain,
        repo.get("languages_top1"),  # enriched 필드 사용
        repo.get("topics", []),
        repo.get("html_url"),
        embedding_str,
        repo.get("llm_input"),
    ))


# ================================
# 이미 처리된 ID 로드 (이어받기)
# ================================
def load_done_ids(cur) -> set:
    cur.execute("SELECT repo_embeddings_id FROM repo_embeddings")
    return {row[0] for row in cur.fetchall()}


# ================================
# 메인 실행
# ================================
def main():
    if not OPENAI_API_KEY:
        print("❌ .env에 OPENAI_API_KEY가 없어!")
        return
    if not DB_PASSWORD:
        print("❌ .env에 DB_PASSWORD가 없어!")
        return

    # DB 연결
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()
    print("✅ DB 연결 성공")

    # 이미 처리된 ID 로드 (중단 후 이어받기)
    done_ids = load_done_ids(cur)
    print(f"📋 이미 처리된 레포: {len(done_ids)}개 (스킵)")

    # 데이터 로드
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        repos = [json.loads(line) for line in f]

    # 미처리 레포만 필터링
    repos = [r for r in repos if r["id"] not in done_ids]
    print(f"✅ 처리할 레포: {len(repos)}개")

    if not repos:
        print("🎉 모든 레포가 이미 처리됨!")
        return

    success, fail = 0, 0
    start_time = time.time()

    for repo in tqdm(repos, desc="처리 중"):
        try:
            # 1. 도메인 분류
            domain = classify_domain(repo)
            time.sleep(0.5)

            # 2. 임베딩 생성 (1개씩)
            embedding = get_embedding(repo["llm_input"][:2000])
            time.sleep(0.5)

            # 3. DB 저장 (레포 단위 커밋)
            save_to_db(cur, repo, domain, embedding)
            conn.commit()
            success += 1

        except Exception as e:
            conn.rollback()
            fail += 1
            print(f"\n❌ 실패 [{repo['full_name']}]: {e}")
            time.sleep(2)

    cur.close()
    conn.close()
    elapsed = str(timedelta(seconds=int(time.time() - start_time)))
    print(f"\n🎉 완료! 성공: {success}개 / 실패: {fail}개")
    print(f"   소요시간: {elapsed}")


if __name__ == "__main__":
    main()