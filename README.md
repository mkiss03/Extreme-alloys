# Extreme Alloys

AI-powered prediction service for alloy behavior under extreme conditions (high temperature, high pressure, thermal cycling).

## Overview

This project uses machine learning models (Graph Neural Networks and specialized creep models) to predict:
- Creep lifetime under extreme conditions
- Failure probability
- Recommended stress limits

## Project Structure

```
extreme-alloys/
├── backend/          # FastAPI backend service
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── models/   # ML models (GNN, Creep)
│   │   ├── services/ # Business logic
│   │   └── tests/    # Unit tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # Next.js frontend
│   ├── app/
│   │   ├── components/
│   │   └── api-client.ts
│   ├── package.json
│   └── Dockerfile
├── data/            # Data storage
│   ├── raw/
│   ├── processed/
│   └── notebooks/
├── docs/            # Documentation
└── docker-compose.yml
```

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Backend API: http://localhost:8000
# Frontend UI: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run server
python -m app.main
# or
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables for local development
# Copy .env.example to .env.local and configure
cp .env.example .env.local

# Edit .env.local to point to your backend:
# NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Run development server
npm run dev
```

Frontend will run on `http://localhost:3000`

**Fontos:** A frontend a `NEXT_PUBLIC_BACKEND_URL` environment változót használja a backend eléréséhez:
- **Lokális fejlesztés**: Állítsd be `frontend/.env.local` fájlban: `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000`
- **Vercel deployment**: Add hozzá a Vercel Project Settings → Environment Variables alatt: `NEXT_PUBLIC_BACKEND_URL=https://extreme-alloys.onrender.com`

## API Usage

### Predict Alloy Behavior

```bash
curl -X POST "http://localhost:8000/api/v1/predict/extreme_alloy" \
  -H "Content-Type: application/json" \
  -d '{
    "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
    "temperature_c": 850.0,
    "pressure_mpa": 150.0,
    "cycles": 10000,
    "model_type": "gnn"
  }'
```

### Response

```json
{
  "creep_lifetime_hours": 3456.7,
  "failure_probability": 0.35,
  "stress_limit_mpa": 642.1,
  "model_version": "gnn_v1.0",
  "confidence": 0.85
}
```

## Features

- **Multiple ML Models**: GNN and specialized creep models
- **Real-time Predictions**: Fast API response times
- **Interactive UI**: Modern React/Next.js frontend
- **Comprehensive Testing**: Unit and API tests
- **Docker Support**: Easy deployment with Docker Compose
- **Extensive Documentation**: API docs via FastAPI Swagger UI

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest app/tests/

# With coverage
pytest --cov=app --cov-report=html
```

### Code Structure

- **Backend** (`backend/app/`):
  - `main.py`: FastAPI application entry point
  - `config.py`: Configuration management
  - `api/`: API route handlers
  - `models/`: ML model implementations
  - `services/`: Business logic and data processing

- **Frontend** (`frontend/app/`):
  - `page.tsx`: Main application page
  - `api-client.ts`: Backend API client
  - `components/`: React components

## Data Sources

This project is designed to work with alloy composition data from:
- Materials Project API
- NIMS Materials Database
- Custom experimental data

## Technology Stack

### Backend
- FastAPI - Modern Python web framework
- PyTorch - Deep learning framework
- NumPy/Pandas - Data processing
- Pydantic - Data validation

### Frontend
- Next.js 14 - React framework
- TypeScript - Type-safe JavaScript
- Tailwind CSS - Utility-first CSS
- Axios - HTTP client

### Infrastructure
- Docker & Docker Compose
- Python 3.11
- Node.js 20

## Deployment

### Backend (Render)

1. Hozz létre új Web Service-t a Render-en
2. Kapcsold össze a GitHub repo-val
3. Beállítások:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Állítsd be a szükséges változókat (ENV, MODEL_PATH, stb.)

### Frontend (Vercel)

1. Importáld a projektet a Vercel-be
2. **Root Directory**: Állítsd be `frontend`-re
3. **Environment Variables** (Project Settings):
   ```
   NEXT_PUBLIC_BACKEND_URL=https://extreme-alloys.onrender.com
   ```
   (Cseréld le a saját Render backend URL-edre)
4. Deploy!

**Fontos:** A `NEXT_PUBLIC_BACKEND_URL` változó nélkül a frontend localhost:8000-re próbál csatlakozni, ami Vercel-ről nem fog működni.

## Roadmap

- [ ] Integrate real Materials Project data
- [ ] Train production GNN models
- [ ] Add uncertainty quantification
- [ ] Implement model versioning
- [ ] Add user authentication
- [ ] Create prediction history tracking
- [ ] Develop advanced visualizations

## License

MIT License (or your preferred license)

## Contributors

Extreme Alloys Team

## Contact

For questions or issues, please open a GitHub issue.
