"""
ML Model Loader Module
Handles loading and caching of machine learning models

This module is prepared for future integration of real ML models (.pth, .onnx, etc.)
Currently uses placeholder/dummy models for demonstration
"""

import numpy as np
import random
from functools import lru_cache
from typing import Dict, Any, Optional
from app.config import logger, MODEL_PATH
import os


# ============================================================================
# Model Loading with Caching
# ============================================================================

@lru_cache(maxsize=1)
def load_gnn_model() -> Dict[str, Any]:
    """
    Load GNN (Graph Neural Network) model for alloy prediction
    
    Uses @lru_cache to load model only once and cache it in memory
    This is a placeholder - when you have a real .pth or .onnx model,
    replace this implementation with actual model loading logic
    
    Returns:
        Dictionary containing model info and dummy predict function
    """
    logger.info("Loading GNN model...")
    
    # TODO: When real model is available, load it like this:
    # import torch
    # model_path = os.path.join(MODEL_PATH, "gnn_alloy_v1.pth")
    # model = torch.load(model_path)
    # model.eval()
    
    # For now, return dummy model info
    model_info = {
        "name": "gnn_placeholder",
        "version": "v2.0_demo",
        "type": "Graph Neural Network",
        "loaded": True,
        "description": "Placeholder GNN model - ready for real model integration"
    }
    
    logger.info(f"GNN model loaded: {model_info['version']}")
    return model_info


@lru_cache(maxsize=1)
def load_physics_model() -> Dict[str, Any]:
    """
    Load physics-based heuristic model
    
    This model uses the mechanics module for physics calculations
    No ML model needed - uses analytical formulas
    
    Returns:
        Dictionary containing model info
    """
    logger.info("Loading physics-based model...")
    
    model_info = {
        "name": "physics_heuristic",
        "version": "v2.0_mechanics",
        "type": "Physics-Based Analytical",
        "loaded": True,
        "description": "Uses real mechanics formulas (creep, stress, safety factors)"
    }
    
    logger.info(f"Physics model loaded: {model_info['version']}")
    return model_info


@lru_cache(maxsize=1)
def load_safety_model() -> Dict[str, Any]:
    """
    Load safety-conservative model
    
    This model applies conservative safety factors to physics predictions
    
    Returns:
        Dictionary containing model info
    """
    logger.info("Loading safety-conservative model...")
    
    model_info = {
        "name": "safety_conservative",
        "version": "v2.0_safe",
        "type": "Conservative Safety Model",
        "loaded": True,
        "description": "Applies 2x safety factors to physics predictions"
    }
    
    logger.info(f"Safety model loaded: {model_info['version']}")
    return model_info


# ============================================================================
# Model Prediction Functions
# ============================================================================

def gnn_predict(features: np.ndarray, base_values: Dict[str, float]) -> Dict[str, float]:
    """
    GNN model prediction with realistic randomization
    
    Args:
        features: Input features as numpy array
        base_values: Base prediction values from physics model
        
    Returns:
        Dictionary with predicted values (creep_lifetime, failure_probability, stress_limit)
    """
    # Add Gaussian noise to make predictions more realistic
    # GNN typically has ±5% variance
    
    creep_lifetime = base_values.get("creep_lifetime_hours", 5000.0)
    failure_prob = base_values.get("failure_probability", 0.5)
    stress_limit = base_values.get("stress_limit_mpa", 400.0)
    
    # Add random variation
    # Use random.gauss for normal distribution
    creep_lifetime_predicted = random.gauss(creep_lifetime, creep_lifetime * 0.05)
    failure_prob_predicted = random.gauss(failure_prob, 0.03)
    stress_limit_predicted = random.gauss(stress_limit, stress_limit * 0.04)
    
    # Ensure values stay in reasonable bounds
    creep_lifetime_predicted = max(100.0, creep_lifetime_predicted)
    failure_prob_predicted = max(0.01, min(0.95, failure_prob_predicted))
    stress_limit_predicted = max(50.0, stress_limit_predicted)
    
    logger.debug(f"GNN prediction: lifetime={creep_lifetime_predicted:.2f}h, "
                f"fail_prob={failure_prob_predicted:.3f}, "
                f"stress={stress_limit_predicted:.2f} MPa")
    
    return {
        "creep_lifetime_hours": creep_lifetime_predicted,
        "failure_probability": failure_prob_predicted,
        "stress_limit_mpa": stress_limit_predicted,
    }


# ============================================================================
# Model Registry
# ============================================================================

MODEL_REGISTRY = {
    "gnn": {
        "loader": load_gnn_model,
        "predictor": gnn_predict,
        "confidence": 0.75,
        "strategy": "data_driven_ml"
    },
    "physics_heuristic": {
        "loader": load_physics_model,
        "predictor": None,  # Uses mechanics module directly
        "confidence": 0.65,
        "strategy": "physics_based"
    },
    "safety_conservative": {
        "loader": load_safety_model,
        "predictor": None,  # Uses mechanics module with safety factors
        "confidence": 0.90,
        "strategy": "conservative_safety"
    }
}


def get_model_info(model_type: str) -> Optional[Dict[str, Any]]:
    """
    Get model information from registry
    
    Args:
        model_type: Model type identifier
        
    Returns:
        Model info dictionary or None if not found
    """
    if model_type not in MODEL_REGISTRY:
        logger.warning(f"Model type '{model_type}' not found in registry")
        return None
    
    return MODEL_REGISTRY[model_type]


def preload_all_models():
    """
    Preload all models at startup for faster first predictions
    This is useful for production deployments
    """
    logger.info("Preloading all models...")
    for model_type in MODEL_REGISTRY.keys():
        info = MODEL_REGISTRY[model_type]
        if info["loader"]:
            info["loader"]()  # This will cache the model via @lru_cache
    logger.info("All models preloaded successfully")
