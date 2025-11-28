# Extreme Alloys - Quick Start Guide

## 🚀 Gyors Indítás

### 1. Docker-rel (Ajánlott)

A legegyszerűbb módszer a teljes rendszer futtatására:

```bash
# Projekt gyökérből
docker-compose up --build

# Szolgáltatások:
# ✓ Backend API: http://localhost:8000
# ✓ Frontend UI: http://localhost:3000
# ✓ API Docs: http://localhost:8000/docs
```

### 2. Manuális Futtatás

#### Backend

```bash
cd backend

# Virtual environment létrehozása
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Függőségek telepítése
pip install -r requirements.txt

# API indítása
uvicorn app.main:app --reload

# Backend: http://localhost:8000
```

#### Frontend

```bash
cd frontend

# Függőségek telepítése
npm install

# Environment változó beállítása lokális fejlesztéshez
# Másold át a .env.example fájlt .env.local-ra
cp .env.example .env.local

# Szerkeszd a .env.local fájlt:
# NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Dev server indítása
npm run dev

# Frontend: http://localhost:3000
```

**Fontos:** A frontend a `NEXT_PUBLIC_BACKEND_URL` környezeti változót használja a backend eléréséhez:
- Lokálisan: `http://localhost:8000`
- Production (Vercel): `https://extreme-alloys.onrender.com` (vagy a saját backend URL-ed)

## 📊 Példa Használat

### API-n keresztül (curl)

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

**Válasz:**
```json
{
  "creep_lifetime_hours": 3456.7,
  "failure_probability": 0.35,
  "stress_limit_mpa": 642.1,
  "model_version": "physics_heuristic_v0.1",
  "confidence": 0.5
}
```

### Python-ból

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/predict/extreme_alloy",
    json={
        "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
        "temperature_c": 850.0,
        "pressure_mpa": 150.0,
        "cycles": 10000
    }
)

result = response.json()
print(f"Predicted lifetime: {result['creep_lifetime_hours']:.1f} hours")
print(f"Failure probability: {result['failure_probability']*100:.1f}%")
```

### Frontend UI-on keresztül

1. Nyisd meg: http://localhost:3000
2. Töltsd ki a formot:
   - **Composition**: `Ni:55,Cr:20,Mo:10,W:12,Co:3`
   - **Temperature**: `850` °C
   - **Pressure**: `150` MPa
   - **Cycles**: `10000`
   - **Model Type**: `gnn`
3. Kattints a "Predict Behavior" gombra
4. Nézd meg az eredményeket a jobb oldali panelen

## 🎓 Model Training

### Alap Training

```bash
cd backend

# Training szintetikus adatokkal (demo)
python train_mlp.py
```

### Valódi Adatokkal

1. Készíts CSV fájlt: `data/processed/extreme_alloys_training.csv`

Formátum:
```csv
Ni,Cr,Mo,W,Co,temperature_c,pressure_mpa,cycles,creep_lifetime_hours,failure_probability,stress_limit_mpa
55,20,10,12,3,850,150,10000,3456.7,0.35,642.1
60,18,8,10,4,900,180,15000,2234.5,0.52,580.3
```

2. Futtasd a training scriptet:
```bash
python train_mlp.py
```

3. A modell mentve lesz: `backend/app/models/saved/extreme_alloy_gnn.pth`

4. A prediction service automatikusan használni fogja

## 🧪 Tesztek Futtatása

```bash
cd backend

# Összes teszt
pytest app/tests/

# Coverage report-tal
pytest --cov=app --cov-report=html

# Csak API tesztek
pytest app/tests/test_api.py

# Csak model tesztek
pytest app/tests/test_models.py
```

## 📁 Projekt Struktúra

```
extreme-alloys/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # REST endpoints
│   │   ├── models/   # PyTorch models
│   │   ├── services/ # Business logic
│   │   └── tests/    # Unit tests
│   ├── train_mlp.py  # Training script
│   └── requirements.txt
├── frontend/         # Next.js frontend
│   └── app/
│       ├── components/
│       └── api-client.ts
├── data/            # Data storage
│   ├── raw/
│   ├── processed/
│   └── notebooks/
├── docs/            # Documentation
└── docker-compose.yml
```

## 🎯 Főbb Funkciók

### ✅ Kész és Működik

- ✓ FastAPI backend teljes CRUD API-val
- ✓ Feature engineering pipeline (parsing, normalizálás)
- ✓ GNN és Creep model struktúrák
- ✓ Model training script
- ✓ Smart model loading with fallback
- ✓ Next.js frontend Tailwind CSS-szel
- ✓ Docker & docker-compose support
- ✓ Unit tesztek (API + models)
- ✓ Swagger API dokumentáció

### 🔄 Jelenleg Physics-Based Heuristics

A rendszer jelenleg fizika-alapú heurisztikákat használ, ha nincs betanított model:

- Hőmérséklet és nyomás hatása az élettartamra
- Ötvözet összetétel (Ni, Cr) hatása
- Ciklusok hatása

### 🎯 Következő Lépések

1. **Valódi adat gyűjtés**: Materials Project / NIMS API
2. **Model training**: Valódi creep tesztek adatain
3. **GNN implementáció**: Graph struktúra az atomokkal
4. **Production deployment**: Kubernetes / cloud platform

## 🆘 Gyakori Problémák

### Port foglalt
```bash
# Ellenőrizd mi fut a portokon
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Állítsd le a docker-compose-t
docker-compose down
```

### Model nem található
Ha a predikció `physics_heuristic_v0.1` modelt használ, ez normális - nincs még betanított model. Futtasd a training scriptet.

### Frontend nem éri el a backend-et
Ellenőrizd a `NEXT_PUBLIC_BACKEND_URL` environment változót:
- **Lokálisan**: `frontend/.env.local` fájlban legyen `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000`
- **Vercel-en**: Project Settings → Environment Variables-ben add hozzá a változót
- **Böngésző console**: Nézd meg, hogy megjelenik-e a `[ExtremeAlloys] Using backend URL: ...` log fejlesztői módban

## 📚 További Dokumentáció

- **API Docs**: `docs/api.md`
- **Architecture**: `docs/architecture.md`
- **Model Specs**: `docs/model_spec.md`
- **Training Guide**: `backend/TRAINING.md`
- **Main README**: `README.md`

## 💡 Tippek

1. **Swagger UI**: Interaktív API tesztelés a `/docs` endpointon
2. **Logs**: Minden API call loggolva van
3. **Hot reload**: Mind a backend, mind a frontend támogatja
4. **Type safety**: TypeScript a frontendon, Pydantic a backendon

## 🎉 Sikeres Setup Ellenőrzése

```bash
# Backend health check
curl http://localhost:8000/health

# Prediction test
curl -X POST http://localhost:8000/api/v1/predict/extreme_alloy \
  -H "Content-Type: application/json" \
  -d '{"composition":"Ni:55,Cr:20,Mo:10,W:12,Co:3","temperature_c":850,"pressure_mpa":150,"cycles":10000}'

# Frontend: Nyisd meg http://localhost:3000 böngészőben
```

Ha minden választ ad, akkor minden rendben működik! 🚀

## 🚀 Production Deployment

### Backend Deployment (Render.com)

1. Jelentkezz be a [Render.com](https://render.com)-ra
2. Hozz létre új **Web Service**-t
3. Kapcsold össze a GitHub repo-dat
4. Beállítások:
   - **Name**: `extreme-alloys-backend`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Environment Variables:
   ```
   ENV=production
   LOG_LEVEL=INFO
   MODEL_PATH=./models/saved
   ```
6. Deploy! 🎉
7. Mentsd el a backend URL-t (pl. `https://extreme-alloys.onrender.com`)

### Frontend Deployment (Vercel)

1. Jelentkezz be a [Vercel](https://vercel.com)-be
2. Importáld a projektet: "Add New" → "Project" → GitHub repo kiválasztása
3. **FONTOS beállítások**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` ← NE HAGYD KI!
   - **Build Command**: `npm run build` (automatikus)
   - **Output Directory**: `.next` (automatikus)
4. **Environment Variables** (Project Settings):
   ```
   NEXT_PUBLIC_BACKEND_URL=https://extreme-alloys.onrender.com
   ```
   ⚠️ Cseréld le a saját Render backend URL-edre!
5. Deploy! 🚀

### Deployment Ellenőrzése

```bash
# Backend health check (Render URL-del)
curl https://extreme-alloys.onrender.com/health

# Frontend ellenőrzés
# Nyisd meg a Vercel deployment URL-t böngészőben
# Próbálj predikciót futtatni
# Ellenőrizd a browser console-ban: látszik-e a "[ExtremeAlloys] Using backend URL: ..." log
```

### Gyakori Deployment Problémák

**❌ Frontend nem éri el a backend-et**
- Ellenőrizd, hogy a `NEXT_PUBLIC_BACKEND_URL` be van-e állítva Vercel-en
- Nézd meg a Vercel deployment logs-ot
- Ellenőrizd a browser Network tab-ot: milyen URL-re megy a kérés?

**❌ Backend nem indul el Render-en**
- Ellenőrizd a Build Logs-ot
- Nézd meg, hogy a Start Command helyes-e
- Port: Render automatikusan beállítja a `$PORT` változót

**❌ CORS hiba**
- A backend `main.py`-ban a CORS middleware engedi az összes origint development módban
- Production-ben szűkítsd le a `allow_origins` listát a frontend URL-re
