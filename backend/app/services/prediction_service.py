# backend/app/services/prediction_service.py
"""
Prediction service for extreme alloy behavior modeling
"""

import os
import numpy as np
import torch
from typing import Dict, Optional
from app.config import logger, MODEL_PATH
from app.models.gnn_model import GNNModel
from app.models.creep_model import CreepModel

# Global model cache
_model_cache = {}


def load_model_cached(model_type: str = "gnn") -> Optional[torch.nn.Module]:
    """
    Load model from disk with caching

    Args:
        model_type: Type of model to load ('gnn' or 'creep')

    Returns:
        Loaded model or None if model file doesn't exist
    """
    if model_type in _model_cache:
        logger.info(f"Using cached {model_type} model")
        return _model_cache[model_type]

    # Determine model path
    model_filename = f"extreme_alloy_{model_type}.pth"
    model_path = os.path.join(MODEL_PATH, model_filename)

    if not os.path.exists(model_path):
        logger.warning(f"Model file not found: {model_path}")
        return None

    try:
        # Load appropriate model
        if model_type == "gnn":
            model = GNNModel(input_dim=8, hidden_dim=64, output_dim=3)
            model.load_model(model_path)
        elif model_type == "creep":
            model = CreepModel(input_dim=8, hidden_dims=[128, 64, 32])
            model.load_model(model_path)
        else:
            logger.error(f"Unknown model type: {model_type}")
            return None

        model.eval()
        _model_cache[model_type] = model
        logger.info(f"Successfully loaded {model_type} model from {model_path}")
        return model

    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        return None


def predict_with_ml_model(features: np.ndarray, model_type: str = "gnn") -> Optional[Dict]:
    """
    Make predictions using actual ML model

    Args:
        features: Normalized feature vector
        model_type: Type of model to use

    Returns:
        Prediction dictionary or None if model not available
    """
    model = load_model_cached(model_type)

    if model is None:
        return None

    try:
        # Convert to torch tensor
        features_tensor = torch.from_numpy(features).float().unsqueeze(0)

        # Make prediction
        with torch.no_grad():
            if model_type == "gnn":
                output = model(features_tensor)
                prediction = {
                    "creep_lifetime_hours": float(output[0, 0].item()),
                    "failure_probability": float(torch.sigmoid(output[0, 1]).item()),
                    "stress_limit_mpa": float(output[0, 2].item()),
                    "model_version": f"{model_type}_v1.0",
                    "confidence": 0.85
                }
            elif model_type == "creep":
                lifetime = model.predict_creep_lifetime(features)
                prediction = {
                    "creep_lifetime_hours": float(lifetime),
                    "failure_probability": 0.5,  # Creep model doesn't predict this
                    "stress_limit_mpa": 650.0,   # Default value
                    "model_version": f"{model_type}_v1.0",
                    "confidence": 0.80
                }

        logger.info(f"ML model prediction: {prediction}")
        return prediction

    except Exception as e:
        logger.error(f"Error during model inference: {str(e)}")
        return None


def predict_extreme_behavior(features: np.ndarray) -> Dict:
    """
    Predict alloy behavior under extreme conditions

    First tries to use ML model, falls back to physics-based heuristics if unavailable

    Args:
        features: Normalized feature vector from preprocessing

    Returns:
        Dictionary with prediction results:
        - creep_lifetime_hours: predicted lifetime in hours
        - failure_probability: probability of failure (0-1)
        - stress_limit_mpa: recommended max stress
    """
    logger.info(f"Generating predictions for features: {features}")

    # Try to use ML model first
    ml_prediction = predict_with_ml_model(features, model_type="gnn")

    if ml_prediction is not None:
        return ml_prediction

    # Fallback: Physics-based heuristic predictions
    logger.info("Using fallback physics-based predictions")

    # Simulate some basic logic based on features
    # Higher temperature and pressure reduce lifetime
    temp_factor = 1.0 - features[5]  # normalized temp
    pressure_factor = 1.0 - features[6]  # normalized pressure
    cycle_factor = 1.0 - features[7]  # normalized cycles

    # Element composition effects (Ni and Cr improve properties)
    ni_factor = features[0]  # Ni percentage (normalized)
    cr_factor = features[1]  # Cr percentage (normalized)
    composition_factor = (ni_factor + cr_factor) / 2

    # Lifetime calculation (in hours)
    base_lifetime = 5000.0
    creep_lifetime = base_lifetime * temp_factor * pressure_factor * cycle_factor * composition_factor
    creep_lifetime = max(100.0, creep_lifetime)

    # Failure probability
    failure_prob = 1.0 - (temp_factor * pressure_factor * composition_factor)
    failure_prob = np.clip(failure_prob, 0.0, 1.0)

    # Stress limit (Cr content helps)
    stress_limit = 800.0 * temp_factor * pressure_factor * (0.5 + cr_factor * 0.5)

    prediction = {
        "creep_lifetime_hours": float(creep_lifetime),
        "failure_probability": float(failure_prob),
        "stress_limit_mpa": float(stress_limit),
        "model_version": "physics_heuristic_v0.1",
        "confidence": 0.5
    }

    logger.info(f"Prediction results: {prediction}")

    return prediction


def predict_with_model(features: np.ndarray, model_type: str = "gnn") -> Dict:
    """
    Make predictions using specified model type

    Args:
        features: Input feature vector
        model_type: Type of model to use ('gnn', 'creep', 'ensemble')

    Returns:
        Prediction dictionary
    """
    logger.info(f"Using model type: {model_type}")

    if model_type == "ensemble":
        # Ensemble: combine GNN and Creep models
        gnn_pred = predict_with_ml_model(features, "gnn")
        creep_pred = predict_with_ml_model(features, "creep")

        if gnn_pred and creep_pred:
            # Average lifetime predictions
            ensemble_lifetime = (gnn_pred["creep_lifetime_hours"] +
                               creep_pred["creep_lifetime_hours"]) / 2

            return {
                "creep_lifetime_hours": ensemble_lifetime,
                "failure_probability": gnn_pred["failure_probability"],
                "stress_limit_mpa": gnn_pred["stress_limit_mpa"],
                "model_version": "ensemble_v1.0",
                "confidence": 0.90
            }

    # Try specific model type
    ml_pred = predict_with_ml_model(features, model_type)

    if ml_pred:
        return ml_pred

    # Fallback to physics-based prediction
    return predict_extreme_behavior(features)
