from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.common.responses import ok
from app.common.errors import AppError, ErrorCode

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/ping")
def ping():
    return ok({"pong": True})


@router.get("/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return ok({"status": "ok"})
    except Exception as e:
        raise AppError(code=ErrorCode.INTERNAL_ERROR, detail=str(e))