# Model Specification

## Overview

This document describes the machine learning models used for predicting alloy behavior under extreme conditions.

## Problem Statement

**Objective:** Predict the behavior of metallic alloys under extreme operating conditions:
- High temperatures (500-1500°C)
- High pressures (0-500 MPa)
- Cyclic loading (thermal and mechanical)

**Target Predictions:**
1. Creep lifetime (hours until failure)
2. Failure probability (0-1)
3. Maximum stress limit (MPa)

## Input Features

### Feature Vector

8-dimensional input vector:

| Index | Feature | Unit | Range | Normalized Range |
|-------|---------|------|-------|------------------|
| 0 | Ni percentage | % | 0-100 | 0-1 |
| 1 | Cr percentage | % | 0-100 | 0-1 |
| 2 | Mo percentage | % | 0-100 | 0-1 |
| 3 | W percentage | % | 0-100 | 0-1 |
| 4 | Co percentage | % | 0-100 | 0-1 |
| 5 | Temperature | K | 300-1500 | 0-1 |
| 6 | Pressure | MPa | 0-500 | 0-1 |
| 7 | Cycles | count | 1-1M | 0-1 (log scale) |

### Normalization

```python
# Element percentages
features[0:5] = element_pct / 100.0

# Temperature
features[5] = temperature_K / 1500.0

# Pressure
features[6] = pressure_mpa / 500.0

# Cycles (logarithmic)
features[7] = log10(max(cycles, 1)) / 6.0
```

## Model 1: Graph Neural Network (GNN)

### Architecture

```
Input Layer (8)
    ↓
Encoder (Linear 8 → 64)
    ↓
ReLU + Dropout(0.2)
    ↓
Hidden Layer 1 (Linear 64 → 64)
    ↓
ReLU + Dropout(0.2)
    ↓
Hidden Layer 2 (Linear 64 → 64)
    ↓
ReLU + Dropout(0.2)
    ↓
Decoder (Linear 64 → 3)
    ↓
Output [lifetime, failure_prob, stress_limit]
```

### Hyperparameters

```python
input_dim = 8
hidden_dim = 64
output_dim = 3
num_layers = 3
dropout = 0.2
activation = ReLU
```

### Output Processing

```python
# Raw outputs
raw_lifetime = output[0]
raw_failure_prob = output[1]
raw_stress = output[2]

# Post-processing
lifetime = raw_lifetime  # Direct regression
failure_prob = sigmoid(raw_failure_prob)  # Probability in [0,1]
stress_limit = raw_stress  # Direct regression
```

### Training (TODO)

**Loss Function:** Multi-task loss
```python
loss = MSE(lifetime_pred, lifetime_true) +
       BCE(failure_prob_pred, failure_prob_true) +
       MSE(stress_pred, stress_true)
```

**Optimizer:** Adam
- Learning rate: 0.001
- Weight decay: 1e-5

**Batch size:** 32
**Epochs:** 100

## Model 2: Creep Prediction Model

### Architecture

Specialized model for creep lifetime prediction only.

```
Input Layer (8)
    ↓
Linear 8 → 128 + BatchNorm + ReLU + Dropout(0.3)
    ↓
Linear 128 → 64 + BatchNorm + ReLU + Dropout(0.3)
    ↓
Linear 64 → 32 + BatchNorm + ReLU + Dropout(0.3)
    ↓
Linear 32 → 1
    ↓
Output [lifetime]
```

### Hyperparameters

```python
input_dim = 8
hidden_dims = [128, 64, 32]
dropout = 0.3
activation = ReLU
use_batch_norm = True
```

### Uncertainty Estimation

Uses **Monte Carlo Dropout** for uncertainty quantification:

```python
# Enable dropout at inference time
model.train()

# Multiple forward passes
predictions = []
for i in range(100):
    pred = model(features)
    predictions.append(pred)

# Statistics
mean = np.mean(predictions)
std = np.std(predictions)
confidence_95 = [
    np.percentile(predictions, 2.5),
    np.percentile(predictions, 97.5)
]
```

### Training (TODO)

**Loss Function:** Mean Squared Error (MSE)

**Optimizer:** Adam
- Learning rate: 0.001
- Weight decay: 1e-4

**Batch size:** 32
**Epochs:** 150

## Model 3: Ensemble (Future)

Combine GNN and Creep models:

```python
ensemble_prediction = {
    'lifetime': 0.5 * gnn_lifetime + 0.5 * creep_lifetime,
    'failure_prob': gnn_failure_prob,
    'stress_limit': gnn_stress_limit,
    'uncertainty': creep_model_uncertainty
}
```

## Data Requirements

### Training Data Format

```csv
Ni,Cr,Mo,W,Co,temp_c,pressure_mpa,cycles,lifetime_hours,failure_prob,stress_limit
55,20,10,12,3,850,150,10000,3456.7,0.35,642.1
60,18,8,10,4,900,180,15000,2234.5,0.52,580.3
...
```

### Data Sources

1. **Materials Project**
   - API: https://materialsproject.org/api
   - Composition data
   - Crystal structures

2. **NIMS Materials Database**
   - High-temperature creep data
   - Mechanical properties

3. **Experimental Data**
   - Lab measurements
   - Industrial testing data

### Data Preprocessing

```python
# 1. Clean data
df = df.dropna()
df = df[df['lifetime_hours'] > 0]

# 2. Split composition
df[['Ni', 'Cr', 'Mo', 'W', 'Co']] = parse_composition(df['composition'])

# 3. Normalize features
X = normalize_features(df[feature_columns])

# 4. Split train/val/test
train, val, test = split_data(X, y, ratios=[0.7, 0.15, 0.15])
```

## Evaluation Metrics

### Regression Metrics (Lifetime, Stress)

- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **R²** (Coefficient of Determination)
- **MAPE** (Mean Absolute Percentage Error)

### Classification Metrics (Failure Probability)

- **Accuracy**
- **Precision/Recall**
- **ROC-AUC**
- **F1 Score**

### Domain-Specific Metrics

- **Safety Margin Error:** |predicted_limit - true_limit| / true_limit
- **Conservative Prediction Rate:** % of predictions that underestimate lifetime

## Model Versioning

```
models/
  saved/
    gnn_v1.0_20250127.pt
    gnn_v1.1_20250215.pt
    creep_v1.0_20250127.pt
    creep_v1.1_20250220.pt
```

**Naming Convention:** `{model_type}_v{version}_{date}.pt`

## Production Deployment

### Model Serving

```python
# Load model
model = GNNModel(input_dim=8, hidden_dim=64, output_dim=3)
model.load_state_dict(torch.load('models/saved/gnn_v1.0.pt'))
model.eval()

# Inference
with torch.no_grad():
    prediction = model(features)
```

### Performance Requirements

- **Latency:** < 100ms per prediction
- **Throughput:** > 100 predictions/second
- **Memory:** < 500MB model size

## Future Improvements

1. **Model Architecture**
   - True graph structure (atom-level)
   - Attention mechanisms
   - Transformer-based models

2. **Features**
   - Crystal structure information
   - Electronic properties
   - Thermodynamic data

3. **Training**
   - Transfer learning
   - Active learning
   - Physics-informed neural networks

4. **Interpretability**
   - SHAP values
   - Attention visualization
   - Feature importance

5. **Uncertainty**
   - Bayesian neural networks
   - Ensemble methods
   - Conformal prediction
