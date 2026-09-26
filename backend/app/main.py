"""
NyayaAI — FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog

from app.config import settings
from app.database import init_db
from app.rag.vector_store import get_vector_store
from app.api import documents, compare, workspaces, lawyer_prep, health

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    logger.info("NyayaAI starting up", version="1.0.0", env=settings.ENVIRONMENT)
    try:
        store = get_vector_store()
        store._reset_collection()
    except Exception as exc:
        logger.warning("Vector store reset failed during startup", error=str(exc))
    await init_db()
    yield
    logger.info("NyayaAI shutting down")


app = FastAPI(
    title="NyayaAI API",
    description="GenAI Legal Assistance & Document Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS: allow localhost in development, but keep production defaults strict and
# configurable via environment variables.
allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"] if settings.ENVIRONMENT == "production" else ["*"]
allow_headers = ["Authorization", "Content-Type", "X-Session-ID"] if settings.ENVIRONMENT == "production" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if request.url.scheme == "https":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


# Routers - v1 prefixes
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(compare.router, prefix="/api/v1/compare", tags=["Compare"])
app.include_router(workspaces.router, prefix="/api/v1/workspaces", tags=["Workspaces"])
app.include_router(lawyer_prep.router, prefix="/api/v1/lawyer-prep", tags=["Lawyer Prep"])

# Legacy/Direct prefixes for flexibility
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(compare.router, prefix="/api/compare", tags=["Compare"])
app.include_router(workspaces.router, prefix="/api/workspaces", tags=["Workspaces"])
app.include_router(lawyer_prep.router, prefix="/api/lawyer-prep", tags=["Lawyer Prep"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )
