"""
Model Selector Module
Routes prediction requests to appropriate model implementation
"""

from typing import Dict, Any, Callable
from app.config import logger
from app.models.model_loader import get_model_info


# ============================================================================
# Model Selection Logic
# ============================================================================

def select_model(model_type: str) -> Dict[str, Any]:
    """
    Select and validate model based on type
    
    Args:
        model_type: Model identifier ("gnn", "physics_heuristic", "safety_conservative")
        
    Returns:
        Dictionary with model information and configuration
        
    Raises:
        ValueError: If model_type is not supported
    """
    # Normalize model type
    model_type = model_type.lower().strip()
    
    # Get model info from registry
    model_info = get_model_info(model_type)
    
    if model_info is None:
        available_models = ["gnn", "physics_heuristic", "safety_conservative"]
        raise ValueError(
            f"Unsupported model type: '{model_type}'. "
            f"Available models: {', '.join(available_models)}"
        )
    
    logger.info(f"Selected model: {model_type} (strategy: {model_info['strategy']})")
    
    return {
        "type": model_type,
        "info": model_info,
        "confidence": model_info["confidence"],
        "strategy": model_info["strategy"]
    }


def get_available_models() -> list:
    """
    Get list of all available models with metadata
    
    Returns:
        List of dictionaries containing model information
    """
    from app.models.model_loader import MODEL_REGISTRY
    
    models = []
    for model_type, info in MODEL_REGISTRY.items():
        models.append({
            "name": model_type,
            "confidence": info["confidence"],
            "strategy": info["strategy"],
            "description": _get_model_description(model_type)
        })
    
    return models


def _get_model_description(model_type: str) -> str:
    """Get human-readable description for model type"""
    descriptions = {
        "gnn": "Graph Neural Network trained on alloy performance data. "
               "Data-driven approach with 75% confidence.",
        
        "physics_heuristic": "Physics-based model using Arrhenius equations, "
                            "creep mechanics, and material science principles. "
                            "Analytical approach with 65% confidence.",
        
        "safety_conservative": "Ultra-conservative model applying 2x safety factors "
                              "to physics predictions. Best for critical applications. "
                              "90% confidence due to conservative margins."
    }
    return descriptions.get(model_type, "No description available")
