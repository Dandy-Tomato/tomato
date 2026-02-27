from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    statusCode: int
    message: str
    data: Optional[T] = None


def _encode_data(data: Any) -> Any:
    if data is None:
        return None

    if isinstance(data, BaseModel):
        return data.model_dump(by_alias=True)

    if isinstance(data, (list, tuple)):
        return [_encode_data(x) for x in data]

    if isinstance(data, dict):
        return {k: _encode_data(v) for k, v in data.items()}

    return jsonable_encoder(data)


def ok(data: T | None = None, message: str = "OK", status_code: int = 200) -> ApiResponse[T]:
    return ApiResponse(
        statusCode=status_code,
        message=message,
        data=_encode_data(data),
    )


def fail(message: str, status_code: int, data: Any | None = None) -> ApiResponse[Any]:
    return ApiResponse(
        statusCode=status_code,
        message=message,
        data=_encode_data(data),
    )
