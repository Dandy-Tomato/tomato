from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(str, Enum):
    # Common
    INTERNAL_ERROR = "COMMON_500"
    INVALID_ARGUMENT = "COMMON_400"
    NOT_FOUND = "COMMON_404"
    UNAUTHORIZED = "COMMON_401"

    # AI / Embedding (Example)
    EMBEDDING_FAILED = "AI_500"


ERROR_HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.INTERNAL_ERROR: 500,
    ErrorCode.INVALID_ARGUMENT: 400,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.EMBEDDING_FAILED: 500,
}


ERROR_MESSAGE_KO: dict[ErrorCode, str] = {
    ErrorCode.INTERNAL_ERROR: "서버 내부 오류가 발생했습니다.",
    ErrorCode.INVALID_ARGUMENT: "요청 파라미터가 올바르지 않습니다.",
    ErrorCode.NOT_FOUND: "대상을 찾을 수 없습니다.",
    ErrorCode.UNAUTHORIZED: "인증에 실패했습니다.",
    ErrorCode.EMBEDDING_FAILED: "AI 임베딩 처리 중 오류가 발생했습니다.",
}


@dataclass
class AppError(Exception):
    code: ErrorCode
    detail: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    def http_status(self) -> int:
        return ERROR_HTTP_STATUS.get(self.code, 500)

    def message(self) -> str:
        return ERROR_MESSAGE_KO.get(self.code, "오류가 발생했습니다.")
