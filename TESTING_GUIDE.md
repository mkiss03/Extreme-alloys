# Tesztelési Útmutató - Extreme Alloys Refactoring

## Áttekintés

Ez az útmutató segít ellenőrizni a projekt átdolgozásának minden funkcióját. A fő ellenőrzési pontok:

1. **Backend API**: 3 különböző modell különböző eredményeket ad
2. **Frontend-Backend kommunikáció**: Vercel deployment helyesen kapcsolódik a backend-hez
3. **UI megjelenítés**: Modell metaadatok (verzió, stratégia, konfidencia) megjelennek
4. **Input validáció**: Hibás bemenet esetén érthető hibaüzenetek

---

## 1. Backend Tesztelés (Swagger UI)

### 1.1 Backend Elindítása (Local)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 1.2 Swagger UI Megnyitása

Navigálj a böngészőben: **http://localhost:8000/docs**

### 1.3 Elérhető Modellek Listázása

1. Kattints a **GET /api/v1/predict/models** endpointra
2. Kattints "Try it out" → "Execute"
3. **Elvárt eredmény**: 3 modell listázása:
   - `gnn` - Graph Neural Network (75% confidence, data_driven)
   - `physics_heuristic` - Physics-based (65% confidence, physics_inspired)
   - `safety_conservative` - Safety Conservative (90% confidence, safety_conservative)

### 1.4 Modellek Összehasonlítása - Ugyanaz a bemenet, különböző eredmények

Használd ezt a teszt bemenetet mindhárom modellnél:

```json
{
  "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
  "temperature_c": 850,
  "pressure_mpa": 150,
  "cycles": 10000,
  "model_type": "gnn"
}
```

#### Test 1: GNN Model
1. **POST /api/v1/predict/extreme_alloy** endpointnál kattints "Try it out"
2. Illeszd be a fenti JSON-t (model_type: "gnn")
3. Execute
4. **Elvárt eredmény**:
   ```json
   {
     "creep_lifetime_hours": ~2000-5000,
     "failure_probability": 0.3-0.7,
     "stress_limit_mpa": 300-600,
     "model_type": "gnn",
     "model_strategy": "data_driven",
     "model_version": "gnn_demo_v0.1",
     "model_confidence": 0.75
   }
   ```

#### Test 2: Physics Heuristic Model
1. Ugyanazt a bemenetet használd, de változtasd: `"model_type": "physics_heuristic"`
2. Execute
3. **Elvárt eredmény**:
   - `creep_lifetime_hours`: **kb. 15%-kal ALACSONYABB** mint GNN
   - `failure_probability`: **kb. +0.05 MAGASABB** mint GNN
   - `stress_limit_mpa`: **kb. 10%-kal ALACSONYABB** mint GNN
   - `model_strategy`: "physics_inspired"
   - `model_confidence`: 0.65
   - `physics_metadata`: Megjelenik (Arrhenius faktor, LMP, stb.)

#### Test 3: Safety Conservative Model
1. Változtasd: `"model_type": "safety_conservative"`
2. Execute
3. **Elvárt eredmény**:
   - `creep_lifetime_hours`: **kb. 40%-kal ALACSONYABB** mint a fizikai modell (60% safety factor)
   - `failure_probability`: **kb. +0.15 MAGASABB** mint a fizikai modell
   - `stress_limit_mpa`: **kb. 20%-kal ALACSONYABB** mint a fizikai modell
   - `model_strategy`: "safety_conservative"
   - `model_confidence`: 0.90
   - `safety_factors`: Megjelenik (lifetime_factor: 0.6, stb.)

### ✅ Ellenőrzési Checklist (Backend)

- [ ] Mind a 3 modell különböző `creep_lifetime_hours` értéket ad ugyanarra a bemenetre
- [ ] Mind a 3 modell különböző `failure_probability` értéket ad
- [ ] Mind a 3 modell különböző `stress_limit_mpa` értéket ad
- [ ] GNN: `model_confidence` = 0.75
- [ ] Physics Heuristic: `model_confidence` = 0.65, `physics_metadata` megjelenik
- [ ] Safety Conservative: `model_confidence` = 0.90, `safety_factors` megjelenik
- [ ] Sorrend: GNN ≈ optimista > Physics Heuristic ≈ realistább > Safety ≈ legkonzervatívabb

---

## 2. Input Validáció Tesztelése (Swagger)

### 2.1 Hibás Composition Formátum

```json
{
  "composition": "Ni55Cr20",  // ❌ Hiányzik a ':'
  "temperature_c": 850,
  "pressure_mpa": 150,
  "cycles": 10000,
  "model_type": "gnn"
}
```

**Elvárt**: 400 Bad Request, hibaüzenet: "Composition must contain 'Element:Percentage' pairs"

### 2.2 Túl Magas Hőmérséklet

```json
{
  "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
  "temperature_c": 3000,  // ❌ Túl magas
  "pressure_mpa": 150,
  "cycles": 10000,
  "model_type": "gnn"
}
```

**Elvárt**: 400 Bad Request, hibaüzenet: "Temperature ... exceeds typical alloy operating range (max ~2000°C)"

### 2.3 Negatív Nyomás

```json
{
  "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
  "temperature_c": 850,
  "pressure_mpa": -50,  // ❌ Negatív
  "cycles": 10000,
  "model_type": "gnn"
}
```

**Elvárt**: 422 Unprocessable Entity vagy 400, hibaüzenet: "Pressure cannot be negative"

### 2.4 Összetétel Összege Nem 100%

```json
{
  "composition": "Ni:30,Cr:20",  // Összesen csak 50%
  "temperature_c": 850,
  "pressure_mpa": 150,
  "cycles": 10000,
  "model_type": "gnn"
}
```

**Elvárt**: 400 Bad Request, hibaüzenet: "Total composition is only 50.0%. This is unusually low."

### ✅ Ellenőrzési Checklist (Validáció Backend)

- [ ] Hibás composition formátum → érthető hibaüzenet
- [ ] Túl magas/alacsony hőmérséklet → specifikus hibaüzenet tartománnyal
- [ ] Negatív nyomás → érthető hibaüzenet
- [ ] Negatív cycles → érthető hibaüzenet
- [ ] Összetétel összege <50% vagy >150% → érthető hibaüzenet
- [ ] Összetétel 90-110% között → auto-normalizálás 100%-ra (warning log)

---

## 3. Frontend Tesztelés (Local Development)

### 3.1 Frontend Elindítása

```bash
cd frontend
npm install
# Hozz létre .env.local fájlt:
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local
npm run dev
```

Navigálj: **http://localhost:3000**

### 3.2 UI Metaadatok Megjelenítése

1. Töltsd ki a formot:
   - Composition: `Ni:55,Cr:20,Mo:10,W:12,Co:3`
   - Temperature: `850`
   - Pressure: `150`
   - Cycles: `10000`
   - Model: Válaszd ki **GNN** modellt
2. Kattints "Predict Behavior"
3. **Ellenőrizd a Results panelben**:
   - [ ] Megjelenik egy szürke box fent: **"Model: gnn"** és **"data_driven"** badge
   - [ ] Megjelenik: **"Version: gnn_demo_v0.1"**
   - [ ] Megjelenik: **"Confidence: 75%"**
   - [ ] Megjelenik: **Creep Lifetime** (kék box)
   - [ ] Megjelenik: **Failure Probability** (piros box)
   - [ ] Megjelenik: **Stress Limit** (lila box)

### 3.3 Modellek Közötti Váltás UI-ban

1. Változtasd a modellt **Physics Heuristic**-ra
2. Kattints "Predict Behavior"
3. **Ellenőrizd**:
   - [ ] Model badge frissül: "physics_inspired"
   - [ ] Version: "physics_heuristic_v0.1"
   - [ ] Confidence: 65%
   - [ ] **Az értékek KÜLÖNBÖZNEK** az előző GNN prediktáláséitól

4. Változtasd a modellt **Safety Conservative**-ra
5. Kattints "Predict Behavior"
6. **Ellenőrizd**:
   - [ ] Model badge: "safety_conservative"
   - [ ] Version: "safety_v0.1"
   - [ ] Confidence: 90%
   - [ ] **Creep Lifetime a LEGALACSONYABB** a 3 közül
   - [ ] **Failure Probability a LEGMAGASABB** a 3 közül

### 3.4 Frontend Input Validáció

#### Test 1: Hibás Composition
1. Írd be: `Ni55Cr20` (nincs ':')
2. Kattints "Predict Behavior"
3. **Elvárt**: Piros hibaüzenet megjelenik a mező alatt: "Composition must include Element:Percentage pairs"

#### Test 2: Túl Magas Hőmérséklet
1. Írd be Temperature: `2500`
2. Kattints "Predict Behavior"
3. **Elvárt**: Piros hibaüzenet: "Temperature exceeds realistic range (max 2000°C)"

#### Test 3: Negatív Nyomás
1. Írd be Pressure: `-50`
2. Kattints "Predict Behavior"
3. **Elvárt**: Piros hibaüzenet: "Pressure cannot be negative"

### ✅ Ellenőrzési Checklist (Frontend Local)

- [ ] Mind a 3 modell különböző eredményt mutat
- [ ] Modell metadata (type, strategy, version, confidence) helyesen megjelenik
- [ ] Loading spinner megjelenik predikció közben
- [ ] Hibás bemenet esetén piros hibaüzenet jelenik meg a mezők alatt
- [ ] Főhibaüzenet megjelenik a Results panelben server error esetén
- [ ] Empty state ikon jelenik meg amikor nincs még predikció

---

## 4. Vercel Deployment Tesztelése

### 4.1 Előfeltételek

1. Backend deployed és fut (pl. Render.com: `https://extreme-alloys.onrender.com`)
2. Frontend deployed Vercel-re
3. Environment variable beállítva Vercel-ben:
   - `NEXT_PUBLIC_BACKEND_URL` = `https://extreme-alloys.onrender.com`

### 4.2 CORS Ellenőrzés

1. Nyisd meg a Vercel deployed alkalmazást (pl. `https://extreme-alloys.vercel.app`)
2. Nyisd meg a böngésző Developer Tools-t (F12)
3. Menj a **Network** tabra
4. Tölts ki egy valid formot és kattints "Predict Behavior"
5. **Ellenőrizd a Network tabban**:
   - [ ] Megjelenik egy POST request: `https://extreme-alloys.onrender.com/api/v1/predict/extreme_alloy`
   - [ ] Status Code: **200 OK** (nem 403, nem CORS error)
   - [ ] Response tartalmazza a prediction JSON-t
   - [ ] **Nincs** `CORS policy` error a Console tabban

### 4.3 Backend URL Helyesség

**Ellenőrizd a Network Request URL-t**:
- ✅ Helyes: `https://extreme-alloys.onrender.com/api/v1/predict/extreme_alloy`
- ❌ Helytelen: `https://extreme-alloys.onrender.com//api/v1/...` (dupla slash)

Ha dupla slash van, az API client automatikusan eltávolítja a trailing slash-t a `NEXT_PUBLIC_BACKEND_URL`-ből.

### 4.4 Production UI Tesztelés

Ismételd meg a **3. Frontend Tesztelés** összes lépését a Vercel deployed verzión:

- [ ] 3 modell különböző eredményt ad
- [ ] Metadata megjelenik helyesen
- [ ] Input validáció működik
- [ ] Hibaüzenetek érthetők

### ✅ Ellenőrzési Checklist (Vercel Production)

- [ ] Fetch sikeresen megy a backend-re (200 OK)
- [ ] Nincs CORS error
- [ ] URL helyes (nincs dupla slash)
- [ ] UI megjelenítés ugyanúgy működik mint local-ban
- [ ] Hibaüzenetek megjelennek frontend és backend erroroknál

---

## 5. Backend CORS Konfiguráció Ellenőrzés

### 5.1 Ellenőrizd a `backend/app/main.py` CORS beállításait

```python
# Győződj meg róla, hogy a Vercel domain be van állítva:
if ENV == "production":
    origins = [
        "https://extreme-alloys.vercel.app",
        "https://extreme-alloys-frontend.vercel.app",
        # Add meg a tényleges Vercel domain-t!
    ]
```

### 5.2 Ha más a Vercel domain

1. Nézd meg az **aktuális Vercel deployment URL-t**
2. Add hozzá a `main.py` origins listájához
3. Redeploy a backend-et
4. Teszteld újra

---

## 6. Összefoglaló Gyors Teszt Checklist

### Backend (Swagger)
- [ ] `/predict/models` lista 3 modellt
- [ ] GNN model működik, confidence 75%
- [ ] Physics Heuristic model működik, confidence 65%, physics_metadata van
- [ ] Safety Conservative model működik, confidence 90%, safety_factors van
- [ ] Mind a 3 modell különböző értékeket ad ugyanarra a bemenetre
- [ ] Hibás input validációk működnek, érthető hibaüzenetekkel

### Frontend (Local)
- [ ] UI megjelenít mindent: model type, strategy, version, confidence
- [ ] 3 modell közötti váltás működik
- [ ] Client-side validáció működik (piros hibaüzenetek a mezőknél)
- [ ] Loading state animáció megjelenik
- [ ] Error state megjelenik server error esetén

### Vercel Production
- [ ] Fetch sikeresen megy a backend-re (nincs CORS error)
- [ ] URL helyes (nincs //)
- [ ] Mind a 3 modell működik production-ban is
- [ ] UI metadata megjelenik
- [ ] Hibaüzenetek működnek

---

## 7. Gyakori Hibák és Megoldások

### Hiba: CORS Error Vercel-ben

**Tünet**: Console-ban `Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy`

**Megoldás**:
1. Ellenőrizd `backend/app/main.py` CORS origins listáját
2. Add hozzá a Vercel domain-t
3. Redeploy a backend-et

### Hiba: 404 Not Found

**Tünet**: Network tab mutatja: 404 error `/api/v1/predict/extreme_alloy`

**Megoldás**:
1. Ellenőrizd hogy a backend valóban fut-e (nyisd meg `/docs` URL-t)
2. Ellenőrizd `NEXT_PUBLIC_BACKEND_URL` environment variable-t

### Hiba: Dupla Slash URL

**Tünet**: Request URL: `https://backend.com//api/v1/...`

**Megoldás**: Az `apiClient.ts` automatikusan eltávolítja a trailing slash-t, de ha továbbra is probléma van:
1. Ellenőrizd `NEXT_PUBLIC_BACKEND_URL` értékét (ne legyen `/` a végén)
2. Redeploy Vercel-ben

### Hiba: Backend Timeout

**Tünet**: Request hosszú ideig pending, majd timeout

**Megoldás**:
1. Render.com free tier néha "alszik" - első request 30-60 másodpercig tarthat
2. Várj 1 percet, próbáld újra
3. Ellenőrizd backend logs-ot Render dashboard-on

---

## 8. Tesztelési Prioritások

### Critical (Kötelező)
1. ✅ 3 modell különböző értéket ad (backend)
2. ✅ Vercel fetch sikeresen megy (nincs CORS error)
3. ✅ UI megjeleníti model metadata-t

### Important (Fontos)
4. ✅ Input validáció működik érthető hibaüzenetekkel
5. ✅ Loading és error states helyesen működnek
6. ✅ Production és local egyformán működik

### Nice to Have
7. Physics metadata megjelenik Physics Heuristic modellnél
8. Safety factors megjelenik Safety Conservative modellnél
9. Auto-normalizáció működik 90-110% composition-nél

---

## Sikerkritériumok

A refactoring **SIKERES**, ha:

✅ **Backend**: Mind a 3 modell működik, különböző eredményeket ad, validáció működik
✅ **Frontend**: Metadata megjelenik, 3 modell közötti váltás működik, validáció működik
✅ **Integration**: Vercel → Render kommunikáció hibátlan (nincs CORS, nincs 404)
✅ **UX**: Hibaüzenetek érthetők, loading state megjelenik

---

**Verzió**: 0.2.0
**Utolsó frissítés**: 2025-11-28
**Refactoring Commit**: dc28aea
