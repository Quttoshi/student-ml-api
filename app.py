"""student-ml-api

A minimal FastAPI inference service used to demonstrate a production-style
MLOps CI/CD workflow (Pull Requests, GitHub Actions CI, Docker, and a
container registry release pipeline).

The prediction logic itself is intentionally trivial -- the point of this
exercise is the delivery pipeline, not model quality.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

APP_NAME = "student-ml-api"
VERSION_FILE = Path(__file__).resolve().parent / "VERSION"


def get_version() -> str:
    """Read the application version from the VERSION file.

    Reading the version from a single file (rather than hard-coding it in
    source) keeps VERSION as the one source of truth that both the app and
    the release workflow agree on.
    """
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "0.0.0-unknown"


APP_VERSION = get_version()

app = FastAPI(title=APP_NAME, version=APP_VERSION)


class PredictRequest(BaseModel):
    """Request body for POST /predict."""

    value: float = Field(..., description="Numeric input to run the prediction on")


def _clean_number(value: float) -> float | int:
    """Return an int when the float is a whole number, else the float.

    Keeps JSON responses looking like {"input": 10} instead of
    {"input": 10.0} for whole-number inputs, matching the API contract.
    """
    return int(value) if value.is_integer() else value


@app.get("/health")
def health() -> dict:
    """Liveness/readiness probe."""
    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION,
    }


@app.post("/predict")
def predict(payload: PredictRequest) -> dict:
    """Return a simple mathematical prediction for the given input.

    prediction = value * 2

    This is a placeholder for a real model inference call; the exercise
    is about the delivery pipeline around the API, not the model itself.
    """
    prediction = payload.value * 2
    return {
        "input": _clean_number(payload.value),
        "prediction": _clean_number(prediction),
    }


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError) -> JSONResponse:
    """Return a clear 422 payload for missing/invalid /predict input.

    FastAPI/Pydantic already reject missing or non-numeric "value" fields
    automatically; this handler just normalizes the error shape.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": "Invalid or missing input",
            "errors": jsonable_encoder(exc.errors()),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
