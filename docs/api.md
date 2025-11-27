# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication. This will be added in future versions.

## Endpoints

### Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "extreme-alloys-api",
  "version": "0.1.0"
}
```

### Prediction Health

**GET** `/predict/health`

Check if the prediction service is available.

**Response:**
```json
{
  "status": "healthy",
  "service": "prediction-api",
  "models_available": ["gnn", "creep", "ensemble"]
}
```

### Predict Alloy Behavior

**POST** `/predict/extreme_alloy`

Predict alloy behavior under extreme conditions.

**Request Body:**
```json
{
  "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
  "temperature_c": 850.0,
  "pressure_mpa": 150.0,
  "cycles": 10000,
  "model_type": "gnn"
}
```

**Parameters:**
- `composition` (string, required): Alloy composition in format "Element:Percentage,Element:Percentage"
- `temperature_c` (float, required): Operating temperature in Celsius
- `pressure_mpa` (float, required): Operating pressure in MPa
- `cycles` (integer, required): Number of thermal/mechanical cycles
- `model_type` (string, optional): Model type - "gnn", "creep", or "ensemble" (default: "gnn")

**Response:**
```json
{
  "creep_lifetime_hours": 3456.7,
  "failure_probability": 0.35,
  "stress_limit_mpa": 642.1,
  "model_version": "gnn_v1.0",
  "confidence": 0.85
}
```

**Status Codes:**
- `200 OK`: Successful prediction
- `400 Bad Request`: Invalid input parameters
- `500 Internal Server Error`: Server error during prediction

### Generate Prediction Report

**POST** `/predict/report`

Generate a comprehensive prediction report with recommendations.

**Request Body:** Same as `/predict/extreme_alloy`

**Response:**
```json
{
  "input_parameters": {
    "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
    "temperature_c": 850.0,
    "pressure_mpa": 150.0,
    "cycles": 10000
  },
  "predictions": {
    "creep_lifetime_hours": 3456.7,
    "failure_probability": 0.35,
    "stress_limit_mpa": 642.1,
    "model_version": "gnn_v1.0",
    "confidence": 0.85
  },
  "recommendations": [
    "✓ Good stability predicted under specified conditions"
  ],
  "metadata": {
    "report_version": "1.0",
    "analysis_type": "extreme_conditions"
  }
}
```

## Error Handling

All endpoints return errors in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

**400 Bad Request**
- Missing required field
- Temperature out of valid range (-273°C to 3000°C)
- Negative pressure value
- Invalid composition format
- Composition percentages don't sum to ~100%

**500 Internal Server Error**
- Model loading failure
- Unexpected processing error

## Rate Limiting

Currently not implemented. May be added in future versions.

## Examples

### Python

```python
import requests

url = "http://localhost:8000/api/v1/predict/extreme_alloy"
payload = {
    "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
    "temperature_c": 850.0,
    "pressure_mpa": 150.0,
    "cycles": 10000,
    "model_type": "gnn"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Predicted lifetime: {result['creep_lifetime_hours']} hours")
print(f"Failure probability: {result['failure_probability']*100}%")
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/api/v1/predict/extreme_alloy', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    composition: "Ni:55,Cr:20,Mo:10,W:12,Co:3",
    temperature_c: 850.0,
    pressure_mpa: 150.0,
    cycles: 10000,
    model_type: "gnn"
  })
});

const result = await response.json();
console.log(result);
```

### cURL

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

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
