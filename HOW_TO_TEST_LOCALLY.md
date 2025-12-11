# How to Test Locally - Extreme Alloys v2.0

Complete guide for testing the v2.0 refactored application on your local machine.

---

## Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 16+** (for frontend)
- **Git** (for version control)

---

## 🔧 1. Backend Setup

### 1.1 Navigate to Backend

```bash
cd backend
```

### 1.2 Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.4 Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

### 1.5 Verify Backend is Running

Open browser and visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Version Info**: http://localhost:8000/version

---

## 🎨 2. Frontend Setup

### 2.1 Navigate to Frontend (in new terminal)

```bash
cd frontend
```

### 2.2 Install Dependencies

```bash
npm install
```

### 2.3 Create Environment File

Create `.env.local` file in `frontend/` directory:

```bash
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local
```

Or manually create `frontend/.env.local`:
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 2.4 Start Frontend Dev Server

```bash
npm run dev
```

You should see:
```
   ▲ Next.js 14.1.0
   - Local:        http://localhost:3000
   - Ready in 2.3s
```

### 2.5 Open Application

Visit: **http://localhost:3000**

---

## ✅ 3. Testing v2.0 Features

### 3.1 Test Backend API (Swagger)

1. Visit http://localhost:8000/docs
2. Try the following endpoints:

#### A) Get Available Models

**GET /api/v1/predict/models**
- Click "Try it out" → "Execute"
- Should return 3 models: `gnn`, `physics_heuristic`, `safety_conservative`

#### B) Test Each Model

**POST /api/v1/predict/extreme_alloy**

Use this test payload:
```json
{
  "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
  "temperature_c": 850,
  "pressure_mpa": 150,
  "cycles": 10000,
  "model_type": "gnn"
}
```

Expected results for **GNN Model**:
- ✅ creep_lifetime_hours: ~3000-6000
- ✅ failure_probability: 0.3-0.7
- ✅ stress_limit_mpa: 300-500
- ✅ model_confidence: 0.75
- ✅ ml_metadata: present

Now change `model_type` to `"physics_heuristic"`:
- ✅ Different values than GNN
- ✅ model_confidence: 0.65
- ✅ physics_metadata: includes temperature_k, safety_factor, applied_stress_mpa

Now change `model_type` to `"safety_conservative"`:
- ✅ Lowest creep_lifetime (most conservative)
- ✅ Highest failure_probability
- ✅ model_confidence: 0.90
- ✅ safety_factors: lifetime_factor: 0.5, etc.

#### C) Test Input Validation

Try invalid inputs:

**Invalid composition** (total < 100%):
```json
{
  "composition": "Ni:30,Cr:20",
  "temperature_c": 850,
  "pressure_mpa": 150,
  "cycles": 10000,
  "model_type": "gnn"
}
```
Expected: 400 error with message about composition total

**Temperature too high**:
```json
{
  "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
  "temperature_c": 2500,
  "pressure_mpa": 150,
  "cycles": 10000,
  "model_type": "gnn"
}
```
Expected: 400 error about temperature exceeding range

**Negative pressure**:
```json
{
  "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
  "temperature_c": 850,
  "pressure_mpa": -50,
  "cycles": 10000,
  "model_type": "gnn"
}
```
Expected: 400/422 error about negative pressure

---

### 3.2 Test Frontend UI

#### A) Basic Functionality

1. Open http://localhost:3000
2. Fill in the form:
   - Composition: `Ni:55,Cr:20,Mo:10,W:12,Co:3`
   - Temperature: `850`
   - Pressure: `150`
   - Cycles: `10000`
   - Model: Select **GNN**
3. Click "Predict Behavior"
4. **Verify**:
   - ✅ Loading spinner appears
   - ✅ Results appear within ~1 second
   - ✅ ModelHeader shows "GNN" with strategy badge
   - ✅ RiskBadge shows risk level (color-coded)
   - ✅ MetricCards show creep lifetime, failure probability, stress limit
   - ✅ ML Metadata section appears (for GNN)

#### B) Test Different Models

1. Select **Physics Heuristic** model
2. Click "Predict Behavior"
3. **Verify**:
   - ✅ Different values than GNN
   - ✅ ModelHeader shows "Physics Heuristic" with purple strategy badge
   - ✅ Physics Metadata section appears (temperature_k, safety_factor, etc.)

4. Select **Safety Conservative** model
5. Click "Predict Behavior"
6. **Verify**:
   - ✅ Most conservative values (lowest lifetime, highest failure probability)
   - ✅ ModelHeader shows "Safety Conservative" with orange strategy badge
   - ✅ Confidence: 90%
   - ✅ Safety Factors section appears (showing 50% lifetime factor, etc.)

#### C) Test Input Validation (Frontend)

1. Enter invalid composition: `Ni55Cr20` (no colons)
2. Click "Predict Behavior"
3. **Verify**: Red error message appears below composition field

4. Enter temperature: `2500` (too high)
5. Click "Predict Behavior"
6. **Verify**: Error message about temperature exceeding range

7. Enter pressure: `-50` (negative)
8. Click "Predict Behavior"
9. **Verify**: Error message about negative pressure

#### D) Test Auto-Normalization

1. Enter composition: `Ni:52,Cr:19,Mo:10,W:12,Co:3` (total = 96%)
2. Click "Predict Behavior"
3. **Verify**:
   - ✅ Prediction succeeds (auto-normalized to 100%)
   - ✅ Check browser console for warning about auto-normalization

#### E) Test UI Components

**ModelHeader**:
- ✅ Shows model name in large text
- ✅ Strategy badge has correct color (blue/purple/orange)
- ✅ Version and confidence displayed

**MetricCard**:
- ✅ Creep Lifetime: Blue gradient, clock icon
- ✅ Failure Probability: Red gradient, warning icon, shows as percentage
- ✅ Stress Limit: Color changes based on value:
  - Green if > 300 MPa
  - Yellow if 150-300 MPa
  - Red if < 150 MPa

**RiskBadge**:
- ✅ Low Risk (green) if failure_probability < 30%
- ✅ Medium Risk (yellow) if 30-60%
- ✅ High Risk (red) if > 60%

**Loader**:
- ✅ Spinning animation
- ✅ Pulsing dots
- ✅ "Running prediction..." message

---

## 🧪 4. Testing Backend Mechanics Module

### 4.1 Python Interactive Test

```bash
cd backend
python3
```

```python
from app.services.mechanics import analyze_material_behavior

# Test realistic physics calculations
result = analyze_material_behavior(
    temperature_c=850,
    pressure_mpa=150,
    composition={"Ni": 55, "Cr": 20, "Mo": 10, "W": 12, "Co": 3},
    cycles=10000
)

print(f"Creep Lifetime: {result['creep_lifetime_hours']:.2f} hours")
print(f"Failure Probability: {result['failure_probability']:.3f}")
print(f"Stress Limit: {result['stress_limit_mpa']:.2f} MPa")
print(f"Safety Factor: {result['safety_factor']:.3f}")
```

Expected output:
```
Creep Lifetime: ~4000-8000 hours
Failure Probability: 0.3-0.7
Stress Limit: 300-500 MPa
Safety Factor: 0.4-0.6
```

### 4.2 Test Individual Functions

```python
from app.services.mechanics import (
    calculate_safety_factor,
    estimate_stress_limit,
    predict_creep_lifetime
)

# Test safety factor (should decrease with temperature)
sf_room = calculate_safety_factor(298)  # Room temp
sf_hot = calculate_safety_factor(1123)  # 850°C in Kelvin

print(f"Safety factor at room temp: {sf_room:.3f}")
print(f"Safety factor at 850°C: {sf_hot:.3f}")
# Expected: sf_hot < sf_room
```

---

## 🐛 5. Common Issues and Solutions

### Issue: Backend fails to start

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
# Make sure you're in the backend directory when running uvicorn
```

### Issue: Frontend shows "NEXT_PUBLIC_BACKEND_URL is not set"

**Solution**:
```bash
cd frontend
# Create .env.local file
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local
# Restart Next.js dev server
npm run dev
```

### Issue: CORS error in browser

**Error**: "Access to fetch... has been blocked by CORS policy"

**Solution**:
- Verify backend is running on port 8000
- Check `backend/app/main.py` includes `http://localhost:3000` in CORS origins
- Restart backend server

### Issue: Frontend shows "Unable to connect to prediction service"

**Solution**:
1. Verify backend is running: http://localhost:8000/health
2. Check `.env.local` has correct URL
3. Check browser console for actual error
4. Try curl:
```bash
curl http://localhost:8000/health
```

---

## 📊 6. Success Criteria

### Backend ✅
- [ ] All 3 models return different predictions
- [ ] Input validation works with helpful error messages
- [ ] Auto-normalization works for composition 95-105%
- [ ] Automatic Kelvin conversion logged
- [ ] Logging middleware shows request timing
- [ ] `/version` endpoint returns model versions
- [ ] Swagger docs show detailed descriptions and examples

### Frontend ✅
- [ ] All 4 new components render correctly (Loader, RiskBadge, MetricCard, ModelHeader)
- [ ] Model metadata displayed properly
- [ ] Color-coded risk levels work
- [ ] Stress limit colors change based on value
- [ ] Loading spinner appears during API calls
- [ ] Error messages are user-friendly
- [ ] Empty state shows before first prediction

### Integration ✅
- [ ] Frontend successfully calls backend API
- [ ] No CORS errors
- [ ] Timeout handling works (try backend down scenario)
- [ ] All 3 models accessible from UI
- [ ] Physics metadata shows for physics_heuristic model
- [ ] Safety factors show for safety_conservative model

---

## 🚀 7. Next Steps

After local testing succeeds:

1. **Deploy Backend** to Render.com
2. **Update Environment Variable** on Vercel: `NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com`
3. **Test Production** deployment
4. **Monitor Logs** for any issues

---

## 📝 8. Key Changes in v2.0

### Backend
- ✅ Realistic physics module with Arrhenius equations
- ✅ Modular prediction service architecture
- ✅ Enhanced input validation (±5% auto-normalization)
- ✅ Logging middleware for all requests
- ✅ `/version` endpoint with deployment info
- ✅ Detailed Swagger documentation

### Frontend
- ✅ 4 new reusable components (Loader, RiskBadge, MetricCard, ModelHeader)
- ✅ Enhanced API client with timeout and error type differentiation
- ✅ Improved UI with gradients and animations
- ✅ Color-coded metrics based on values
- ✅ Professional empty/loading/error states

---

**Version**: 2.0.0
**Last Updated**: 2025-12-11
**Tested On**: macOS/Linux/Windows
