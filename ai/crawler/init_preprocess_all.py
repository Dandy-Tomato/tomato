import json
import math
import re
import time
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
DB_READY_DIR = ROOT_DIR / "db_ready"
INDUSTRIES_PATH = CONFIG_DIR / "industries.json"

BASE_MASTER_CODE = "10007"


# =========================
# 0) 보충 리스트
# =========================
SUPPLEMENT_SKILL_NAMES = [
    "React",
    "Next.js",
    "Vue.js",
    "Nuxt.js",
    "Angular",
    "Svelte",
    "TypeScript",
    "JavaScript",
    "Tailwind CSS",
    "React Native",
    "Flutter",
    "Swift",
    "Kotlin",
    "Node.js",
    "Spring Boot",
    "Django",
    "FastAPI",
    "Flask",
    "NestJS",
    "Express",
    "Java",
    "Python",
    "Go",
    "Rust",
    "C#",
    "PHP",
    "Ruby on Rails",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Redis",
    "Elasticsearch",
    "Firebase",
    "Supabase",
    "GraphQL",
    "REST API",
    "gRPC",
    "Docker",
    "Kubernetes",
    "AWS",
    "GCP",
    "Azure",
    "GitHub Actions",
    "Jenkins",
    "Terraform",
    "Nginx",
    "Kafka",
    "RabbitMQ",
    "WebSocket",
    "OAuth2",
    "JWT",
    "TensorFlow",
    "PyTorch",
    "LangChain",
    "OpenAI API",
    "Pandas",
    "Spark",
    "Airflow",
    "Prometheus",
    "Grafana",
    "C/C++",
    "RTOS",
    "Arduino",
    "Raspberry Pi",
    "MQTT",
]


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


def save_csv(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        try:
            path.unlink()
        except PermissionError:
            raise PermissionError(
                f"파일이 열려 있어서 저장할 수 없습니다: {path}\n"
                f"엑셀/메모장/VSCode/탐색기 미리보기에서 해당 파일을 닫고 다시 실행하세요."
            )

    df.to_csv(path, index=False, encoding="utf-8-sig")


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


def find_raw_csv_for_industry(major_code: str, major_name: str) -> Path | None:
    base_dir = get_industry_dir(major_code, major_name)
    raw_dir = base_dir / "raw"

    if not raw_dir.exists():
        return None

    candidates = sorted(raw_dir.glob(f"jobkorea_{major_code}_*_all_pages.csv"))
    if not candidates:
        return None

    return candidates[0]


# =========================
# 1-1) skills.csv용 db_name 생성
# =========================
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
    }

    if low in special_map:
        return special_map[low]

    t = t.replace("&", "and")
    t = re.sub(r"[./+\-\s]+", "_", t.lower())
    t = re.sub(r"[^a-z0-9_]", "", t)
    t = re.sub(r"_+", "_", t).strip("_")
    return t


# =========================
# 2) 스킬 추출용 전처리
# =========================
def preprocess_raw_skill_text(s) -> str:
    t = clean_text(s)
    if not t:
        return ""

    t = re.sub(
        r'(^|[,|;\n\r•·ㆍ，｜/]\s*)[\'"’‘+\-*•·ㆍ_@]+',
        r"\1",
        t
    )
    t = re.sub(r'^[\'"’‘+\-*•·ㆍ_@]+', "", t)

    t = re.sub(
        r'(^|[,|;\n\r•·ㆍ，｜/]\s*)\.(?!NET\b|Net\b)[A-Za-z0-9]+(?=\s*([,|;\n\r•·ㆍ，｜/]|$))',
        r"\1",
        t
    )

    t = re.sub(
        r'(^|[,|;\n\r•·ㆍ，｜/]\s*)[\[\]\(\)\{\}]+(?=\s*([,|;\n\r•·ㆍ，｜/]|$))',
        r"\1",
        t
    )

    t = re.sub(r"\s*[,|;\n\r•·ㆍ，｜/]\s*", ", ", t)
    t = re.sub(r"(,\s*){2,}", ", ", t)
    t = t.strip(" ,")

    return clean_text(t)


def split_outside_parentheses(text: str, delimiters=None) -> list[str]:
    if delimiters is None:
        delimiters = {",", "|", ";", "\n", "\r", "•", "·", "ㆍ", "，", "｜", "/"}

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


def split_with_inner_parentheses_expansion(text: str) -> list[str]:
    base_tokens = split_outside_parentheses(text)
    out = []

    for token in base_tokens:
        token = clean_text(token)
        if not token:
            continue

        out.append(token)

        inner_groups = re.findall(r"\((.*?)\)", token)
        for inner in inner_groups:
            inner = clean_text(inner)
            if not inner:
                continue

            inner_parts = split_outside_parentheses(inner)
            for p in inner_parts:
                p = clean_text(p)
                if p:
                    out.append(p)

    return out


# =========================
# 3) 제거/정규화 규칙
# =========================
BAD_EXACT = {
    "우대조건", "스킬", "핵심역량",
    "무관", "없음", "해당없음", "지원", "채용", "공고",
    "우대", "가능자", "관련자", "관련",
    "상세요강 참고", "상세내용 참고", "내용 참고",
    "세부내용 확인", "세부 내용 확인",
    "필수", "우대사항", "자격요건", "지원자격",
    "인근거주자", "운전가능자", "장기근무 가능자", "야간근무 가능자",
    "차량소지자", "즉시출근 가능자", "출장 가능자", "지방근무 가능자",
    "해외근무 가능자", "교대근무 가능자", "2교대 근무 가능자", "3교대 근무 가능자",
    "기숙사 생활가능자", "문서작성 우수자",
    "유관업무 경험자", "유관업무경험자", "유관업무 경력자", "유관업무경력자",
    "보호대상", "국가유공자", "보훈대상자", "장애인", "취업보호대상자",
    "고용촉진지원금 대상자", "병역특례", "중장년층",
    "[]", "()", "{}", "[ ]", "( )", "{ }",
    "com", "등", "기타", "우대사항 참조",
    "cloud 환경 유경험자", "클라우드 환경 유경험자",
    "인문", "수학", "영어", "국어", "일본어", "중국어", "외국어",
    "인턴", "알바", "아르바이트", "신입", "경력", "경력직", "주니어", "시니어",
    "사무", "행정", "문서작성", "커뮤니케이션", "커뮤니케이션 능력",
    "비즈니스 영어", "비즈니스영어", "무역영어",
    "ccna", "CCNA",
    "전자정부표준프레임워크",
    "cloud", "Cloud",
    "ui", "UI", "ux", "UX", "ai", "AI",
    "풀스택", "ChatGPT", "Spreadsheets",
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
    "기숙사 생활가능",
    "문서작성 우수",
    "유관업무 경험",
    "유관업무 경력",
    "국가유공",
    "보훈대상",
    "취업보호대상",
    "고용촉진지원금 대상",
    "병역특례",
    "관련 자격",
    "관련 자격증",
    "관련 학과",
    "관련 학부",
    "관련 전공",
    "비흡연",
    "금연",
    "운전면허",
    "영어 구사",
    "영어 가능",
    "영어 능력",
    "영어 커뮤니케이션",
    "비즈니스 레벨의 영어",
    "외국어 가능",
    "의사소통 가능",
    "관심이 있",
    "교육 받은 경험",
    "교육받은 경험",
    "실무 가능",
    "가능하신 분",
    "능통한 자",
    "번역",
    "식자 편집",
    "인턴 경험",
    "알바 경험",
    "전자정부표준프레임워크",
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
    r"^\[\]$",
    r"^\(\)$",
    r"^\{\}$",
    r"^\.[A-Za-z0-9]+$",
    r"^\(필수\).*$",
    r"^\(우대\).*$",
    r"^\[필수\].*$",
    r"^\[우대\].*$",
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
    r".*생활가능자$",
    r"^@[A-Za-z0-9_.]+$",
    r"^etc$",
    r"^others?$",
    r"^and more$",
    r"^등$",
    r"^.*영어.*$",
    r"^.*일본어.*$",
    r"^.*중국어.*$",
    r"^.*외국어.*$",
    r"^.*인턴.*$",
    r"^.*알바.*$",
    r"^.*아르바이트.*$",
    r"^.*관심이 있.*$",
    r"^.*교육 받은 경험.*$",
    r"^.*교육받은 경험.*$",
    r"^.*가능하신 분.*$",
    r"^.*의사소통 가능.*$",
    r"^.*구사 능력.*$",
    r"^.*능통한 자.*$",
    r"^.*커뮤니케이션.*$",
    r"^ccna$",
    r"^전자정부표준프레임워크$",
]

EXCLUDE_SKILLS_EXACT = {
    "비흡연자",
    "흡연",
    "금연",
    "운전면허",
    "1종보통",
    "1종대형",
    "2종보통",
    "대형면허",
    "일러스트",
    "일러스터",
    "Illustrator",
    "Photoshop",
    "Blender",
    "Maya",
    "3ds Max",
    "Cinema 4D",
    "ZBrush",
    "SketchUp",
    "InDesign",
    "Premiere Pro",
    "After Effects",
    "Lightroom",
    "AutoCAD",
    "CAD",
    "Rhino",
    "Figma",
    "XD",
    "Adobe XD",
    "Sketch",
    "Notion",
    "Slack",
    "Jira",
    "Confluence",
    "ERP",
    "SAP",
    "더존 프로그램",
    "사방넷",
    "EzAdmin",
    "i-cube",
    "ChatGPT",
    "Cloud",
    "UI",
    "UX",
    "AI",
    "풀스택",
    "Spreadsheets",
    "CCNA",
    "전자정부표준프레임워크",
    "Excel",
    "PowerPoint",
    "Word",
    "워드",
    "한컴",
    "Microsoft Office",
    "OA",
    "컴퓨터활용능력",
}

EXCLUDE_SKILLS_LOWER = {
    "비흡연자",
    "흡연",
    "금연",
    "운전면허",
    "1종보통",
    "1종대형",
    "2종보통",
    "대형면허",
    "illustrator",
    "photoshop",
    "blender",
    "maya",
    "3ds max",
    "cinema 4d",
    "zbrush",
    "sketchup",
    "indesign",
    "premiere pro",
    "after effects",
    "lightroom",
    "autocad",
    "cad",
    "rhino",
    "figma",
    "xd",
    "adobe xd",
    "sketch",
    "notion",
    "slack",
    "jira",
    "confluence",
    "erp",
    "sap",
    "더존 프로그램",
    "사방넷",
    "ezadmin",
    "i-cube",
    "chatgpt",
    "cloud",
    "ui",
    "ux",
    "ai",
    "풀스택",
    "spreadsheets",
    "ccna",
    "전자정부표준프레임워크",
    "excel",
    "powerpoint",
    "word",
    "워드",
    "한컴",
    "microsoft office",
    "oa",
    "컴퓨터활용능력",
}

EXCLUDE_CONTAINS = [
    "일러스트", "일러스터", "포토샵", "블렌더", "마야", "렌더링", "모델링",
    "영상편집", "이미지편집", "편집툴", "콘텐츠제작편집",
    "도면", "캐드", "cad", "설계도", "3d프린터", "3d printer",
]

EXCLUDE_PATTERNS = [
    r"^2d.*$",
    r"^3d.*$",
    r"^3d\s.*$",
    r"^3dmax.*$",
    r"^3ds\s*max.*$",
    r"^3d\s*modeling.*$",
    r"^3d\s*rendering.*$",
    r"^3d설계.*$",
    r"^2d설계.*$",
    r"^2d도면.*$",
    r"^회로도면.*$",
    r"^기술도면.*$",
    r"^전극설계.*$",
    r"^전장설계.*$",
    r"^방산설계.*$",
    r"^사출금형설계.*$",
    r"^부품 설계.*$",
    r"^부품설계.*$",
    r"^도면.*$",
    r"^설계$",
    r"^영상편집.*$",
    r"^이미지편집.*$",
    r"^편집$",
    r"^스마트에디터.*$",
    r"^유투브콘텐츠제작편집.*$",
    r"^gstarcad$",
    r"^orcad$",
    r"^autocad$",
    r"^cad$",
    r"^e3d$",
    r"^s3d$",
]

MASTER_EXCLUDE_PATTERNS = [
    r".*비흡연.*",
    r".*운전면허.*",
    r".*면허.*",
    r".*디자인.*",
    r".*포토샵.*",
    r".*일러스트.*",
    r".*블렌더.*",
    r".*마야.*",
    r"^ccna$",
    r"^전자정부표준프레임워크$",
]


CANONICAL_SKILL_MAP = {
    "aws": "AWS",
    "amazon web services": "AWS",
    "aws cloud": "AWS",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "vmware": "VMware",

    "spring": "Spring",
    "스프링": "Spring",
    "spring framework": "Spring",
    "spring 프레임워크": "Spring",
    "spring framework 기반": "Spring",
    "spring-boot": "Spring Boot",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    "스프링부트": "Spring Boot",
    "spring batch": "Spring Batch",
    "spring security": "Spring Security",
    "spring mvc": "Spring MVC",
    "spring cloud": "Spring Cloud",
    "spring data jpa": "Spring Data JPA",

    "python": "Python",
    "파이썬": "Python",
    "java": "Java",
    "자바": "Java",
    "javascript": "JavaScript",
    "java script": "JavaScript",
    "js": "JavaScript",
    "자바스크립트": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "타입스크립트": "TypeScript",
    "html": "HTML",
    "css": "CSS",
    "sql": "SQL",
    "r": "R",
    "php": "PHP",
    "c": "C",
    "c++": "C/C++",
    "c#": "C#",
    ".net": ".NET",
    "dotnet": ".NET",
    "asp.net": "ASP.NET",

    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "리액트": "React",
    "react native": "React Native",
    "react-native": "React Native",
    "리액트 네이티브": "React Native",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "뷰": "Vue.js",
    "angular": "Angular",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "nest.js": "NestJS",
    "nestjs": "NestJS",
    "android": "Android",
    "ios": "iOS",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "flutter": "Flutter",
    "android studio": "Android Studio",

    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "laravel": "Laravel",
    "express": "Express",
    "jsp": "JSP",
    "jquery": "jQuery",
    "jquery.js": "jQuery",
    "ajax": "Ajax",
    "jpa": "JPA",
    "mybatis": "MyBatis",
    "was": "WAS",
    "websquare": "WebSquare",
    "nexacro": "Nexacro",

    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "oracle": "Oracle",
    "오라클": "Oracle",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "mariadb": "MariaDB",
    "mssql": "MSSQL",
    "rdbms": "RDBMS",
    "dbms": "DBMS",
    "nosql": "NoSQL",
    "tibero": "Tibero",

    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "linux": "Linux",
    "unix": "Unix",
    "git": "Git",
    "github": "GitHub",
    "git hub": "GitHub",
    "gitlab": "GitLab",
    "jenkins": "Jenkins",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "rest api": "REST API",
    "restful api": "REST API",
    "api": "API",
    "kafka": "Kafka",
    "msa": "MSA",
    "saas": "SaaS",

    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "opencv": "OpenCV",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "spss": "SPSS",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "llm": "LLM",
    "rag": "RAG",

    "google analytics": "Google Analytics",
    "google optimize": "Google Optimize",

    "mqtt": "MQTT",
    "raspberry pi": "Raspberry Pi",
    "raspberrypi": "Raspberry Pi",
    "라즈베리파이": "Raspberry Pi",
    "arduino": "Arduino",
    "아두이노": "Arduino",
    "embedded": "Embedded",
    "embedded linux": "Embedded Linux",
    "임베디드": "Embedded",
    "임베디드 리눅스": "Embedded Linux",
    "rtos": "RTOS",
    "freertos": "FreeRTOS",
    "zephyr": "Zephyr",
    "ros": "ROS",
    "ros2": "ROS2",
    "ros 2": "ROS2",
    "can": "CAN",
    "can bus": "CAN",
    "modbus": "Modbus",
    "uart": "UART",
    "spi": "SPI",
    "i2c": "I2C",
    "ble": "BLE",
    "bluetooth low energy": "BLE",
    "zigbee": "Zigbee",
    "lorawan": "LoRaWAN",
    "lora": "LoRa",
    "edge ai": "Edge AI",
    "onnx": "ONNX",
}

TECH_KEYWORDS = {
    "aws", "azure", "gcp", "vmware",
    "python", "java", "javascript", "typescript", "sql", "r", "php", "c", "c++", "c#", ".net", "asp.net", "html", "css",
    "react", "react native", "vue", "angular", "node", "next.js", "nestjs", "android", "ios", "swift", "kotlin", "flutter", "android studio",
    "spring", "spring boot", "spring batch", "spring security", "spring mvc", "spring cloud", "spring data jpa",
    "django", "flask", "fastapi", "express", "laravel", "jsp", "jquery", "ajax", "jpa", "mybatis", "was", "websquare", "nexacro",
    "mysql", "postgresql", "postgres", "oracle", "mongodb", "redis", "mariadb", "mssql", "rdbms", "dbms", "nosql", "tibero",
    "docker", "kubernetes", "jenkins", "terraform", "ansible", "linux", "unix", "git", "github", "gitlab",
    "rest api", "api", "kafka", "msa", "saas",
    "pytorch", "tensorflow", "opencv", "pandas", "numpy", "scikit-learn", "sklearn", "tableau", "power bi", "spss", "llm", "rag",
    "google analytics", "google optimize",
    "mqtt", "raspberry pi", "arduino", "embedded", "embedded linux", "rtos", "freertos", "zephyr",
    "ros", "ros2", "can", "can bus", "modbus", "uart", "spi", "i2c", "ble", "zigbee", "lorawan", "lora", "edge ai", "onnx",
}


def normalize_token(token: str) -> str:
    t = clean_text(token)
    if not t:
        return ""

    t = re.sub(r"^[\'\"’‘\+\-\*•·ㆍ_]+", "", t)
    t = t.strip(" ,|/;:")
    t = clean_text(t)

    if not t:
        return ""

    t = re.sub(r"\s*\(\s*", "(", t)
    t = re.sub(r"\s*\)\s*", ")", t)
    t = re.sub(r"\s*/\s*", "/", t)
    t = re.sub(r"\s*\+\s*", "+", t)
    t = re.sub(r"\s+", " ", t)
    t = t.rstrip(",")

    t = re.sub(r"\s*등$", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*외$", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*etc\.?$", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*and more$", "", t, flags=re.IGNORECASE)

    t = t.strip("()[]{} ").strip()

    return clean_text(t)


def strip_non_skill_phrase(t: str) -> str:
    if not t:
        return ""

    patterns = [
        r"(.+?)\s+이해$",
        r"(.+?)\s+가능자$",
        r"(.+?)\s+경험자$",
        r"(.+?)\s+경력자$",
        r"(.+?)\s+우대$",
        r"(.+?)\s+기반 프레임워크 개발$",
        r"(.+?)\s+프레임워크$",
        r"WEB 어플리케이션\((.+?)$",
    ]

    for p in patterns:
        m = re.match(p, t, flags=re.IGNORECASE)
        if m:
            core = clean_text(m.group(1))
            if core:
                return core

    return t


def canonicalize_skill(token: str) -> str:
    t = normalize_token(token)
    if not t:
        return ""

    t = strip_non_skill_phrase(t)
    t = normalize_token(t)
    if not t:
        return ""

    low = t.lower()

    if low in CANONICAL_SKILL_MAP:
        return CANONICAL_SKILL_MAP[low]

    if low.startswith("aws"):
        return "AWS"
    if low.startswith("azure"):
        return "Azure"
    if low.startswith("gcp"):
        return "GCP"
    if low.startswith("google cloud"):
        return "GCP"
    if low.startswith("vmware"):
        return "VMware"

    if low.startswith("spring boot") or low == "스프링부트" or low == "springboot":
        return "Spring Boot"
    if low.startswith("spring batch"):
        return "Spring Batch"
    if low.startswith("spring security"):
        return "Spring Security"
    if low.startswith("spring mvc"):
        return "Spring MVC"
    if low.startswith("spring cloud"):
        return "Spring Cloud"
    if low.startswith("spring data jpa"):
        return "Spring Data JPA"
    if low.startswith("spring") or low == "스프링":
        return "Spring"

    if low.startswith("react native"):
        return "React Native"
    if low.startswith("react"):
        return "React"
    if low.startswith("vue"):
        return "Vue.js"
    if low.startswith("node"):
        return "Node.js"
    if low.startswith("javascript") or low == "js" or low == "자바스크립트":
        return "JavaScript"
    if low.startswith("typescript") or low == "ts" or low == "타입스크립트":
        return "TypeScript"
    if low.startswith("power bi"):
        return "Power BI"
    if low in {"jquery.js"}:
        return "jQuery"

    if low.startswith("raspberry"):
        return "Raspberry Pi"
    if low.startswith("mqtt"):
        return "MQTT"
    if low.startswith("arduino"):
        return "Arduino"
    if low.startswith("embedded linux"):
        return "Embedded Linux"
    if low.startswith("embedded"):
        return "Embedded"
    if low.startswith("rtos"):
        return "RTOS"
    if low.startswith("freertos"):
        return "FreeRTOS"
    if low.startswith("zephyr"):
        return "Zephyr"
    if low.startswith("ros2") or low == "ros 2":
        return "ROS2"
    if low.startswith("ros"):
        return "ROS"
    if low.startswith("modbus"):
        return "Modbus"
    if low.startswith("can"):
        return "CAN"

    return t


def looks_like_noise(token: str) -> bool:
    t = normalize_token(token)
    if not t:
        return True

    if len(t) <= 1 and t not in {"R", "C"}:
        return True

    if re.fullmatch(r"[0-9]+", t):
        return True

    if re.fullmatch(r"@[A-Za-z0-9_.]+", t):
        return True

    if re.fullmatch(r"\.[A-Za-z0-9]+", t) and not t.lower().startswith(".net"):
        return True

    if re.fullmatch(r"[\[\]\(\)\{\}]+", t):
        return True

    if re.fullmatch(r"[A-Za-z]{1,2}", t) and t.lower() not in {"r", "c", "js", "ts", "db"}:
        return True

    return False


def should_drop_token(token: str) -> bool:
    t = normalize_token(token)
    if not t:
        return True

    low = t.lower()

    if low in {"nan", "none", "null", "na", "n/a"}:
        return True

    if t in BAD_EXACT:
        return True

    for bad in BAD_CONTAINS:
        if bad in t:
            return True

    for p in BAD_PATTERNS:
        if re.match(p, t, flags=re.IGNORECASE):
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


def is_excluded_skill(skill: str) -> bool:
    s = clean_text(skill)
    if not s:
        return True

    low = s.lower()

    if s in EXCLUDE_SKILLS_EXACT:
        return True

    if low in EXCLUDE_SKILLS_LOWER:
        return True

    for bad in EXCLUDE_CONTAINS:
        if bad.lower() in low:
            return True

    for p in EXCLUDE_PATTERNS:
        if re.fullmatch(p, s, flags=re.IGNORECASE):
            return True

    for p in MASTER_EXCLUDE_PATTERNS:
        if re.fullmatch(p, s, flags=re.IGNORECASE):
            return True

    return False


def looks_like_tech_skill(skill: str) -> bool:
    s = clean_text(skill)
    if not s:
        return False

    low = s.lower()

    if low in TECH_KEYWORDS:
        return True

    exact_patterns = [
        r"^spring(\s+boot|\s+batch|\s+security|\s+mvc|\s+framework|\s+data(\s+jpa)?|\s+cloud)?$",
        r"^react(\s+native)?$",
        r"^node(\.js)?$",
        r"^vue(\.js)?$",
        r"^next(\.js)?$",
        r"^nestjs$",
        r"^c/c\+\+$",
        r"^c#$",
        r"^\.net$",
        r"^asp\.net$",
        r"^google analytics$",
        r"^google optimize$",
        r"^mqtt$",
        r"^raspberry pi$",
        r"^arduino$",
        r"^embedded( linux)?$",
        r"^rtos$",
        r"^freertos$",
        r"^zephyr$",
        r"^ros2?$",
        r"^modbus$",
        r"^can$",
        r"^uart$",
        r"^spi$",
        r"^i2c$",
        r"^ble$",
        r"^zigbee$",
        r"^lorawan$",
        r"^lora$",
        r"^onnx$",
        r"^edge ai$",
    ]
    for p in exact_patterns:
        if re.fullmatch(p, low):
            return True

    return False


# =========================
# 4) 텍스트 검색 기반 보강
# =========================
SKILL_ALIAS_PATTERNS = {
    r"\bmqtt\b": "MQTT",
    r"\braspberry\s*pi\b|라즈베리파이": "Raspberry Pi",
    r"\barduino\b|아두이노": "Arduino",
    r"\bembedded linux\b|임베디드\s*리눅스": "Embedded Linux",
    r"\bembedded\b|임베디드": "Embedded",
    r"\brtos\b": "RTOS",
    r"\bfreertos\b": "FreeRTOS",
    r"\bzephyr\b": "Zephyr",
    r"\bros\s*2\b|\bros2\b": "ROS2",
    r"\bros\b": "ROS",
    r"\bcan(\s*bus)?\b": "CAN",
    r"\bmodbus\b": "Modbus",
    r"\buart\b": "UART",
    r"\bspi\b": "SPI",
    r"\bi2c\b": "I2C",
    r"\bble\b|bluetooth low energy": "BLE",
    r"\bzigbee\b": "Zigbee",
    r"\blorawan\b": "LoRaWAN",
    r"\blora\b": "LoRa",
    r"\bedge ai\b": "Edge AI",
    r"\bonnx\b": "ONNX",
}


def extract_known_skills_by_search(text: str) -> list[str]:
    t = clean_text(text)
    if not t:
        return []

    found = []
    seen = set()

    for pattern, canonical in SKILL_ALIAS_PATTERNS.items():
        if re.search(pattern, t, flags=re.IGNORECASE):
            if canonical not in seen:
                seen.add(canonical)
                found.append(canonical)

    return found


# =========================
# 5) 스킬 추출
# =========================
def extract_skill_candidates_from_text(text: str) -> list[str]:
    if is_missing_value(text):
        return []

    text = preprocess_raw_skill_text(text)
    raw_tokens = split_with_inner_parentheses_expansion(text)

    out = []
    seen = set()

    for raw in raw_tokens:
        token = normalize_token(raw)
        if not token:
            continue

        if should_drop_token(token):
            continue

        skill = canonicalize_skill(token)
        if not skill:
            continue

        if should_drop_token(skill):
            continue

        if is_excluded_skill(skill):
            continue

        if not looks_like_tech_skill(skill):
            continue

        if skill not in seen:
            seen.add(skill)
            out.append(skill)

    search_based = extract_known_skills_by_search(text)
    for skill in search_based:
        skill = canonicalize_skill(skill)
        if not skill:
            continue
        if should_drop_token(skill):
            continue
        if is_excluded_skill(skill):
            continue
        if not looks_like_tech_skill(skill):
            continue
        if skill not in seen:
            seen.add(skill)
            out.append(skill)

    return out


def extract_skill_candidates(row: pd.Series) -> list[str]:
    values = []

    if "스킬" in row and not is_missing_value(row["스킬"]):
        values.extend(extract_skill_candidates_from_text(str(row["스킬"])))

    out = []
    seen = set()

    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)

    return out


# =========================
# 6) 데이터 로드
# =========================
def load_raw_by_code(major_code: str) -> pd.DataFrame:
    industries = load_industries()

    target = None
    for item in industries:
        if str(item["major_code"]).strip() == str(major_code):
            target = item
            break

    if target is None:
        raise ValueError(f"industries.json 에 major_code={major_code} 가 없습니다.")

    major_name = str(target["major_name"]).strip()
    raw_csv = find_raw_csv_for_industry(major_code, major_name)

    if raw_csv is None:
        print(f"[WARN] raw 없음: {major_code} / {major_name}", flush=True)
        return pd.DataFrame()

    print(f"[INFO] load raw: {raw_csv}", flush=True)

    df = pd.read_csv(raw_csv, encoding="utf-8-sig")
    if df.empty:
        print(f"[WARN] raw 비어 있음: {major_code} / {major_name}", flush=True)
        return pd.DataFrame()

    if "스킬" in df.columns:
        df["스킬"] = df["스킬"].fillna("").astype(str).map(preprocess_raw_skill_text)
    else:
        df["스킬"] = ""

    df["domain_id"] = int(major_code)
    df["domain_name"] = major_name
    return df


def load_other_industries_except(base_code: str) -> pd.DataFrame:
    industries = load_industries()
    frames = []

    for item in industries:
        major_code = str(item["major_code"]).strip()
        major_name = str(item["major_name"]).strip()

        if major_code == str(base_code):
            continue

        raw_csv = find_raw_csv_for_industry(major_code, major_name)
        if raw_csv is None:
            print(f"[WARN] raw 없음: {major_code} / {major_name}", flush=True)
            continue

        print(f"[INFO] load raw: {raw_csv}", flush=True)

        df = pd.read_csv(raw_csv, encoding="utf-8-sig")
        if df.empty:
            print(f"[WARN] raw 비어 있음: {major_code} / {major_name}", flush=True)
            continue

        if "스킬" in df.columns:
            df["스킬"] = df["스킬"].fillna("").astype(str).map(preprocess_raw_skill_text)
        else:
            df["스킬"] = ""

        df["domain_id"] = int(major_code)
        df["domain_name"] = major_name
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


# =========================
# 7) master skill 생성
# =========================
def build_master_skill_counter(base_df: pd.DataFrame) -> dict[str, int]:
    counter = {}

    for _, row in base_df.iterrows():
        skills = extract_skill_candidates(row)
        for skill in skills:
            skill = canonicalize_skill(skill)

            if not skill:
                continue
            if is_excluded_skill(skill):
                continue
            if should_drop_token(skill):
                continue
            if not looks_like_tech_skill(skill):
                continue

            counter[skill] = counter.get(skill, 0) + 1

    return counter


def build_master_skills(base_df: pd.DataFrame, min_count: int = 2) -> set[str]:
    counter = build_master_skill_counter(base_df)

    master_skills = {
        skill
        for skill, cnt in counter.items()
        if cnt >= min_count and not is_excluded_skill(skill)
    }

    print(f"[INFO] master skills count = {len(master_skills)}", flush=True)
    return master_skills


# =========================
# 8) other 산업 필터링
# =========================
def extract_only_master_skills_from_row(row: pd.Series, master_skills: set[str]) -> list[str]:
    candidates = extract_skill_candidates(row)

    out = []
    seen = set()

    for skill in candidates:
        skill = canonicalize_skill(skill)
        if not skill:
            continue
        if is_excluded_skill(skill):
            continue
        if should_drop_token(skill):
            continue
        if not looks_like_tech_skill(skill):
            continue
        if skill not in master_skills:
            continue

        if skill not in seen:
            seen.add(skill)
            out.append(skill)

    return out


def filter_rows_with_master_skills(df: pd.DataFrame, master_skills: set[str]) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    rows = []

    for _, row in df.iterrows():
        matched_skills = extract_only_master_skills_from_row(row, master_skills)
        if not matched_skills:
            continue

        row_copy = row.copy()
        row_copy["_matched_master_skills"] = ", ".join(matched_skills)
        rows.append(row_copy)

    if not rows:
        cols = list(df.columns)
        if "_matched_master_skills" not in cols:
            cols.append("_matched_master_skills")
        return pd.DataFrame(columns=cols)

    out = pd.DataFrame(rows).reset_index(drop=True)
    print(f"[INFO] matched rows = {len(out)}", flush=True)
    return out


# =========================
# 9) pair 생성
# =========================
def build_company_skill_pairs_from_master(
    df: pd.DataFrame,
    master_skills: set[str]
) -> pd.DataFrame:
    rows = []

    for _, row in df.iterrows():
        company = clean_text(row.get("기업명", ""))
        domain_id = row.get("domain_id", None)
        domain_name = clean_text(row.get("domain_name", ""))

        if is_missing_value(company):
            continue

        matched_master_skills = extract_only_master_skills_from_row(row, master_skills)
        if not matched_master_skills:
            continue

        for skill in matched_master_skills:
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
    pair_df["스킬"] = pair_df["스킬"].map(canonicalize_skill)

    pair_df = pair_df[
        (pair_df["기업명"] != "") &
        (pair_df["스킬"] != "")
    ]

    pair_df = pair_df[~pair_df["스킬"].map(is_excluded_skill)]
    pair_df = pair_df[pair_df["스킬"].isin(master_skills)]

    pair_df = pair_df.drop_duplicates(
        subset=["domain_id", "기업명", "스킬"]
    ).reset_index(drop=True)

    return pair_df


# =========================
# 10) skills / ERD 생성
# =========================
def build_skills_df(pair_df: pd.DataFrame) -> pd.DataFrame:
    """
    1. 전처리 결과에서 실제 나온 스킬만 먼저 생성
    2. 그 다음 보충 리스트에서 없는 것만 추가
    3. 최종 스키마: skill_id, front_name, db_name
    """
    if pair_df.empty:
        actual_skills = []
    else:
        actual_skills = sorted(
            {
                canonicalize_skill(x)
                for x in pair_df["스킬"].dropna().astype(str).tolist()
                if canonicalize_skill(x) != "" and not is_excluded_skill(canonicalize_skill(x))
            }
        )

    rows = []
    for idx, skill_name in enumerate(actual_skills, start=1):
        rows.append({
            "skill_id": idx,
            "front_name": skill_name,
            "db_name": make_db_name_from_front_name(skill_name),
        })

    skills_df = pd.DataFrame(rows, columns=["skill_id", "front_name", "db_name"])
    existing_names = set(actual_skills)

    extra_names = []
    for skill_name in SUPPLEMENT_SKILL_NAMES:
        canonical_name = canonicalize_skill(skill_name)
        if not canonical_name:
            continue
        if canonical_name not in existing_names:
            extra_names.append(canonical_name)
            existing_names.add(canonical_name)

    if extra_names:
        start_id = 1 if skills_df.empty else int(skills_df["skill_id"].max()) + 1
        extra_df = pd.DataFrame({
            "skill_id": range(start_id, start_id + len(extra_names)),
            "front_name": extra_names,
            "db_name": [make_db_name_from_front_name(x) for x in extra_names],
        })
        skills_df = pd.concat([skills_df, extra_df], ignore_index=True)

    skills_df = skills_df.drop_duplicates(subset=["db_name"]).reset_index(drop=True)
    skills_df["skill_id"] = range(1, len(skills_df) + 1)

    return skills_df[["skill_id", "front_name", "db_name"]]


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
        clean_text(row["front_name"]): int(row["skill_id"])
        for _, row in skills_df.iterrows()
    }

    rows = []
    for _, row in pair_df.iterrows():
        domain_id = int(row["domain_id"])
        company_name = clean_text(row["기업명"])
        skill_name = canonicalize_skill(row["스킬"])

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
# 11) 디버그 저장
# =========================
def save_master_skill_debug(master_skills: set[str], counter: dict[str, int], path: Path):
    rows = []
    for skill in sorted(master_skills):
        rows.append({
            "skill": skill,
            "count_in_10007": counter.get(skill, 0)
        })
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")


# =========================
# 12) 메인
# =========================
def main():
    print("=" * 70, flush=True)
    print("[INIT_PREPROCESS_ALL] start", flush=True)
    print("=" * 70, flush=True)

    DB_READY_DIR.mkdir(parents=True, exist_ok=True)

    # 1) 10007 로드
    base_df = load_raw_by_code(BASE_MASTER_CODE)
    if base_df.empty:
        print(f"[WARN] {BASE_MASTER_CODE} raw 데이터가 없습니다.", flush=True)
        return

    print(f"[INFO] {BASE_MASTER_CODE} raw rows: {len(base_df)}", flush=True)

    # 2) master skill 생성 (최소 2회 등장)
    master_counter = build_master_skill_counter(base_df)
    master_skills = build_master_skills(base_df, min_count=2)

    # 3) 10007 자체 pair 생성
    base_pair_df = build_company_skill_pairs_from_master(base_df, master_skills)
    print(f"[INFO] {BASE_MASTER_CODE} pairs: {len(base_pair_df)}", flush=True)

    # 4) 나머지 산업 로드
    other_df = load_other_industries_except(BASE_MASTER_CODE)
    print(f"[INFO] other raw rows: {len(other_df)}", flush=True)

    # 5) master skill 포함 공고만 남김
    matched_other_df = filter_rows_with_master_skills(other_df, master_skills)
    print(f"[INFO] matched other rows: {len(matched_other_df)}", flush=True)

    # 6) 저장은 master skill만
    other_pair_df = build_company_skill_pairs_from_master(matched_other_df, master_skills)
    print(f"[INFO] other pairs: {len(other_pair_df)}", flush=True)

    # 7) 통합
    pair_df = pd.concat([base_pair_df, other_pair_df], ignore_index=True)
    pair_df["스킬"] = pair_df["스킬"].map(canonicalize_skill)
    pair_df = pair_df[~pair_df["스킬"].map(is_excluded_skill)]
    pair_df = pair_df.drop_duplicates(subset=["domain_id", "기업명", "스킬"]).reset_index(drop=True)

    # 8) ERD
    domains_df = build_domains_df(pair_df)
    companies_df = build_companies_df(pair_df)
    skills_df = build_skills_df(pair_df)
    company_skills_df = build_company_skills_df(pair_df, companies_df, skills_df)

    # 9) 저장
    save_csv(pair_df, DB_READY_DIR / "company_skill_pairs.csv")
    save_csv(domains_df, DB_READY_DIR / "domains.csv")
    save_csv(companies_df, DB_READY_DIR / "companies.csv")
    save_csv(skills_df, DB_READY_DIR / "skills.csv")
    save_csv(company_skills_df, DB_READY_DIR / "company_skills.csv")

    # 10) 디버그 파일
    save_csv(base_df, DB_READY_DIR / "debug_10007_raw.csv")
    save_csv(base_pair_df, DB_READY_DIR / "debug_10007_pairs.csv")
    save_csv(matched_other_df, DB_READY_DIR / "debug_other_matched_rows.csv")
    save_csv(other_pair_df, DB_READY_DIR / "debug_other_pairs.csv")
    save_master_skill_debug(master_skills, master_counter, DB_READY_DIR / "debug_master_skills.csv")

    print("\n[DEBUG] master skills sample", flush=True)
    print(sorted(list(master_skills))[:150], flush=True)

    print("\n[DEBUG] pair_df head", flush=True)
    if pair_df.empty:
        print("(empty)", flush=True)
    else:
        print(pair_df.head(50).to_string(), flush=True)

    print(f"\n[DONE] pairs={len(pair_df)}", flush=True)
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