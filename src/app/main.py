"""
FastAPI Application Entry Point.

SOLID Principles Applied:
- Single Responsibility (S): Main app only handles application setup
- Dependency Inversion (D): All dependencies injected via DI container
- Open/Closed (O): Easy to add new routers without modifying core

This is the main entry point that wires everything together using
dependency injection, demonstrating the culmination of SOLID principles.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.dependencies import initialize_dependencies, shutdown_dependencies
from app.core.logging_config import setup_logging
from app.models.schemas import HealthResponse
from app.routes import auth_router, query_router

# Initialize settings and logging
settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    try:
        await initialize_dependencies()
        logger.info("Application started successfully")
        yield
    finally:
        # Shutdown
        logger.info("Shutting down application")
        await shutdown_dependencies()
        logger.info("Application shut down complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise AI Knowledge Assistant with RAG capabilities",
    lifespan=lifespan,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        Application health status
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        services={"database": "connected", "vector_store": "connected", "llm": "connected"},
    )


# Include routers
app.include_router(auth_router.router, prefix=settings.api_prefix)

app.include_router(query_router.router, prefix=settings.api_prefix)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": f"{settings.api_prefix}/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
