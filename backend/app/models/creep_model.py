# backend/app/models/creep_model.py
"""
Specialized model for creep behavior prediction under extreme conditions
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Optional
from app.config import logger


class CreepModel(nn.Module):
    """
    Neural network model specifically designed for creep lifetime prediction

    Creep: slow, progressive deformation of material under constant stress
    at high temperatures
    """

    def __init__(
        self,
        input_dim: int = 8,
        hidden_dims: list = [128, 64, 32],
        dropout_rate: float = 0.3
    ):
        super(CreepModel, self).__init__()

        self.input_dim = input_dim
        self.hidden_dims = hidden_dims

        # Build network layers
        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim

        # Output layer (single value: lifetime)
        layers.append(nn.Linear(prev_dim, 1))

        self.network = nn.Sequential(*layers)

        logger.info(f"Initialized Creep model with architecture: {hidden_dims}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass

        Args:
            x: Input features [batch_size, input_dim]

        Returns:
            Predicted creep lifetime [batch_size, 1]
        """
        return self.network(x)

    def predict_creep_lifetime(self, features: np.ndarray) -> float:
        """
        Predict creep lifetime from input features

        Args:
            features: Numpy array of input features

        Returns:
            Predicted lifetime in hours
        """
        self.eval()

        # Convert to torch tensor
        x = torch.from_numpy(features).float().unsqueeze(0)

        with torch.no_grad():
            lifetime = self.forward(x)

        return float(lifetime.item())

    def predict_with_uncertainty(
        self,
        features: np.ndarray,
        n_samples: int = 100
    ) -> Dict[str, float]:
        """
        Predict with uncertainty estimation using dropout at inference

        Args:
            features: Input features
            n_samples: Number of Monte Carlo samples

        Returns:
            Dictionary with mean, std, and confidence intervals
        """
        self.train()  # Keep dropout active

        x = torch.from_numpy(features).float().unsqueeze(0)

        predictions = []
        for _ in range(n_samples):
            with torch.no_grad():
                pred = self.forward(x)
                predictions.append(pred.item())

        predictions = np.array(predictions)

        return {
            "mean_lifetime": float(np.mean(predictions)),
            "std_lifetime": float(np.std(predictions)),
            "confidence_interval_95": [
                float(np.percentile(predictions, 2.5)),
                float(np.percentile(predictions, 97.5))
            ]
        }

    def save_model(self, path: str):
        """Save model checkpoint"""
        checkpoint = {
            "model_state": self.state_dict(),
            "input_dim": self.input_dim,
            "hidden_dims": self.hidden_dims
        }
        torch.save(checkpoint, path)
        logger.info(f"Creep model saved to {path}")

    def load_model(self, path: str):
        """Load model checkpoint"""
        checkpoint = torch.load(path)
        self.load_state_dict(checkpoint["model_state"])
        logger.info(f"Creep model loaded from {path}")
