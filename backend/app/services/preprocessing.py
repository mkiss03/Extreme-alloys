# backend/app/services/preprocessing.py
# UPDATED: Robust input validation with detailed error messages and auto-normalization
"""
Data preprocessing and feature engineering for alloy composition analysis
"""

import numpy as np
from typing import Dict, List, Tuple
from app.config import logger


def parse_composition(composition_str: str) -> Dict[str, float]:
    """
    Parse composition string into element percentages with robust error handling

    Args:
        composition_str: String like "Ni:55,Cr:20,Mo:10,W:12,Co:3"

    Returns:
        Dictionary mapping element symbols to percentages

    Raises:
        ValueError: If composition format is invalid
    """
    composition = {}

    if not composition_str or not isinstance(composition_str, str):
        raise ValueError("Composition must be a non-empty string")

    try:
        for pair in composition_str.split(","):
            pair = pair.strip()
            if not pair:
                continue

            if ":" not in pair:
                raise ValueError(f"Invalid format in '{pair}'. Expected 'Element:Percentage'")

            element, percentage = pair.split(":", 1)
            element = element.strip()
            percentage_str = percentage.strip()

            # Validate element symbol (basic check)
            if not element or not element[0].isupper():
                raise ValueError(f"Invalid element symbol: '{element}'")

            # Parse percentage
            try:
                pct = float(percentage_str)
            except ValueError:
                raise ValueError(f"Invalid percentage value '{percentage_str}' for element {element}")

            # Range check
            if pct < 0 or pct > 100:
                raise ValueError(f"Percentage for {element} must be between 0 and 100, got {pct}")

            composition[element] = pct

    except Exception as e:
        raise ValueError(f"Failed to parse composition '{composition_str}': {str(e)}")

    if not composition:
        raise ValueError("Composition cannot be empty")

    return composition


def validate_and_normalize_composition(composition: Dict[str, float]) -> Dict[str, float]:
    """
    Validate composition percentages sum to ~100 and normalize if needed

    Args:
        composition: Dictionary of element -> percentage

    Returns:
        Normalized composition dictionary

    Raises:
        ValueError: If composition is invalid
    """
    total = sum(composition.values())

    # Check if total is reasonable
    if total < 50.0:
        raise ValueError(
            f"Total composition is only {total:.1f}%. This is unusually low. "
            "Please check your input."
        )

    if total > 150.0:
        raise ValueError(
            f"Total composition is {total:.1f}%. This exceeds reasonable limits. "
            "Percentages should sum to approximately 100%."
        )

    # If total is close to 100, it's fine
    if 99.0 <= total <= 101.0:
        return composition

    # Auto-normalize if within reasonable range
    if 90.0 <= total <= 110.0:
        logger.warning(
            f"Composition totals {total:.1f}%, auto-normalizing to 100%"
        )
        normalized = {elem: (pct / total) * 100.0 for elem, pct in composition.items()}
        return normalized

    # Otherwise, it's an error
    raise ValueError(
        f"Composition percentages sum to {total:.1f}%, which is outside acceptable range (90-110%). "
        "Please check your input values."
    )


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

    Raises:
        ValueError: If input data is invalid
    """
    logger.info(f"Processing input: {input_data}")

    # Parse composition string
    composition = parse_composition(input_data["composition"])

    # Validate and normalize composition
    composition = validate_and_normalize_composition(composition)

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
    Validate input data format and ranges with comprehensive checks

    Returns:
        (is_valid, error_message)
    """
    required_fields = ["composition", "temperature_c", "pressure_mpa", "cycles"]

    # Check required fields
    for field in required_fields:
        if field not in input_data:
            return False, f"Missing required field: {field}"

    # Validate temperature range (realistic for metallurgy)
    temp = input_data["temperature_c"]
    if not isinstance(temp, (int, float)):
        return False, f"Temperature must be a number, got {type(temp).__name__}"

    if temp < -273:
        return False, f"Temperature cannot be below absolute zero: {temp}°C"

    if temp < 0:
        return False, f"Temperature must be positive for this application: {temp}°C"

    if temp > 2000:
        return False, f"Temperature {temp}°C exceeds typical alloy operating range (max ~2000°C)"

    # Validate pressure
    pressure = input_data["pressure_mpa"]
    if not isinstance(pressure, (int, float)):
        return False, f"Pressure must be a number, got {type(pressure).__name__}"

    if pressure < 0:
        return False, f"Pressure cannot be negative: {pressure} MPa"

    if pressure > 1000:
        return False, f"Pressure {pressure} MPa is unusually high (typical max ~1000 MPa)"

    # Validate cycles
    cycles = input_data["cycles"]
    if not isinstance(cycles, int):
        return False, f"Cycles must be an integer, got {type(cycles).__name__}"

    if cycles < 0:
        return False, f"Cycles cannot be negative: {cycles}"

    if cycles > 10000000:
        return False, f"Cycles {cycles} is unrealistically high (max ~10M)"

    # Validate composition format
    try:
        composition = parse_composition(input_data["composition"])
        validate_and_normalize_composition(composition)
    except ValueError as e:
        return False, str(e)

    return True, ""
