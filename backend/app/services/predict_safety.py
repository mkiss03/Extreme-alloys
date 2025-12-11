"""
Safety-Conservative Prediction Module
Handles predictions with conservative safety margins
"""

from typing import Dict, Any
import numpy as np
from app.config import logger
from app.models.model_loader import load_safety_model
from app.services.mechanics import analyze_material_behavior


# ============================================================================
# Conservative Safety Factors
# ============================================================================

# Apply 2x safety margins for ultra-conservative predictions
SAFETY_FACTOR_LIFETIME = 0.5   # Divide lifetime by 2
SAFETY_MARGIN_FAILURE = 0.15   # Add 15% to failure probability
SAFETY_FACTOR_STRESS = 0.8     # Reduce stress limit by 20%


# ============================================================================
# Safety-Conservative Prediction
# ============================================================================

def predict_with_safety(input_data: Dict[str, Any], features: np.ndarray) -> Dict[str, Any]:
    """
    Make prediction using safety-conservative model
    
    This model applies conservative safety factors to physics predictions:
    - Lifetime: Reduced by 50% (2x safety factor)
    - Failure probability: Increased by +15%
    - Stress limit: Reduced by 20%
    
    Best for critical applications where safety is paramount
    
    Args:
        input_data: Original input data
        features: Preprocessed feature array (not used)
        
    Returns:
        Prediction dictionary with conservative estimates
    """
    logger.info("Running safety-conservative prediction...")
    
    # Load model info
    model_info = load_safety_model()
    
    # Get base physics predictions
    mechanics_result = analyze_material_behavior(
        temperature_c=input_data["temperature_c"],
        pressure_mpa=input_data["pressure_mpa"],
        composition=input_data["composition_dict"],
        cycles=input_data["cycles"]
    )
    
    # Apply conservative safety factors
    conservative_lifetime = mechanics_result["creep_lifetime_hours"] * SAFETY_FACTOR_LIFETIME
    conservative_failure_prob = min(0.95, mechanics_result["failure_probability"] + SAFETY_MARGIN_FAILURE)
    conservative_stress_limit = mechanics_result["stress_limit_mpa"] * SAFETY_FACTOR_STRESS
    
    prediction = {
        "creep_lifetime_hours": conservative_lifetime,
        "failure_probability": conservative_failure_prob,
        "stress_limit_mpa": conservative_stress_limit,
        
        # Metadata
        "model_type": "safety_conservative",
        "model_strategy": "conservative_safety",
        "model_version": model_info["version"],
        "model_confidence": 0.90,  # High confidence due to conservative margins
        
        # Safety factors applied
        "safety_factors": {
            "lifetime_factor": SAFETY_FACTOR_LIFETIME,
            "failure_margin": SAFETY_MARGIN_FAILURE,
            "stress_factor": SAFETY_FACTOR_STRESS,
            "description": "Conservative 2x safety margins applied",
            "base_lifetime_hours": mechanics_result["creep_lifetime_hours"],
            "base_failure_probability": mechanics_result["failure_probability"],
            "base_stress_limit_mpa": mechanics_result["stress_limit_mpa"]
        },
        
        # Include physics metadata
        "physics_metadata": {
            "temperature_k": mechanics_result["temperature_k"],
            "safety_factor": mechanics_result["safety_factor"],
            "applied_stress_mpa": mechanics_result["applied_stress_mpa"],
        }
    }
    
    logger.info(f"Safety prediction complete: conservative lifetime={prediction['creep_lifetime_hours']:.2f}h")
    return prediction
