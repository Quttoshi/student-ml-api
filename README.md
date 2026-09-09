# student-ml-api

A minimal ML inference API used to demonstrate a production-style MLOps
delivery pipeline: feature branches, Pull Requests, GitHub Actions CI,
Docker, and a versioned release to a container registry (GHCR).

```
Git manages the evolution of source code. Pull Requests control how changes
enter the main branch. CI verifies those changes. Docker converts approved
source code into a reproducible artifact. The container registry stores and
distributes versioned artifacts that can later be delivered consistently to
staging and production.
```

## API

### `GET /health`

```json
{
  "status": "healthy",
  "application": "student-ml-api",
  "version": "1.0.0"
}
```

### `POST /predict`

Request:

```json
{ "value": 10 }
```

Response:

```json
{ "input": 10, "prediction": 20 }
```

`prediction = value * 2`. The model logic is intentionally trivial — this
exercise is about the delivery pipeline, not model quality.

## Local development

```bash
uv venv --python 3.12
uv pip install -r requirements-dev.txt

# run the app
.venv/Scripts/python.exe -m uvicorn app:app --host 0.0.0.0 --port 5000

# run the tests
.venv/Scripts/python.exe -m pytest -v
```

(Any standard `pip install -r requirements-dev.txt` + `venv` workflow works
the same way — `uv` is just what was used to build this repo.)

## Docker

```bash
docker build -t student-ml-api:1.0.0 .
docker run -d --name student-ml-api -p 5000:5000 student-ml-api:1.0.0
curl http://localhost:5000/health
```

Image metadata (OCI labels) baked in at build time:

```bash
docker inspect student-ml-api:1.0.0 --format '{{json .Config.Labels}}'
```

## Versioning & releases

- `VERSION` holds the current application version and is the single source
  of truth read by `app.py` at startup.
- A release is triggered by pushing a semantic-version Git tag (`vX.Y.Z`):
  `.github/workflows/release.yml` derives `X.Y.Z` from the tag automatically
  (never hard-coded), builds the Docker image, and pushes it to
  `ghcr.io/<owner>/student-ml-api` tagged `X.Y.Z`, `latest`, and the short
  commit SHA.
- `.github/workflows/ci.yml` runs on every Pull Request into `main`: it
  installs dependencies, runs `pytest`, and does a build-only Docker
  validation. It never publishes anything.

## Rollback

See [`docs/rollback.md`](docs/rollback.md) — restoring a previous version is
a `docker pull` of an already-built, already-tested image, not a rebuild.

## Project docs

- [`docs/branch-protection.md`](docs/branch-protection.md) — `main` branch protection settings
- [`docs/traceability.md`](docs/traceability.md) — PR → commit → tag → image → digest records
- [`docs/failure-analysis.md`](docs/failure-analysis.md) — deliberate failure/diagnosis log
- [`docs/rollback.md`](docs/rollback.md) — rollback & artifact-reproducibility walkthrough
- [`docs/viva-answers.md`](docs/viva-answers.md) — prepared answers to the viva questions
