#!/usr/bin/env python3
"""
Backend Deployment Diagnostic Script
Tests the deployed backend API to verify it's working correctly
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "https://extreme-alloys.onrender.com"
TIMEOUT = 30  # seconds

def test_health_check():
    """Test the /health endpoint"""
    print("\n🔍 Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=TIMEOUT)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health Check Passed")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Environment: {data.get('environment')}")
            return True
        else:
            print(f"   ❌ Health Check Failed")
            return False
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout - Backend might be sleeping (Render free tier)")
        print(f"   Retrying in 30 seconds...")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_models_endpoint():
    """Test the /api/v1/predict/models endpoint"""
    print("\n🔍 Testing Models Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/predict/models", timeout=TIMEOUT)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Models Endpoint Passed")
            print(f"   Available Models: {', '.join([m['name'] for m in data.get('models', [])])}")
            return True
        else:
            print(f"   ❌ Models Endpoint Failed")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_prediction_endpoint():
    """Test the /api/v1/predict/extreme_alloy endpoint"""
    print("\n🔍 Testing Prediction Endpoint (GNN Model)...")

    test_data = {
        "composition": "Ni:55,Cr:20,Mo:10,W:12,Co:3",
        "temperature_c": 850,
        "pressure_mpa": 150,
        "cycles": 10000,
        "model_type": "gnn"
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/predict/extreme_alloy",
            json=test_data,
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Prediction Endpoint Passed")
            print(f"   Model: {data.get('model_type')} ({data.get('model_strategy')})")
            print(f"   Confidence: {data.get('model_confidence')*100:.0f}%")
            print(f"   Creep Lifetime: {data.get('creep_lifetime_hours'):.2f} hours")
            print(f"   Failure Probability: {data.get('failure_probability'):.3f}")
            print(f"   Stress Limit: {data.get('stress_limit_mpa'):.2f} MPa")
            return True
        else:
            print(f"   ❌ Prediction Endpoint Failed")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_cors_headers():
    """Test CORS headers"""
    print("\n🔍 Testing CORS Configuration...")
    try:
        # Simulate preflight request
        response = requests.options(
            f"{BACKEND_URL}/api/v1/predict/extreme_alloy",
            headers={
                "Origin": "https://bhomev2-fh6c.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            },
            timeout=TIMEOUT
        )

        cors_header = response.headers.get("Access-Control-Allow-Origin")
        print(f"   Status Code: {response.status_code}")
        print(f"   Access-Control-Allow-Origin: {cors_header}")

        if cors_header == "https://bhomev2-fh6c.vercel.app":
            print(f"   ✅ CORS Configuration Correct")
            return True
        else:
            print(f"   ⚠️  CORS might not be configured for Vercel domain")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("="*60)
    print("🚀 Backend Deployment Diagnostic Tool")
    print(f"   Backend URL: {BACKEND_URL}")
    print("="*60)

    results = []

    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Models Endpoint", test_models_endpoint()))
    results.append(("Prediction Endpoint", test_prediction_endpoint()))
    results.append(("CORS Configuration", test_cors_headers()))

    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")

    print(f"\n   Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n   🎉 All tests passed! Backend is fully operational.")
        return 0
    else:
        print("\n   ⚠️  Some tests failed. Check the logs above for details.")
        print("\n   Common issues:")
        print("   - Render.com free tier might sleep (first request takes 30-60s)")
        print("   - CORS configuration needs backend redeploy")
        print("   - Check Render.com logs for errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
