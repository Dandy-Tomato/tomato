import time
import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from crawler.common import (
    build_driver,
    safe_quit_driver,
    restart_driver,
    clean_text,
    load_settings,
)
from crawler.paths import (
    get_state_dir,
    get_output_dir,
    ensure_dirs,
)


SETTINGS = load_settings()

SAVE_EVERY = SETTINGS.get("save_every", 50)
RESTART_EVERY = SETTINGS.get("restart_every", 120)


COLUMNS = [
    "기업명", "기업구분",
    "모집분야", "모집인원", "고용형태", "직급/직책", "급여", "근무시간", "근무지주소",
    "경력", "학력", "우대조건", "스킬", "핵심역량",
    "기업URL",
    "collect_status",
    "collect_error_reason",
]

LABEL_TO_COL = {
    "기업구분": "기업구분",
    "모집분야": "모집분야",
    "모집인원": "모집인원",
    "고용형태": "고용형태",
    "직급/직책": "직급/직책",
    "급여": "급여",
    "근무시간": "근무시간",
    "근무지주소": "근무지주소",
    "경력": "경력",
    "학력": "학력",
    "우대조건": "우대조건",
    "스킬": "스킬",
    "핵심역량": "핵심역량",
}
TARGET_LABELS = set(LABEL_TO_COL.keys())

BAD_FIELD_PATTERNS = [
    r"홈페이지\s*지원", r"즉시\s*지원", r"간편\s*지원", r"지원하기", r"입사지원",
    r"채용\s*공고", r"공고\s*바로가기", r"바로\s*지원",
]


# =========================
# 1) 유틸 / 상태
# =========================
def _dedup_list(items):
    out, seen = [], set()
    for x in items:
        x = clean_text(x)
        if not x or x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def merge_and_replace_csv(path: Path, df: pd.DataFrame, columns: list[str]):
    """
    append 대신:
    기존 CSV 읽기 -> 신규 DF 병합 -> tmp 저장 -> replace
    collect 단계는 같은 run 안에서 같은 파일명에만 계속 저장하므로
    dedupe는 굳이 강하게 하지 않고 순서 보존 위주로 간다.
    """
    if df.empty:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        old_df = pd.read_csv(path, encoding="utf-8-sig")
    else:
        old_df = pd.DataFrame(columns=columns)

    for col in columns:
        if col not in old_df.columns:
            old_df[col] = None

    incoming_df = df.copy()
    for col in columns:
        if col not in incoming_df.columns:
            incoming_df[col] = None

    old_df = old_df[columns].copy()
    incoming_df = incoming_df[columns].copy()

    merged = pd.concat([old_df, incoming_df], ignore_index=True)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    merged.to_csv(tmp_path, index=False, encoding="utf-8-sig")
    tmp_path.replace(path)


def append_lines(path: Path, values: list[str]):
    if not values:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for value in values:
            value = clean_text(value)
            if value:
                f.write(f"{value}\n")


def dedup_str_list(values: list[str]) -> list[str]:
    out = []
    seen = set()
    for value in values:
        value = clean_text(value)
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def is_new_react_detail(html: str) -> bool:
    return ('data-sentry-component' in html) or ('data-accent-color="gray700"' in html)


def is_bad_mojip_field(text: str) -> bool:
    t = clean_text(text)
    if not t or len(t) <= 2:
        return True
    return any(re.search(p, t) for p in BAD_FIELD_PATTERNS)


def load_existing_seen_ids(path) -> set[str]:
    if not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def safe_get(driver, url, sleep_after=0.20, retry=1):
    for attempt in range(retry + 1):
        try:
            driver.get(url)
            time.sleep(sleep_after)
            return True
        except TimeoutException:
            try:
                driver.execute_script("window.stop();")
            except Exception:
                pass
            time.sleep(0.15)
            return True
        except Exception as e:
            msg = str(e)
            if "Read timed out" in msg or "HTTPConnectionPool(host='localhost'" in msg:
                raise
            if attempt < retry:
                time.sleep(0.5)
                continue
            return False


def wait_detail_ready(driver, timeout=7) -> bool:
    candidates = [
        (By.CSS_SELECTOR, 'div[data-sentry-component="RecruitmentGuidelines"]'),
        (By.CSS_SELECTOR, 'div[data-sentry-component="Qualification"]'),
        (By.CSS_SELECTOR, 'div[data-sentry-component="RecruitmentField"]'),
        (By.CSS_SELECTOR, 'span[data-accent-color="gray700"]'),
        (By.XPATH, "//*[contains(., '모집요강') or contains(., '지원자격')]"),
    ]

    end = time.time() + timeout
    while time.time() < end:
        for by, sel in candidates:
            try:
                driver.find_element(by, sel)
                return True
            except Exception:
                continue
        time.sleep(0.15)

    html = (driver.page_source or "")[:4000].lower()
    if "captcha" in html or "cloudflare" in html or "로봇" in html:
        return False
    return False


def make_fallback_row(company_name: str, job_detail_url: str, title_text: str = None, error_reason: str = None):
    row = {col: None for col in COLUMNS}
    row["기업명"] = company_name
    row["기업URL"] = job_detail_url
    row["모집분야"] = clean_text(title_text) if title_text else None
    row["collect_status"] = "failed"
    row["collect_error_reason"] = clean_text(error_reason)
    return row


# =========================
# 2) 신형(React) 파서
# =========================
def safe_click_more_buttons_in_section(section_el, max_clicks=3):
    try:
        for _ in range(max_clicks):
            btns = section_el.find_elements(By.CSS_SELECTOR, "button")
            clicked = False
            for b in btns:
                try:
                    t = clean_text(b.text)
                    if t in ("", "...", "…"):
                        b.click()
                        time.sleep(0.05)
                        clicked = True
                except Exception:
                    continue
            if not clicked:
                break
    except Exception:
        pass


def pick_value_texts(root_el, label_text: str):
    vals = []
    allow_gray = (label_text == "모집분야")

    try:
        spans = root_el.find_elements(By.CSS_SELECTOR, "span")
        for sp in spans:
            t = clean_text(sp.text)
            if not t or t == label_text:
                continue
            accent = (sp.get_attribute("data-accent-color") or "").strip()
            if (accent in ("gray700", "gray500")) and (not allow_gray):
                continue
            vals.append(t)
    except Exception:
        pass

    try:
        lis = root_el.find_elements(By.CSS_SELECTOR, "ul li")
        for li in lis:
            t = clean_text(li.text)
            if t and t != label_text:
                vals.append(t)
    except Exception:
        pass

    return _dedup_list(vals)


def extract_by_label_span(label_el):
    label = clean_text(label_el.text)
    if not label or label not in TARGET_LABELS:
        return None, None

    values = []
    try:
        sib = label_el.find_element(By.XPATH, "following-sibling::*[1]")
        values = pick_value_texts(sib, label)
    except Exception:
        values = []

    if not values:
        try:
            container = label_el.find_element(By.XPATH, "ancestor::div[1]")
            values = pick_value_texts(container, label)
        except Exception:
            values = []

    if not values:
        return label, None
    return label, " | ".join(values)


def harvest_labels_in_component(driver, component_name: str):
    out = {}
    try:
        sec = WebDriverWait(driver, 4).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f'div[data-sentry-component="{component_name}"]')
            )
        )
    except Exception:
        return out

    safe_click_more_buttons_in_section(sec, max_clicks=3)

    label_spans = sec.find_elements(By.CSS_SELECTOR, 'span[data-accent-color="gray700"]')
    for lb in label_spans:
        try:
            lab, val = extract_by_label_span(lb)
            if not lab or not val:
                continue
            if lab in LABEL_TO_COL and (lab not in out or not out[lab]):
                out[lab] = val
        except Exception:
            continue

    return out


def harvest_labels_anywhere(driver):
    out = {}
    label_spans = driver.find_elements(By.CSS_SELECTOR, 'span[data-accent-color="gray700"]')
    for lb in label_spans:
        try:
            lab, val = extract_by_label_span(lb)
            if not lab or not val:
                continue
            if lab in LABEL_TO_COL and (lab not in out or not out[lab]):
                out[lab] = val
        except Exception:
            continue
    return out


def fallback_recruitment_field_component(driver):
    fields = []
    try:
        els = driver.find_elements(By.CSS_SELECTOR, 'div[data-sentry-component="RecruitmentField"]')
        for el in els:
            t = clean_text(el.text)
            if t:
                fields.append(t)
    except Exception:
        pass
    fields = _dedup_list(fields)
    return " | ".join(fields) if fields else None


def scroll_and_collect_new_all_labels(driver, max_steps=10, step_px=1400, wait=0.08):
    collected = {}
    same_cnt = 0

    for _ in range(max_steps):
        before = len(collected)

        merged = {}
        merged.update(harvest_labels_in_component(driver, "RecruitmentGuidelines"))
        merged.update(harvest_labels_in_component(driver, "Qualification"))

        if len(merged) < len(TARGET_LABELS):
            merged.update(harvest_labels_anywhere(driver))

        for lab, val in merged.items():
            if lab not in collected or not collected[lab]:
                collected[lab] = val

        if not clean_text(collected.get("모집분야")):
            v = fallback_recruitment_field_component(driver)
            if v:
                collected["모집분야"] = v

        if TARGET_LABELS.issubset(set(collected.keys())):
            break

        after = len(collected)
        if after == before:
            same_cnt += 1
        else:
            same_cnt = 0

        if same_cnt >= 3:
            break

        try:
            driver.execute_script(f"window.scrollBy(0, {step_px});")
        except Exception:
            pass
        time.sleep(wait)

    return collected


# =========================
# 3) 구형(GI_Read) 파서
# =========================
def legacy_find_label_value(soup: BeautifulSoup, label: str):
    candidates = soup.find_all(string=re.compile(rf"^{re.escape(label)}$"))
    if not candidates:
        candidates = soup.find_all(string=re.compile(rf"^{re.escape(label)}\s*[:：]?\s*$"))

    for s in candidates[:10]:
        try:
            tag = s.parent

            nxt = tag.find_next_sibling()
            if nxt:
                v = clean_text(nxt.get_text(" ", strip=True))
                if v and v != label:
                    return v

            parent = tag.parent
            if parent:
                full = clean_text(parent.get_text(" ", strip=True))
                v = clean_text(re.sub(rf"^{re.escape(label)}\s*[:：]?\s*", "", full))
                if v and v != full and v != label:
                    return v
        except Exception:
            continue

    return None


def parse_legacy_detail(html: str):
    soup = BeautifulSoup(html, "lxml")
    out = {}
    for lab in TARGET_LABELS:
        val = legacy_find_label_value(soup, lab)
        if val:
            out[lab] = val
    return out


# =========================
# 4) 상세 파싱
# =========================
def parse_company_detail_full(driver, company_name: str, job_detail_url: str, title_text: str = None):
    row = {col: None for col in COLUMNS}
    row["기업명"] = company_name
    row["기업URL"] = job_detail_url
    row["collect_status"] = "success"
    row["collect_error_reason"] = None

    html = driver.page_source
    if is_new_react_detail(html):
        collected = scroll_and_collect_new_all_labels(driver)
    else:
        collected = parse_legacy_detail(html)

    for lab, val in collected.items():
        col = LABEL_TO_COL.get(lab)
        if col:
            row[col] = val

    if is_bad_mojip_field(row.get("모집분야")):
        row["모집분야"] = clean_text(title_text) if title_text else row.get("모집분야")

    return row


# =========================
# 5) 메인 실행
# =========================
def run_collect(
    major_code: str,
    major_name: str,
    input_csv_path: str | None = None,
):
    ensure_dirs(major_code, major_name)

    output_dir = get_output_dir(major_code, major_name)
    state_dir = get_state_dir(major_code, major_name)

    seen_path = state_dir / f"seen_job_ids_{major_code}.txt"

    if input_csv_path:
        input_csv = Path(input_csv_path)
        if not input_csv.exists():
            raise FileNotFoundError(f"전달받은 링크 CSV가 없습니다: {input_csv}")
    else:
        input_csv_candidates = sorted(output_dir.glob(f"new_job_links_{major_code}_*.csv"))
        if not input_csv_candidates:
            print(f"[INFO] no discover file: {major_code}", flush=True)
            return {
                "major_code": major_code,
                "major_name": major_name,
                "input_csv": None,
                "detail_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "out_csv": None,
                "success_job_ids_path": None,
                "failed_job_ids_path": None,
            }
        input_csv = input_csv_candidates[-1]

    out_ts = time.strftime("%Y%m%d_%H%M%S")
    out_raw_csv = output_dir / f"new_job_details_{major_code}_{out_ts}.csv"
    success_job_ids_path = output_dir / f"successful_job_ids_{major_code}_{out_ts}.txt"
    failed_job_ids_path = output_dir / f"failed_job_ids_{major_code}_{out_ts}.txt"

    existing_seen = load_existing_seen_ids(seen_path)

    links_df = pd.read_csv(input_csv, encoding="utf-8-sig")
    if links_df.empty:
        print("[INFO] 신규 링크 파일이 비어 있습니다.", flush=True)
        return {
            "major_code": major_code,
            "major_name": major_name,
            "input_csv": str(input_csv),
            "detail_count": 0,
            "success_count": 0,
            "fail_count": 0,
            "out_csv": str(out_raw_csv),
            "success_job_ids_path": None,
            "failed_job_ids_path": None,
        }

    print(f"[INFO] input csv: {input_csv}", flush=True)
    print(f"[INFO] rows in input: {len(links_df)}", flush=True)

    records = []
    for _, r in links_df.iterrows():
        job_id = clean_text(r.get("job_id", ""))
        if not job_id or job_id in existing_seen:
            continue

        records.append({
            "job_id": job_id,
            "company": clean_text(r.get("company", "")),
            "title": clean_text(r.get("title", "")),
            "url": clean_text(r.get("url", "")),
        })

    print(f"[INFO] settings: save_every={SAVE_EVERY}, restart_every={RESTART_EVERY}", flush=True)
    print(f"[INFO] records after seen filter: {len(records)}", flush=True)

    if not records:
        print("[INFO] 새로 수집할 공고가 없습니다.", flush=True)
        return {
            "major_code": major_code,
            "major_name": major_name,
            "input_csv": str(input_csv),
            "detail_count": 0,
            "success_count": 0,
            "fail_count": 0,
            "out_csv": str(out_raw_csv),
            "success_job_ids_path": None,
            "failed_job_ids_path": None,
        }

    driver = build_driver()

    buffer_rows = []
    success_job_ids = []
    failed_job_ids = []
    detail_count = 0
    consecutive_failures = 0

    def flush_buffer():
        nonlocal buffer_rows
        if not buffer_rows:
            return

        merge_and_replace_csv(
            out_raw_csv,
            pd.DataFrame(buffer_rows, columns=COLUMNS),
            COLUMNS,
        )
        print(f"[SAVE] buffer merge+replace -> {out_raw_csv} (rows={len(buffer_rows)})", flush=True)
        buffer_rows.clear()

    try:
        for idx, item in enumerate(records, start=1):
            company_name = item["company"]
            job_detail_url = item["url"]
            title_text = item["title"]
            job_id = item["job_id"]

            print(f"[{idx}/{len(records)}] {job_id} | {company_name} | {job_detail_url}", flush=True)

            if idx % RESTART_EVERY == 0:
                print("[INFO] periodic restart driver", flush=True)
                driver = restart_driver(driver)
                consecutive_failures = 0

            ok = False
            get_error_reason = None
            try:
                ok = safe_get(driver, job_detail_url, sleep_after=0.20, retry=1)
                if not ok:
                    get_error_reason = "safe_get_failed"
            except Exception as e:
                print(f"[ERR] get exception: {type(e).__name__} | {str(e)[:200]}", flush=True)
                ok = False
                get_error_reason = f"get_exception:{type(e).__name__}"

            if ok:
                ready = wait_detail_ready(driver, timeout=7)
                if not ready:
                    get_error_reason = "detail_dom_not_ready"
            else:
                ready = False

            if not ready:
                print("[WARN] detail dom not ready -> fallback row", flush=True)

                fallback = make_fallback_row(
                    company_name=company_name,
                    job_detail_url=job_detail_url,
                    title_text=title_text,
                    error_reason=get_error_reason or "detail_not_ready",
                )

                buffer_rows.append(fallback)
                failed_job_ids.append(job_id)
                detail_count += 1

                consecutive_failures += 1
                if consecutive_failures >= 3:
                    print("[INFO] restart driver by consecutive failures", flush=True)
                    driver = restart_driver(driver)
                    consecutive_failures = 0

                if len(buffer_rows) >= SAVE_EVERY:
                    flush_buffer()
                continue

            try:
                row = parse_company_detail_full(
                    driver,
                    company_name,
                    job_detail_url,
                    title_text=title_text,
                )
                buffer_rows.append(row)
                success_job_ids.append(job_id)
                detail_count += 1
                consecutive_failures = 0

                print("[OK] parsed", flush=True)
                time.sleep(0.03)

            except Exception as e:
                print(f"[ERR] parse exception: {type(e).__name__} | {str(e)[:200]}", flush=True)

                fallback = make_fallback_row(
                    company_name=company_name,
                    job_detail_url=job_detail_url,
                    title_text=title_text,
                    error_reason=f"parse_exception:{type(e).__name__}",
                )

                buffer_rows.append(fallback)
                failed_job_ids.append(job_id)
                detail_count += 1

                consecutive_failures += 1
                if consecutive_failures >= 3:
                    print("[INFO] restart driver by consecutive failures", flush=True)
                    driver = restart_driver(driver)
                    consecutive_failures = 0

            if len(buffer_rows) >= SAVE_EVERY:
                flush_buffer()

        flush_buffer()

        success_job_ids = dedup_str_list(success_job_ids)
        failed_job_ids = dedup_str_list(failed_job_ids)

        if success_job_ids:
            append_lines(success_job_ids_path, success_job_ids)

        if failed_job_ids:
            append_lines(failed_job_ids_path, failed_job_ids)

        print(f"[DONE] saved detail csv: {out_raw_csv}", flush=True)
        if success_job_ids:
            print(f"[DONE] saved success job ids: {len(success_job_ids)} -> {success_job_ids_path}", flush=True)
        if failed_job_ids:
            print(f"[DONE] saved failed job ids: {len(failed_job_ids)} -> {failed_job_ids_path}", flush=True)

        return {
            "major_code": major_code,
            "major_name": major_name,
            "input_csv": str(input_csv),
            "detail_count": detail_count,
            "success_count": len(success_job_ids),
            "fail_count": len(failed_job_ids),
            "success_job_ids": len(success_job_ids),
            "out_csv": str(out_raw_csv),
            "success_job_ids_path": str(success_job_ids_path) if success_job_ids else None,
            "failed_job_ids_path": str(failed_job_ids_path) if failed_job_ids else None,
        }

    finally:
        driver = safe_quit_driver(driver)