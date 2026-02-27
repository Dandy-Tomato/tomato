from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.errors import AppError
from app.common.responses import fail


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        status_code = exc.http_status()
        body = fail(
            message=exc.message() if exc.detail is None else f"{exc.message()} ({exc.detail})",
            status_code=status_code,
            data=exc.meta,
        )
        return JSONResponse(status_code=status_code, content=body.model_dump())

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        status_code = exc.status_code
        body = fail(message=str(exc.detail), status_code=status_code, data=None)
        return JSONResponse(status_code=status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        status_code = 422
        body = fail(message="요청 값이 올바르지 않습니다.", status_code=status_code, data={"errors": exc.errors()})
        return JSONResponse(status_code=status_code, content=body.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        status_code = 500
        body = fail(message="서버 내부 오류가 발생했습니다.", status_code=status_code, data=None)
        return JSONResponse(status_code=status_code, content=body.model_dump())
