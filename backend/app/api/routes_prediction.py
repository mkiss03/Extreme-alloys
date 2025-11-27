# backend/app/api/routes_prediction.py
"""
Prediction API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional
from app.services.preprocessing import prepare_features, validate_input
from app.services.prediction_service import predict_extreme_behavior
from app.services.reporting import generate_report
from app.config import logger

router = APIRouter(prefix="/predict", tags=["predictions"])


class AlloyPredictionRequest(BaseModel):
    """
    Request model for alloy behavior prediction
    """
    composition: str = Field(
        ...,
        example="Ni:55,Cr:20,Mo:10,W:12,Co:3",
        description="Alloy composition as 'Element:Percentage' pairs"
    )
    temperature_c: float = Field(
        ...,
        example=850.0,
        description="Operating temperature in Celsius"
    )
    pressure_mpa: float = Field(
        ...,
        example=150.0,
        description="Operating pressure in MPa"
    )
    cycles: int = Field(
        ...,
        example=10000,
        description="Number of thermal/mechanical cycles"
    )
    model_type: Optional[str] = Field(
        default="gnn",
        example="gnn",
        description="Model type: 'gnn', 'creep', or 'ensemble'"
    )


class AlloyPredictionResponse(BaseModel):
    """
    Response model for prediction results
    """
    creep_lifetime_hours: float
    failure_probability: float
    stress_limit_mpa: float
    model_version: str
    confidence: float


@router.post("/extreme_alloy", response_model=AlloyPredictionResponse)
async def predict_alloy_behavior(request: AlloyPredictionRequest):
    """
    Predict alloy behavior under extreme conditions

    This endpoint takes alloy composition and operating conditions,
    then returns predictions for:
    - Creep lifetime (hours)
    - Failure probability (0-1)
    - Recommended stress limits (MPa)
    """
    try:
        # Convert request to dict for processing
        input_data = request.dict()

        # Validate input
        is_valid, error_msg = validate_input(input_data)
        if not is_valid:
            logger.error(f"Input validation failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        # Prepare features
        features = prepare_features(input_data)

        # Generate prediction
        prediction = predict_extreme_behavior(features)

        logger.info(f"Successful prediction for composition: {request.composition}")

        return prediction

    except ValueError as e:
        logger.error(f"Value error in prediction: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/report")
async def generate_prediction_report(request: AlloyPredictionRequest):
    """
    Generate detailed prediction report with recommendations
    """
    try:
        input_data = request.dict()

        # Validate and process
        is_valid, error_msg = validate_input(input_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        features = prepare_features(input_data)
        prediction = predict_extreme_behavior(features)

        # Generate comprehensive report
        report = generate_report(prediction, input_data)

        return report

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def prediction_health():
    """
    Health check for prediction service
    """
    return {
        "status": "healthy",
        "service": "prediction-api",
        "models_available": ["gnn", "creep", "ensemble"]
    }
