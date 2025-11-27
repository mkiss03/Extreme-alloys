# backend/app/services/preprocessing.py
"""
Data preprocessing and feature engineering for alloy composition analysis
"""

import numpy as np
from typing import Dict, List, Tuple
from app.config import logger


def parse_composition(composition_str: str) -> Dict[str, float]:
    """
    Parse composition string into element percentages

    Args:
        composition_str: String like "Ni:55,Cr:20,Mo:10,W:12,Co:3"

    Returns:
        Dictionary mapping element symbols to percentages
    """
    composition = {}

    for pair in composition_str.split(","):
        element, percentage = pair.strip().split(":")
        composition[element.strip()] = float(percentage)

    return composition


def prepare_features(input_data: Dict) -> np.ndarray:
    """
    Convert input data into normalized feature vector for ML model

    Expected input format:
    {
        "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
        "temperature_c": 850.0,
        "pressure_mpa": 150.0,
        "cycles": 10000
    }

    Returns:
        Normalized numpy array: [Ni%, Cr%, Mo%, W%, Co%, temp_K, pressure, cycles]
    """
    logger.info(f"Processing input: {input_data}")

    # Parse composition string
    composition = parse_composition(input_data["composition"])

    # Define element order (fixed for consistent feature vector)
    element_order = ["Ni", "Cr", "Mo", "W", "Co"]

    # Extract element percentages (default to 0 if not present)
    element_percentages = [composition.get(elem, 0.0) for elem in element_order]

    # Convert temperature from Celsius to Kelvin
    temperature_k = input_data["temperature_c"] + 273.15

    # Extract other features
    pressure_mpa = float(input_data["pressure_mpa"])
    cycles = int(input_data["cycles"])

    # Build feature vector
    features = element_percentages + [temperature_k, pressure_mpa, cycles]

    # Convert to numpy array
    feature_array = np.array(features, dtype=np.float32)

    # Apply normalization
    # Element percentages: already in 0-100 range, divide by 100
    feature_array[:5] = feature_array[:5] / 100.0

    # Temperature: normalize to typical range (300K - 1500K)
    feature_array[5] = feature_array[5] / 1500.0

    # Pressure: normalize to typical range (0 - 500 MPa)
    feature_array[6] = feature_array[6] / 500.0

    # Cycles: normalize to log scale (typical range: 1 - 1e6)
    feature_array[7] = np.log10(max(feature_array[7], 1)) / 6.0

    logger.info(f"Generated feature vector: {feature_array}")

    return feature_array


def validate_input(input_data: Dict) -> Tuple[bool, str]:
    """
    Validate input data format and ranges

    Returns:
        (is_valid, error_message)
    """
    required_fields = ["composition", "temperature_c", "pressure_mpa", "cycles"]

    # Check required fields
    for field in required_fields:
        if field not in input_data:
            return False, f"Missing required field: {field}"

    # Validate temperature range (reasonable for metallurgy)
    temp = input_data["temperature_c"]
    if not (-273 < temp < 3000):
        return False, f"Temperature out of valid range: {temp}°C"

    # Validate pressure
    pressure = input_data["pressure_mpa"]
    if pressure < 0:
        return False, f"Pressure must be positive: {pressure} MPa"

    # Validate cycles
    cycles = input_data["cycles"]
    if cycles < 0:
        return False, f"Cycles must be non-negative: {cycles}"

    # Validate composition format
    try:
        composition = parse_composition(input_data["composition"])
        total = sum(composition.values())
        if not (99.0 <= total <= 101.0):  # Allow small rounding errors
            return False, f"Composition percentages should sum to ~100, got {total}"
    except Exception as e:
        return False, f"Invalid composition format: {str(e)}"

    return True, ""
