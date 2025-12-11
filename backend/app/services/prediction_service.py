"""
Prediction Service - Main Entry Point (v2.0)

Refactored modular architecture:
- Routes requests to specialized model modules
- Clean separation of concerns
- Easy to extend with new models

Architecture:
    prediction_service.py (this file) → Router/Orchestrator
    ├── model_selector.py → Model selection logic
    ├── predict_gnn.py → GNN predictions
    ├── predict_physics.py → Physics-based predictions
    └── predict_safety.py → Conservative predictions
"""

import numpy as np
from typing import Dict, Any
from app.config import logger
from app.services.model_selector import select_model
from app.services.predict_gnn import predict_with_gnn
from app.services.predict_physics import predict_with_physics
from app.services.predict_safety import predict_with_safety


# ============================================================================
# Main Prediction Function
# ============================================================================

def predict_extreme_behavior(
    features: np.ndarray,
    input_data: Dict[str, Any],
    model_type: str = "gnn"
) -> Dict[str, Any]:
    """
    Main prediction function - orchestrates the prediction workflow

    Workflow:
    1. Select and validate model
    2. Route to appropriate predictor
    3. Return results with metadata

    Args:
        features: Preprocessed feature vector (numpy array)
        input_data: Original input data dictionary containing:
            - temperature_c: Temperature in Celsius
            - pressure_mpa: Pressure in MPa
            - composition_dict: Parsed composition dictionary
            - cycles: Number of thermal cycles
        model_type: Model identifier ("gnn", "physics_heuristic", "safety_conservative")

    Returns:
        Dictionary containing:
            - creep_lifetime_hours: Predicted creep lifetime
            - failure_probability: Probability of failure (0-1)
            - stress_limit_mpa: Maximum allowable stress
            - model_type: Model used
            - model_strategy: Strategy description
            - model_version: Model version
            - model_confidence: Confidence score (0-1)
            - Additional model-specific metadata

    Raises:
        ValueError: If model_type is invalid
    """
    logger.info(f"=== Prediction Request ===")
    logger.info(f"Model type: {model_type}")
    logger.info(f"Temperature: {input_data.get('temperature_c')}°C")
    logger.info(f"Pressure: {input_data.get('pressure_mpa')} MPa")
    logger.info(f"Cycles: {input_data.get('cycles')}")

    # Step 1: Select and validate model
    try:
        model_config = select_model(model_type)
    except ValueError as e:
        logger.error(f"Model selection failed: {str(e)}")
        raise

    # Step 2: Route to appropriate predictor
    prediction = _route_to_predictor(
        model_type=model_config["type"],
        features=features,
        input_data=input_data
    )

    logger.info(f"=== Prediction Complete ===")
    logger.info(f"Creep Lifetime: {prediction['creep_lifetime_hours']:.2f} hours")
    logger.info(f"Failure Probability: {prediction['failure_probability']:.3f}")
    logger.info(f"Stress Limit: {prediction['stress_limit_mpa']:.2f} MPa")

    return prediction


def _route_to_predictor(
    model_type: str,
    features: np.ndarray,
    input_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Route prediction request to appropriate model predictor

    Args:
        model_type: Validated model type
        features: Feature vector
        input_data: Input data dictionary

    Returns:
        Prediction dictionary
    """
    # Route to specialized predictor modules
    if model_type == "gnn":
        return predict_with_gnn(input_data, features)

    elif model_type == "physics_heuristic":
        return predict_with_physics(input_data, features)

    elif model_type == "safety_conservative":
        return predict_with_safety(input_data, features)

    else:
        # This should never happen due to model_selector validation
        # But included for defensive programming
        logger.error(f"Unexpected model_type: {model_type}")
        raise ValueError(f"Invalid model_type: {model_type}")


# ============================================================================
# Convenience Wrapper
# ============================================================================

def predict_with_model(
    features: np.ndarray,
    input_data: Dict[str, Any],
    model_type: str = "gnn"
) -> Dict[str, Any]:
    """
    Convenience wrapper for predict_extreme_behavior

    Provides a clean API for external callers

    Args:
        features: Feature vector
        input_data: Input data dictionary
        model_type: Model type identifier

    Returns:
        Prediction dictionary
    """
    return predict_extreme_behavior(features, input_data, model_type)
