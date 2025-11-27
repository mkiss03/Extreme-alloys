# Architecture Documentation

## System Overview

Extreme Alloys is a full-stack application for predicting alloy behavior under extreme conditions using machine learning.

```
┌─────────────┐      HTTP/REST       ┌─────────────┐
│   Frontend  │ ──────────────────> │   Backend   │
│  (Next.js)  │ <────────────────── │  (FastAPI)  │
└─────────────┘                      └─────────────┘
                                            │
                                            ▼
                                     ┌─────────────┐
                                     │  ML Models  │
                                     │ (PyTorch)   │
                                     └─────────────┘
```

## Components

### Frontend (Next.js + TypeScript)

**Location:** `frontend/`

**Technology Stack:**
- Next.js 14 (React framework)
- TypeScript
- Tailwind CSS
- Axios for API communication

**Key Components:**
- `page.tsx` - Main application page
- `api-client.ts` - API communication layer
- `components/` - React UI components
  - `Layout.tsx` - Page layout and navigation
  - `InputForm.tsx` - User input form
  - `ResultsView.tsx` - Prediction results display
  - `Charts.tsx` - Data visualizations

**Responsibilities:**
- User interface
- Form validation
- API communication
- Results visualization
- Error handling

### Backend (FastAPI + Python)

**Location:** `backend/`

**Technology Stack:**
- FastAPI (async web framework)
- Pydantic (data validation)
- PyTorch (ML models)
- NumPy/Pandas (data processing)

**Architecture Layers:**

1. **API Layer** (`app/api/`)
   - Route handlers
   - Request/response models
   - Input validation
   - Error handling

2. **Service Layer** (`app/services/`)
   - Business logic
   - Data preprocessing
   - Prediction orchestration
   - Report generation

3. **Model Layer** (`app/models/`)
   - ML model implementations
   - Model loading/saving
   - Inference logic

**Key Modules:**

- `main.py` - Application entry point
- `config.py` - Configuration management
- `api/routes_prediction.py` - Prediction endpoints
- `services/preprocessing.py` - Feature engineering
- `services/prediction_service.py` - Prediction logic
- `models/gnn_model.py` - Graph Neural Network
- `models/creep_model.py` - Creep prediction model

## Data Flow

### Prediction Request Flow

```
1. User Input (Frontend)
   │
   ▼
2. API Request (POST /predict/extreme_alloy)
   │
   ▼
3. Input Validation (Pydantic)
   │
   ▼
4. Feature Preprocessing
   │  - Parse composition
   │  - Convert units (°C → K)
   │  - Normalize features
   │
   ▼
5. Model Inference
   │  - Load model
   │  - Forward pass
   │  - Post-processing
   │
   ▼
6. Response Formation
   │
   ▼
7. Display Results (Frontend)
```

### Feature Engineering Pipeline

```
Input:
{
  composition: "Ni:55,Cr:20,Mo:10,W:12,Co:3",
  temperature_c: 850,
  pressure_mpa: 150,
  cycles: 10000
}

Processing:
1. Parse composition → [55, 20, 10, 12, 3]
2. Convert temperature → 1123.15 K
3. Build feature vector → [0.55, 0.20, 0.10, 0.12, 0.03, 1123.15, 150, 10000]
4. Normalize → [0.55, 0.20, 0.10, 0.12, 0.03, 0.748, 0.30, 0.666]

Output:
Normalized numpy array ready for ML model
```

## ML Models

### 1. Graph Neural Network (GNN)

**File:** `backend/app/models/gnn_model.py`

**Architecture:**
- Input: Material features (composition, conditions)
- Hidden layers: 3 layers with 64 hidden units
- Output: [lifetime, failure_prob, stress_limit]

**Future Enhancement:**
- Graph structure representing atomic bonds
- Message passing between atoms
- Attention mechanisms

### 2. Creep Model

**File:** `backend/app/models/creep_model.py`

**Architecture:**
- Specialized for creep lifetime prediction
- Deeper network: [128, 64, 32] hidden layers
- Batch normalization
- Dropout for regularization
- Monte Carlo Dropout for uncertainty estimation

**Features:**
- Single output: creep lifetime
- Uncertainty quantification
- Domain-specific design for high-temperature behavior

## Configuration

### Environment Variables

**Backend:**
```bash
ENV=development
API_HOST=0.0.0.0
API_PORT=8000
MODEL_PATH=./models/saved
DEVICE=cpu  # or 'cuda' for GPU
LOG_LEVEL=INFO
```

**Frontend:**
```bash
API_BASE_URL=http://localhost:8000
NODE_ENV=development
```

## Testing Strategy

### Backend Tests

**Location:** `backend/app/tests/`

**Test Types:**
1. **API Tests** (`test_api.py`)
   - Endpoint functionality
   - Input validation
   - Error handling
   - Response format

2. **Model Tests** (`test_models.py`)
   - Model initialization
   - Forward pass
   - Save/load functionality
   - Prediction methods

**Running Tests:**
```bash
pytest app/tests/
pytest --cov=app --cov-report=html
```

## Deployment

### Docker Architecture

```yaml
services:
  backend:
    - FastAPI application
    - Port 8000
    - Volumes: code, data, models

  frontend:
    - Next.js application
    - Port 3000
    - Depends on: backend
```

### Production Considerations

1. **Scalability**
   - Horizontal scaling with load balancer
   - Model caching
   - Redis for session management

2. **Security**
   - API authentication (JWT)
   - Rate limiting
   - Input sanitization
   - CORS configuration

3. **Monitoring**
   - Health checks
   - Logging (structured logs)
   - Metrics (Prometheus)
   - Error tracking (Sentry)

4. **Model Management**
   - Model versioning
   - A/B testing
   - Gradual rollout
   - Fallback models

## Future Enhancements

1. **Backend**
   - Database integration (PostgreSQL)
   - Caching layer (Redis)
   - Async task queue (Celery)
   - Model versioning system

2. **Frontend**
   - User authentication
   - Prediction history
   - Advanced visualizations
   - Export functionality (PDF reports)

3. **ML**
   - Active learning
   - Model retraining pipeline
   - Ensemble models
   - Explainable AI (SHAP, LIME)

4. **Infrastructure**
   - Kubernetes deployment
   - CI/CD pipeline
   - Automated testing
   - Performance monitoring
