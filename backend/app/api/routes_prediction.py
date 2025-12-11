# backend/app/api/routes_prediction.py
# UPDATED: Enhanced schema with model_type routing and comprehensive response metadata
"""
Prediction API endpoints with multiple model support
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, Any
from app.services.preprocessing import prepare_features, validate_input
from app.services.prediction_service import predict_with_model
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
        description="Alloy composition as 'Element:Percentage' pairs separated by commas"
    )
    temperature_c: float = Field(
        ...,
        example=850.0,
        description="Operating temperature in Celsius",
        ge=0,
        le=2000
    )
    pressure_mpa: float = Field(
        ...,
        example=150.0,
        description="Operating pressure in MPa",
        ge=0,
        le=1000
    )
    cycles: int = Field(
        ...,
        example=10000,
        description="Number of thermal/mechanical cycles",
        ge=0,
        le=10000000
    )
    model_type: Optional[str] = Field(
        default="gnn",
        example="gnn",
        description="Model type: 'gnn' (default), 'physics_heuristic', or 'safety_conservative'"
    )

    @validator('model_type')
    def validate_model_type(cls, v):
        """Ensure model_type is valid"""
        valid_types = ['gnn', 'physics_heuristic', 'safety_conservative']
        if v and v not in valid_types:
            raise ValueError(
                f"model_type must be one of {valid_types}, got '{v}'"
            )
        return v or 'gnn'  # Default to gnn if None

    @validator('composition')
    def validate_composition_format(cls, v):
        """Basic validation of composition string format"""
        if not v or not isinstance(v, str):
            raise ValueError("Composition must be a non-empty string")
        if ':' not in v:
            raise ValueError("Composition must contain 'Element:Percentage' pairs")
        return v


class AlloyPredictionResponse(BaseModel):
    """
    Response model for prediction results with full metadata
    """
    # Core predictions
    creep_lifetime_hours: float = Field(
        ...,
        description="Predicted creep lifetime in hours"
    )
    failure_probability: float = Field(
        ...,
        description="Probability of failure (0-1)",
        ge=0,
        le=1
    )
    stress_limit_mpa: float = Field(
        ...,
        description="Recommended maximum stress in MPa"
    )

    # Model metadata
    model_type: str = Field(
        ...,
        description="Model type used for prediction"
    )
    model_strategy: str = Field(
        ...,
        description="Model strategy (data_driven, physics_inspired, safety_conservative)"
    )
    model_version: str = Field(
        ...,
        description="Model version identifier"
    )
    model_confidence: float = Field(
        ...,
        description="Model confidence score (0-1)",
        ge=0,
        le=1
    )

    # Optional metadata
    physics_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Physics-based calculation metadata (if applicable)"
    )
    safety_factors: Optional[Dict[str, float]] = Field(
        default=None,
        description="Safety factors applied (if applicable)"
    )


@router.post(
    "/extreme_alloy",
    response_model=AlloyPredictionResponse,
    summary="Predict Alloy Behavior",
    description="""
    Predict extreme alloy behavior under high temperature, pressure, and cyclic loading.

    **Supported Models:**

    1. **GNN (Graph Neural Network)** [default]
       - Strategy: Data-driven machine learning
       - Confidence: 75%
       - Best for: General-purpose predictions with balanced accuracy

    2. **Physics Heuristic**
       - Strategy: Physics-based analytical calculations
       - Confidence: 65%
       - Uses: Arrhenius equations, creep mechanics, material science principles
       - Best for: When physical understanding is prioritized over accuracy

    3. **Safety Conservative**
       - Strategy: Conservative safety margins (2x safety factors)
       - Confidence: 90%
       - Applies: 50% lifetime reduction, +15% failure probability, 20% stress reduction
       - Best for: Critical applications requiring worst-case estimates

    **Example Request:**
    ```json
    {
      "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
      "temperature_c": 850,
      "pressure_mpa": 150,
      "cycles": 10000,
      "model_type": "gnn"
    }
    ```

    **Returns:**
    - Creep lifetime (hours)
    - Failure probability (0-1)
    - Recommended stress limit (MPa)
    - Model metadata and confidence score
    """,
    responses={
        200: {
            "description": "Successful prediction",
            "content": {
                "application/json": {
                    "example": {
                        "creep_lifetime_hours": 4523.8,
                        "failure_probability": 0.342,
                        "stress_limit_mpa": 387.5,
                        "model_type": "gnn",
                        "model_strategy": "data_driven_ml",
                        "model_version": "v2.0_demo",
                        "model_confidence": 0.75
                    }
                }
            }
        },
        400: {"description": "Invalid input data"},
        500: {"description": "Internal server error"}
    }
)
async def predict_alloy_behavior(request: AlloyPredictionRequest):
    """Main prediction endpoint - v2.0"""
    try:
        # Convert request to dict for processing
        input_data = request.dict()
        model_type = input_data.get("model_type", "gnn")

        logger.info(f"Prediction request received - model_type: {model_type}")

        # Validate input
        is_valid, error_msg = validate_input(input_data)
        if not is_valid:
            logger.error(f"Input validation failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        # Prepare features and enrich input data
        try:
            features, enriched_input = prepare_features(input_data)
        except ValueError as e:
            logger.error(f"Feature preparation failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid input data: {str(e)}"
            )

        # Generate prediction with specified model
        prediction = predict_with_model(features, enriched_input, model_type)

        logger.info(
            f"Successful prediction - model: {model_type}, "
            f"lifetime: {prediction['creep_lifetime_hours']:.1f}h"
        )

        return prediction

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.error(f"Value error in prediction: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during prediction. Please try again."
        )


@router.post(
    "/report",
    summary="Generate Prediction Report",
    description="Generate a comprehensive PDF-style report with predictions, recommendations, and visualizations"
)
async def generate_prediction_report(request: AlloyPredictionRequest):
    """
    Generate detailed prediction report with recommendations

    Returns:
        Comprehensive report including input parameters, predictions, and recommendations
    """
    try:
        input_data = request.dict()
        model_type = input_data.get("model_type", "gnn")

        # Validate and process
        is_valid, error_msg = validate_input(input_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        features, enriched_input = prepare_features(input_data)
        prediction = predict_with_model(features, enriched_input, model_type)

        # Generate comprehensive report
        report = generate_report(prediction, enriched_input)

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def prediction_health():
    """
    Health check for prediction service
    """
    return {
        "status": "healthy",
        "service": "prediction-api",
        "version": "0.2.0",
        "models_available": ["gnn", "physics_heuristic", "safety_conservative"]
    }


@router.get(
    "/models",
    summary="List Available Models",
    description="Get a list of all available prediction models with detailed descriptions and recommendations"
)
async def list_available_models():
    """List all available prediction models with descriptions"""
    from app.services.model_selector import get_available_models

    models = get_available_models()

    return {
        "total_models": len(models),
        "models": models,
        "default_model": "gnn",
        "usage_note": "Specify 'model_type' in prediction request to select model"
    }
