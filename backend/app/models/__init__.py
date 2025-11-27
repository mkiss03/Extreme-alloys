# backend/app/models/__init__.py
"""
ML models for extreme alloy behavior prediction
"""

from .gnn_model import GNNModel
from .creep_model import CreepModel

__all__ = ["GNNModel", "CreepModel"]
