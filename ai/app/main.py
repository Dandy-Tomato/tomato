from __future__ import annotations

from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.recommendation_router import router as recommendation_router
from app.settings import settings
from app.common.exception_handlers import register_exception_handlers

import logging

app = FastAPI(
    title="to-mato AI API",
    description="AI Server for recommendations and embeddings",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(recommendation_router)

register_exception_handlers(app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)