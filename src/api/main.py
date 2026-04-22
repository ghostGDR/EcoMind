"""FastAPI application main module"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from src.api.models import HealthResponse, ErrorResponse
from src.api.routes import chat, conversations, documents
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Henry API",
    version="1.0.0",
    description="AI 电商专家对话系统 API"
)

# CORS middleware - allow all origins in development
# TODO: Restrict origins in production (T-06-01 mitigation)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for structured error responses

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError as 400 Bad Request"""
    logger.warning(f"ValueError: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    """Handle FileNotFoundError as 404 Not Found"""
    logger.warning(f"FileNotFoundError: {str(exc)}")
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions as 500 Internal Server Error"""
    # T-06-02 mitigation: Don't expose stack traces in production
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Readiness flag
is_ready = False

# Lifecycle events

@app.on_event("startup")
async def startup_event():
    """Initialize resources on application startup"""
    import threading
    from src.api.dependencies import get_vector_store
    
    logger.info("Henry API starting up...")
    
    def preload_resources():
        global is_ready
        try:
            logger.info("Preloading model and vector store...")
            get_vector_store()
            is_ready = True
            logger.info("All resources preloaded and ready!")
        except Exception as e:
            logger.error(f"Error preloading resources: {e}")

    # Start preloading in a background thread to not block startup
    threading.Thread(target=preload_resources, daemon=True).start()
    logger.info("FastAPI application initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown"""
    logger.info("Henry API shutting down...")
    # Close any open connections if needed
    logger.info("Cleanup complete")


# Include routers
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(documents.router)


# API endpoints

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with readiness status"""
    return HealthResponse(
        status="ok" if is_ready else "loading",
        service="henry-api"
    )


# Mount frontend static files
# This must be LAST - catch-all route
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
