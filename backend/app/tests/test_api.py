# backend/app/tests/test_api.py
"""
API endpoint tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_prediction_endpoint_valid_input():
    """Test prediction with valid input"""
    payload = {
        "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
        "temperature_c": 850.0,
        "pressure_mpa": 150.0,
        "cycles": 10000
    }

    response = client.post("/api/v1/predict/extreme_alloy", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "creep_lifetime_hours" in data
    assert "failure_probability" in data
    assert "stress_limit_mpa" in data
    assert data["creep_lifetime_hours"] > 0


def test_prediction_endpoint_missing_field():
    """Test prediction with missing required field"""
    payload = {
        "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
        "temperature_c": 850.0,
        # Missing pressure_mpa and cycles
    }

    response = client.post("/api/v1/predict/extreme_alloy", json=payload)
    assert response.status_code == 422  # Validation error


def test_prediction_endpoint_invalid_temperature():
    """Test prediction with out-of-range temperature"""
    payload = {
        "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
        "temperature_c": -500.0,  # Invalid temperature
        "pressure_mpa": 150.0,
        "cycles": 10000
    }

    response = client.post("/api/v1/predict/extreme_alloy", json=payload)
    assert response.status_code == 400  # Bad request


def test_report_generation():
    """Test full report generation"""
    payload = {
        "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
        "temperature_c": 850.0,
        "pressure_mpa": 150.0,
        "cycles": 10000
    }

    response = client.post("/api/v1/predict/report", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "input_parameters" in data
    assert "predictions" in data
    assert "recommendations" in data


def test_prediction_health():
    """Test prediction service health check"""
    response = client.get("/api/v1/predict/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "models_available" in data
