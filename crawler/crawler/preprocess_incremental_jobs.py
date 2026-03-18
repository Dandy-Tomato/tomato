import json
import re
import time
from pathlib import Path

import pandas as pd

from crawler.paths import ensure_dirs, get_output_dir, get_processed_dir
from crawler.preprocess_new_jobs import (
    clean_text,
    force_clean_skill_series,
    hard_clean_df_for_output,
    now_ts,
)

from init_preprocess_all import (
    extract_skill_candidates,
    canonicalize_skill,
    is_excluded_skill,
    looks_like_tech_skill,
    should_drop_token,
)


ROOT_DIR = Path(__file__).resolve().parent.parent
DB_READY_DIR = ROOT_DIR / "db_ready"

NEW_SKILL_MIN_COUNT = 1


# =========================
# 0) 기본 유틸
# =========================
def save_csv(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def load_csv_if_exists(path: Path, columns=None) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path, encoding="utf-8-sig")

    if columns is None:
        return pd.DataFrame()

    return pd.DataFrame(columns=columns)


def save_json_atomic(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp_path.replace(path)


def load_json_if_exists(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text_set(path: Path) -> set[str]:
    if not path.exists():
        return set()

    with open(path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def save_text_set_atomic(path: Path, values: set[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        for value in sorted(values):
            f.write(f"{value}\n")

    tmp_path.replace(path)


def get_latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(
        directory.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not files:
        return None
    return files[0]


def dedupe_df(df: pd.DataFrame, subset_cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return df
    return df.drop_duplicates(subset=subset_cols).reset_index(drop=True)


def normalize_skill_key(text: str) -> str:
    t = clean_text(text).lower()
    if not t:
        return ""

    t = t.replace("&", "and")
    t = re.sub(r"[.\-_/+\s()]+", "", t)
    return t


def get_run_date_folder_name() -> str:
    return time.strftime("%y%m%d")


def get_run_db_ready_dir(run_date: str | None = None) -> Path:
    if run_date is None:
        run_date = get_run_date_folder_name()
    path = DB_READY_DIR / run_date
    path.mkdir(parents=True, exist_ok=True)
    return path


def make_db_name_from_front_name(text: str) -> str:
    t = clean_text(text)
    if not t:
        return ""

    low = t.lower()

    special_map = {
        "c#": "csharp",
        "c/c++": "cpp",
        "c++": "cpp",
        "rest api": "rest_api",
        "react native": "react_native",
        "android studio": "android_studio",
        "embedded linux": "embedded_linux",
        "spring boot": "spring_boot",
        "spring batch": "spring_batch",
        "spring mvc": "spring_mvc",
        "spring security": "spring_security",
        "next.js": "nextjs",
        "node.js": "nodejs",
        "vue.js": "vuejs",
        "express.js": "expressjs",
        "express": "expressjs",
        "ruby on rails": "rails",
        "raspberry pi": "raspberry_pi",
        "scikit-learn": "scikit_learn",
        "openai api": "openai_api",
        "github actions": "github_actions",
        "tailwind css": "tailwind",
        "google analytics": "google_analytics",
        "google optimize": "google_optimize",
        "react": "react",
        "nextjs": "nextjs",
        "nuxt.js": "nuxtjs",
        "nuxtjs": "nuxtjs",
        "angular": "angular",
        "svelte": "svelte",
        "typescript": "typescript",
        "javascript": "javascript",
        "flutter": "flutter",
        "swift": "swift",
        "kotlin": "kotlin",
        "django": "django",
        "fastapi": "fastapi",
        "flask": "flask",
        "nestjs": "nestjs",
        "java": "java",
        "python": "python",
        "go": "go",
        "rust": "rust",
        "php": "php",
        "mysql": "mysql",
        "postgresql": "postgresql",
        "mongodb": "mongodb",
        "redis": "redis",
        "elasticsearch": "elasticsearch",
        "firebase": "firebase",
        "supabase": "supabase",
        "graphql": "graphql",
        "grpc": "grpc",
        "docker": "docker",
        "kubernetes": "kubernetes",
        "aws": "aws",
        "gcp": "gcp",
        "azure": "azure",
        "jenkins": "jenkins",
        "terraform": "terraform",
        "nginx": "nginx",
        "kafka": "kafka",
        "rabbitmq": "rabbitmq",
        "websocket": "websocket",
        "oauth2": "oauth2",
        "jwt": "jwt",
        "tensorflow": "tensorflow",
        "pytorch": "pytorch",
        "langchain": "langchain",
        "pandas": "pandas",
        "spark": "spark",
        "airflow": "airflow",
        "prometheus": "prometheus",
        "grafana": "grafana",
        "rtos": "rtos",
        "arduino": "arduino",
        "mqtt": "mqtt",
        "ros2": "ros2",
        "ros": "ros",
        "can": "can",
        "modbus": "modbus",
        "uart": "uart",
        "spi": "spi",
        "i2c": "i2c",
        "ble": "ble",
        "zigbee": "zigbee",
        "lorawan": "lorawan",
        "lora": "lora",
        "onnx": "onnx",
        "edge ai": "edge_ai",
        "freertos": "freertos",
    }

    if low in special_map:
        return special_map[low]

    t = t.replace("&", "and")
    t = re.sub(r"[./+\-\s]+", "_", t.lower())
    t = re.sub(r"[^a-z0-9_]", "", t)
    t = re.sub(r"_+", "_", t).strip("_")
    return t


def merge_and_replace_csv(
    path: Path,
    new_df: pd.DataFrame,
    columns: list[str],
    dedupe_subset: list[str],
    sort_by: list[str] | None = None,
):
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        old_df = pd.read_csv(path, encoding="utf-8-sig")
    else:
        old_df = pd.DataFrame(columns=columns)

    if old_df.empty and new_df.empty:
        return old_df

    old_df = old_df.copy()
    for col in columns:
        if col not in old_df.columns:
            old_df[col] = ""

    incoming_df = new_df.copy()
    for col in columns:
        if col not in incoming_df.columns:
            incoming_df[col] = ""

    old_df = old_df[columns].copy()
    incoming_df = incoming_df[columns].copy()

    merged = pd.concat([old_df, incoming_df], ignore_index=True)

    if dedupe_subset:
        merged = merged.drop_duplicates(subset=dedupe_subset, keep="first")

    if sort_by:
        sort_cols = [c for c in sort_by if c in merged.columns]
        if sort_cols:
            merged = merged.sort_values(sort_cols).reset_index(drop=True)
    else:
        merged = merged.reset_index(drop=True)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    merged.to_csv(tmp_path, index=False, encoding="utf-8-sig")
    tmp_path.replace(path)

    return merged


# =========================
# 0-1) key 유틸
# =========================
def get_state_dir(major_code: str, major_name: str) -> Path:
    output_dir = get_output_dir(major_code, major_name)
    state_dir = output_dir.parent / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def get_state_file_paths(major_code: str, major_name: str) -> dict[str, Path]:
    state_dir = get_state_dir(major_code, major_name)
    return {
        "state_dir": state_dir,
        "next_ids": state_dir / "next_ids.json",
        "company_key_to_id": state_dir / "company_key_to_id.json",
        "skill_key_to_id": state_dir / "skill_key_to_id.json",
        "seen_pair_keys": state_dir / "seen_pair_keys.txt",
        "seen_company_skill_keys": state_dir / "seen_company_skill_keys.txt",
    }


def build_pair_key(domain_id: int, company_name: str, skill_name: str) -> str:
    return f"{int(domain_id)}||{clean_text(company_name)}||{clean_text(skill_name)}"


def build_company_key(domain_id: int, company_name: str) -> str:
    return f"{int(domain_id)}||{clean_text(company_name)}"


def build_company_skill_key(company_id: int, skill_id: int) -> str:
    return f"{int(company_id)}||{int(skill_id)}"


# =========================
# 1) 초기 핵심 규칙 전부 반영용
# =========================
def is_valid_skill_by_initial_rules(skill: str) -> bool:
    skill = canonicalize_skill(skill)
    if not skill:
        return False
    if is_excluded_skill(skill):
        return False
    if should_drop_token(skill):
        return False
    if not looks_like_tech_skill(skill):
        return False
    return True


def load_existing_valid_skills_from_skills_csv() -> set[str]:
    skills_path = DB_READY_DIR / "skills.csv"
    skills_df = load_csv_if_exists(
        skills_path,
        columns=["skill_id", "front_name", "db_name"],
    )

    if skills_df.empty:
        return set()

    out = set()
    skills_df["front_name"] = skills_df["front_name"].fillna("").astype(str).map(clean_text)

    for skill in skills_df["front_name"].tolist():
        skill = canonicalize_skill(skill)
        if is_valid_skill_by_initial_rules(skill):
            out.add(skill)

    return out


def build_incremental_skill_counter(details_df: pd.DataFrame) -> dict[str, int]:
    counter = {}

    for _, row in details_df.iterrows():
        candidates = extract_skill_candidates(row)

        seen_in_row = set()
        for skill in candidates:
            skill = canonicalize_skill(skill)
            if not is_valid_skill_by_initial_rules(skill):
                continue

            if skill in seen_in_row:
                continue

            seen_in_row.add(skill)
            counter[skill] = counter.get(skill, 0) + 1

    return counter


def extract_only_allowed_skills_from_incremental_row(
    row: pd.Series,
    allowed_skills: set[str],
) -> list[str]:
    candidates = extract_skill_candidates(row)

    out = []
    seen = set()

    for skill in candidates:
        skill = canonicalize_skill(skill)
        if not is_valid_skill_by_initial_rules(skill):
            continue

        if skill not in allowed_skills:
            continue

        if skill not in seen:
            seen.add(skill)
            out.append(skill)

    return out


def build_company_skill_pairs_with_initial_rules(
    df: pd.DataFrame,
    allowed_skills: set[str],
) -> pd.DataFrame:
    rows = []

    for _, row in df.iterrows():
        company = clean_text(row.get("기업명", ""))
        domain_id = row.get("domain_id", None)
        domain_name = clean_text(row.get("domain_name", ""))

        if not company:
            continue

        matched_skills = extract_only_allowed_skills_from_incremental_row(
            row=row,
            allowed_skills=allowed_skills,
        )
        if not matched_skills:
            continue

        for skill in matched_skills:
            rows.append({
                "domain_id": int(domain_id) if pd.notna(domain_id) else None,
                "domain_name": domain_name,
                "기업명": company,
                "스킬": skill,
            })

    if not rows:
        return pd.DataFrame(columns=["domain_id", "domain_name", "기업명", "스킬"])

    pair_df = pd.DataFrame(rows)
    pair_df = pair_df.dropna(subset=["domain_id", "기업명", "스킬"]).copy()

    pair_df["기업명"] = pair_df["기업명"].map(clean_text)
    pair_df["스킬"] = pair_df["스킬"].fillna("").astype(str).map(canonicalize_skill)
    pair_df["스킬"] = force_clean_skill_series(pair_df["스킬"])

    pair_df = pair_df[
        (pair_df["기업명"] != "") &
        (pair_df["스킬"] != "")
    ]

    pair_df = pair_df[pair_df["스킬"].map(is_valid_skill_by_initial_rules)]
    pair_df = pair_df[pair_df["스킬"].isin(allowed_skills)]

    pair_df = pair_df.drop_duplicates(
        subset=["domain_id", "기업명", "스킬"]
    ).reset_index(drop=True)

    return pair_df


# =========================
# 2) 기존 DB csv 로드
# =========================
def load_existing_db_tables():
    skills_path = DB_READY_DIR / "skills.csv"
    pairs_path = DB_READY_DIR / "company_skill_pairs.csv"
    companies_path = DB_READY_DIR / "companies.csv"
    company_skills_path = DB_READY_DIR / "company_skills.csv"

    skills_df = load_csv_if_exists(
        skills_path,
        columns=["skill_id", "front_name", "db_name"],
    )
    pair_df = load_csv_if_exists(
        pairs_path,
        columns=["domain_id", "domain_name", "기업명", "스킬"],
    )
    companies_df = load_csv_if_exists(
        companies_path,
        columns=["company_id", "name", "created_at", "updated_at", "domain_id"],
    )
    company_skills_df = load_csv_if_exists(
        company_skills_path,
        columns=["company_skill_id", "company_id", "skill_id"],
    )

    if not skills_df.empty:
        skills_df["skill_id"] = skills_df["skill_id"].astype(int)
        skills_df["front_name"] = skills_df["front_name"].fillna("").astype(str).map(clean_text)
        skills_df["db_name"] = skills_df["db_name"].fillna("").astype(str).map(clean_text)

    if not pair_df.empty:
        pair_df["domain_id"] = pair_df["domain_id"].astype(int)
        pair_df["domain_name"] = pair_df["domain_name"].fillna("").astype(str).map(clean_text)
        pair_df["기업명"] = pair_df["기업명"].fillna("").astype(str).map(clean_text)
        pair_df["스킬"] = pair_df["스킬"].fillna("").astype(str).map(clean_text)

    if not companies_df.empty:
        companies_df["company_id"] = companies_df["company_id"].astype(int)
        companies_df["domain_id"] = companies_df["domain_id"].astype(int)
        companies_df["name"] = companies_df["name"].fillna("").astype(str).map(clean_text)

    if not company_skills_df.empty:
        company_skills_df["company_skill_id"] = company_skills_df["company_skill_id"].astype(int)
        company_skills_df["company_id"] = company_skills_df["company_id"].astype(int)
        company_skills_df["skill_id"] = company_skills_df["skill_id"].astype(int)

    return skills_df, pair_df, companies_df, company_skills_df


def load_skills_table_only() -> pd.DataFrame:
    skills_path = DB_READY_DIR / "skills.csv"
    skills_df = load_csv_if_exists(
        skills_path,
        columns=["skill_id", "front_name", "db_name"],
    )

    if not skills_df.empty:
        skills_df["skill_id"] = skills_df["skill_id"].astype(int)
        skills_df["front_name"] = skills_df["front_name"].fillna("").astype(str).map(clean_text)
        skills_df["db_name"] = skills_df["db_name"].fillna("").astype(str).map(clean_text)
        skills_df = dedupe_df(skills_df, ["skill_id"])
        skills_df = skills_df.sort_values("skill_id").reset_index(drop=True)

    return skills_df


# =========================
# 3) state bootstrap
# =========================
def bootstrap_state_from_db_ready_if_needed(major_code: str, major_name: str):
    state_files = get_state_file_paths(major_code, major_name)

    required_paths = [
        state_files["next_ids"],
        state_files["company_key_to_id"],
        state_files["skill_key_to_id"],
        state_files["seen_pair_keys"],
        state_files["seen_company_skill_keys"],
    ]

    if all(path.exists() for path in required_paths):
        return

    print("[INFO] state bootstrap from db_ready start", flush=True)

    skills_df, pair_df, companies_df, company_skills_df = load_existing_db_tables()

    skill_key_to_id = {}
    if not skills_df.empty:
        for _, row in skills_df.iterrows():
            skill_id = int(row["skill_id"])
            front_name = canonicalize_skill(clean_text(row["front_name"]))
            db_name = clean_text(row["db_name"])

            if not is_valid_skill_by_initial_rules(front_name):
                continue

            k1 = normalize_skill_key(front_name)
            k2 = normalize_skill_key(db_name)

            if k1:
                skill_key_to_id[k1] = skill_id
            if k2:
                skill_key_to_id[k2] = skill_id

    company_key_to_id = {}
    if not companies_df.empty:
        companies_df = companies_df.sort_values("company_id").reset_index(drop=True)
        for _, row in companies_df.iterrows():
            domain_id = int(row["domain_id"])
            name = clean_text(row["name"])
            company_key = build_company_key(domain_id, name)
            if company_key and company_key not in company_key_to_id:
                company_key_to_id[company_key] = int(row["company_id"])

    seen_pair_keys = set()
    if not pair_df.empty:
        for _, row in pair_df.iterrows():
            skill_name = canonicalize_skill(clean_text(row["스킬"]))
            if not is_valid_skill_by_initial_rules(skill_name):
                continue

            seen_pair_keys.add(
                build_pair_key(
                    domain_id=int(row["domain_id"]),
                    company_name=clean_text(row["기업명"]),
                    skill_name=skill_name,
                )
            )

    seen_company_skill_keys = set()
    if not company_skills_df.empty:
        for _, row in company_skills_df.iterrows():
            seen_company_skill_keys.add(
                build_company_skill_key(
                    company_id=int(row["company_id"]),
                    skill_id=int(row["skill_id"]),
                )
            )

    next_ids = {
        "next_skill_id": int(skills_df["skill_id"].max()) + 1 if not skills_df.empty else 1,
        "next_company_id": int(companies_df["company_id"].max()) + 1 if not companies_df.empty else 1,
        "next_company_skill_id": int(company_skills_df["company_skill_id"].max()) + 1 if not company_skills_df.empty else 1,
    }

    save_json_atomic(state_files["next_ids"], next_ids)
    save_json_atomic(state_files["company_key_to_id"], company_key_to_id)
    save_json_atomic(state_files["skill_key_to_id"], skill_key_to_id)
    save_text_set_atomic(state_files["seen_pair_keys"], seen_pair_keys)
    save_text_set_atomic(state_files["seen_company_skill_keys"], seen_company_skill_keys)

    print("[INFO] state bootstrap from db_ready done", flush=True)


# =========================
# 4) 증분 상세 CSV 로드
# =========================
def load_incremental_details(
    major_code: str,
    major_name: str,
    details_csv_path: str | None = None,
) -> tuple[pd.DataFrame, Path]:
    if details_csv_path:
        path = Path(details_csv_path)
        if not path.exists():
            raise FileNotFoundError(f"전달받은 상세 CSV가 없습니다: {path}")
    else:
        output_dir = get_output_dir(major_code, major_name)
        path = get_latest_file(output_dir, f"new_job_details_{major_code}_*.csv")

        if path is None:
            raise FileNotFoundError(
                f"증분 상세 CSV가 없습니다: {output_dir} / pattern=new_job_details_{major_code}_*.csv"
            )

    df = pd.read_csv(path, encoding="utf-8-sig")
    if df.empty:
        raise ValueError(f"증분 상세 CSV가 비어 있습니다: {path}")

    if "collect_status" in df.columns:
        before = len(df)
        df = df[df["collect_status"].fillna("").astype(str).str.lower() != "failed"].reset_index(drop=True)
        print(f"[INFO] filtered failed detail rows: {before} -> {len(df)}", flush=True)

    if df.empty:
        raise ValueError(f"증분 상세 CSV에서 성공 row가 없습니다: {path}")

    df["domain_id"] = int(major_code)
    df["domain_name"] = major_name

    return df, path


# =========================
# 5) skills master lookup / 신규 스킬 추가
# =========================
def build_skill_master_lookup(skills_df: pd.DataFrame) -> dict:
    lookup = {}

    if skills_df.empty:
        return lookup

    for _, row in skills_df.iterrows():
        skill_id = int(row["skill_id"])
        front_name = canonicalize_skill(clean_text(row["front_name"]))
        db_name = clean_text(row["db_name"])

        if not is_valid_skill_by_initial_rules(front_name):
            continue

        row_data = {
            "skill_id": skill_id,
            "front_name": front_name,
            "db_name": db_name,
        }

        k1 = normalize_skill_key(front_name)
        k2 = normalize_skill_key(db_name)

        if k1:
            lookup[k1] = row_data
        if k2:
            lookup[k2] = row_data

    return lookup


def append_new_skills_fast(
    pair_df_new: pd.DataFrame,
    skills_df_existing: pd.DataFrame,
    next_ids: dict,
    skill_key_to_id: dict,
):
    if pair_df_new.empty:
        return (
            skills_df_existing.copy(),
            {},
            pd.DataFrame(columns=["skill_id", "front_name", "db_name"]),
            next_ids,
            skill_key_to_id,
        )

    skills_df = skills_df_existing.copy()
    skill_lookup = build_skill_master_lookup(skills_df)

    unique_skills = (
        pair_df_new["스킬"]
        .fillna("")
        .astype(str)
        .map(canonicalize_skill)
        .tolist()
    )
    unique_skills = [x for x in unique_skills if is_valid_skill_by_initial_rules(x)]
    unique_skills = list(dict.fromkeys(unique_skills))

    next_skill_id = int(next_ids.get("next_skill_id", 1))

    resolution_rows = []
    new_skill_rows = []

    for raw_skill in unique_skills:
        raw_skill = canonicalize_skill(clean_text(raw_skill))
        if not is_valid_skill_by_initial_rules(raw_skill):
            continue

        skill_key = normalize_skill_key(raw_skill)

        matched = skill_lookup.get(skill_key)
        if matched is not None:
            resolution_rows.append({
                "original_skill": raw_skill,
                "skill_id": matched["skill_id"],
                "front_name": matched["front_name"],
                "db_name": matched["db_name"],
            })
            continue

        mapped_skill_id = skill_key_to_id.get(skill_key)
        if mapped_skill_id is not None:
            matched_row = skills_df[skills_df["skill_id"] == int(mapped_skill_id)]
            if not matched_row.empty:
                row0 = matched_row.iloc[0]
                front_name = canonicalize_skill(clean_text(row0["front_name"]))
                if is_valid_skill_by_initial_rules(front_name):
                    resolution_rows.append({
                        "original_skill": raw_skill,
                        "skill_id": int(row0["skill_id"]),
                        "front_name": front_name,
                        "db_name": clean_text(row0["db_name"]),
                    })
                    continue

        new_front_name = raw_skill
        new_db_name = make_db_name_from_front_name(new_front_name)

        fallback_key = normalize_skill_key(new_db_name)
        matched = skill_lookup.get(fallback_key)
        if matched is not None:
            resolution_rows.append({
                "original_skill": raw_skill,
                "skill_id": matched["skill_id"],
                "front_name": matched["front_name"],
                "db_name": matched["db_name"],
            })
            continue

        mapped_skill_id = skill_key_to_id.get(fallback_key)
        if mapped_skill_id is not None:
            matched_row = skills_df[skills_df["skill_id"] == int(mapped_skill_id)]
            if not matched_row.empty:
                row0 = matched_row.iloc[0]
                front_name = canonicalize_skill(clean_text(row0["front_name"]))
                if is_valid_skill_by_initial_rules(front_name):
                    resolution_rows.append({
                        "original_skill": raw_skill,
                        "skill_id": int(row0["skill_id"]),
                        "front_name": front_name,
                        "db_name": clean_text(row0["db_name"]),
                    })
                    continue

        new_row = {
            "skill_id": next_skill_id,
            "front_name": new_front_name,
            "db_name": new_db_name,
        }
        next_skill_id += 1

        new_skill_rows.append(new_row)
        resolution_rows.append({
            "original_skill": raw_skill,
            "skill_id": new_row["skill_id"],
            "front_name": new_row["front_name"],
            "db_name": new_row["db_name"],
        })

        k1 = normalize_skill_key(new_front_name)
        k2 = normalize_skill_key(new_db_name)

        if k1:
            skill_key_to_id[k1] = int(new_row["skill_id"])
            skill_lookup[k1] = new_row
        if k2:
            skill_key_to_id[k2] = int(new_row["skill_id"])
            skill_lookup[k2] = new_row

    new_skills_df = pd.DataFrame(
        new_skill_rows,
        columns=["skill_id", "front_name", "db_name"],
    )
    resolution_df = pd.DataFrame(
        resolution_rows,
        columns=["original_skill", "skill_id", "front_name", "db_name"],
    )

    if not new_skills_df.empty:
        skills_df = pd.concat([skills_df, new_skills_df], ignore_index=True)

    if not skills_df.empty:
        skills_df = dedupe_df(skills_df, ["skill_id"])
        skills_df = skills_df.sort_values("skill_id").reset_index(drop=True)

    skill_resolution_map = {}
    if not resolution_df.empty:
        for _, row in resolution_df.iterrows():
            skill_resolution_map[clean_text(row["original_skill"])] = {
                "skill_id": int(row["skill_id"]),
                "front_name": canonicalize_skill(clean_text(row["front_name"])),
                "db_name": clean_text(row["db_name"]),
            }

    next_ids["next_skill_id"] = next_skill_id

    return skills_df, skill_resolution_map, new_skills_df, next_ids, skill_key_to_id


# =========================
# 6) pair standardize / append
# =========================
def standardize_pair_skills(pair_df_new: pd.DataFrame, skill_resolution_map: dict) -> pd.DataFrame:
    if pair_df_new.empty:
        return pair_df_new.copy()

    out = pair_df_new.copy()

    def replace_skill_name(x):
        key = canonicalize_skill(clean_text(x))
        resolved = skill_resolution_map.get(key)
        if resolved is None:
            return key
        return canonicalize_skill(resolved["front_name"])

    out["스킬"] = out["스킬"].fillna("").astype(str).map(replace_skill_name)
    out["스킬"] = force_clean_skill_series(out["스킬"])
    out = out[out["스킬"] != ""].reset_index(drop=True)
    out = out[out["스킬"].map(is_valid_skill_by_initial_rules)].reset_index(drop=True)

    return out


def append_pairs_fast(pair_df_new: pd.DataFrame, seen_pair_keys: set[str]):
    if pair_df_new.empty:
        return (
            pd.DataFrame(columns=["domain_id", "domain_name", "기업명", "스킬"]),
            seen_pair_keys,
        )

    append_rows = []

    for _, row in pair_df_new.iterrows():
        domain_id = int(row["domain_id"])
        domain_name = clean_text(row["domain_name"])
        company_name = clean_text(row["기업명"])
        skill_name = canonicalize_skill(clean_text(row["스킬"]))

        if not is_valid_skill_by_initial_rules(skill_name):
            continue

        key = build_pair_key(domain_id, company_name, skill_name)
        if key in seen_pair_keys:
            continue

        seen_pair_keys.add(key)
        append_rows.append({
            "domain_id": domain_id,
            "domain_name": domain_name,
            "기업명": company_name,
            "스킬": skill_name,
        })

    added_df = pd.DataFrame(
        append_rows,
        columns=["domain_id", "domain_name", "기업명", "스킬"],
    )
    return added_df, seen_pair_keys


# =========================
# 7) companies append
# =========================
def append_companies_fast(
    pair_df_new: pd.DataFrame,
    company_key_to_id: dict,
    next_ids: dict,
):
    if pair_df_new.empty:
        return (
            company_key_to_id,
            pd.DataFrame(columns=["company_id", "name", "created_at", "updated_at", "domain_id"]),
            next_ids,
        )

    unique_companies = (
        pair_df_new[["domain_id", "기업명"]]
        .drop_duplicates(subset=["domain_id", "기업명"], keep="first")
        .reset_index(drop=True)
    )

    next_company_id = int(next_ids.get("next_company_id", 1))
    ts = now_ts()
    new_rows = []

    for _, row in unique_companies.iterrows():
        domain_id = int(row["domain_id"])
        company_name = clean_text(row["기업명"])
        company_key = build_company_key(domain_id, company_name)

        if company_key in company_key_to_id:
            continue

        company_key_to_id[company_key] = int(next_company_id)
        new_rows.append({
            "company_id": int(next_company_id),
            "name": company_name,
            "created_at": ts,
            "updated_at": ts,
            "domain_id": domain_id,
        })
        next_company_id += 1

    next_ids["next_company_id"] = next_company_id

    new_companies_df = pd.DataFrame(
        new_rows,
        columns=["company_id", "name", "created_at", "updated_at", "domain_id"],
    )
    return company_key_to_id, new_companies_df, next_ids


# =========================
# 8) company_skills append
# =========================
def build_skill_name_to_id_map(skills_df: pd.DataFrame) -> dict:
    out = {}

    if skills_df.empty:
        return out

    for _, row in skills_df.iterrows():
        skill_id = int(row["skill_id"])
        front_name = canonicalize_skill(clean_text(row["front_name"]))
        db_name = clean_text(row["db_name"])

        if not is_valid_skill_by_initial_rules(front_name):
            continue

        k1 = normalize_skill_key(front_name)
        k2 = normalize_skill_key(db_name)

        if k1:
            out[k1] = skill_id
        if k2:
            out[k2] = skill_id

    return out


def append_company_skills_fast(
    pair_df_new: pd.DataFrame,
    company_key_to_id: dict,
    skills_df: pd.DataFrame,
    seen_company_skill_keys: set[str],
    next_ids: dict,
):
    if pair_df_new.empty:
        return (
            pd.DataFrame(columns=["company_skill_id", "company_id", "skill_id"]),
            seen_company_skill_keys,
            next_ids,
        )

    skill_name_to_id = build_skill_name_to_id_map(skills_df)
    next_company_skill_id = int(next_ids.get("next_company_skill_id", 1))

    new_rows = []

    for _, row in pair_df_new.iterrows():
        domain_id = int(row["domain_id"])
        company_name = clean_text(row["기업명"])
        skill_front_name = canonicalize_skill(clean_text(row["스킬"]))

        if not is_valid_skill_by_initial_rules(skill_front_name):
            continue

        company_key = build_company_key(domain_id, company_name)
        company_id = company_key_to_id.get(company_key)
        skill_id = skill_name_to_id.get(normalize_skill_key(skill_front_name))

        if company_id is None or skill_id is None:
            continue

        key = build_company_skill_key(company_id, skill_id)
        if key in seen_company_skill_keys:
            continue

        seen_company_skill_keys.add(key)
        new_rows.append({
            "company_skill_id": int(next_company_skill_id),
            "company_id": int(company_id),
            "skill_id": int(skill_id),
        })
        next_company_skill_id += 1

    next_ids["next_company_skill_id"] = next_company_skill_id

    new_company_skills_df = pd.DataFrame(
        new_rows,
        columns=["company_skill_id", "company_id", "skill_id"],
    )

    return new_company_skills_df, seen_company_skill_keys, next_ids


# =========================
# 9) processed 디버그 저장
# =========================
def save_processed_debug_files(
    major_code: str,
    major_name: str,
    details_path: Path,
    pair_df_new: pd.DataFrame,
    new_skills_df: pd.DataFrame,
    new_companies_df: pd.DataFrame,
    new_company_skills_df: pd.DataFrame,
    debug_incremental_skill_counter: dict[str, int],
    debug_allowed_skills: set[str],
):
    processed_dir = get_processed_dir(major_code, major_name)
    processed_dir.mkdir(parents=True, exist_ok=True)

    stamp = time.strftime("%Y%m%d_%H%M%S")

    save_csv(pair_df_new, processed_dir / f"processed_pairs_{major_code}_{stamp}.csv")
    save_csv(new_skills_df, processed_dir / f"processed_new_skills_{major_code}_{stamp}.csv")
    save_csv(new_companies_df, processed_dir / f"processed_new_companies_{major_code}_{stamp}.csv")
    save_csv(new_company_skills_df, processed_dir / f"processed_new_company_skills_{major_code}_{stamp}.csv")

    counter_df = pd.DataFrame(
        [{"skill": k, "count_in_incremental": v} for k, v in sorted(debug_incremental_skill_counter.items())]
    )
    save_csv(counter_df, processed_dir / f"processed_incremental_skill_counter_{major_code}_{stamp}.csv")

    allowed_df = pd.DataFrame({"skill": sorted(debug_allowed_skills)})
    save_csv(allowed_df, processed_dir / f"processed_allowed_skills_{major_code}_{stamp}.csv")

    meta_df = pd.DataFrame([{
        "major_code": major_code,
        "major_name": major_name,
        "source_details_csv": str(details_path),
        "processed_at": now_ts(),
        "pairs_added": len(pair_df_new),
        "skills_added": len(new_skills_df),
        "companies_added": len(new_companies_df),
        "company_skills_added": len(new_company_skills_df),
    }])
    save_csv(meta_df, processed_dir / f"processed_meta_{major_code}_{stamp}.csv")


# =========================
# 10) 날짜 폴더 저장
# =========================
def save_incremental_outputs_to_run_folder(
    run_db_ready_dir: Path,
    new_skills_df: pd.DataFrame,
    actually_added_pair_df: pd.DataFrame,
    new_companies_df: pd.DataFrame,
    new_company_skills_df: pd.DataFrame,
):
    save_csv(new_skills_df, run_db_ready_dir / "skills.csv")
    save_csv(actually_added_pair_df, run_db_ready_dir / "company_skill_pairs.csv")
    save_csv(new_companies_df, run_db_ready_dir / "companies.csv")
    save_csv(new_company_skills_df, run_db_ready_dir / "company_skills.csv")

    meta_df = pd.DataFrame([{
        "saved_at": now_ts(),
        "skills_added": len(new_skills_df),
        "pairs_added": len(actually_added_pair_df),
        "companies_added": len(new_companies_df),
        "company_skills_added": len(new_company_skills_df),
    }])
    save_csv(meta_df, run_db_ready_dir / "meta.csv")


# =========================
# 11) 루트 마스터 갱신
# =========================
def update_root_master_tables(
    new_skills_df: pd.DataFrame,
    actually_added_pair_df: pd.DataFrame,
    new_companies_df: pd.DataFrame,
    new_company_skills_df: pd.DataFrame,
):
    merged_skills_df = merge_and_replace_csv(
        DB_READY_DIR / "skills.csv",
        new_skills_df,
        ["skill_id", "front_name", "db_name"],
        dedupe_subset=["skill_id"],
        sort_by=["skill_id"],
    )
    merged_pairs_df = merge_and_replace_csv(
        DB_READY_DIR / "company_skill_pairs.csv",
        actually_added_pair_df,
        ["domain_id", "domain_name", "기업명", "스킬"],
        dedupe_subset=["domain_id", "기업명", "스킬"],
        sort_by=["domain_id", "기업명", "스킬"],
    )
    merged_companies_df = merge_and_replace_csv(
        DB_READY_DIR / "companies.csv",
        new_companies_df,
        ["company_id", "name", "created_at", "updated_at", "domain_id"],
        dedupe_subset=["domain_id", "name"],
        sort_by=["company_id"],
    )
    merged_company_skills_df = merge_and_replace_csv(
        DB_READY_DIR / "company_skills.csv",
        new_company_skills_df,
        ["company_skill_id", "company_id", "skill_id"],
        dedupe_subset=["company_id", "skill_id"],
        sort_by=["company_skill_id"],
    )

    return merged_skills_df, merged_pairs_df, merged_companies_df, merged_company_skills_df


# =========================
# 12) 메인 실행 함수
# =========================
def run_incremental_preprocess(
    major_code: str,
    major_name: str,
    details_csv_path: str | None = None,
):
    print("=" * 70, flush=True)
    print(f"[INCREMENTAL_PREPROCESS] start {major_code} / {major_name}", flush=True)
    print("=" * 70, flush=True)

    ensure_dirs(major_code, major_name)
    DB_READY_DIR.mkdir(parents=True, exist_ok=True)

    run_date = get_run_date_folder_name()
    run_db_ready_dir = get_run_db_ready_dir(run_date)
    print(f"[INFO] run date folder: {run_db_ready_dir}", flush=True)

    state_files = get_state_file_paths(major_code, major_name)
    bootstrap_state_from_db_ready_if_needed(major_code, major_name)

    next_ids = load_json_if_exists(
        state_files["next_ids"],
        {
            "next_skill_id": 1,
            "next_company_id": 1,
            "next_company_skill_id": 1,
        },
    )
    company_key_to_id = load_json_if_exists(state_files["company_key_to_id"], {})
    skill_key_to_id = load_json_if_exists(state_files["skill_key_to_id"], {})
    seen_pair_keys = load_text_set(state_files["seen_pair_keys"])
    seen_company_skill_keys = load_text_set(state_files["seen_company_skill_keys"])

    details_df, details_path = load_incremental_details(
        major_code=major_code,
        major_name=major_name,
        details_csv_path=details_csv_path,
    )
    print(f"[INFO] details csv: {details_path}", flush=True)
    print(f"[INFO] details rows: {len(details_df)}", flush=True)

    existing_valid_skills = load_existing_valid_skills_from_skills_csv()
    print(f"[INFO] existing valid skills from skills.csv: {len(existing_valid_skills)}", flush=True)

    incremental_skill_counter = build_incremental_skill_counter(details_df)
    print(f"[INFO] incremental valid skill candidates: {len(incremental_skill_counter)}", flush=True)

    new_valid_skills = {
        skill
        for skill, cnt in incremental_skill_counter.items()
        if cnt >= NEW_SKILL_MIN_COUNT and skill not in existing_valid_skills
    }
    print(f"[INFO] new valid skills from incremental: {len(new_valid_skills)}", flush=True)

    allowed_skills = set()
    allowed_skills.update(existing_valid_skills)
    allowed_skills.update(new_valid_skills)

    allowed_skills = {canonicalize_skill(x) for x in allowed_skills if is_valid_skill_by_initial_rules(x)}
    allowed_skills = {x for x in allowed_skills if x}

    print(f"[INFO] total allowed skills: {len(allowed_skills)}", flush=True)

    pair_df_new_raw = build_company_skill_pairs_with_initial_rules(
        df=details_df,
        allowed_skills=allowed_skills,
    )
    pair_df_new_raw = hard_clean_df_for_output(pair_df_new_raw)

    if not pair_df_new_raw.empty and "스킬" in pair_df_new_raw.columns:
        pair_df_new_raw["스킬"] = force_clean_skill_series(pair_df_new_raw["스킬"])
        pair_df_new_raw["스킬"] = pair_df_new_raw["스킬"].fillna("").astype(str).map(canonicalize_skill)
        pair_df_new_raw = pair_df_new_raw[pair_df_new_raw["스킬"].map(is_valid_skill_by_initial_rules)].reset_index(drop=True)

    pair_df_new_raw = dedupe_df(pair_df_new_raw, ["domain_id", "기업명", "스킬"])
    print(f"[INFO] extracted new pairs before append: {len(pair_df_new_raw)}", flush=True)

    existing_skills_df = load_skills_table_only()

    updated_skills_df, skill_resolution_map, new_skills_df, next_ids, skill_key_to_id = append_new_skills_fast(
        pair_df_new=pair_df_new_raw,
        skills_df_existing=existing_skills_df,
        next_ids=next_ids,
        skill_key_to_id=skill_key_to_id,
    )

    pair_df_new = standardize_pair_skills(pair_df_new_raw, skill_resolution_map)
    pair_df_new = pair_df_new[pair_df_new["스킬"].map(is_valid_skill_by_initial_rules)].reset_index(drop=True)
    pair_df_new = dedupe_df(pair_df_new, ["domain_id", "기업명", "스킬"])

    actually_added_pair_df, seen_pair_keys = append_pairs_fast(
        pair_df_new=pair_df_new,
        seen_pair_keys=seen_pair_keys,
    )

    company_key_to_id, new_companies_df, next_ids = append_companies_fast(
        pair_df_new=actually_added_pair_df,
        company_key_to_id=company_key_to_id,
        next_ids=next_ids,
    )

    new_company_skills_df, seen_company_skill_keys, next_ids = append_company_skills_fast(
        pair_df_new=actually_added_pair_df,
        company_key_to_id=company_key_to_id,
        skills_df=updated_skills_df,
        seen_company_skill_keys=seen_company_skill_keys,
        next_ids=next_ids,
    )

    new_skills_df = hard_clean_df_for_output(new_skills_df)
    actually_added_pair_df = hard_clean_df_for_output(actually_added_pair_df)
    new_companies_df = hard_clean_df_for_output(new_companies_df)
    new_company_skills_df = hard_clean_df_for_output(new_company_skills_df)

    if not new_skills_df.empty:
        new_skills_df["front_name"] = new_skills_df["front_name"].fillna("").astype(str).map(canonicalize_skill)
        new_skills_df["db_name"] = new_skills_df["db_name"].fillna("").astype(str).map(clean_text)
        new_skills_df = new_skills_df[new_skills_df["front_name"].map(is_valid_skill_by_initial_rules)].reset_index(drop=True)
        new_skills_df = dedupe_df(new_skills_df, ["skill_id"])
        new_skills_df = new_skills_df.sort_values("skill_id").reset_index(drop=True)

    if not actually_added_pair_df.empty:
        actually_added_pair_df["스킬"] = actually_added_pair_df["스킬"].fillna("").astype(str).map(canonicalize_skill)
        actually_added_pair_df = actually_added_pair_df[actually_added_pair_df["스킬"].map(is_valid_skill_by_initial_rules)].reset_index(drop=True)
        actually_added_pair_df = dedupe_df(actually_added_pair_df, ["domain_id", "기업명", "스킬"])

    if not new_companies_df.empty:
        new_companies_df = dedupe_df(new_companies_df, ["company_id"])
        new_companies_df = new_companies_df.sort_values("company_id").reset_index(drop=True)

    if not new_company_skills_df.empty:
        new_company_skills_df = dedupe_df(new_company_skills_df, ["company_skill_id"])
        new_company_skills_df = new_company_skills_df.sort_values("company_skill_id").reset_index(drop=True)

    # 1) 날짜 폴더: 이번 증분에서 새로 추가된 것만 저장
    save_incremental_outputs_to_run_folder(
        run_db_ready_dir=run_db_ready_dir,
        new_skills_df=new_skills_df,
        actually_added_pair_df=actually_added_pair_df,
        new_companies_df=new_companies_df,
        new_company_skills_df=new_company_skills_df,
    )

    # 2) 루트 db_ready: 최신 마스터로 누적 갱신
    merged_skills_df, merged_pairs_df, merged_companies_df, merged_company_skills_df = update_root_master_tables(
        new_skills_df=new_skills_df,
        actually_added_pair_df=actually_added_pair_df,
        new_companies_df=new_companies_df,
        new_company_skills_df=new_company_skills_df,
    )

    save_json_atomic(state_files["next_ids"], next_ids)
    save_json_atomic(state_files["company_key_to_id"], company_key_to_id)
    save_json_atomic(state_files["skill_key_to_id"], skill_key_to_id)
    save_text_set_atomic(state_files["seen_pair_keys"], seen_pair_keys)
    save_text_set_atomic(state_files["seen_company_skill_keys"], seen_company_skill_keys)

    save_processed_debug_files(
        major_code=major_code,
        major_name=major_name,
        details_path=details_path,
        pair_df_new=actually_added_pair_df,
        new_skills_df=new_skills_df,
        new_companies_df=new_companies_df,
        new_company_skills_df=new_company_skills_df,
        debug_incremental_skill_counter=incremental_skill_counter,
        debug_allowed_skills=allowed_skills,
    )

    total_skills = int(len(merged_skills_df.drop_duplicates(subset=["skill_id"]))) if not merged_skills_df.empty else 0
    total_pairs = int(len(merged_pairs_df.drop_duplicates(subset=["domain_id", "기업명", "스킬"]))) if not merged_pairs_df.empty else 0
    total_companies = int(len(merged_companies_df.drop_duplicates(subset=["domain_id", "name"]))) if not merged_companies_df.empty else 0
    total_company_skills = int(len(merged_company_skills_df.drop_duplicates(subset=["company_id", "skill_id"]))) if not merged_company_skills_df.empty else 0

    print(f"[DONE] run folder={run_db_ready_dir}", flush=True)
    print(f"[DONE] added pairs={len(actually_added_pair_df)}", flush=True)
    print(f"[DONE] added skills={len(new_skills_df)}", flush=True)
    print(f"[DONE] added companies={len(new_companies_df)}", flush=True)
    print(f"[DONE] added company_skills={len(new_company_skills_df)}", flush=True)
    print(f"[DONE] skills total(master)={total_skills}", flush=True)
    print(f"[DONE] pairs total(master)={total_pairs}", flush=True)
    print(f"[DONE] companies total(master)={total_companies}", flush=True)
    print(f"[DONE] company_skills total(master)={total_company_skills}", flush=True)

    print("=" * 70, flush=True)
    print(f"[INCREMENTAL_PREPROCESS] finished {major_code} / {major_name}", flush=True)
    print("=" * 70, flush=True)

    return {
        "major_code": major_code,
        "major_name": major_name,
        "details_csv": str(details_path),
        "run_db_ready_dir": str(run_db_ready_dir),
        "added_pairs": int(len(actually_added_pair_df)),
        "added_skills": int(len(new_skills_df)),
        "added_companies": int(len(new_companies_df)),
        "added_company_skills": int(len(new_company_skills_df)),
        "total_skills_master": int(total_skills),
        "total_pairs_master": int(total_pairs),
        "total_companies_master": int(total_companies),
        "total_company_skills_master": int(total_company_skills),
    }


def main():
    major_code = "10007"
    major_name = "IT정보통신업"
    run_incremental_preprocess(
        major_code=major_code,
        major_name=major_name,
    )


if __name__ == "__main__":
    main()