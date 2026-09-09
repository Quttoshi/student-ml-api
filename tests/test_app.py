"""Automated tests for student-ml-api.

Covers the four cases required by the assignment:
1. GET  /health
2. POST /predict - successful prediction
3. POST /predict - missing input
4. POST /predict - invalid input
"""
from fastapi.testclient import TestClient

from app import APP_VERSION, app

client = TestClient(app)


def test_health_returns_healthy_status():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["application"] == "student-ml-api"
    assert body["version"] == APP_VERSION


def test_predict_returns_correct_prediction():
    response = client.post("/predict", json={"value": 10})

    assert response.status_code == 200
    body = response.json()
    assert body["input"] == 10
    assert body["prediction"] == 20


def test_predict_missing_input_is_rejected():
    response = client.post("/predict", json={})

    assert response.status_code == 422


def test_predict_invalid_input_is_rejected():
    response = client.post("/predict", json={"value": "not-a-number"})

    assert response.status_code == 422


def test_predict_handles_negative_and_fractional_values():
    response = client.post("/predict", json={"value": -2.5})

    assert response.status_code == 200
    body = response.json()
    assert body["input"] == -2.5
    assert body["prediction"] == -5.0
