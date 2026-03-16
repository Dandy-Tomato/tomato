"""
취업준비생 포트폴리오 레포 수집
- 별 0개 이상 + README 있음 + 포트폴리오 키워드 포함
- SSAFY, 부트캠프, 포트폴리오 관련 키워드 기반 수집
"""

import requests
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN or TOKEN == "여기에_토큰_붙여넣기":
    print("❌ .env 파일에 GITHUB_TOKEN을 설정해주세요!")
    exit()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

FIELDS = [
    "id", "full_name", "html_url", "created_at",
    "pushed_at", "updated_at", "stargazers_count",
    "language", "topics", "default_branch"
]

# 포트폴리오/취준생 키워드 쿼리
PORTFOLIO_QUERIES = [
    "ssafy in:name,description,readme",
    "ssafy in:topics",
    "부트캠프 포트폴리오 in:name,description",
    "bootcamp portfolio in:name,description",
    "portfolio project in:name,description pushed:>2022-01-01",
    "졸업프로젝트 in:name,description",
    "final project bootcamp in:name,description",
    "구름톤 in:name,description",
    "우아한테크코스 in:name,description",
    "likelion in:name,description",
    "codestates in:name,description",
    "캡스톤 in:name,description",
    "capstone in:name,description"
]

# 라이브러리/패키지 제외 키워드
EXCLUDE_NAME_KEYWORDS = [
    "-plugin", "-library", "-lib", "-sdk", "-framework",
    "-spec", "-rfc", "-standard", "-docs", "-book",
    "awesome-", "cheatsheet", "tutorial",
]
EXCLUDE_TOPICS = {"library", "plugin", "sdk", "framework", "package", "module", "spec", "rfc"}


def safe_request(url, params=None, retries=3):
    for i in range(retries):
        res = requests.get(url, headers=HEADERS, params=params)

        if res.status_code == 403:
            reset_time = int(res.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset_time - int(time.time()) + 5, 10)
            print(f"⏳ Rate limit! {wait}초 대기 중...")
            time.sleep(wait)
            continue

        if res.status_code == 404:
            return None

        if res.status_code != 200:
            print(f"⚠️ 오류 {res.status_code}: {url}")
            return None

        time.sleep(0.5)
        return res.json()

    return None


def is_excluded_repo(repo: dict) -> tuple[bool, str]:
    name   = (repo.get("full_name") or "").lower()
    topics = {t.lower() for t in (repo.get("topics") or [])}

    if any(kw in name for kw in EXCLUDE_NAME_KEYWORDS):
        return True, f"레포명 키워드: {name}"
    if EXCLUDE_TOPICS & topics:
        return True, f"라이브러리 토픽: {EXCLUDE_TOPICS & topics}"

    return False, ""


def collect_portfolio_repos(output_file="repos_portfolio.jsonl"):
    total_saved    = 0
    total_excluded = 0

    # 중복 방지 - 기존 수집 ID 로드
    done_ids = set()
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    done_ids.add(json.loads(line)["id"])
                except:
                    continue
    print(f"📋 이미 수집된 레포: {len(done_ids)}개 (스킵)\n")

    for query_str in PORTFOLIO_QUERIES:
        print(f"\n📦 수집 시작: {query_str}")

        # README 있는 레포만 (has:readme), stars 0 이상
        query = f"{query_str} is:public archived:false has:readme pushed:>2022-01-01"

        for page in range(1, 11):  # 최대 10페이지 = 1000개
            params = {
                "q":        query,
                "sort":     "updated",
                "order":    "desc",
                "per_page": 100,
                "page":     page,
            }

            data = safe_request("https://api.github.com/search/repositories", params=params)

            if not data:
                print(f"  ❌ 응답 없음 (page {page}), 다음 쿼리로 넘어갑니다.")
                break

            items = data.get("items", [])
            if not items:
                print(f"  ✅ page {page}: 더 이상 결과 없음")
                break

            saved_this_page = 0
            with open(output_file, "a", encoding="utf-8") as f:
                for repo in items:
                    # 중복 스킵
                    if repo.get("id") in done_ids:
                        continue

                    # 부적합 필터링
                    excluded_flag, reason = is_excluded_repo(repo)
                    if excluded_flag:
                        total_excluded += 1
                        continue

                    row = {field: repo.get(field) for field in FIELDS}
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    done_ids.add(repo.get("id"))
                    total_saved    += 1
                    saved_this_page += 1

            print(f"  ✅ page {page}: {saved_this_page}개 저장 (누적: {total_saved}개, 제외: {total_excluded}개)")
            time.sleep(2)  # Search API 분당 30회 제한 대응

    print(f"\n🎉 수집 완료! 총 {total_saved}개 저장, {total_excluded}개 제외 → {output_file}")


if __name__ == "__main__":
    collect_portfolio_repos()