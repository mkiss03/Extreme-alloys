"""
Mechanical Engineering Module for Extreme Alloys
Realistic physics-based calculations for material behavior under extreme conditions

This module implements simplified but physically-grounded models for:
- Linear elasticity
- Creep prediction (time-dependent deformation)
- Temperature-dependent safety factors
- Stress limit estimation
"""

import math
from typing import Dict, Any
from app.config import logger

# ============================================================================
# Physical Constants
# ============================================================================

# Gas constant (J/mol·K)
R_GAS = 8.314

# Young's modulus baseline for Ni-based superalloys (GPa)
YOUNGS_MODULUS_BASE = 200.0  # GPa

# Activation energy for creep in Ni-based alloys (kJ/mol)
Q_CREEP = 300.0  # kJ/mol

# Material strength baseline (MPa)
BASE_STRENGTH = 600.0  # MPa for Ni-based superalloys at room temp


# ============================================================================
# Linear Elasticity
# ============================================================================

def calculate_stress_from_strain(strain: float, temperature_k: float) -> float:
    """
    Calculate stress from strain using Hooke's Law with temperature correction
    σ = E * ε

    Args:
        strain: Engineering strain (dimensionless, typically 0.001 - 0.05)
        temperature_k: Temperature in Kelvin

    Returns:
        Stress in MPa
    """
    # Temperature correction: E decreases with temperature
    # E(T) = E₀ * (1 - 0.0005 * (T - 298))
    temp_factor = 1.0 - 0.0005 * (temperature_k - 298.0)
    temp_factor = max(0.3, temp_factor)  # Don't go below 30% of original

    E_temp = YOUNGS_MODULUS_BASE * temp_factor  # GPa
    stress_gpa = E_temp * strain
    stress_mpa = stress_gpa * 1000.0  # Convert GPa to MPa

    logger.debug(f"Stress calculation: ε={strain}, T={temperature_k}K, σ={stress_mpa:.2f} MPa")
    return stress_mpa


# ============================================================================
# Creep Prediction
# ============================================================================

def predict_creep_lifetime(
    temperature_k: float,
    stress_mpa: float,
    time_hours: float = 10000.0
) -> float:
    """
    Predict creep lifetime using simplified Arrhenius-type equation

    Creep rate: ε̇ = A * exp(-Q / (R*T)) * σⁿ
    Lifetime: t_f ≈ ε_f / ε̇

    Args:
        temperature_k: Temperature in Kelvin
        stress_mpa: Applied stress in MPa
        time_hours: Reference time period in hours

    Returns:
        Estimated creep lifetime in hours
    """
    # Pre-exponential factor (1/hour)
    A = 1e-15  # Calibrated for Ni-based superalloys

    # Stress exponent (Norton exponent)
    n = 5.0

    # Convert activation energy to J/mol
    Q_joules = Q_CREEP * 1000.0

    # Arrhenius term
    arrhenius = math.exp(-Q_joules / (R_GAS * temperature_k))

    # Stress term (normalized to 100 MPa)
    stress_normalized = stress_mpa / 100.0
    stress_term = math.pow(stress_normalized, n)

    # Creep rate (1/hour)
    creep_rate = A * arrhenius * stress_term

    # Typical failure strain for superalloys
    epsilon_failure = 0.02  # 2% strain

    # Lifetime = failure strain / creep rate
    if creep_rate > 1e-20:
        lifetime = epsilon_failure / creep_rate
    else:
        lifetime = 1e8  # Very long lifetime if creep rate is negligible

    # Cap at reasonable values
    lifetime = min(lifetime, 1e6)  # Max 1 million hours
    lifetime = max(lifetime, 10.0)  # Min 10 hours

    logger.debug(f"Creep prediction: T={temperature_k}K, σ={stress_mpa} MPa → lifetime={lifetime:.2f} h")
    return lifetime


# ============================================================================
# Temperature-Dependent Safety Factor
# ============================================================================

def calculate_safety_factor(temperature_k: float) -> float:
    """
    Calculate temperature-dependent safety factor

    Safety factor decreases as temperature increases:
    SF = 1 - (T / (T + T_ref))

    Where T_ref is chosen to give realistic behavior:
    - At room temp (298K): SF ≈ 0.73
    - At 800K: SF ≈ 0.50
    - At 1200K: SF ≈ 0.40

    Args:
        temperature_k: Temperature in Kelvin

    Returns:
        Safety factor (0 to 1)
    """
    T_ref = 800.0  # Reference temperature

    safety_factor = 1.0 - (temperature_k / (temperature_k + T_ref))

    # Ensure it stays in reasonable bounds
    safety_factor = max(0.2, min(0.9, safety_factor))

    logger.debug(f"Safety factor at T={temperature_k}K: {safety_factor:.3f}")
    return safety_factor


# ============================================================================
# Stress Limit Estimation
# ============================================================================

def estimate_stress_limit(
    temperature_k: float,
    composition: Dict[str, float],
    pressure_mpa: float
) -> float:
    """
    Estimate allowable stress limit based on temperature and composition

    stress_limit = base_strength * safety_factor * composition_factor * pressure_factor

    Args:
        temperature_k: Temperature in Kelvin
        composition: Element composition dict (e.g., {"Ni": 55, "Cr": 20, ...})
        pressure_mpa: Applied pressure in MPa

    Returns:
        Stress limit in MPa
    """
    # Temperature effect via safety factor
    sf = calculate_safety_factor(temperature_k)

    # Composition strengthening factor
    comp_factor = calculate_composition_factor(composition)

    # Pressure effect (high pressure slightly increases allowable stress)
    pressure_factor = 1.0 + 0.0001 * pressure_mpa
    pressure_factor = min(pressure_factor, 1.2)  # Cap at 20% increase

    # Calculate stress limit
    stress_limit = BASE_STRENGTH * sf * comp_factor * pressure_factor

    logger.debug(f"Stress limit: {stress_limit:.2f} MPa (T={temperature_k}K, P={pressure_mpa} MPa)")
    return stress_limit


def calculate_composition_factor(composition: Dict[str, float]) -> float:
    """
    Calculate strengthening factor based on alloying elements

    Different elements contribute differently to strength:
    - Ni: baseline (1.0)
    - Cr: moderate strengthening (1.1)
    - Mo, W: strong strengthening (1.3)
    - Co: slight strengthening (1.05)
    - Al, Ti: precipitation strengthening (1.4)

    Args:
        composition: Element composition dict with percentages

    Returns:
        Composition factor (typically 0.8 - 1.3)
    """
    # Strengthening coefficients
    coefficients = {
        "Ni": 1.00,
        "Cr": 1.10,
        "Mo": 1.30,
        "W": 1.30,
        "Co": 1.05,
        "Al": 1.40,
        "Ti": 1.40,
        "Ta": 1.35,
        "Nb": 1.35,
        "Re": 1.50,
    }

    # Weighted average
    total_weight = 0.0
    total_percentage = 0.0

    for element, percentage in composition.items():
        coeff = coefficients.get(element, 1.0)  # Default to 1.0 if unknown
        total_weight += coeff * percentage
        total_percentage += percentage

    if total_percentage > 0:
        comp_factor = total_weight / total_percentage
    else:
        comp_factor = 1.0

    # Normalize to reasonable range
    comp_factor = max(0.8, min(1.3, comp_factor))

    logger.debug(f"Composition factor: {comp_factor:.3f}")
    return comp_factor


# ============================================================================
# Failure Probability Estimation
# ============================================================================

def estimate_failure_probability(
    temperature_k: float,
    stress_mpa: float,
    stress_limit_mpa: float,
    cycles: int
) -> float:
    """
    Estimate failure probability based on stress ratio and thermal cycling

    P_fail = base_prob * stress_ratio^2 * cycle_factor

    Args:
        temperature_k: Operating temperature in Kelvin
        stress_mpa: Applied stress in MPa
        stress_limit_mpa: Material stress limit in MPa
        cycles: Number of thermal cycles

    Returns:
        Failure probability (0 to 1)
    """
    # Stress ratio
    if stress_limit_mpa > 0:
        stress_ratio = stress_mpa / stress_limit_mpa
    else:
        stress_ratio = 1.0

    # Base probability increases with stress ratio
    base_prob = 0.1  # 10% baseline
    stress_effect = math.pow(stress_ratio, 2.0)

    # Thermal cycling effect (fatigue)
    # More cycles → higher failure probability
    cycle_factor = 1.0 + math.log10(max(1, cycles)) * 0.05

    # Temperature effect
    # Higher temperature → higher failure probability
    temp_effect = 1.0 + (temperature_k - 298.0) / 1000.0
    temp_effect = max(1.0, temp_effect)

    # Combined failure probability
    failure_prob = base_prob * stress_effect * cycle_factor * temp_effect

    # Cap at reasonable bounds
    failure_prob = max(0.01, min(0.95, failure_prob))

    logger.debug(f"Failure probability: {failure_prob:.3f} (stress_ratio={stress_ratio:.2f})")
    return failure_prob


# ============================================================================
# Complete Mechanical Analysis
# ============================================================================

def analyze_material_behavior(
    temperature_c: float,
    pressure_mpa: float,
    composition: Dict[str, float],
    cycles: int,
    applied_stress: float = None
) -> Dict[str, Any]:
    """
    Perform complete mechanical analysis of material behavior

    Args:
        temperature_c: Temperature in Celsius
        pressure_mpa: Pressure in MPa
        composition: Element composition dict
        cycles: Number of thermal cycles
        applied_stress: Optional applied stress (MPa), otherwise estimated

    Returns:
        Dictionary with mechanical analysis results
    """
    # Convert temperature to Kelvin
    temperature_k = temperature_c + 273.15

    # Estimate stress limit
    stress_limit = estimate_stress_limit(temperature_k, composition, pressure_mpa)

    # Estimate applied stress if not provided
    if applied_stress is None:
        # Assume operating at ~60% of stress limit
        applied_stress = stress_limit * 0.6

    # Predict creep lifetime
    creep_lifetime = predict_creep_lifetime(temperature_k, applied_stress)

    # Estimate failure probability
    failure_prob = estimate_failure_probability(
        temperature_k, applied_stress, stress_limit, cycles
    )

    # Safety factor
    safety_factor = calculate_safety_factor(temperature_k)

    return {
        "creep_lifetime_hours": creep_lifetime,
        "stress_limit_mpa": stress_limit,
        "failure_probability": failure_prob,
        "safety_factor": safety_factor,
        "applied_stress_mpa": applied_stress,
        "temperature_k": temperature_k,
        "mechanics_metadata": {
            "composition_factor": calculate_composition_factor(composition),
            "stress_ratio": applied_stress / stress_limit if stress_limit > 0 else 0,
            "thermal_cycles": cycles,
        }
    }
