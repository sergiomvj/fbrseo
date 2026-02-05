from fastapi import FastAPI, Request, status
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from app.config import settings
from app.database import engine, Base
from app.api.v1 import router as api_v1_router
from app.middleware.logging import log_api_usage
from app.models import auth, domain  # Import para criar tabelas

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    # Ensure data directory exists for SQLite
    if "sqlite" in settings.DATABASE_URL and "/data/" in settings.DATABASE_URL:
        data_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", ""))
        if data_dir and not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir, exist_ok=True)
                print(f"✅ Created data directory: {data_dir}")
            except Exception as e:
                print(f"⚠️ Could not create data directory {data_dir}: {e}")

    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    yield
    # Shutdown
    print("🔴 Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    return await log_api_usage(request, call_next)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Routes
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "message": "SEO API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}
