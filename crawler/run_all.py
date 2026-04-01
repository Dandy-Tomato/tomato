import json
import os
import time
import traceback
from pathlib import Path

from crawler.discover_new_jobs import run_discover
from crawler.collect_new_job_details import run_collect
from crawler.preprocess_incremental_jobs import run_incremental_preprocess
from crawler.paths import ensure_dirs, get_state_dir


TARGET_MAJOR_CODE = "10007"
TARGET_MAJOR_NAME = "IT정보통신업"

ROOT_DIR = Path(__file__).resolve().parent
LOCK_PATH = ROOT_DIR / "run_all.lock"

LOCK_STALE_SECONDS = 60 * 60 * 6  # 6시간


def save_jsonl_line(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def load_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def save_text_lines_atomic(path: Path, values: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        for value in values:
            value = str(value).strip()
            if value:
                f.write(f"{value}\n")

    tmp_path.replace(path)


def merge_seen_ids_atomic(path: Path, job_ids: list[str]) -> int:
    """
    seen_job_ids를 append하지 않고
    기존 내용 + 신규 job_ids를 합쳐 dedupe 후 atomic replace 한다.
    """
    if not job_ids:
        return 0

    existing = load_lines(path)
    existing_set = set(existing)

    added = []
    for job_id in job_ids:
        job_id = str(job_id).strip()
        if not job_id or job_id in existing_set:
            continue
        existing_set.add(job_id)
        added.append(job_id)

    if not added:
        return 0

    merged = existing + added
    save_text_lines_atomic(path, merged)
    return len(added)


def _read_lock_info(lock_path: Path) -> dict:
    try:
        return json.loads(lock_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_lock_info_atomic(lock_path: Path, lock_info: dict):
    tmp_path = lock_path.with_suffix(lock_path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(lock_info, f, ensure_ascii=False, indent=2)
    tmp_path.replace(lock_path)


def acquire_lock(lock_path: Path):
    """
    원자적으로 lock 생성.
    stale lock이면 제거 후 재시도.
    """
    now_ts = int(time.time())
    lock_info = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "created_ts": now_ts,
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_ts": now_ts,
        "pid": os.getpid(),
    }

    payload = json.dumps(lock_info, ensure_ascii=False, indent=2)

    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(payload)
            return
        except FileExistsError:
            info = _read_lock_info(lock_path)
            updated_ts = int(info.get("updated_ts", 0) or 0)
            created_ts = int(info.get("created_ts", 0) or 0)
            now_ts = int(time.time())

            base_ts = updated_ts if updated_ts > 0 else created_ts
            is_stale = False
            if base_ts > 0 and (now_ts - base_ts) > LOCK_STALE_SECONDS:
                is_stale = True

            if is_stale:
                print(f"[WARN] stale lock detected -> removing: {lock_path}", flush=True)
                try:
                    lock_path.unlink()
                    continue
                except Exception as e:
                    raise RuntimeError(
                        f"stale lock exists but failed to remove: {lock_path} | error={e}"
                    ) from e

            raise RuntimeError(
                f"another batch is already running. lock exists: {lock_path} | info={json.dumps(info, ensure_ascii=False)}"
            )


def touch_lock(lock_path: Path, extra: dict | None = None):
    """
    lock heartbeat 갱신.
    """
    if not lock_path.exists():
        return

    info = _read_lock_info(lock_path)
    info["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    info["updated_ts"] = int(time.time())

    if extra:
        for k, v in extra.items():
            info[k] = v

    _write_lock_info_atomic(lock_path, info)


def release_lock(lock_path: Path):
    if lock_path.exists():
        lock_path.unlink()


def log_step_done(step_name: str, extra: dict | None = None):
    msg = f"[STEP-DONE] {step_name}"
    if extra:
        msg += f" | {json.dumps(extra, ensure_ascii=False)}"
    print(msg, flush=True)

    heartbeat_extra = {"last_step": step_name}
    if extra:
        heartbeat_extra.update(extra)
    touch_lock(LOCK_PATH, heartbeat_extra)


def run_industry(major_code, major_name):
    print("\n" + "=" * 70, flush=True)
    print(f"[RUN_ALL] start industry {major_code} / {major_name}", flush=True)
    print("=" * 70, flush=True)

    try:
        ensure_dirs(major_code, major_name)
        touch_lock(
            LOCK_PATH,
            {"phase": "start_industry", "major_code": major_code, "major_name": major_name},
        )

        print("[STEP] discover", flush=True)
        discover_result = run_discover(
            major_code=major_code,
            major_name=major_name,
        )
        log_step_done(
            "discover",
            {
                "discover_new_count": int(discover_result.get("new_count", 0) or 0),
                "discover_csv": discover_result.get("out_csv"),
            },
        )

        discover_new_count = int(discover_result.get("new_count", 0) or 0)
        discover_links_csv = discover_result.get("out_csv")

        if discover_new_count > 0 and discover_links_csv:
            print("[STEP] collect", flush=True)
            collect_result = run_collect(
                major_code=major_code,
                major_name=major_name,
                input_csv_path=discover_links_csv,
            )
            log_step_done(
                "collect",
                {
                    "detail_count": int(collect_result.get("detail_count", 0) or 0),
                    "success_count": int(collect_result.get("success_count", 0) or 0),
                    "fail_count": int(collect_result.get("fail_count", 0) or 0),
                    "details_csv": collect_result.get("out_csv"),
                },
            )
        else:
            print("[STEP] collect skipped (no new links)", flush=True)
            collect_result = {
                "major_code": major_code,
                "major_name": major_name,
                "skipped": True,
                "reason": "no_new_links",
                "input_csv": discover_links_csv,
                "out_csv": None,
                "detail_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "success_job_ids_path": None,
                "failed_job_ids_path": None,
            }
            log_step_done("collect_skipped", {"reason": "no_new_links"})

        collect_success_count = int(collect_result.get("success_count", 0) or 0)
        details_csv = collect_result.get("out_csv")

        if collect_success_count > 0 and details_csv:
            print("[STEP] incremental preprocess", flush=True)
            preprocess_result = run_incremental_preprocess(
                major_code=major_code,
                major_name=major_name,
                details_csv_path=details_csv,
            )
            log_step_done(
                "incremental_preprocess",
                {
                    "added_pairs": int(preprocess_result.get("added_pairs", 0) or 0),
                    "added_skills": int(preprocess_result.get("added_skills", 0) or 0),
                    "added_companies": int(preprocess_result.get("added_companies", 0) or 0),
                    "added_company_skills": int(preprocess_result.get("added_company_skills", 0) or 0),
                },
            )
        else:
            print("[STEP] incremental preprocess skipped (no successful details)", flush=True)
            preprocess_result = {
                "major_code": major_code,
                "major_name": major_name,
                "skipped": True,
                "reason": "no_successful_details",
                "details_csv": None,
                "added_pairs": 0,
                "added_skills": 0,
                "added_companies": 0,
                "added_company_skills": 0,
                "total_skills": 0,
                "total_pairs": 0,
                "total_companies": 0,
                "total_company_skills": 0,
            }
            log_step_done("incremental_preprocess_skipped", {"reason": "no_successful_details"})

        # preprocess 성공 후에만 seen 반영
        seen_append_count = 0
        success_job_ids_path = collect_result.get("success_job_ids_path")
        preprocess_ok = preprocess_result.get("skipped") is not True

        if collect_success_count > 0 and details_csv and success_job_ids_path and preprocess_ok:
            success_job_ids_file = Path(success_job_ids_path)
            if success_job_ids_file.exists():
                success_job_ids = load_lines(success_job_ids_file)

                state_dir = get_state_dir(major_code, major_name)
                seen_path = state_dir / f"seen_job_ids_{major_code}.txt"

                seen_append_count = merge_seen_ids_atomic(seen_path, success_job_ids)
                print(
                    f"[DONE] appended seen ids after preprocess success: {seen_append_count} -> {seen_path}",
                    flush=True,
                )
                touch_lock(
                    LOCK_PATH,
                    {
                        "phase": "seen_append_done",
                        "seen_append_count": seen_append_count,
                    },
                )

        print(f"[DONE] industry finished: {major_code} / {major_name}", flush=True)

        return {
            "major_code": major_code,
            "major_name": major_name,
            "discover": discover_result,
            "collect": collect_result,
            "preprocess": preprocess_result,
            "seen_append_count": seen_append_count,
            "status": "success",
        }

    except Exception as e:
        print(f"[ERROR] industry failed: {major_code} / {major_name}", flush=True)
        print(f"[ERROR] {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()

        touch_lock(
            LOCK_PATH,
            {
                "phase": "industry_failed",
                "error_type": type(e).__name__,
                "error": str(e),
            },
        )

        return {
            "major_code": major_code,
            "major_name": major_name,
            "error": str(e),
            "status": "failed",
        }


def main():
    print("=" * 70, flush=True)
    print("[RUN_ALL] start", flush=True)
    print("=" * 70, flush=True)

    start_time = time.time()
    run_started_at = time.strftime("%Y-%m-%d %H:%M:%S")
    lock_acquired = False

    try:
        acquire_lock(LOCK_PATH)
        lock_acquired = True
        touch_lock(LOCK_PATH, {"phase": "lock_acquired"})

        result = run_industry(
            major_code=TARGET_MAJOR_CODE,
            major_name=TARGET_MAJOR_NAME,
        )

    except Exception as e:
        result = {
            "major_code": TARGET_MAJOR_CODE,
            "major_name": TARGET_MAJOR_NAME,
            "status": "failed",
            "error": str(e),
        }
        print(f"[ERROR] RUN_ALL failed before/during execution: {type(e).__name__}: {e}", flush=True)

    finally:
        if lock_acquired:
            release_lock(LOCK_PATH)

    elapsed = round(time.time() - start_time, 2)

    print("\n" + "=" * 70, flush=True)
    print("[RUN_ALL] finished", flush=True)
    print(f"elapsed: {elapsed} sec", flush=True)
    print("=" * 70, flush=True)

    state_dir = get_state_dir(TARGET_MAJOR_CODE, TARGET_MAJOR_NAME)
    batch_log_path = state_dir / f"batch_run_log_{TARGET_MAJOR_CODE}.jsonl"

    if result.get("status") == "success":
        print("[SUMMARY] success=1, failed=0", flush=True)

        discover_result = result.get("discover", {}) or {}
        collect_result = result.get("collect", {}) or {}
        preprocess_result = result.get("preprocess", {}) or {}

        discover_new = int(discover_result.get("new_count", 0) or 0)
        collect_detail_count = int(collect_result.get("detail_count", 0) or 0)
        collect_success_count = int(collect_result.get("success_count", 0) or 0)
        collect_fail_count = int(collect_result.get("fail_count", 0) or 0)

        added_pairs = int(preprocess_result.get("added_pairs", 0) or 0)
        added_skills = int(preprocess_result.get("added_skills", 0) or 0)
        added_companies = int(preprocess_result.get("added_companies", 0) or 0)
        added_company_skills = int(preprocess_result.get("added_company_skills", 0) or 0)
        seen_append_count = int(result.get("seen_append_count", 0) or 0)

        print(f"[SUMMARY] discover_new={discover_new}", flush=True)
        print(f"[SUMMARY] collect_detail_count={collect_detail_count}", flush=True)
        print(f"[SUMMARY] collect_success_count={collect_success_count}", flush=True)
        print(f"[SUMMARY] collect_fail_count={collect_fail_count}", flush=True)
        print(f"[SUMMARY] added_pairs={added_pairs}", flush=True)
        print(f"[SUMMARY] added_skills={added_skills}", flush=True)
        print(f"[SUMMARY] added_companies={added_companies}", flush=True)
        print(f"[SUMMARY] added_company_skills={added_company_skills}", flush=True)
        print(f"[SUMMARY] seen_appended={seen_append_count}", flush=True)

        save_jsonl_line(
            batch_log_path,
            {
                "run_started_at": run_started_at,
                "run_finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "elapsed_sec": elapsed,
                "major_code": TARGET_MAJOR_CODE,
                "major_name": TARGET_MAJOR_NAME,
                "status": "success",
                "discover_new": discover_new,
                "collect_detail_count": collect_detail_count,
                "collect_success_count": collect_success_count,
                "collect_fail_count": collect_fail_count,
                "added_pairs": added_pairs,
                "added_skills": added_skills,
                "added_companies": added_companies,
                "added_company_skills": added_company_skills,
                "seen_append_count": seen_append_count,
                "details_csv": collect_result.get("out_csv"),
                "discover_csv": discover_result.get("out_csv"),
                "success_job_ids_path": collect_result.get("success_job_ids_path"),
                "failed_job_ids_path": collect_result.get("failed_job_ids_path"),
            },
        )

    else:
        print("[SUMMARY] success=0, failed=1", flush=True)

        save_jsonl_line(
            batch_log_path,
            {
                "run_started_at": run_started_at,
                "run_finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "elapsed_sec": elapsed,
                "major_code": TARGET_MAJOR_CODE,
                "major_name": TARGET_MAJOR_NAME,
                "status": "failed",
                "error": result.get("error", ""),
            },
        )


if __name__ == "__main__":
    main()