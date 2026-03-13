import csv
import math
import time
import re
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from crawler.common import (
    build_driver,
    safe_quit_driver,
    restart_driver,
    clean_text,
    extract_job_id,
    load_settings,
    save_json_atomic,
)
from crawler.paths import (
    get_state_dir,
    get_output_dir,
    ensure_dirs,
)


SETTINGS = load_settings()

BASE = SETTINGS.get("base_url", "https://www.jobkorea.co.kr")
LIST_URL = SETTINGS.get(
    "list_url",
    "https://www.jobkorea.co.kr/recruit/joblist?menucode=industry",
)

MAX_PAGES = SETTINGS.get("max_pages", 150)
SORT_VALUE = SETTINGS.get("sort_value", "2")   # 등록일순
ZERO_NEW_STOP_STREAK = SETTINGS.get("zero_new_stop_streak", 2)


# =========================
# 1) 상태 / 유틸
# =========================
def load_seen_ids(path) -> set[str]:
    if not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def dedup_rows(rows: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for row in rows:
        key = (
            row.get("job_id", ""),
            row.get("company", ""),
            row.get("title", ""),
            row.get("url", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def safe_write_text(path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(text, encoding="utf-8")
    tmp_path.replace(path)


def safe_get(driver, url, sleep_after=0.25, retry=1):
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


# =========================
# 2) 필터 적용 / 정렬
# =========================
def click_label_for(driver, input_id: str):
    lb = driver.find_element(By.CSS_SELECTOR, f'label[for="{input_id}"]')
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", lb)
    time.sleep(0.02)
    lb.click()


def get_selected_conditions_text(driver) -> str:
    try:
        box = driver.find_element(By.CSS_SELECTOR, "div#devCndtDispArea")
        return clean_text(box.text)
    except Exception:
        return ""


def check_all_industry_subcategories(driver, major_code: str):
    major_id = f"industry_step1_{major_code}"
    WebDriverWait(driver, 12).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"#{major_id}"))
    )
    major_input = driver.find_element(By.CSS_SELECTOR, f"#{major_id}")
    if not major_input.is_selected():
        click_label_for(driver, major_id)
        time.sleep(0.08)

    ul_id = f"industry_step2_{major_code}_ly"
    ul = WebDriverWait(driver, 12).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"ul#{ul_id}"))
    )

    try:
        scroll_box = ul.find_element(
            By.XPATH,
            "ancestor::div[contains(@class,'nano-content') and contains(@class,'dev-sub')]"
        )
    except Exception:
        scroll_box = None

    inputs = ul.find_elements(
        By.CSS_SELECTOR,
        'input[type="checkbox"][id^="industry_step2_"]'
    )
    for inp in inputs:
        try:
            if inp.is_selected():
                continue

            iid = inp.get_attribute("id")

            if scroll_box is not None:
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[1].offsetTop - 120;",
                    scroll_box,
                    inp,
                )
            else:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    inp,
                )

            time.sleep(0.003)
            click_label_for(driver, iid)
            time.sleep(0.005)
        except Exception:
            continue


def get_total_count(driver) -> int:
    el = WebDriverWait(driver, 12).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input#hdnGICnt"))
    )
    raw = el.get_attribute("value") or "0"
    return int(re.sub(r"[^\d]", "", raw) or "0")


def wait_list_loaded(driver):
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tr.devloopArea"))
    )
    time.sleep(0.05)


def wait_count_stabilized_after_search(driver, prev_cnt: int, timeout=14):
    end = time.time() + timeout
    last = None
    stable_hits = 0

    while time.time() < end:
        try:
            wait_list_loaded(driver)
            cnt = get_total_count(driver)
        except Exception:
            time.sleep(0.15)
            continue

        if last is not None and cnt == last:
            stable_hits += 1
        else:
            stable_hits = 0
        last = cnt

        if cnt != prev_cnt and stable_hits >= 1:
            return cnt

        time.sleep(0.15)

    return last if last is not None else prev_cnt


def get_first_job_signature(driver) -> str:
    try:
        tr = driver.find_elements(By.CSS_SELECTOR, "tr.devloopArea")[0]
        a = tr.find_element(By.CSS_SELECTOR, "td.tplTit a")
        href = a.get_attribute("href") or ""
        title = clean_text(a.text)
        url = urljoin(BASE, href)
        job_id = extract_job_id(url) or ""
        return f"{job_id}|{href}|{title}"
    except Exception:
        return ""


def wait_first_job_changed(driver, old_first_sig: str, timeout=6):
    end = time.time() + timeout
    while time.time() < end:
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "tr.devloopArea")
            if rows:
                new_sig = get_first_job_signature(driver)
                if new_sig and new_sig != old_first_sig:
                    return True
        except Exception:
            pass
        time.sleep(0.08)
    return False


def set_sort_order(driver, value: str = None, timeout=10):
    if value is None:
        value = SORT_VALUE

    wait_list_loaded(driver)
    old_sig = get_first_job_signature(driver)

    sel_el = WebDriverWait(driver, 12).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select#orderTab"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", sel_el)
    time.sleep(0.03)

    sel = Select(sel_el)
    sel.select_by_value(value)

    try:
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            sel_el
        )
    except Exception:
        pass

    changed = wait_first_job_changed(driver, old_sig, timeout=timeout)
    if not changed:
        wait_list_loaded(driver)
        time.sleep(0.15)


def apply_major_industry_all_sub_and_search(driver, major_code: str):
    ok = safe_get(driver, LIST_URL, sleep_after=0.20, retry=1)
    if not ok:
        raise RuntimeError(f"failed to open list page: {LIST_URL}")

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.detailWrap"))
    )
    time.sleep(0.12)

    prev_cnt = 0
    try:
        prev_cnt = get_total_count(driver)
    except Exception:
        prev_cnt = 0

    check_all_industry_subcategories(driver, major_code=major_code)

    btn = WebDriverWait(driver, 12).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button#dev-btn-search.btn_sch"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    time.sleep(0.02)
    btn.click()

    wait_list_loaded(driver)
    new_cnt = wait_count_stabilized_after_search(
        driver,
        prev_cnt=prev_cnt,
        timeout=12,
    )

    try:
        set_sort_order(driver, value=SORT_VALUE, timeout=10)
        wait_list_loaded(driver)
    except Exception:
        pass

    cond_text = get_selected_conditions_text(driver)
    return new_cnt, cond_text


# =========================
# 3) 페이지네이션
# =========================
def get_current_page(driver) -> int:
    try:
        now = driver.find_element(By.CSS_SELECTOR, "div.tplPagination.newVer span.now")
        dp = now.get_attribute("data-page")
        if dp and dp.isdigit():
            return int(dp)
        t = clean_text(now.text)
        if t.isdigit():
            return int(t)
    except Exception:
        pass
    return -1


def click_page_number(driver, page: int) -> bool:
    try:
        old_sig = get_first_job_signature(driver)
        pager = driver.find_element(By.CSS_SELECTOR, "div.tplPagination.newVer")
        a = pager.find_element(By.CSS_SELECTOR, f'a[data-page="{page}"]')
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", a)
        time.sleep(0.05)
        a.click()
        ok = wait_first_job_changed(driver, old_sig, timeout=10)
        return ok
    except Exception:
        return False


def click_next_block(driver) -> bool:
    try:
        pager = driver.find_element(By.CSS_SELECTOR, "div.tplPagination.newVer")
    except Exception:
        return False

    for sel in ["a.tplBtn.btnPgnNext", "a.btnPgnNext"]:
        try:
            nxt = pager.find_element(By.CSS_SELECTOR, sel)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", nxt)
            time.sleep(0.05)
            old_sig = get_first_job_signature(driver)
            nxt.click()
            ok = wait_first_job_changed(driver, old_sig, timeout=10)
            return ok
        except Exception:
            continue
    return False


def ensure_filter_not_lost(driver, baseline_cnt: int, baseline_cond_text: str):
    cur_cond = get_selected_conditions_text(driver)
    if baseline_cond_text and baseline_cond_text not in cur_cond:
        raise RuntimeError("filter_lost: condition_text_changed")

    try:
        cur_cnt = get_total_count(driver)
        if baseline_cnt and cur_cnt and abs(cur_cnt - baseline_cnt) > 5:
            print(f"[WARN] total_count changed {baseline_cnt} -> {cur_cnt}", flush=True)
    except Exception:
        pass


def goto_page_by_datapage(
    driver,
    target_page: int,
    baseline_cnt: int,
    baseline_cond_text: str,
    safety_steps=800,
) -> bool:
    cur = get_current_page(driver)
    if cur == target_page:
        return True

    steps = 0
    while steps < safety_steps:
        steps += 1

        if click_page_number(driver, target_page):
            ensure_filter_not_lost(driver, baseline_cnt, baseline_cond_text)
            return True

        if not click_next_block(driver):
            return False

        ensure_filter_not_lost(driver, baseline_cnt, baseline_cond_text)

    return False


def collect_job_list_on_current_page(driver):
    job_list = []
    trs = driver.find_elements(By.CSS_SELECTOR, "tr.devloopArea")

    for tr in trs:
        try:
            a = tr.find_element(By.CSS_SELECTOR, "td.tplTit a")
            href = a.get_attribute("href")
            title_text = clean_text(a.text)

            company = ""
            try:
                company = clean_text(tr.find_element(By.CSS_SELECTOR, "td.tplCo a").text)
            except Exception:
                try:
                    company = clean_text(tr.find_element(By.CSS_SELECTOR, "td.tplCo span").text)
                except Exception:
                    company = ""

            if not company or not href:
                continue

            job_url = urljoin(BASE, href)
            job_id = extract_job_id(job_url)
            job_list.append((company, job_url, title_text, job_id))
        except Exception:
            continue

    return job_list


# =========================
# 4) 메타 저장
# =========================
def save_discover_state_files(
    state_dir,
    major_code: str,
    major_name: str,
    out_csv,
    out_txt,
    new_count: int,
    baseline_cnt: int,
    total_count: int,
    scanned_pages: int,
    baseline_cond_text: str,
):
    latest_file_path = state_dir / f"latest_discover_file_{major_code}.txt"
    latest_meta_path = state_dir / f"latest_discover_meta_{major_code}.json"

    safe_write_text(latest_file_path, str(out_csv))

    meta = {
        "major_code": major_code,
        "major_name": major_name,
        "links_csv": str(out_csv),
        "new_job_ids_txt": str(out_txt),
        "new_count": int(new_count),
        "baseline_cnt": int(baseline_cnt),
        "total_count": int(total_count),
        "scanned_pages": int(scanned_pages),
        "baseline_cond_text": clean_text(baseline_cond_text),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_json_atomic(latest_meta_path, meta)


# =========================
# 5) 메인 실행
# =========================
def run_discover(major_code: str, major_name: str):
    ensure_dirs(major_code, major_name)

    state_dir = get_state_dir(major_code, major_name)
    output_dir = get_output_dir(major_code, major_name)

    seen_path = state_dir / f"seen_job_ids_{major_code}.txt"
    seen_ids = load_seen_ids(seen_path)

    run_ts = time.strftime("%Y%m%d_%H%M%S")
    out_csv = output_dir / f"new_job_links_{major_code}_{run_ts}.csv"
    out_txt = output_dir / f"new_job_ids_{major_code}_{run_ts}.txt"

    print(f"[INFO] settings: max_pages={MAX_PAGES}, sort_value={SORT_VALUE}, zero_new_stop_streak={ZERO_NEW_STOP_STREAK}", flush=True)
    print(f"[INFO] seen ids loaded: {len(seen_ids)}", flush=True)

    driver = build_driver()

    try:
        try:
            baseline_cnt, baseline_cond_text = apply_major_industry_all_sub_and_search(
                driver,
                major_code=major_code,
            )
        except Exception:
            driver = restart_driver(driver)
            baseline_cnt, baseline_cond_text = apply_major_industry_all_sub_and_search(
                driver,
                major_code=major_code,
            )

        print(f"[DEBUG] baseline_cnt={baseline_cnt}", flush=True)
        print(f"[DEBUG] baseline_cond_text={baseline_cond_text[:200]}", flush=True)

        total = get_total_count(driver)
        max_page_est = max(1, math.ceil(total / 40))
        target_pages = min(MAX_PAGES, max_page_est)

        print(
            f"[INFO] total={total}, estimated_pages={max_page_est}, scanning_pages=1~{target_pages}",
            flush=True
        )

        all_new_rows = []
        scanned_pages = 0
        zero_new_streak = 0

        for page in range(1, target_pages + 1):
            scanned_pages = page

            cur = get_current_page(driver)
            if cur != -1 and cur != page:
                ok = goto_page_by_datapage(driver, page, baseline_cnt, baseline_cond_text)
                if not ok:
                    print(f"[WARN] page {page} 이동 실패", flush=True)
                    break

            ensure_filter_not_lost(driver, baseline_cnt, baseline_cond_text)

            page_jobs = collect_job_list_on_current_page(driver)
            page_new_count = 0
            page_seen_count = 0

            for company, url, title, job_id in page_jobs:
                if not job_id:
                    continue

                if job_id in seen_ids:
                    page_seen_count += 1
                    continue

                all_new_rows.append({
                    "page": page,
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "url": url,
                })
                page_new_count += 1

            if page_new_count == 0:
                zero_new_streak += 1
            else:
                zero_new_streak = 0

            print(
                f"[INFO] page={page}, page_jobs={len(page_jobs)}, new_jobs={page_new_count}, seen_jobs={page_seen_count}, zero_new_streak={zero_new_streak}",
                flush=True
            )

            if zero_new_streak >= ZERO_NEW_STOP_STREAK:
                print(
                    f"[INFO] zero-new streak reached {ZERO_NEW_STOP_STREAK} pages -> stop early at page={page}",
                    flush=True
                )
                break

            time.sleep(0.05)

        all_new_rows = dedup_rows(all_new_rows)

        print(f"[INFO] total new jobs found: {len(all_new_rows)}", flush=True)

        with open(out_txt, "w", encoding="utf-8") as f:
            for row in all_new_rows:
                f.write(f"{row['job_id']}\n")

        with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["page", "job_id", "title", "company", "url"]
            )
            writer.writeheader()
            writer.writerows(all_new_rows)

        save_discover_state_files(
            state_dir=state_dir,
            major_code=major_code,
            major_name=major_name,
            out_csv=out_csv,
            out_txt=out_txt,
            new_count=len(all_new_rows),
            baseline_cnt=baseline_cnt,
            total_count=total,
            scanned_pages=scanned_pages,
            baseline_cond_text=baseline_cond_text,
        )

        print(f"[DONE] saved ids: {out_txt}", flush=True)
        print(f"[DONE] saved links: {out_csv}", flush=True)
        print(f"[DONE] saved latest discover pointer/meta in state", flush=True)

        return {
            "major_code": major_code,
            "major_name": major_name,
            "new_count": len(all_new_rows),
            "out_csv": str(out_csv),
            "out_txt": str(out_txt),
            "scanned_pages": int(scanned_pages),
            "total_count": int(total),
            "baseline_cnt": int(baseline_cnt),
        }

    finally:
        driver = safe_quit_driver(driver)