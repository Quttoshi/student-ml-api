# Failure Analysis (Part 26)

Three failures were deliberately reproduced and diagnosed: the mandatory
failing-test demonstration (Part 6), plus two of the optional failure
scenarios, both reproduced locally against the built `student-ml-api:1.0.0`
image.

---

## 1. Failed `pytest` (mandatory demonstration, Part 6)

**Symptom**
`GET /health` test asserted the wrong expected value:

```python
assert data["status"] == "wrong"
```

Pushing this to the `feature/prediction-api` branch made the **CI** workflow's
`Unit Tests` job fail, which failed the whole pull request check.

**Root Cause**
The assertion in `tests/test_app.py::test_health_returns_healthy_status` was
deliberately changed to expect `"wrong"` instead of `"healthy"`, which no
longer matches what `GET /health` actually returns.

**Evidence**
- Local repro: `pytest -v` fails with:
  `AssertionError: assert 'healthy' == 'wrong'`
- GitHub Actions: PR run shows the `Unit Tests` job with a red ❌ and the
  `CI` check on the PR reporting **Failing**.
  *(Screenshot/link recorded once pushed — see PR #1.)*

**Correction**
Reverted the assertion to:

```python
assert data["status"] == "healthy"
```

Committed as `fix: correct health endpoint test`, pushed, and the `CI`
workflow re-ran and passed (green ✅) on the same PR.

---

## 2. Application bound to `127.0.0.1` instead of `0.0.0.0`

**Symptom**
Container starts and reports healthy in its own logs, but the API is
completely unreachable from the host, even with the port published:

```
$ docker run -d --name student-ml-api-badport -p 5000:5000 student-ml-api:1.0.0 \
    uvicorn app:app --host 127.0.0.1 --port 5000

$ curl -m 3 http://localhost:5000/health
HTTP_CODE:000   # connection could not be established
```

**Root Cause**
`127.0.0.1` inside a container refers to the container's own network
namespace loopback interface, not the host. Docker's `-p 5000:5000` port
mapping forwards traffic to the container's external interface, which a
process bound to `127.0.0.1` never listens on. The container logs even
confirm this: `Uvicorn running on http://127.0.0.1:5000`.

**Evidence**

```
--- container logs ---
INFO:     Uvicorn running on http://127.0.0.1:5000 (Press CTRL+C to quit)
--- curl from host ---
HTTP_CODE:000 ERR:52
```

**Correction**
The Dockerfile's `CMD` explicitly binds `--host 0.0.0.0`:

```dockerfile
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
```

which makes the service reachable on every interface inside the container,
including the one Docker's port-forwarding targets. Re-running with the
real image (no CMD override) confirms `GET /health` succeeds.

---

## 3. Wrong container port mapping

**Symptom**
`docker run -p 5000:6000 student-ml-api:1.0.0` (host `5000` mapped to
container `6000`, but the app listens on `5000` inside the container):

```
$ curl -m 3 http://localhost:5000/health
HTTP_CODE:000   # connection refused
```

while the app is demonstrably healthy *inside* the container:

```
$ docker exec student-ml-api-wrongport python -c \
    "import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:5000/health').read())"
b'{"status":"healthy","application":"student-ml-api","version":"1.0.0"}'
```

**Root Cause**
Docker's `-p HOST:CONTAINER` mapping forwards `hostPort -> containerPort`.
The app is listening on container port `5000`, but the mapping was
`5000:6000`, i.e. host `5000` was wired to container port `6000`, on which
nothing is listening. No process is bound to `6000`, so the connection is
refused before it ever reaches the app.

**Evidence**
See the two `curl`/`docker exec` outputs above, captured from the same
image (`student-ml-api:1.0.0`) with no code changes — only the `-p` flag
differs.

**Correction**
Use the correct mapping, matching the image's `EXPOSE 5000` and the app's
actual listen port:

```
docker run -d --name student-ml-api -p 5000:5000 student-ml-api:1.0.0
curl http://localhost:5000/health   # 200 OK
```
