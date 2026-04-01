"""
STEP 3. README 전처리
- repos_enriched.jsonl 읽기
- readme_text를 LLM이 읽기 좋은 형태로 정제
- 결과: repos_preprocessed.jsonl
"""

import re
import json
import hashlib
import os
import time
from datetime import timedelta
from typing import Dict, List, Tuple, Optional, Any

# =============================================================
# 전처리 상수 정의
# =============================================================

DOMAIN_SECTION_KEYWORDS = [
    "about", "overview", "introduction", "intro", "background",
    "problem", "why", "motivation",
    "features", "feature", "what it does", "use case", "usecase",
    "description", "project", "service", "goal", "objectives",
    "domain", "business", "product"
]

TECH_SECTION_KEYWORDS = [
    "tech", "stack", "built", "architecture",
    "requirements", "requirement", "dependency", "dependencies",
    "install", "installation", "setup", "getting started", "quickstart",
    "usage", "run", "build", "deploy",
    "environment", "config", "configuration",
    "docker", "kubernetes", "ci", "cd", "github actions"
]

EXCLUDE_SECTION_KEYWORDS = [
    "license", "contributing", "contributor", "authors", "acknowledg",
    "changelog", "release", "roadmap", "faq", "screenshots", "screenshot",
    "demo", "history", "credits", "security", "code of conduct"
]

KEEP_CODEBLOCK_LANGS = {
    "json", "yaml", "yml", "xml", "toml",
    "gradle", "groovy", "properties",
    "dockerfile", "bash", "sh", "shell"
}

KEEP_CODEBLOCK_CONTENT_KEYWORDS = [
    "dependency", "dependencies", "plugins", "repositories",
    "spring", "springboot", "spring-boot",
    "react", "next", "vue", "angular",
    "node", "npm", "pnpm", "yarn",
    "django", "flask", "fastapi",
    "kafka", "redis", "mysql", "postgres", "postgresql", "mongodb",
    "docker", "kubernetes", "helm",
    "github actions", "workflow", "ci", "cd"
]

# =============================================================
# 전처리 함수들
# =============================================================

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).lower()

def _remove_images(md: str) -> str:
    md = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", md)
    md = re.sub(r"<img[^>]*>", "", md, flags=re.IGNORECASE)
    return md

def _remove_url_only_lines(md: str) -> str:
    out = []
    for line in md.splitlines():
        s = line.strip()
        if not s:
            out.append(line)
            continue
        if "shields.io" in s:
            out.append(line)
            continue
        if re.fullmatch(r"https?://\S+", s):
            continue
        out.append(line)
    return "\n".join(out)

def _extract_badge_tokens(md: str, max_lines: int = 80) -> List[str]:
    tokens = set()
    for line in md.splitlines()[:max_lines]:
        if "shields.io" not in line:
            continue
        matches = re.findall(r"shields\.io\/badge\/([^)\s]+)", line)
        for part in matches:
            label = part.split("-")[0]
            label = label.replace("_", " ").replace("%20", " ")
            label = re.sub(r"[^A-Za-z0-9\+\.\# ]+", " ", label).strip()
            if label:
                tokens.add(label)
    return sorted(tokens)

def _split_sections(md: str) -> List[Tuple[str, str]]:
    lines = md.splitlines()
    header_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    sections: List[Tuple[str, List[str]]] = []
    title = "__intro__"
    buf: List[str] = []

    for line in lines:
        m = header_re.match(line)
        if m:
            sections.append((title, buf))
            title = m.group(2).strip()
            buf = []
        else:
            buf.append(line)

    sections.append((title, buf))
    return [(t, "\n".join(b).strip()) for t, b in sections]

def _is_excluded(title: str) -> bool:
    t = _norm(title)
    return any(k in t for k in EXCLUDE_SECTION_KEYWORDS)

def _is_domain_section(title: str) -> bool:
    t = _norm(title)
    return any(k in t for k in DOMAIN_SECTION_KEYWORDS)

def _is_tech_section(title: str) -> bool:
    t = _norm(title)
    return any(k in t for k in TECH_SECTION_KEYWORDS)

def _extract_codeblocks(md: str, max_blocks: int = 10) -> List[str]:
    blocks = []
    pattern = re.compile(r"```([a-zA-Z0-9\-\+]*)\n(.*?)\n```", re.DOTALL)
    for lang, body in pattern.findall(md):
        lang_norm = _norm(lang)
        body_norm = _norm(body)
        keep = False
        if lang_norm in KEEP_CODEBLOCK_LANGS:
            keep = True
        elif any(k in body_norm for k in KEEP_CODEBLOCK_CONTENT_KEYWORDS):
            keep = True
        if keep:
            blocks.append(f"```{lang.strip()}\n{body.strip()}\n```")
        if len(blocks) >= max_blocks:
            break
    return blocks


def preprocess_readme(
    readme_md: str,
    repo_full_name: Optional[str] = None,
    description: Optional[str] = None,
    topics: Optional[List[str]] = None,
    max_chars: int = 5000,
    intro_chars: int = 1200,
    max_section_chars: int = 2200
) -> Dict[str, Any]:
    """
    README를 LLM 입력용으로 전처리.
    반환값: llm_input (str) + 메타 정보
    """
    readme_md = readme_md or ""
    md = readme_md.replace("\r\n", "\n")
    md = _remove_images(md)
    md = _remove_url_only_lines(md)

    readme_hash = hashlib.sha256(md.encode("utf-8", errors="ignore")).hexdigest()
    badges = _extract_badge_tokens(md)
    codeblocks = _extract_codeblocks(md)
    sections = _split_sections(md)

    intro = ""
    domain_sections: List[Tuple[str, str]] = []
    tech_sections: List[Tuple[str, str]] = []

    for title, content in sections:
        if title == "__intro__":
            intro = content.strip()[:intro_chars]
            continue
        if _is_excluded(title):
            continue
        c = content.strip()
        if len(c) > max_section_chars:
            c = c[:max_section_chars] + "\n...(truncated)"
        if _is_domain_section(title):
            domain_sections.append((title, c))
        if _is_tech_section(title):
            tech_sections.append((title, c))

    # fallback: 아무 섹션도 못 잡으면 짧은 섹션 사용
    if not domain_sections and not tech_sections:
        fallback = []
        for title, content in sections:
            if title == "__intro__" or _is_excluded(title):
                continue
            c = content.strip()
            if 120 <= len(c) <= 1200:
                fallback.append((title, c))
            if len(fallback) >= 2:
                break
        domain_sections = fallback[:1]
        tech_sections = fallback[1:2]

    # LLM 입력 조합
    parts = []
    if repo_full_name:
        parts.append(f"[REPO]\n{repo_full_name}\n")
    if topics:
        parts.append("[TOPICS]\n" + "\n".join(f"- {t}" for t in topics) + "\n")
    if description:
        parts.append("[DESCRIPTION]\n" + description.strip() + "\n")
    if badges:
        parts.append("[BADGES]\n" + "\n".join(f"- {b}" for b in badges) + "\n")
    if intro:
        parts.append("[INTRO]\n" + intro.strip() + "\n")
    if domain_sections:
        parts.append("[DOMAIN_SECTIONS]")
        for title, c in domain_sections[:3]:
            parts.append(f"## {title}\n{c}\n")
    if tech_sections:
        parts.append("[TECH_SECTIONS]")
        for title, c in tech_sections[:3]:
            parts.append(f"## {title}\n{c}\n")
    if codeblocks:
        parts.append("[CODE_BLOCKS]")
        for cb in codeblocks[:8]:
            parts.append(cb + "\n")

    llm_input = "\n".join(parts).strip()
    if len(llm_input) > max_chars:
        llm_input = llm_input[:max_chars] + "\n...(truncated)"

    return {
        "readme_hash": readme_hash,
        "badges": badges,
        "llm_input": llm_input,
    }


# =============================================================
# 메인: repos_enriched.jsonl → repos_preprocessed.jsonl
# =============================================================

def preprocess_all(
    input_file="repos_enriched.jsonl",
    output_file="repos_preprocessed.jsonl"
):
    # 부적합 레포 판단 키워드
    # ⚠️ collect_repos.py의 EXCLUDE_NAME_KEYWORDS, EXCLUDE_TOPICS와 항상 동기화할 것
    EXCLUDE_README_KEYWORDS = [
        # 패키지/라이브러리 선언
        "this is a plugin", "this is a library", "this is a package",
        "this is a framework", "this is a sdk", "this is a module",
        "this package", "this library", "this plugin", "this module",
        "this gem", "this crate", "this extension",
        # 설치 명령어 (패키지 배포용 레포 특징)
        "npm install", "pip install", "gem install", "composer require",
        "yarn add", "cargo add", "go get",
        # 튜토리얼/강의 자료
        "this repository contains", "this repo contains solutions",
        "this repo contains examples", "lecture", "course material",
        "algorithm solutions", "coding test", "baekjoon", "leetcode",
    ]
    EXCLUDE_NAME_KEYWORDS = [
        # 라이브러리/패키지 (collect_repos.py와 동기화)
        "-plugin", "-library", "-lib", "-sdk", "-framework",
        "-utils", "-util", "-helper", "-helpers",
        "-collection", "-components", "-hooks", "-wrapper",
        "-cli", "-api-client", "-client-sdk",
        # 문서/학습 자료
        "-spec", "-rfc", "-standard", "-docs", "-book",
        "awesome-", "cheatsheet", "tutorial", "boilerplate",
        "-starter", "-template", "-scaffold", "-generator",
        "-example", "-examples", "-demo", "-samples",
    ]
    LIB_TOPICS = {
        # (collect_repos.py와 동기화)
        "library", "plugin", "sdk", "framework", "package",
        "module", "spec", "rfc", "boilerplate", "template",
        "starter-kit", "starter", "scaffold", "generator",
        "utility", "utilities", "helpers", "components",
    }

    def is_excluded(repo: dict) -> tuple[bool, str]:
        name   = (repo.get("full_name") or "").lower()
        topics = {t.lower() for t in (repo.get("topics") or [])}
        readme = (repo.get("readme_text") or "").lower()[:500]

        if any(kw in name for kw in EXCLUDE_NAME_KEYWORDS):
            return True, f"레포명 키워드: {name}"
        if LIB_TOPICS & topics:
            return True, f"라이브러리 토픽: {LIB_TOPICS & topics}"
        if any(kw in readme for kw in EXCLUDE_README_KEYWORDS):
            return True, "README 패키지 키워드 감지"
        if readme and len(readme) < 100:
            return True, "README 너무 짧음"
        return False, ""
    # 이어받기용 이미 처리된 ID 로드
    done_ids = set()
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    row = json.loads(line)
                    done_ids.add(row["id"])
                except:
                    continue
    print(f"📋 이미 처리된 레포: {len(done_ids)}개 (스킵)")

    # 전체 수 카운트
    with open(input_file, "r", encoding="utf-8") as f:
        total = sum(1 for _ in f)
    print(f"📦 총 처리 대상: {total}개\n")

    start_time = time.time()
    processed = 0
    skipped = 0
    excluded = 0
    readme_none = 0

    with open(input_file, "r", encoding="utf-8") as f_in, \
         open(output_file, "a", encoding="utf-8") as f_out:

        for line in f_in:
            try:
                repo = json.loads(line)
            except:
                continue

            repo_id = repo.get("id")

            if repo_id in done_ids:
                skipped += 1
                continue

            # 부적합 레포 필터링
            excluded_flag, reason = is_excluded(repo)
            if excluded_flag:
                excluded += 1
                continue

            readme_text = repo.get("readme_text")

            # README 없으면 llm_input을 description + topics 기반으로만 구성
            if not readme_text:
                readme_none += 1

            result = preprocess_readme(
                readme_md=readme_text or "",
                repo_full_name=repo.get("full_name"),
                description=repo.get("description"),
                topics=repo.get("topics") or [],
            )

            output_row = {
                **repo,
                "readme_hash": result["readme_hash"],
                "badges": result["badges"],
                "llm_input": result["llm_input"],
            }

            f_out.write(json.dumps(output_row, ensure_ascii=False) + "\n")
            processed += 1

            if processed % 200 == 0:
                print(f"  ✅ {processed}/{total} 처리 완료...")

    elapsed = time.time() - start_time
    print(f"\n🎉 전처리 완료!")
    print(f"   처리: {processed}개 / 스킵: {skipped}개 / 제외: {excluded}개 / README 없음: {readme_none}개")
    print(f"   소요시간: {str(timedelta(seconds=int(elapsed)))}")
    print(f"   결과 파일: {output_file}")


# =============================================================
# 결과 샘플 확인용 (선택 실행)
# =============================================================

def preview(file="repos_preprocessed.jsonl", n=3):
    print(f"\n{'='*60}")
    print(f"📄 {file} 샘플 {n}개 미리보기")
    print(f"{'='*60}\n")
    with open(file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            repo = json.loads(line)
            print(f"[{i+1}] {repo.get('full_name')}")
            print(f"  badges   : {repo.get('badges')}")
            print(f"  llm_input 길이: {len(repo.get('llm_input', ''))}")
            print(f"  llm_input 앞 300자:\n{repo.get('llm_input', '')[:300]}")
            print()


if __name__ == "__main__":
    preprocess_all()

    # 결과 확인하고 싶으면 아래 주석 해제
    preview()