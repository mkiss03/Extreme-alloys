# backend/app/services/physics.py
# NEW FILE: Mini physics engine for materials science calculations
"""
Physics-based utility functions for creep and stress calculations
Based on fundamental materials science principles
"""

import math
import numpy as np


# Physical constants
R_GAS = 8.314  # Universal gas constant (J/mol·K)
Q_CREEP_NI = 300000  # Activation energy for Ni-based superalloys (J/mol) - approximate


def arrhenius_creep_factor(temperature_k: float, activation_energy: float = Q_CREEP_NI) -> float:
    """
    Calculate Arrhenius temperature dependence for creep rate

    Creep rate ∝ exp(-Q/RT)
    Higher temperature → exponentially faster creep → shorter lifetime

    Args:
        temperature_k: Temperature in Kelvin
        activation_energy: Activation energy for creep (J/mol)

    Returns:
        Creep factor (0-1), lower means slower creep (better)
    """
    try:
        exponent = -activation_energy / (R_GAS * temperature_k)
        # Normalize to 0-1 range for typical alloy temperatures (600-1200K)
        # At 800K, factor ≈ 1.8e-16, so we scale appropriately
        raw_factor = math.exp(exponent)
        # Scale to practical range
        normalized = min(1.0, raw_factor * 1e15)
        return normalized
    except (OverflowError, ZeroDivisionError):
        return 1.0  # Worst case


def larson_miller_parameter(temperature_k: float, lifetime_hours: float, C: float = 20) -> float:
    """
    Larson-Miller Parameter (LMP) for creep life prediction

    LMP = T * (C + log10(t))

    Where:
    - T is temperature in Kelvin
    - t is time to rupture in hours
    - C is material constant (typically 15-25)

    Args:
        temperature_k: Temperature in Kelvin
        lifetime_hours: Predicted lifetime in hours
        C: Material constant (default 20 for Ni-based alloys)

    Returns:
        Larson-Miller parameter value
    """
    if lifetime_hours <= 0:
        lifetime_hours = 1.0

    log_time = math.log10(lifetime_hours)
    lmp = temperature_k * (C + log_time)
    return lmp


def stress_temperature_correction(
    base_stress: float,
    temperature_k: float,
    reference_temp: float = 873.15  # 600°C
) -> float:
    """
    Adjust stress limit based on temperature

    Higher temperature → lower allowable stress
    Uses simple linear degradation model

    Args:
        base_stress: Base stress limit at reference temperature (MPa)
        temperature_k: Operating temperature (K)
        reference_temp: Reference temperature (K)

    Returns:
        Temperature-corrected stress limit (MPa)
    """
    # Linear degradation: ~0.5% per 10K above reference
    temp_diff = temperature_k - reference_temp
    degradation_factor = 1.0 - (temp_diff * 0.0005)

    # Ensure we don't go negative or above base
    degradation_factor = max(0.1, min(1.0, degradation_factor))

    corrected_stress = base_stress * degradation_factor
    return corrected_stress


def composition_strength_factor(ni_percent: float, cr_percent: float, mo_percent: float) -> float:
    """
    Estimate strengthening effect from composition

    Ni: base matrix, moderate strength
    Cr: oxidation resistance, some strengthening
    Mo/W: solid solution strengthening

    Args:
        ni_percent: Nickel percentage (0-100)
        cr_percent: Chromium percentage (0-100)
        mo_percent: Molybdenum percentage (0-100)

    Returns:
        Strength factor (0.5-1.5), higher is better
    """
    # Normalize percentages
    ni_frac = ni_percent / 100.0
    cr_frac = cr_percent / 100.0
    mo_frac = mo_percent / 100.0

    # Weighted contribution (simplified model)
    # Ni: baseline (weight 0.8)
    # Cr: moderate contribution (weight 1.0)
    # Mo: strong strengthening (weight 1.5)
    strength = (
        ni_frac * 0.8 +
        cr_frac * 1.0 +
        mo_frac * 1.5
    )

    # Clamp to reasonable range
    strength = max(0.5, min(1.5, strength))

    return strength


def estimate_failure_probability(
    temperature_k: float,
    pressure_mpa: float,
    cycles: int,
    max_temp: float = 1500,
    max_pressure: float = 500,
    max_cycles: int = 100000
) -> float:
    """
    Estimate failure probability based on operating conditions

    Combines temperature, pressure, and cycle effects

    Args:
        temperature_k: Operating temperature (K)
        pressure_mpa: Operating pressure (MPa)
        cycles: Number of cycles
        max_temp, max_pressure, max_cycles: Reference maxima

    Returns:
        Failure probability (0-1)
    """
    # Normalize each factor
    temp_factor = min(1.0, temperature_k / max_temp)
    pressure_factor = min(1.0, pressure_mpa / max_pressure)
    cycle_factor = min(1.0, cycles / max_cycles)

    # Combined probability (multiplicative model)
    # Assumes factors are semi-independent
    failure_prob = (temp_factor * 0.5 + pressure_factor * 0.3 + cycle_factor * 0.2)

    # Clamp to [0, 1]
    failure_prob = max(0.0, min(1.0, failure_prob))

    return failure_prob


def physics_based_lifetime_estimate(
    temperature_c: float,
    pressure_mpa: float,
    cycles: int,
    ni_percent: float,
    cr_percent: float,
    mo_percent: float
) -> dict:
    """
    Complete physics-based lifetime estimation

    Combines multiple physics models for comprehensive prediction

    Returns:
        Dictionary with lifetime, failure_prob, stress_limit, and physics metadata
    """
    # Convert to Kelvin
    temperature_k = temperature_c + 273.15

    # Calculate physics factors
    arrhenius_factor = arrhenius_creep_factor(temperature_k)
    strength_factor = composition_strength_factor(ni_percent, cr_percent, mo_percent)
    failure_prob = estimate_failure_probability(temperature_k, pressure_mpa, cycles)

    # Base lifetime calculation
    # Start with reference lifetime at moderate conditions
    base_lifetime = 10000.0  # hours

    # Apply corrections
    # Lower temperature (lower arrhenius) → longer life
    temp_correction = (1.0 - arrhenius_factor) * 2.0

    # Better composition → longer life
    comp_correction = strength_factor

    # More cycles → shorter life (fatigue)
    cycle_correction = max(0.3, 1.0 - (cycles / 100000.0) * 0.5)

    # Combined lifetime
    lifetime_hours = base_lifetime * temp_correction * comp_correction * cycle_correction
    lifetime_hours = max(50.0, lifetime_hours)  # Minimum realistic lifetime

    # Stress limit calculation
    base_stress = 800.0  # MPa reference
    stress_limit = stress_temperature_correction(base_stress, temperature_k)
    stress_limit = stress_limit * strength_factor  # Composition effect

    return {
        "lifetime_hours": float(lifetime_hours),
        "failure_probability": float(failure_prob),
        "stress_limit_mpa": float(stress_limit),
        "physics_metadata": {
            "arrhenius_factor": float(arrhenius_factor),
            "strength_factor": float(strength_factor),
            "temperature_k": float(temperature_k)
        }
    }
