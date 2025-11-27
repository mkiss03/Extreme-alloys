# backend/app/main.py
"""
Main FastAPI application for Extreme Alloys prediction service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import API_PREFIX, logger
from app.api.routes_prediction import router as prediction_router

# Initialize FastAPI app
app = FastAPI(
    title="Extreme Alloys API",
    description="AI-powered prediction service for alloys under extreme conditions",
    version="0.1.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prediction_router, prefix=API_PREFIX)


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "extreme-alloys-api",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """
    Root endpoint with basic info
    """
    return {
        "message": "Extreme Alloys Prediction API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    from app.config import API_HOST, API_PORT

    logger.info(f"Starting Extreme Alloys API on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
