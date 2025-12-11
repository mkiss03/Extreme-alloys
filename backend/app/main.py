# backend/app/main.py
# v2.0: Production-ready with logging middleware, CORS, and /version endpoint
"""
Main FastAPI application for Extreme Alloys prediction service

Features:
- Multiple prediction models (GNN, Physics, Safety)
- Request logging middleware
- CORS configuration
- Health checks and version info
"""

import time
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import API_PREFIX, logger, ENV
from app.api.routes_prediction import router as prediction_router

# Deployment timestamp
DEPLOYED_AT = datetime.utcnow().isoformat() + "Z"

# Initialize FastAPI app
app = FastAPI(
    title="Extreme Alloys API v2.0",
    description="""
    AI-powered prediction service for alloys under extreme conditions.

    **Features:**
    - Multiple prediction models (GNN, Physics Heuristic, Safety Conservative)
    - Realistic physics-based calculations using Arrhenius equations
    - Comprehensive input validation with auto-normalization
    - Request logging and monitoring
    - Production-ready CORS configuration

    **Version:** 2.0.0
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Allow frontend origins
# NOTE: Set ENV=production on Render.com for production configuration
origins = [
    # Production Vercel deployments
    "https://extreme-alloys.vercel.app",
    "https://extreme-alloys-frontend.vercel.app",
    "https://bhomev2-fh6c.vercel.app",  # Actual Vercel deployment
    # Development
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]

# Allow all vercel.app domains if needed
if ENV != "production":
    logger.warning("Running in development mode - CORS allows all origins from vercel.app")
    # In development, we might use different Vercel preview deployments

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ============================================================================
# Logging Middleware
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all incoming requests with timing information
    """
    start_time = time.time()

    # Log request
    logger.info(f"→ {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log response
    logger.info(
        f"← {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Duration: {duration:.3f}s"
    )

    return response


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
        "version": "2.0.0",
        "environment": ENV,
        "uptime": "OK"
    }


@app.get("/version")
async def version_info():
    """
    Get detailed version information about the API and models

    Returns version info, model versions, and deployment timestamp
    """
    from app.models.model_loader import MODEL_REGISTRY

    model_versions = {}
    for model_type, info in MODEL_REGISTRY.items():
        if info["loader"]:
            try:
                model_info = info["loader"]()
                model_versions[model_type] = model_info.get("version", "unknown")
            except:
                model_versions[model_type] = "not_loaded"

    return {
        "api_version": "2.0.0",
        "api_name": "Extreme Alloys Prediction API",
        "environment": ENV,
        "deployed_at": DEPLOYED_AT,
        "model_versions": model_versions,
        "models_available": list(MODEL_REGISTRY.keys()),
        "features": [
            "Multi-model prediction (GNN, Physics, Safety)",
            "Realistic physics calculations (Arrhenius, creep mechanics)",
            "Auto-normalization (±5% tolerance)",
            "Automatic Kelvin conversion",
            "Request logging middleware",
            "Comprehensive input validation"
        ]
    }


@app.get("/")
async def root():
    """
    Root endpoint with API overview
    """
    return {
        "message": "Extreme Alloys Prediction API v2.0",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "version": "/version",
            "predict": f"{API_PREFIX}/predict/extreme_alloy",
            "models": f"{API_PREFIX}/predict/models"
        },
        "models": ["gnn", "physics_heuristic", "safety_conservative"]
    }


if __name__ == "__main__":
    import uvicorn
    from app.config import API_HOST, API_PORT

    logger.info(f"Starting Extreme Alloys API on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
