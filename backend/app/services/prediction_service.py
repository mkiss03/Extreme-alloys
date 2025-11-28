# backend/app/services/prediction_service.py
# UPDATED: Three distinct model types with physics-based calculations
"""
Prediction service with multiple model strategies:
- GNN (Graph Neural Network) - data-driven default
- Physics Heuristic - physics-inspired calculations
- Safety Conservative - most cautious predictions
"""

import os
import numpy as np
import torch
from typing import Dict, Optional
from app.config import logger, MODEL_PATH
from app.models.gnn_model import GNNModel
from app.models.creep_model import CreepModel
from app.services.physics import physics_based_lifetime_estimate
from app.services.preprocessing import parse_composition

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


def predict_gnn_model(features: np.ndarray, input_data: Dict) -> Dict:
    """
    Graph Neural Network prediction (data-driven, default model)

    This is the baseline model using simple heuristics
    In production, this would use a trained neural network

    Args:
        features: Normalized feature vector
        input_data: Original input dictionary

    Returns:
        Prediction dictionary with model metadata
    """
    logger.info("Using GNN (Graph Neural Network) model")

    # Extract composition for strength calculation
    composition = parse_composition(input_data["composition"])
    ni_pct = composition.get("Ni", 0)
    cr_pct = composition.get("Cr", 0)
    mo_pct = composition.get("Mo", 0)

    # Feature-based calculation (baseline model)
    temp_factor = 1.0 - features[5]  # Lower temp = better
    pressure_factor = 1.0 - features[6]  # Lower pressure = better
    cycle_factor = 1.0 - features[7]  # Fewer cycles = better

    # Composition effect (Ni and Cr improve properties)
    composition_factor = (ni_pct / 100.0 + cr_pct / 100.0) / 2.0

    # Lifetime calculation
    base_lifetime = 5000.0
    creep_lifetime = base_lifetime * temp_factor * pressure_factor * cycle_factor * composition_factor
    creep_lifetime = max(100.0, creep_lifetime)

    # Failure probability
    failure_prob = 1.0 - (temp_factor * pressure_factor * composition_factor)
    failure_prob = np.clip(failure_prob, 0.0, 1.0)

    # Stress limit (Cr helps)
    stress_limit = 800.0 * temp_factor * pressure_factor * (0.5 + (cr_pct / 100.0) * 0.5)

    return {
        "creep_lifetime_hours": float(creep_lifetime),
        "failure_probability": float(failure_prob),
        "stress_limit_mpa": float(stress_limit),
        "model_type": "gnn",
        "model_strategy": "data_driven",
        "model_version": "gnn_demo_v0.1",
        "model_confidence": 0.75
    }


def predict_physics_heuristic(features: np.ndarray, input_data: Dict) -> Dict:
    """
    Physics-inspired heuristic model

    Uses fundamental materials science equations for predictions
    More conservative than GNN, incorporates Arrhenius behavior

    Args:
        features: Normalized feature vector
        input_data: Original input dictionary

    Returns:
        Prediction dictionary with physics metadata
    """
    logger.info("Using Physics Heuristic model")

    # Extract composition
    composition = parse_composition(input_data["composition"])
    ni_pct = composition.get("Ni", 0)
    cr_pct = composition.get("Cr", 0)
    mo_pct = composition.get("Mo", 0)

    # Use physics-based calculation
    physics_result = physics_based_lifetime_estimate(
        temperature_c=input_data["temperature_c"],
        pressure_mpa=input_data["pressure_mpa"],
        cycles=input_data["cycles"],
        ni_percent=ni_pct,
        cr_percent=cr_pct,
        mo_percent=mo_pct
    )

    # Apply physics heuristic adjustments (slightly more conservative)
    creep_lifetime = physics_result["lifetime_hours"] * 0.85
    failure_prob = min(1.0, physics_result["failure_probability"] + 0.05)
    stress_limit = physics_result["stress_limit_mpa"] * 0.9

    return {
        "creep_lifetime_hours": float(creep_lifetime),
        "failure_probability": float(failure_prob),
        "stress_limit_mpa": float(stress_limit),
        "model_type": "physics_heuristic",
        "model_strategy": "physics_inspired",
        "model_version": "physics_heuristic_v0.1",
        "model_confidence": 0.65,
        "physics_metadata": physics_result.get("physics_metadata", {})
    }


def predict_safety_conservative(features: np.ndarray, input_data: Dict) -> Dict:
    """
    Safety-conservative model (most cautious predictions)

    Provides worst-case estimates for critical applications
    Reduces lifetime and stress, increases failure probability

    Args:
        features: Normalized feature vector
        input_data: Original input dictionary

    Returns:
        Prediction dictionary with safety metadata
    """
    logger.info("Using Safety-Conservative model")

    # Start with physics-based baseline
    composition = parse_composition(input_data["composition"])
    ni_pct = composition.get("Ni", 0)
    cr_pct = composition.get("Cr", 0)
    mo_pct = composition.get("Mo", 0)

    physics_result = physics_based_lifetime_estimate(
        temperature_c=input_data["temperature_c"],
        pressure_mpa=input_data["pressure_mpa"],
        cycles=input_data["cycles"],
        ni_percent=ni_pct,
        cr_percent=cr_pct,
        mo_percent=mo_pct
    )

    # Apply conservative safety factors
    SAFETY_FACTOR_LIFETIME = 0.6  # Reduce lifetime by 40%
    SAFETY_MARGIN_FAILURE = 0.15  # Add 15% to failure probability
    SAFETY_FACTOR_STRESS = 0.8  # Reduce allowable stress by 20%

    creep_lifetime = physics_result["lifetime_hours"] * SAFETY_FACTOR_LIFETIME
    failure_prob = min(1.0, physics_result["failure_probability"] + SAFETY_MARGIN_FAILURE)
    stress_limit = physics_result["stress_limit_mpa"] * SAFETY_FACTOR_STRESS

    return {
        "creep_lifetime_hours": float(creep_lifetime),
        "failure_probability": float(failure_prob),
        "stress_limit_mpa": float(stress_limit),
        "model_type": "safety_conservative",
        "model_strategy": "safety_conservative",
        "model_version": "safety_v0.1",
        "model_confidence": 0.90,  # High confidence in conservative estimates
        "safety_factors": {
            "lifetime_factor": SAFETY_FACTOR_LIFETIME,
            "failure_margin": SAFETY_MARGIN_FAILURE,
            "stress_factor": SAFETY_FACTOR_STRESS
        }
    }


def predict_extreme_behavior(features: np.ndarray, input_data: Dict, model_type: str = "gnn") -> Dict:
    """
    Main prediction function - routes to appropriate model

    Args:
        features: Normalized feature vector from preprocessing
        input_data: Original input dictionary
        model_type: Model type ("gnn", "physics_heuristic", "safety_conservative")

    Returns:
        Prediction dictionary with model metadata
    """
    logger.info(f"Generating predictions with model_type: {model_type}")

    # Route to appropriate model
    if model_type == "physics_heuristic":
        return predict_physics_heuristic(features, input_data)
    elif model_type == "safety_conservative":
        return predict_safety_conservative(features, input_data)
    else:
        # Default to GNN
        return predict_gnn_model(features, input_data)


def predict_with_model(features: np.ndarray, input_data: Dict, model_type: str = "gnn") -> Dict:
    """
    Make predictions using specified model type

    This is the main entry point for predictions

    Args:
        features: Input feature vector
        input_data: Original input dictionary
        model_type: Type of model to use

    Returns:
        Prediction dictionary
    """
    logger.info(f"Prediction requested with model_type: {model_type}")

    # Validate model type
    valid_models = ["gnn", "physics_heuristic", "safety_conservative"]
    if model_type not in valid_models:
        logger.warning(f"Invalid model_type '{model_type}', defaulting to 'gnn'")
        model_type = "gnn"

    # Generate prediction
    prediction = predict_extreme_behavior(features, input_data, model_type)

    logger.info(f"Prediction complete: {prediction}")
    return prediction
