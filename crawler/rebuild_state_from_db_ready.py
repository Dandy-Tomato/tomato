import json
import re
from pathlib import Path

import pandas as pd

from crawler.paths import ensure_dirs, get_state_dir
from crawler.preprocess_new_jobs import clean_text


ROOT_DIR = Path(__file__).resolve().parent
DB_READY_DIR = ROOT_DIR / "db_ready"

TARGET_MAJOR_CODE = "10007"
TARGET_MAJOR_NAME = "IT정보통신업"


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


def save_text_set_atomic(path: Path, values: set[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        for value in sorted(values):
            f.write(f"{value}\n")
    tmp_path.replace(path)


def normalize_skill_key(text: str) -> str:
    t = clean_text(text).lower()
    if not t:
        return ""
    t = t.replace("&", "and")
    t = re.sub(r"[.\-_/+\s()]+", "", t)
    return t


def build_pair_key(domain_id: int, company_name: str, skill_name: str) -> str:
    return f"{int(domain_id)}||{clean_text(company_name)}||{clean_text(skill_name)}"


def build_company_key(domain_id: int, company_name: str) -> str:
    return f"{int(domain_id)}||{clean_text(company_name)}"


def build_company_skill_key(company_id: int, skill_id: int) -> str:
    return f"{int(company_id)}||{int(skill_id)}"


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


def rebuild_state_from_db_ready(major_code: str, major_name: str):
    print("=" * 70, flush=True)
    print(f"[REBUILD_STATE] start {major_code} / {major_name}", flush=True)
    print("=" * 70, flush=True)

    ensure_dirs(major_code, major_name)
    state_dir = get_state_dir(major_code, major_name)

    next_ids_path = state_dir / "next_ids.json"
    company_key_to_id_path = state_dir / "company_key_to_id.json"
    skill_key_to_id_path = state_dir / "skill_key_to_id.json"
    seen_pair_keys_path = state_dir / "seen_pair_keys.txt"
    seen_company_skill_keys_path = state_dir / "seen_company_skill_keys.txt"

    skills_df, pair_df, companies_df, company_skills_df = load_existing_db_tables()

    skill_key_to_id = {}
    if not skills_df.empty:
        for _, row in skills_df.iterrows():
            skill_id = int(row["skill_id"])
            front_name = clean_text(row["front_name"])
            db_name = clean_text(row["db_name"])

            k1 = normalize_skill_key(front_name)
            k2 = normalize_skill_key(db_name)

            if k1:
                skill_key_to_id[k1] = skill_id
            if k2:
                skill_key_to_id[k2] = skill_id

    company_key_to_id = {}
    if not companies_df.empty:
        for _, row in companies_df.iterrows():
            company_key = build_company_key(
                domain_id=int(row["domain_id"]),
                company_name=clean_text(row["name"]),
            )
            company_key_to_id[company_key] = int(row["company_id"])

    seen_pair_keys = set()
    if not pair_df.empty:
        for _, row in pair_df.iterrows():
            seen_pair_keys.add(
                build_pair_key(
                    domain_id=int(row["domain_id"]),
                    company_name=clean_text(row["기업명"]),
                    skill_name=clean_text(row["스킬"]),
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

    save_json_atomic(next_ids_path, next_ids)
    save_json_atomic(company_key_to_id_path, company_key_to_id)
    save_json_atomic(skill_key_to_id_path, skill_key_to_id)
    save_text_set_atomic(seen_pair_keys_path, seen_pair_keys)
    save_text_set_atomic(seen_company_skill_keys_path, seen_company_skill_keys)

    print(f"[DONE] next_ids -> {next_ids_path}", flush=True)
    print(f"[DONE] company_key_to_id -> {company_key_to_id_path} ({len(company_key_to_id)})", flush=True)
    print(f"[DONE] skill_key_to_id -> {skill_key_to_id_path} ({len(skill_key_to_id)})", flush=True)
    print(f"[DONE] seen_pair_keys -> {seen_pair_keys_path} ({len(seen_pair_keys)})", flush=True)
    print(f"[DONE] seen_company_skill_keys -> {seen_company_skill_keys_path} ({len(seen_company_skill_keys)})", flush=True)

    print("=" * 70, flush=True)
    print(f"[REBUILD_STATE] finished {major_code} / {major_name}", flush=True)
    print("=" * 70, flush=True)


def main():
    rebuild_state_from_db_ready(
        major_code=TARGET_MAJOR_CODE,
        major_name=TARGET_MAJOR_NAME,
    )


if __name__ == "__main__":
    main()