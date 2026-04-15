from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.models.database import MongoDB
from app.api import auth, jobs, applications, preferences

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle: startup and shutdown"""
    
    # Startup
    logger.info("🚀 Starting Job Finder API...")
    await MongoDB.connect_db(settings.mongodb_url, settings.db_name)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Job Finder API...")
    await MongoDB.close_db()


# Create FastAPI app
app = FastAPI(
    title="Job Finder API",
    description="AI-powered job application assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(preferences.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Job Finder API",
        "description": "AI-powered job application assistant",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
