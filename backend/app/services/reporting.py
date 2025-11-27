# backend/app/services/reporting.py
"""
Reporting and visualization utilities for prediction results
"""

from typing import Dict, List
import json


def generate_report(prediction: Dict, input_data: Dict) -> Dict:
    """
    Generate comprehensive report from prediction results

    Args:
        prediction: Model prediction output
        input_data: Original input parameters

    Returns:
        Formatted report dictionary
    """
    report = {
        "input_parameters": input_data,
        "predictions": prediction,
        "recommendations": generate_recommendations(prediction),
        "metadata": {
            "report_version": "1.0",
            "analysis_type": "extreme_conditions"
        }
    }

    return report


def generate_recommendations(prediction: Dict) -> List[str]:
    """
    Generate actionable recommendations based on predictions
    """
    recommendations = []

    lifetime = prediction.get("creep_lifetime_hours", 0)
    failure_prob = prediction.get("failure_probability", 0)

    if lifetime < 1000:
        recommendations.append("⚠️ Low predicted lifetime - consider alternative alloy composition")

    if failure_prob > 0.7:
        recommendations.append("⚠️ High failure risk - reduce operating temperature or pressure")

    if failure_prob < 0.3:
        recommendations.append("✓ Good stability predicted under specified conditions")

    return recommendations
