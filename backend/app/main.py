import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import init_db, AsyncSessionLocal
from app.rag.ingest import seed_sample_transcripts_if_empty
from app.api.v1.health import router as health_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.chat import router as chat_router
from app.api.v1.artifacts import router as artifacts_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.eval import router as eval_router

setup_logging()

import asyncio

async def background_startup_ingest():
    """Runs transcript ingestion in background so server starts immediately."""
    await asyncio.sleep(1) # Brief yield to let Uvicorn bind port
    try:
        async with AsyncSessionLocal() as db:
            await seed_sample_transcripts_if_empty(db)
    except Exception as e:
        logger.error(f"Background startup ingestion error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    # Initialize Database Schema & pgvector extension immediately
    try:
        await init_db()
        # Launch ingestion in background without blocking server startup
        asyncio.create_task(background_startup_ingest())
    except Exception as e:
        logger.warning(f"Database initialization deferred or encountered warning: {e}")
        
    yield
    logger.info("Shutting down Lenny Growth Assistant...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-stack AI Growth Advisor grounded in Lenny's Podcast transcripts with pgvector RAG, Ship 30 for 30 skills, and in-app Artifact Viewer.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Timing & Tracing Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please check server logs."}
    )

# Include API Routers
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(sessions_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(artifacts_router, prefix=settings.API_V1_STR)
app.include_router(ingestion_router, prefix=settings.API_V1_STR)
app.include_router(eval_router, prefix=f"{settings.API_V1_STR}/eval", tags=["Evaluation"])

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
