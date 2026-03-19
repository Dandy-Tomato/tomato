from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"


def get_industry_dir(major_code, major_name):
    folder_mapping = {
        "10007_IT정보통신업": "10007_it_ict"
    }
    raw_name = f"{major_code}_{major_name}"
    folder_name = folder_mapping.get(raw_name, raw_name)
    return DATA_DIR / folder_name


def get_raw_dir(major_code, major_name):

    return get_industry_dir(major_code, major_name) / "raw"


def get_state_dir(major_code, major_name):

    return get_industry_dir(major_code, major_name) / "state"


def get_output_dir(major_code, major_name):

    return get_industry_dir(major_code, major_name) / "incremental_output"


def get_processed_dir(major_code, major_name):

    return get_industry_dir(major_code, major_name) / "processed"


def ensure_dirs(major_code, major_name):

    dirs = [
        get_raw_dir(major_code, major_name),
        get_state_dir(major_code, major_name),
        get_output_dir(major_code, major_name),
        get_processed_dir(major_code, major_name),
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)