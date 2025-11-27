# Model Training Guide

## Quick Start

### Training the Model

```bash
cd backend
python train_mlp.py
```

## Data Format

The training script expects data in `data/processed/extreme_alloys_training.csv` with the following columns:

### Feature Columns
- `Ni` - Nickel percentage (0-100)
- `Cr` - Chromium percentage (0-100)
- `Mo` - Molybdenum percentage (0-100)
- `W` - Tungsten percentage (0-100)
- `Co` - Cobalt percentage (0-100)
- `temperature_c` - Temperature in Celsius
- `pressure_mpa` - Pressure in MPa
- `cycles` - Number of thermal/mechanical cycles

### Target Columns
- `creep_lifetime_hours` - Creep lifetime in hours
- `failure_probability` - Failure probability (0-1)
- `stress_limit_mpa` - Maximum stress limit in MPa

## Example CSV Format

```csv
Ni,Cr,Mo,W,Co,temperature_c,pressure_mpa,cycles,creep_lifetime_hours,failure_probability,stress_limit_mpa
55,20,10,12,3,850,150,10000,3456.7,0.35,642.1
60,18,8,10,4,900,180,15000,2234.5,0.52,580.3
52,22,12,11,3,800,120,8000,4567.2,0.28,695.4
```

## Training Configuration

Edit these parameters in `train_mlp.py`:

```python
BATCH_SIZE = 32
LEARNING_RATE = 0.001
EPOCHS = 100
VALIDATION_SPLIT = 0.15
TEST_SPLIT = 0.15
```

## Output

The trained model will be saved to:
```
backend/app/models/saved/extreme_alloy_gnn.pth
```

## Using Synthetic Data

If no training data is available, the script will automatically generate synthetic data for demonstration purposes.

## Monitoring Training

The script logs:
- Epoch number
- Training loss
- Validation loss
- Best model checkpoints

## Model Architecture

**GNN Model (Default)**
- Input: 8 features
- Hidden layers: 64 units, 3 layers
- Output: 3 predictions (lifetime, failure_prob, stress_limit)
- Dropout: 0.2
- Activation: ReLU

## Advanced Training

### Using Real Data

1. Obtain data from Materials Project or NIMS
2. Process into CSV format
3. Place in `data/processed/extreme_alloys_training.csv`
4. Run training script

### Custom Model Architecture

Modify `backend/app/models/gnn_model.py` to change:
- Number of layers
- Hidden dimensions
- Activation functions
- Regularization

### Transfer Learning

To fine-tune a pre-trained model:

```python
# In train_mlp.py
model = GNNModel(input_dim=8, hidden_dim=64, output_dim=3)
model.load_model('path/to/pretrained/model.pth')
# Continue training...
```

## Troubleshooting

**Out of Memory**
- Reduce `BATCH_SIZE`
- Reduce model `hidden_dim`

**Slow Training**
- Enable CUDA if GPU available
- Increase `BATCH_SIZE`
- Use mixed precision training

**Poor Performance**
- Increase model capacity (more layers/units)
- Collect more training data
- Adjust learning rate
- Add data augmentation
