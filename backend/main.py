import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.router import api_router
from app.config import settings
from app.logging_config import setup_logging
from app.vector_db import chroma_client

# Initialize Logging configuration immediately on entry
setup_logging()
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown processes of the application.
    Enables database pool setups, vector-db connection checks, etc.
    """
    logger.info("Initializing system dependencies...")
    
    # Verify vector DB connection on startup
    chroma_client.connect()
    if not chroma_client.check_health():
        logger.warning("ChromaDB vector store is currently unreachable. RAG operations will fail.")
    else:
        logger.info("ChromaDB vector store connection verified successfully.")

    yield

    logger.info("Shutting down application server...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade Platform Infrastructure API.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """
    HTTP Middleware logging details about every API request/response cycle.
    Captures processing time, status, method, and URI.
    """
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(
        f"Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "client_host": request.client.host if request.client else "unknown",
        }
    )
    return response


# Include master router
app.include_router(api_router, prefix="/api")


@app.get("/", include_in_schema=False)
async def root_redirect():
    """
    Redirect root path to interactive Swagger API documentation page.
    """
    return RedirectResponse(url="/docs")
