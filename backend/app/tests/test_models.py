# backend/app/tests/test_models.py
"""
ML model tests
"""

import pytest
import torch
import numpy as np
from app.models.gnn_model import GNNModel
from app.models.creep_model import CreepModel


def test_gnn_model_initialization():
    """Test GNN model can be initialized"""
    model = GNNModel(input_dim=8, hidden_dim=64, output_dim=3)
    assert model is not None
    assert model.input_dim == 8
    assert model.hidden_dim == 64


def test_gnn_model_forward_pass():
    """Test GNN model forward pass"""
    model = GNNModel(input_dim=8, hidden_dim=64, output_dim=3)

    # Create dummy input
    batch_size = 4
    x = torch.randn(batch_size, 8)

    # Forward pass
    output = model(x)

    assert output.shape == (batch_size, 3)


def test_gnn_model_predict():
    """Test GNN model prediction method"""
    model = GNNModel(input_dim=8, hidden_dim=64, output_dim=3)

    # Create dummy input
    x = torch.randn(1, 8)

    # Make prediction
    result = model.predict(x)

    assert isinstance(result, dict)
    assert "creep_lifetime_hours" in result
    assert "failure_probability" in result
    assert "stress_limit_mpa" in result


def test_creep_model_initialization():
    """Test Creep model initialization"""
    model = CreepModel(input_dim=8, hidden_dims=[128, 64, 32])
    assert model is not None
    assert model.input_dim == 8


def test_creep_model_forward_pass():
    """Test Creep model forward pass"""
    model = CreepModel(input_dim=8, hidden_dims=[128, 64, 32])

    # Create dummy input
    batch_size = 4
    x = torch.randn(batch_size, 8)

    # Forward pass
    output = model(x)

    assert output.shape == (batch_size, 1)


def test_creep_model_predict():
    """Test Creep model prediction"""
    model = CreepModel(input_dim=8, hidden_dims=[64, 32])

    # Create dummy features
    features = np.random.randn(8).astype(np.float32)

    # Predict
    lifetime = model.predict_creep_lifetime(features)

    assert isinstance(lifetime, float)


def test_creep_model_uncertainty():
    """Test Creep model uncertainty estimation"""
    model = CreepModel(input_dim=8, hidden_dims=[64, 32])

    # Create dummy features
    features = np.random.randn(8).astype(np.float32)

    # Predict with uncertainty
    result = model.predict_with_uncertainty(features, n_samples=50)

    assert "mean_lifetime" in result
    assert "std_lifetime" in result
    assert "confidence_interval_95" in result
    assert len(result["confidence_interval_95"]) == 2


def test_model_save_load(tmp_path):
    """Test model saving and loading"""
    model1 = GNNModel(input_dim=8, hidden_dim=32, output_dim=3)

    # Save model
    model_path = tmp_path / "test_model.pt"
    model1.save_model(str(model_path))

    assert model_path.exists()

    # Load model
    model2 = GNNModel(input_dim=8, hidden_dim=32, output_dim=3)
    model2.load_model(str(model_path))

    # Compare outputs
    x = torch.randn(1, 8)
    with torch.no_grad():
        out1 = model1(x)
        out2 = model2(x)

    assert torch.allclose(out1, out2)
