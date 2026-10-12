"""
FastAPI application entry point.
- Configures CORS from environment variables
- Loads NLP model on startup
- Initialises database tables
- Mounts API router at /api
"""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.database import init_db
from app.services import semantic_matcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Matchly AI – Resume Matcher API",
    description=(
        "NLP-powered resume-to-job-description compatibility scoring. "
        "Upload a resume and paste a job description to get a detailed match analysis."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Mount router
# ---------------------------------------------------------------------------
app.include_router(router, prefix="/api")


# ---------------------------------------------------------------------------
# Lifecycle events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Matchly AI backend …")

    # Initialise database
    try:
        await init_db()
        logger.info("Database tables verified/created.")
    except Exception as exc:
        logger.error("Database initialisation failed: %s", exc)

    # Load NLP model (non-blocking failure)
    model_name = settings.SENTENCE_MODEL
    ok = semantic_matcher.init_model(model_name)
    if ok:
        logger.info("NLP model '%s' is ready.", model_name)
    else:
        logger.warning(
            "NLP model '%s' could not be loaded. "
            "TF-IDF fallback will be used for semantic similarity.",
            model_name,
        )


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Matchly AI backend.")


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Matchly AI – Resume Matcher API",
        "docs": "/api/docs",
        "health": "/api/health",
    }
