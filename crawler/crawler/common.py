import json
import re
from pathlib import Path

import math
import undetected_chromedriver as uc


ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT_DIR / "config"
SETTINGS_PATH = CONFIG_DIR / "settings.json"


def load_settings() -> dict:
    """
    config/settings.json 로드.
    파일이 없거나 파싱 실패하면 빈 dict 반환.
    """
    if not SETTINGS_PATH.exists():
        return {}

    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_json_atomic(path: Path, data: dict):
    """
    JSON을 원자적으로 저장.
    - 먼저 임시 파일에 저장
    - 저장 성공 후 기존 파일 교체
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    tmp_path.replace(path)

def clean_text(s) -> str:
    if s is None:
        return ""
    if isinstance(s, float) and math.isnan(s):
        return ""
    return " ".join(str(s).split()).strip()


def extract_job_id(url: str):
    if not url:
        return None
    m = re.search(r"/Recruit/GI_Read/(\d+)", str(url), flags=re.IGNORECASE)
    return m.group(1) if m else None


def build_driver():
    settings = load_settings()

    chrome_version_main = settings.get("chrome_version_main", 144)
    headless = settings.get("headless", True)
    page_load_timeout = settings.get("page_load_timeout", 20)
    use_subprocess = settings.get("use_subprocess", True)

    options = uc.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-renderer-backgrounding")

    driver = uc.Chrome(
        options=options,
        version_main=chrome_version_main,
        use_subprocess=use_subprocess,
    )

    try:
        driver.set_page_load_timeout(page_load_timeout)
    except Exception:
        pass

    return driver


def safe_quit_driver(driver):
    if driver is None:
        return None

    try:
        driver.quit()
    except OSError:
        pass
    except Exception:
        pass

    try:
        driver.quit = lambda *args, **kwargs: None
    except Exception:
        pass

    return None


def restart_driver(old_driver=None):
    safe_quit_driver(old_driver)
    return build_driver()