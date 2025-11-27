# backend/train_mlp.py
"""
Training script for Extreme Alloys MLP model

This script trains the ExtremeAlloyRegressor model on processed data
and saves the trained model for inference.
"""

import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import logging

from app.models.gnn_model import GNNModel
from app.config import logger

# Training configuration
BATCH_SIZE = 32
LEARNING_RATE = 0.001
EPOCHS = 100
VALIDATION_SPLIT = 0.15
TEST_SPLIT = 0.15
MODEL_SAVE_PATH = "app/models/saved/extreme_alloy_gnn.pth"
DATA_PATH = "data/processed/extreme_alloys_training.csv"


class AlloyDataset(Dataset):
    """
    PyTorch Dataset for alloy data
    """

    def __init__(self, features, targets):
        self.features = torch.FloatTensor(features)
        self.targets = torch.FloatTensor(targets)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]


def load_training_data(data_path):
    """
    Load and preprocess training data from CSV

    Expected columns:
    - Ni, Cr, Mo, W, Co (percentages)
    - temperature_c, pressure_mpa, cycles
    - creep_lifetime_hours, failure_probability, stress_limit_mpa (targets)
    """
    logger.info(f"Loading data from {data_path}")

    if not os.path.exists(data_path):
        logger.error(f"Data file not found: {data_path}")
        raise FileNotFoundError(f"Please provide training data at {data_path}")

    df = pd.read_csv(data_path)

    # Feature columns
    feature_cols = ['Ni', 'Cr', 'Mo', 'W', 'Co',
                    'temperature_c', 'pressure_mpa', 'cycles']

    # Target columns
    target_cols = ['creep_lifetime_hours', 'failure_probability', 'stress_limit_mpa']

    # Check required columns
    missing_cols = set(feature_cols + target_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing columns in data: {missing_cols}")

    X = df[feature_cols].values
    y = df[target_cols].values

    logger.info(f"Loaded {len(df)} samples with {X.shape[1]} features")

    return X, y


def normalize_features(X_train, X_val, X_test):
    """
    Normalize features using StandardScaler
    """
    scaler = StandardScaler()

    X_train_norm = scaler.fit_transform(X_train)
    X_val_norm = scaler.transform(X_val)
    X_test_norm = scaler.transform(X_test)

    return X_train_norm, X_val_norm, X_test_norm, scaler


def split_data(X, y, val_split=0.15, test_split=0.15, random_state=42):
    """
    Split data into train, validation, and test sets
    """
    # First split: separate test set
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_split, random_state=random_state
    )

    # Second split: separate validation from training
    val_ratio = val_split / (1 - test_split)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_ratio, random_state=random_state
    )

    logger.info(f"Data split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")

    return X_train, X_val, X_test, y_train, y_val, y_test


def train_epoch(model, dataloader, criterion, optimizer, device):
    """
    Train for one epoch
    """
    model.train()
    total_loss = 0.0

    for features, targets in dataloader:
        features = features.to(device)
        targets = targets.to(device)

        # Forward pass
        optimizer.zero_grad()
        outputs = model(features)
        loss = criterion(outputs, targets)

        # Backward pass
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(dataloader)


def validate(model, dataloader, criterion, device):
    """
    Validate the model
    """
    model.eval()
    total_loss = 0.0

    with torch.no_grad():
        for features, targets in dataloader:
            features = features.to(device)
            targets = targets.to(device)

            outputs = model(features)
            loss = criterion(outputs, targets)

            total_loss += loss.item()

    return total_loss / len(dataloader)


def train_model():
    """
    Main training function
    """
    logger.info("Starting model training...")

    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    # Load data
    try:
        X, y = load_training_data(DATA_PATH)
    except FileNotFoundError:
        logger.warning("No training data found. Creating synthetic data for demonstration...")
        X, y = generate_synthetic_data(1000)

    # Split data
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(
        X, y,
        val_split=VALIDATION_SPLIT,
        test_split=TEST_SPLIT
    )

    # Normalize features
    X_train_norm, X_val_norm, X_test_norm, scaler = normalize_features(
        X_train, X_val, X_test
    )

    # Create datasets and dataloaders
    train_dataset = AlloyDataset(X_train_norm, y_train)
    val_dataset = AlloyDataset(X_val_norm, y_val)
    test_dataset = AlloyDataset(X_test_norm, y_test)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Initialize model
    input_dim = X_train_norm.shape[1]
    output_dim = y_train.shape[1]

    model = GNNModel(
        input_dim=input_dim,
        hidden_dim=64,
        output_dim=output_dim,
        num_layers=3
    ).to(device)

    logger.info(f"Model initialized with {input_dim} inputs and {output_dim} outputs")

    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-5)

    # Training loop
    best_val_loss = float('inf')
    patience = 10
    patience_counter = 0

    for epoch in range(EPOCHS):
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss = validate(model, val_loader, criterion, device)

        logger.info(f"Epoch {epoch+1}/{EPOCHS} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0

            # Save best model
            os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
            model.save_model(MODEL_SAVE_PATH)
            logger.info(f"Best model saved with val_loss: {val_loss:.4f}")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"Early stopping at epoch {epoch+1}")
                break

    # Evaluate on test set
    model.load_model(MODEL_SAVE_PATH)
    test_loss = validate(model, test_loader, criterion, device)
    logger.info(f"Final Test Loss: {test_loss:.4f}")

    logger.info("Training completed!")
    return model


def generate_synthetic_data(n_samples=1000):
    """
    Generate synthetic training data for demonstration
    This is a placeholder - replace with real data
    """
    logger.info(f"Generating {n_samples} synthetic samples...")

    np.random.seed(42)

    # Features
    Ni = np.random.uniform(40, 70, n_samples)
    Cr = np.random.uniform(10, 30, n_samples)
    Mo = np.random.uniform(5, 15, n_samples)
    W = np.random.uniform(5, 15, n_samples)
    Co = np.random.uniform(0, 10, n_samples)

    # Normalize to sum to 100
    total = Ni + Cr + Mo + W + Co
    Ni = (Ni / total) * 100
    Cr = (Cr / total) * 100
    Mo = (Mo / total) * 100
    W = (W / total) * 100
    Co = (Co / total) * 100

    temperature_c = np.random.uniform(600, 1200, n_samples)
    pressure_mpa = np.random.uniform(50, 300, n_samples)
    cycles = np.random.randint(1000, 50000, n_samples)

    X = np.column_stack([Ni, Cr, Mo, W, Co, temperature_c, pressure_mpa, cycles])

    # Synthetic targets (based on simplified physics)
    creep_lifetime = 5000 * (1 - temperature_c/1500) * (1 - pressure_mpa/500) * (Ni/100)
    creep_lifetime = np.clip(creep_lifetime, 100, 10000)

    failure_prob = temperature_c / 1500 * pressure_mpa / 500
    failure_prob = np.clip(failure_prob, 0.0, 1.0)

    stress_limit = 800 * (1 - temperature_c/1500) * (Cr/100)
    stress_limit = np.clip(stress_limit, 200, 900)

    y = np.column_stack([creep_lifetime, failure_prob, stress_limit])

    return X, y


if __name__ == "__main__":
    train_model()
