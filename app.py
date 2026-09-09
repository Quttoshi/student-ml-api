"""student-ml-api: FastAPI inference service."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

APP_NAME = "student-ml-api"
VERSION_FILE = Path(__file__).resolve().parent / "VERSION"

# Tracked independently of APP_VERSION - the model doesn't change on every API release.
MODEL_VERSION = "model-1"


def get_version() -> str:
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "0.0.0-unknown"


APP_VERSION = get_version()

app = FastAPI(title=APP_NAME, version=APP_VERSION)


class PredictRequest(BaseModel):
    value: float = Field(..., description="Numeric input to run the prediction on")


def _clean_number(value: float) -> float | int:
    """Return int for whole numbers so {"input": 10} isn't {"input": 10.0}."""
    return int(value) if value.is_integer() else value


@app.get("/health")
def health() -> dict:
    return {
        "status": "healthy",
        "application": APP_NAME,
        "application_version": APP_VERSION,
        "model_version": MODEL_VERSION,
    }


@app.post("/predict")
def predict(payload: PredictRequest) -> dict:
    prediction = payload.value * 2
    return {
        "input": _clean_number(payload.value),
        "prediction": _clean_number(prediction),
    }


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError) -> JSONResponse:
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
