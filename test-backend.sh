#!/bin/bash
# Test script to check backend endpoints

BACKEND_URL="${1:-https://extreme-alloys.onrender.com}"

echo "🧪 Testing Extreme Alloys Backend: $BACKEND_URL"
echo "================================================"

# Test 1: Root endpoint (GET)
echo ""
echo "1️⃣ Testing GET / (root)..."
curl -s -X GET "$BACKEND_URL/" | jq . 2>/dev/null || curl -s -X GET "$BACKEND_URL/"

# Test 2: Health check (GET)
echo ""
echo "2️⃣ Testing GET /health..."
curl -s -X GET "$BACKEND_URL/health" | jq . 2>/dev/null || curl -s -X GET "$BACKEND_URL/health"

# Test 3: Prediction health (GET)
echo ""
echo "3️⃣ Testing GET /api/v1/predict/health..."
curl -s -X GET "$BACKEND_URL/api/v1/predict/health" | jq . 2>/dev/null || curl -s -X GET "$BACKEND_URL/api/v1/predict/health"

# Test 4: Prediction endpoint (POST)
echo ""
echo "4️⃣ Testing POST /api/v1/predict/extreme_alloy..."
curl -s -X POST "$BACKEND_URL/api/v1/predict/extreme_alloy" \
  -H "Content-Type: application/json" \
  -d '{
    "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
    "temperature_c": 850.0,
    "pressure_mpa": 150.0,
    "cycles": 10000
  }' | jq . 2>/dev/null || curl -s -X POST "$BACKEND_URL/api/v1/predict/extreme_alloy" \
  -H "Content-Type: application/json" \
  -d '{
    "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
    "temperature_c": 850.0,
    "pressure_mpa": 150.0,
    "cycles": 10000
  }'

# Test 5: Wrong method (GET instead of POST) - should give 405
echo ""
echo "5️⃣ Testing GET /api/v1/predict/extreme_alloy (should fail with 405)..."
curl -s -w "\nHTTP Status: %{http_code}\n" -X GET "$BACKEND_URL/api/v1/predict/extreme_alloy"

echo ""
echo "================================================"
echo "✅ Backend test complete!"
