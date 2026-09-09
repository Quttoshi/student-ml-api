# syntax=docker/dockerfile:1

# --- student-ml-api production image -----------------------------------
# Explicit, pinned base image (never :latest) for reproducible builds.
FROM python:3.12.10-slim

# Run as a non-root user (production best practice).
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Install dependencies first so this layer is cached independently of
# application source changes (see Part 25: COPY ordering / build cache).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the application source. Changing app.py alone will only bust
# this layer (and later), not the dependency-install layer above.
COPY app.py .
COPY VERSION .

# OCI image metadata / labels for traceability (overridable at build time).
# See Part 23: application version, git commit, repository, build date.
# Declared *after* the dependency/source layers above, on purpose: these
# ARGs (especially GIT_COMMIT and BUILD_DATE) change on every single build,
# so any layer that depends on them can never be cache-hit. Placing them
# this late means only these last few layers pay that cost, instead of
# invalidating (and re-running) the expensive pip install above every time.
ARG APP_VERSION=unknown
ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown
ARG REPOSITORY=unknown

LABEL org.opencontainers.image.title="student-ml-api" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT}" \
      org.opencontainers.image.source="${REPOSITORY}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.description="Student ML inference API (FastAPI)"

# Re-expose the build args as runtime env vars so the running app/tools
# can introspect exactly what produced this image.
ENV APP_VERSION=${APP_VERSION} \
    GIT_COMMIT=${GIT_COMMIT} \
    BUILD_DATE=${BUILD_DATE} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER app

EXPOSE 5000

# Bind 0.0.0.0 so the service is reachable from outside the container
# (binding 127.0.0.1 here would be unreachable from the host - see Part 26).
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
