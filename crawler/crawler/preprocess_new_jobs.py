import json
import math
import re
import time
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
DB_READY_DIR = ROOT_DIR / "db_ready"
INDUSTRIES_PATH = CONFIG_DIR / "industries.json"


# =========================
# 1) 기본 유틸
# =========================
def clean_text(s) -> str:
    if s is None:
        return ""
    if isinstance(s, float) and math.isnan(s):
        return ""

    text = str(s)
    text = re.sub(r"[\x00-\x1F\x7F]", " ", text)
    text = text.replace("\u00A0", " ")
    text = text.replace("\u200B", " ")
    text = text.replace("\ufeff", " ")

    return " ".join(text.split()).strip()


def is_missing_value(s) -> bool:
    t = clean_text(s).lower()
    return t in {"", "nan", "none", "null", "na", "n/a"}


def now_ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def load_industries():
    if not INDUSTRIES_PATH.exists():
        raise FileNotFoundError(f"industries.json 파일이 없습니다: {INDUSTRIES_PATH}")

    with open(INDUSTRIES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("industries.json 형식이 잘못되었습니다. 리스트여야 합니다.")

    return data


def get_industry_dir(major_code: str, major_name: str) -> Path:
    return DATA_DIR / f"{major_code}_{major_name}"


def save_csv(df: pd.DataFrame, path: Path):
    df.to_csv(path, index=False, encoding="utf-8-sig")


# =========================
# 1-1) 저장 직전 강제 정리
# =========================
LEADING_JUNK_CHARS = {"'", '"', "’", "‘", "+", "-", "*", "•", "·", "ㆍ", "_"}


def hard_clean_output_text(s: str) -> str:
    t = clean_text(s)
    if not t:
        return ""

    t = t.strip()

    while t and t[0] in LEADING_JUNK_CHARS:
        t = t[1:].lstrip()

    while t.startswith("_"):
        t = t[1:].lstrip()

    if re.fullmatch(r"@[A-Za-z0-9_.]+", t):
        return ""

    if t.lower().startswith("powerpo"):
        t = "PowerPoint"

    return clean_text(t)


def hard_clean_df_for_output(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    obj_cols = out.select_dtypes(include=["object"]).columns
    for col in obj_cols:
        out[col] = (
            out[col]
            .fillna("")
            .astype(str)
            .map(hard_clean_output_text)
        )

    return out


def force_clean_skill_series(series: pd.Series) -> pd.Series:
    s = series.fillna("").astype(str).map(hard_clean_output_text)

    s = s.str.replace(r"^[\'\"’‘\+\-\*•·ㆍ_]+", "", regex=True)
    s = s.str.strip()
    s = s.mask(s.str.fullmatch(r"@[A-Za-z0-9_.]+", na=False), "")
    s = s.str.replace(r"(?i)^powerpo.*$", "PowerPoint", regex=True)

    return s.map(clean_text)


def remove_bad_prefixed_skills(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return df

    out = df.copy()
    out[col] = force_clean_skill_series(out[col])

    out = out[out[col] != ""]
    out = out[~out[col].str.fullmatch(r"@[A-Za-z0-9_.]+", na=False)]
    out = out[~out[col].str.startswith(("'", '"', "’", "‘", "+", "-", "@", "_", "*"), na=False)]

    return out.reset_index(drop=True)


# =========================
# 2) 괄호 밖에서만 split
# =========================
def split_outside_parentheses(text: str, delimiters=None) -> list[str]:
    if delimiters is None:
        delimiters = {",", "|", ";", "\n", "\r", "•", "·", "ㆍ", "，", "｜"}

    text = clean_text(text)
    if not text:
        return []

    parts = []
    buf = []
    depth = 0

    for ch in text:
        if ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch in delimiters and depth == 0:
            token = clean_text("".join(buf))
            if token:
                parts.append(token)
            buf = []
        else:
            buf.append(ch)

    last = clean_text("".join(buf))
    if last:
        parts.append(last)

    return parts


# =========================
# 3) 제거/정규화 규칙
# =========================
BAD_EXACT = {
    "우대조건", "스킬", "핵심역량",
    "무관", "없음", "해당없음", "지원", "채용", "공고",
    "우대", "가능자", "관련자",
    "상세요강 참고", "상세내용 참고", "내용 참고",

    "인근거주자",
    "운전가능자",
    "장기근무 가능자",
    "야간근무 가능자",
    "차량소지자",
    "즉시출근 가능자",
    "출장 가능자",
    "지방근무 가능자",
    "해외근무 가능자",
    "교대근무 가능자",
    "2교대 근무 가능자",
    "3교대 근무 가능자",

    "유관업무 경험자",
    "유관업무경험자",
    "유관업무 경력자",
    "유관업무경력자",

    "보호대상",
    "국가유공자",
    "보훈대상자",
    "장애인",
    "취업보호대상자",
    "고용촉진지원금 대상자",
    "병역특례",
}

BAD_CONTAINS = [
    "상세요강",
    "자세한 내용",
    "지원부문별 상이",
    "상이할 수",
    "참고 바랍니다",
    "문의",
    "홈페이지",
    "접수",
    "채용공고",
    "입사지원",
    "지원방법",
    "전형절차",
    "제출서류",
    "근무조건",
    "근무환경",
    "복리후생",

    "인근거주",
    "운전가능",
    "장기근무 가능",
    "야간근무 가능",
    "차량소지",
    "즉시출근 가능",
    "출장 가능",
    "지방근무 가능",
    "해외근무 가능",
    "교대근무 가능",
    "유관업무 경험",
    "유관업무 경력",

    "국가유공",
    "보훈대상",
    "취업보호대상",
    "고용촉진지원금 대상",
    "병역특례",
]

BAD_PATTERNS = [
    r"^채용.*$",
    r"^공고.*$",
    r"^지원.*$",
    r"^홈페이지.*$",
    r"^즉시.*$",
    r"^간편.*$",
    r"^바로.*$",
    r"^접수.*$",
    r"^문의.*$",
    r"^제출.*$",
    r"^전형.*$",
    r"^근무.*$",
    r"^복리후생.*$",
    r"^※.*$",
    r"^\(※.*\)$",

    r".*가능자$",
    r".*경험자$",
    r".*경력자$",
    r".*보유자$",
    r".*소지자$",
    r".*전공자$",
    r".*우대$",
    r".*대상자$",
    r".*출신자$",
    r".*수상자$",
    r".*소유자$",

    r".*\s가능자$",
    r".*\s경험자$",
    r".*\s경력자$",
    r".*\s보유자$",
    r".*\s소지자$",
    r".*\s전공자$",
    r".*\s우대$",
    r".*\s대상자$",
    r".*\s출신자$",
    r".*\s수상자$",

    r"^@[A-Za-z0-9_.]+$",
]

LICENSE_SUFFIX_PATTERNS = [
    r"(.+?)\s*자격증\s*$",
    r"(.+?)\s*자격\s*$",
    r"(.+?)\s*면허증\s*$",
    r"(.+?)\s*면허\s*$",
    r"(.+?)\s*자격증\s*보유\s*$",
    r"(.+?)\s*자격\s*보유\s*$",
    r"(.+?)\s*면허증\s*보유\s*$",
    r"(.+?)\s*면허\s*보유\s*$",
]

RAW_REPLACE_MAP = {
    "powerpo": "PowerPoint",
    "power point": "PowerPoint",
    "power-point": "PowerPoint",
    "ms office powerpoint": "PowerPoint",
    "msoffice powerpoint": "PowerPoint",
    "ppt": "PowerPoint",
    "pptx": "PowerPoint",

    "excel": "Excel",
    "word": "Word",
    "hwp": "한글",
    "한컴": "한글",
    "한글워드": "한글",
    "포토샵": "Photoshop",
    "일러스트": "Illustrator",
    "illustrator": "Illustrator",
    "photoshop": "Photoshop",
    "figma": "Figma",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vs code": "VSCode",
    "vscode": "VSCode",
    "github": "GitHub",
    "html": "HTML",
    "java": "JAVA",
    "rest api": "REST API",
}


def normalize_token(token: str) -> str:
    t = clean_text(token)
    if not t:
        return ""

    t = hard_clean_output_text(t)
    t = t.strip(" ,|/;")
    t = clean_text(t)

    if t in {"()", "( )"}:
        return ""

    t = re.sub(r"\s*\(\s*", "(", t)
    t = re.sub(r"\s*\)\s*", ")", t)
    t = t.rstrip(",")

    return clean_text(t)


def normalize_space_around_specials(t: str) -> str:
    t = re.sub(r"\s*/\s*", "/", t)
    t = re.sub(r"\s*\+\s*", "+", t)
    return clean_text(t)


def apply_replace_map(t: str) -> str:
    low = clean_text(t).lower()
    if low in RAW_REPLACE_MAP:
        return RAW_REPLACE_MAP[low]
    return t


def strip_company_prefix(token: str) -> str:
    t = normalize_token(token)
    if not t:
        return ""

    patterns = [
        r"^\([^)]*\)\s*[^A-Za-z가-힣0-9]*?(PowerPoint|Excel|Word|VSCode|GitHub|HTML|JAVA|REST API|Vue\.js|Figma|Illustrator|Photoshop)$",
        r"^\([^)]*\)\s*.*?(PowerPoint|Excel|Word|VSCode|GitHub|HTML|JAVA|REST API|Vue\.js|Figma|Illustrator|Photoshop)$",
    ]

    for p in patterns:
        m = re.match(p, t, flags=re.IGNORECASE)
        if m:
            return m.group(1)

    return t


def looks_like_noise(token: str) -> bool:
    t = normalize_token(token)
    if not t:
        return True

    if len(t) <= 1:
        return True

    if re.fullmatch(r"[0-9]+", t):
        return True

    if re.fullmatch(r"@[A-Za-z0-9_.]+", t):
        return True

    if re.fullmatch(r"[A-Za-z]{1,3}", t) and t.lower() not in {"sql", "aws", "erp", "cad"}:
        return True

    return False


def should_drop_even_after_normalization(token: str) -> bool:
    t = normalize_token(token)
    if not t:
        return True

    if t.lower() in {"nan", "none", "null", "na", "n/a"}:
        return True

    if t in BAD_EXACT:
        return True

    for bad in BAD_CONTAINS:
        if bad in t:
            return True

    for p in BAD_PATTERNS:
        if re.match(p, t):
            return True

    if t.endswith("학과") or t.endswith("학부") or t.endswith("계열") or t.endswith("전공"):
        return True

    if "학위 수여자" in t:
        return True

    if t.endswith("능숙자") or t.endswith("우수자") or t.endswith("소유자"):
        return True

    if looks_like_noise(t):
        return True

    return False


def try_normalize_license_or_cert(token: str) -> str:
    t = normalize_token(token)
    if not t:
        return ""

    for p in LICENSE_SUFFIX_PATTERNS:
        m = re.match(p, t)
        if m:
            core = normalize_token(m.group(1))
            return core

    return t


def finalize_known_skill(token: str) -> str:
    t = normalize_token(token)
    t = normalize_space_around_specials(t)
    t = apply_replace_map(t)
    t = strip_company_prefix(t)
    t = apply_replace_map(t)

    if t.lower().startswith("powerpo"):
        t = "PowerPoint"

    return normalize_token(t)


def normalize_skill_token(token: str) -> str:
    t = normalize_token(token)
    if not t:
        return ""

    if should_drop_even_after_normalization(t):
        return ""

    t2 = try_normalize_license_or_cert(t)
    t2 = finalize_known_skill(t2)

    if should_drop_even_after_normalization(t2):
        return ""

    return t2


def extract_skill_candidates_from_text(text: str) -> list[str]:
    if is_missing_value(text):
        return []

    tokens = split_outside_parentheses(text)

    out = []
    seen = set()

    for token in tokens:
        normalized = normalize_skill_token(token)
        if not normalized:
            continue

        if normalized not in seen:
            seen.add(normalized)
            out.append(normalized)

    return out


def extract_skill_candidates(row: pd.Series) -> list[str]:
    values = []

    for col in ["우대조건", "스킬"]:
        if col not in row:
            continue

        col_value = row[col]
        if is_missing_value(col_value):
            continue

        values.extend(extract_skill_candidates_from_text(str(col_value)))

    out = []
    seen = set()

    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)

    return out


# =========================
# 4) 산업별 raw 로드
# =========================
def find_raw_csv_for_industry(major_code: str, major_name: str) -> Path | None:
    base_dir = get_industry_dir(major_code, major_name)
    raw_dir = base_dir / "raw"

    if not raw_dir.exists():
        return None

    candidates = sorted(raw_dir.glob(f"jobkorea_{major_code}_*_all_pages.csv"))
    if not candidates:
        return None

    return candidates[0]


def load_all_raw_data() -> pd.DataFrame:
    industries = load_industries()

    frames = []

    for item in industries:
        major_code = str(item["major_code"]).strip()
        major_name = str(item["major_name"]).strip()

        raw_csv = find_raw_csv_for_industry(major_code, major_name)
        if raw_csv is None:
            print(f"[WARN] raw 없음: {major_code} / {major_name}", flush=True)
            continue

        print(f"[INFO] load raw: {raw_csv}", flush=True)

        df = pd.read_csv(raw_csv, encoding="utf-8-sig")
        if df.empty:
            print(f"[WARN] raw 비어 있음: {major_code} / {major_name}", flush=True)
            continue

        df["domain_id"] = int(major_code)
        df["domain_name"] = major_name
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


# =========================
# 5) company-skill pair 생성
# =========================
def build_company_skill_pairs(all_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for _, row in all_df.iterrows():
        company = clean_text(row.get("기업명", ""))
        domain_id = row.get("domain_id", None)
        domain_name = clean_text(row.get("domain_name", ""))

        if is_missing_value(company):
            continue

        skills = extract_skill_candidates(row)
        if not skills:
            continue

        for skill in skills:
            skill = hard_clean_output_text(skill)

            if is_missing_value(skill):
                continue

            if should_drop_even_after_normalization(skill):
                continue

            rows.append({
                "domain_id": int(domain_id) if pd.notna(domain_id) else None,
                "domain_name": domain_name,
                "기업명": company,
                "스킬": skill,
            })

    if not rows:
        return pd.DataFrame(columns=["domain_id", "domain_name", "기업명", "스킬"])

    pair_df = pd.DataFrame(rows)
    pair_df = pair_df.dropna(subset=["domain_id", "기업명", "스킬"])

    pair_df["기업명"] = pair_df["기업명"].map(clean_text)
    pair_df["스킬"] = force_clean_skill_series(pair_df["스킬"])

    pair_df = pair_df[
        (pair_df["기업명"] != "") &
        (pair_df["스킬"] != "")
    ]

    pair_df = pair_df[
        ~pair_df["스킬"].str.fullmatch(r"@[A-Za-z0-9_.]+", na=False)
    ]

    pair_df = pair_df[
        ~pair_df["스킬"].str.startswith(("'", '"', "’", "‘", "+", "-", "@", "_", "*"), na=False)
    ]

    pair_df = pair_df.drop_duplicates(
        subset=["domain_id", "기업명", "스킬"]
    ).reset_index(drop=True)

    return pair_df


# =========================
# 6) ERD용 정규화 테이블 생성
# =========================
def build_domains_df(pair_df: pd.DataFrame) -> pd.DataFrame:
    if pair_df.empty:
        return pd.DataFrame(columns=["domain_id", "name"])

    df = pair_df[["domain_id", "domain_name"]].drop_duplicates().copy()
    df = df.rename(columns={"domain_name": "name"})
    df = df.sort_values(["domain_id", "name"]).reset_index(drop=True)
    return df


def build_companies_df(pair_df: pd.DataFrame) -> pd.DataFrame:
    if pair_df.empty:
        return pd.DataFrame(columns=["company_id", "name", "created_at", "updated_at", "domain_id"])

    ts = now_ts()

    base = pair_df[["domain_id", "기업명"]].drop_duplicates().copy()
    base = base.sort_values(["domain_id", "기업명"]).reset_index(drop=True)
    base["company_id"] = range(1, len(base) + 1)
    base["created_at"] = ts
    base["updated_at"] = ts
    base = base.rename(columns={"기업명": "name"})

    return base[["company_id", "name", "created_at", "updated_at", "domain_id"]]


def build_skills_df(pair_df: pd.DataFrame) -> pd.DataFrame:
    if pair_df.empty:
        return pd.DataFrame(columns=["skill_id", "name"])

    base = pair_df[["스킬"]].copy()
    base["스킬"] = force_clean_skill_series(base["스킬"])

    base = base[base["스킬"] != ""]
    base = base[~base["스킬"].str.fullmatch(r"@[A-Za-z0-9_.]+", na=False)]
    base = base[~base["스킬"].str.startswith(("'", '"', "’", "‘", "+", "-", "@", "_", "*"), na=False)]

    base = base.drop_duplicates().copy()
    base = base.sort_values(["스킬"]).reset_index(drop=True)
    base["skill_id"] = range(1, len(base) + 1)
    base = base.rename(columns={"스킬": "name"})

    return base[["skill_id", "name"]]


def build_company_skills_df(
    pair_df: pd.DataFrame,
    companies_df: pd.DataFrame,
    skills_df: pd.DataFrame
) -> pd.DataFrame:
    if pair_df.empty or companies_df.empty or skills_df.empty:
        return pd.DataFrame(columns=["company_skill_id", "company_id", "skill_id"])

    company_key_to_id = {
        (int(row["domain_id"]), clean_text(row["name"])): int(row["company_id"])
        for _, row in companies_df.iterrows()
    }

    skill_name_to_id = {
        clean_text(row["name"]): int(row["skill_id"])
        for _, row in skills_df.iterrows()
    }

    rows = []
    for _, row in pair_df.iterrows():
        domain_id = int(row["domain_id"])
        company_name = clean_text(row["기업명"])
        skill_name = hard_clean_output_text(row["스킬"])

        company_id = company_key_to_id.get((domain_id, company_name))
        skill_id = skill_name_to_id.get(skill_name)

        if company_id is None or skill_id is None:
            continue

        rows.append({
            "company_id": company_id,
            "skill_id": skill_id,
        })

    if not rows:
        return pd.DataFrame(columns=["company_skill_id", "company_id", "skill_id"])

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["company_id", "skill_id"]).reset_index(drop=True)
    df["company_skill_id"] = range(1, len(df) + 1)

    return df[["company_skill_id", "company_id", "skill_id"]]


# =========================
# 7) 메인
# =========================
def main():
    print("=" * 70, flush=True)
    print("[INIT_PREPROCESS_ALL] start", flush=True)
    print("=" * 70, flush=True)

    DB_READY_DIR.mkdir(parents=True, exist_ok=True)

    all_df = load_all_raw_data()
    if all_df.empty:
        print("[WARN] 전체 raw 데이터가 없습니다.", flush=True)
        return

    print(f"[INFO] total raw rows: {len(all_df)}", flush=True)

    pair_df = build_company_skill_pairs(all_df)
    domains_df = build_domains_df(pair_df)
    companies_df = build_companies_df(pair_df)
    skills_df = build_skills_df(pair_df)
    company_skills_df = build_company_skills_df(pair_df, companies_df, skills_df)

    pair_df = hard_clean_df_for_output(pair_df)
    domains_df = hard_clean_df_for_output(domains_df)
    companies_df = hard_clean_df_for_output(companies_df)
    skills_df = hard_clean_df_for_output(skills_df)
    company_skills_df = hard_clean_df_for_output(company_skills_df)

    if "스킬" in pair_df.columns:
        pair_df["스킬"] = force_clean_skill_series(pair_df["스킬"])
        pair_df = pair_df[pair_df["스킬"] != ""]
        pair_df = pair_df.drop_duplicates(subset=["domain_id", "기업명", "스킬"]).reset_index(drop=True)

    if "name" in skills_df.columns:
        skills_df["name"] = force_clean_skill_series(skills_df["name"])
        skills_df = skills_df[skills_df["name"] != ""]
        skills_df = skills_df.drop_duplicates(subset=["name"]).reset_index(drop=True)
        skills_df["skill_id"] = range(1, len(skills_df) + 1)

    pair_df = remove_bad_prefixed_skills(pair_df, "스킬")
    skills_df = remove_bad_prefixed_skills(skills_df, "name")

    if not skills_df.empty:
        skills_df = skills_df.drop_duplicates(subset=["name"]).reset_index(drop=True)
        skills_df["skill_id"] = range(1, len(skills_df) + 1)

    print("\n[DEBUG] skills_df head BEFORE save", flush=True)
    print(skills_df.head(30).to_string(), flush=True)

    save_csv(pair_df, DB_READY_DIR / "company_skill_pairs.csv")
    save_csv(domains_df, DB_READY_DIR / "domains.csv")
    save_csv(companies_df, DB_READY_DIR / "companies.csv")
    save_csv(skills_df, DB_READY_DIR / "skills.csv")
    save_csv(company_skills_df, DB_READY_DIR / "company_skills.csv")

    print(f"[DONE] pairs={len(pair_df)}", flush=True)
    print(f"[DONE] domains={len(domains_df)}", flush=True)
    print(f"[DONE] companies={len(companies_df)}", flush=True)
    print(f"[DONE] skills={len(skills_df)}", flush=True)
    print(f"[DONE] company_skills={len(company_skills_df)}", flush=True)
    print(f"[DONE] output dir: {DB_READY_DIR}", flush=True)

    print("=" * 70, flush=True)
    print("[INIT_PREPROCESS_ALL] finished", flush=True)
    print("=" * 70, flush=True)


if __name__ == "__main__":
    main()