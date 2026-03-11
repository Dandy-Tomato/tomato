import requests
import os
import time
import json
from dotenv import load_dotenv

# ✅ .env 파일에서 토큰 불러오기
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

# ✅ 저장할 필드
FIELDS = [
    "id", "full_name", "html_url", "created_at",
    "pushed_at", "updated_at", "stargazers_count",
    "language", "topics", "default_branch"
]

# ✅ Rate Limit 대응 요청 함수
def safe_request(url, params=None, retries=3):
    for i in range(retries):
        res = requests.get(url, headers=HEADERS, params=params)

        if res.status_code == 403:
            reset_time = int(res.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset_time - int(time.time()) + 5, 10)
            print(f"⏳ Rate limit 감지! {wait}초 대기 중...")
            time.sleep(wait)
            continue

        if res.status_code == 404:
            return None

        if res.status_code != 200:
            print(f"⚠️ 오류 {res.status_code}: {url}")
            return None

        time.sleep(0.5)  # API 부하 방지용 딜레이
        return res.json()

    return None


# ✅ stars 구간별로 쪼개서 수집 (1000개 제한 우회)
STAR_RANGES = [
    "stars:20..50",
    "stars:51..100",
    "stars:101..200",
    "stars:201..300",
]

def collect_repos(output_file="repos.jsonl"):
    total_saved = 0

    for star_range in STAR_RANGES:
        print(f"\n📦 수집 시작: {star_range}")
        query = f"archived:false is:public pushed:>2023-01-01 {star_range}"

        for page in range(1, 11):  # 최대 10페이지 = 1000개
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": 100,
                "page": page
            }

            data = safe_request("https://api.github.com/search/repositories", params=params)

            if not data:
                print(f"  ❌ 응답 없음 (page {page}), 다음 구간으로 넘어갑니다.")
                break

            items = data.get("items", [])
            if not items:
                print(f"  ✅ page {page}: 더 이상 결과 없음")
                break

            with open(output_file, "a", encoding="utf-8") as f:
                for repo in items:
                    row = {field: repo.get(field) for field in FIELDS}
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")

            total_saved += len(items)
            print(f"  ✅ page {page}: {len(items)}개 저장 (누적: {total_saved}개)")

            # Search API: 분당 30회 제한 대응
            time.sleep(2)

    print(f"\n🎉 수집 완료! 총 {total_saved}개 → {output_file}")


# ✅ 실행
if __name__ == "__main__":
    collect_repos()