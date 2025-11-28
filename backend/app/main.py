# backend/app/main.py
# UPDATED: Production-ready CORS configuration with specific origins
"""
Main FastAPI application for Extreme Alloys prediction service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import API_PREFIX, logger, ENV
from app.api.routes_prediction import router as prediction_router

# Initialize FastAPI app
app = FastAPI(
    title="Extreme Alloys API",
    description="AI-powered prediction service for alloys under extreme conditions",
    version="0.2.0"
)

# CORS middleware - production-ready configuration
# In production, only allow specific frontend origins
if ENV == "production":
    origins = [
        "https://extreme-alloys.vercel.app",  # Replace with your actual Vercel domain
        "https://extreme-alloys-frontend.vercel.app",
    ]
else:
    # Development: allow localhost
    origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
        "version": "0.2.0",
        "environment": ENV
    }


@app.get("/")
async def root():
    """
    Root endpoint with basic info
    """
    return {
        "message": "Extreme Alloys Prediction API",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health",
        "models": ["gnn", "physics_heuristic", "safety_conservative"]
    }


if __name__ == "__main__":
    import uvicorn
    from app.config import API_HOST, API_PORT

    logger.info(f"Starting Extreme Alloys API on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
