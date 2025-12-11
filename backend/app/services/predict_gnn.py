"""
GNN Model Prediction Module
Handles predictions using Graph Neural Network model
"""

import numpy as np
from typing import Dict, Any
from app.config import logger
from app.models.model_loader import load_gnn_model, gnn_predict
from app.services.mechanics import analyze_material_behavior


# ============================================================================
# GNN Prediction
# ============================================================================

def predict_with_gnn(input_data: Dict[str, Any], features: np.ndarray) -> Dict[str, Any]:
    """
    Make prediction using GNN model
    
    Args:
        input_data: Original input data (temperature, pressure, composition, cycles)
        features: Preprocessed feature array
        
    Returns:
        Prediction dictionary with results and metadata
    """
    logger.info("Running GNN prediction...")
    
    # Load model (cached via @lru_cache)
    model_info = load_gnn_model()
    
    # Get base values from mechanics analysis
    mechanics_result = analyze_material_behavior(
        temperature_c=input_data["temperature_c"],
        pressure_mpa=input_data["pressure_mpa"],
        composition=input_data["composition_dict"],
        cycles=input_data["cycles"]
    )
    
    # Get GNN prediction with realistic randomization
    gnn_result = gnn_predict(features, mechanics_result)
    
    # Combine results
    prediction = {
        "creep_lifetime_hours": gnn_result["creep_lifetime_hours"],
        "failure_probability": gnn_result["failure_probability"],
        "stress_limit_mpa": gnn_result["stress_limit_mpa"],
        
        # Metadata
        "model_type": "gnn",
        "model_strategy": "data_driven_ml",
        "model_version": model_info["version"],
        "model_confidence": 0.75,
        
        # Additional info
        "ml_metadata": {
            "model_name": model_info["name"],
            "model_description": model_info["description"],
            "feature_vector_size": len(features),
            "prediction_method": "neural_network"
        }
    }
    
    logger.info(f"GNN prediction complete: lifetime={prediction['creep_lifetime_hours']:.2f}h")
    return prediction
