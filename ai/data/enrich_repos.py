import requests
import os
import time
import json
import base64
from dotenv import load_dotenv

# ✅ 토큰 로드
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

# ✅ Rate Limit 대응 요청 함수
def safe_request(url, retries=3):
    for i in range(retries):
        res = requests.get(url, headers=HEADERS)

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

        time.sleep(0.3)
        return res.json()

    return None


# ✅ Languages 가져오기
def get_languages(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    data = safe_request(url)
    if not data:
        return {}, None, None, None

    total = sum(data.values()) or 1
    sorted_langs = sorted(data.items(), key=lambda x: x[1], reverse=True)

    top1 = sorted_langs[0][0] if len(sorted_langs) > 0 else None
    top2 = sorted_langs[1][0] if len(sorted_langs) > 1 else None
    top3 = sorted_langs[2][0] if len(sorted_langs) > 2 else None

    ratio = {lang: round(bytes_ / total, 4) for lang, bytes_ in sorted_langs}

    return data, top1, top2, top3, ratio


# ✅ README 가져오기 (base64 디코딩)
def get_readme(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    data = safe_request(url)
    if not data:
        return None

    try:
        content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return content
    except Exception:
        return None


# ✅ 이미 처리된 레포 ID 불러오기 (중단 후 이어받기용)
def load_done_ids(output_file):
    done = set()
    if not os.path.exists(output_file):
        return done
    with open(output_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
                done.add(row["id"])
            except:
                continue
    return done


# ✅ 메인 풍부화 함수
def enrich_repos(input_file="repos.jsonl", output_file="repos_enriched.jsonl"):
    # 이어받기: 이미 처리된 ID 스킵
    done_ids = load_done_ids(output_file)
    print(f"📋 이미 처리된 레포: {len(done_ids)}개 (스킵)")

    # 전체 레포 수 먼저 카운트
    with open(input_file, "r", encoding="utf-8") as f:
        total = sum(1 for _ in f)

    print(f"📦 총 처리 대상: {total}개\n")

    processed = 0
    skipped = 0

    with open(input_file, "r", encoding="utf-8") as f_in, \
         open(output_file, "a", encoding="utf-8") as f_out:

        for line in f_in:
            try:
                repo = json.loads(line)
            except:
                continue

            repo_id = repo.get("id")

            # 이미 처리된 레포 스킵
            if repo_id in done_ids:
                skipped += 1
                continue

            full_name = repo.get("full_name", "")
            if "/" not in full_name:
                continue

            owner, repo_name = full_name.split("/", 1)

            print(f"  🔍 [{processed + skipped + 1}/{total}] {full_name}")

            # Languages 수집
            lang_result = get_languages(owner, repo_name)
            if lang_result is None or len(lang_result) != 5:
                languages_raw, top1, top2, top3, ratio = {}, None, None, None, {}
            else:
                languages_raw, top1, top2, top3, ratio = lang_result

            # README 수집
            readme_text = get_readme(owner, repo_name)

            # 기존 데이터에 풍부화 필드 추가
            enriched = {
                **repo,
                "languages_raw": languages_raw,
                "languages_top1": top1,
                "languages_top2": top2,
                "languages_top3": top3,
                "languages_ratio": ratio,
                "readme_text": readme_text[:5000] if readme_text else None,  # 최대 5000자
            }

            f_out.write(json.dumps(enriched, ensure_ascii=False) + "\n")
            processed += 1

            # 100개마다 진행상황 출력
            if processed % 100 == 0:
                print(f"\n✅ {processed}개 완료 (전체 {total}개 중)\n")

    print(f"\n🎉 풍부화 완료!")
    print(f"   처리: {processed}개 / 스킵: {skipped}개")
    print(f"   결과 파일: {output_file}")


# ✅ 실행
if __name__ == "__main__":
    enrich_repos()