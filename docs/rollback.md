# Rollback & Artifact Reproducibility (Parts 17 & 20)

## Part 17 — Prove artifact reproducibility

```bash
# Remove the local image entirely
docker rmi student-ml-api:1.0.0

# Pull the exact same artifact back from the registry
docker pull ghcr.io/quttoshi/student-ml-api:1.0.0

# Run it and confirm it behaves identically
docker run -d --name student-ml-api -p 5000:5000 ghcr.io/quttoshi/student-ml-api:1.0.0
curl http://localhost:5000/health
```

This proves:

```
Build Machine -> Container Registry -> Different Runtime Environment
```

without ever rebuilding the application. The bytes that were tested in CI
and built once in the release workflow are the exact bytes running here —
nothing was recompiled, re-`pip install`ed, or re-interpreted differently on
this machine.

**Evidence (actually run):**

```
$ docker inspect --format='{{index .RepoDigests 0}}' ghcr.io/quttoshi/student-ml-api:1.0.0
ghcr.io/quttoshi/student-ml-api@sha256:0c2678c5cb6a532fba9e3cd37bdfa87b06d0a4321c4f811df2de19c74da29409

$ docker rmi ghcr.io/quttoshi/student-ml-api:1.0.0
Untagged: ghcr.io/quttoshi/student-ml-api:1.0.0
Deleted: sha256:0c2678c5cb6a532fba9e3cd37bdfa87b06d0a4321c4f811df2de19c74da29409

$ docker pull ghcr.io/quttoshi/student-ml-api:1.0.0
Digest: sha256:0c2678c5cb6a532fba9e3cd37bdfa87b06d0a4321c4f811df2de19c74da29409
Status: Downloaded newer image for ghcr.io/quttoshi/student-ml-api:1.0.0
```

Same digest before deletion and after re-pulling — byte-identical artifact.

## Part 20 — Rollback exercise

Assume `1.1.0` has a production issue. Without touching source code and
without rebuilding anything:

```bash
docker rm -f student-ml-api
docker pull ghcr.io/quttoshi/student-ml-api:1.0.0
docker run -d --name student-ml-api -p 5000:5000 ghcr.io/quttoshi/student-ml-api:1.0.0
curl http://localhost:5000/health
# {"status": "healthy", "application": "student-ml-api", "version": "1.0.0"}
```

**Evidence (actually run):** before rollback, the running container
(`1.1.0`) reported:

```json
{"status":"healthy","application":"student-ml-api","application_version":"1.1.0","model_version":"model-1"}
```

After removing it, deleting the local `1.0.0` image entirely, and pulling
`1.0.0` fresh from GHCR:

```json
{"status":"healthy","application":"student-ml-api","version":"1.0.0"}
```

Correctly back to the old response shape (`version`, no
`application_version`/`model_version`) — confirming this is genuinely the
old code running, not a hybrid or a rebuild.

The registry keeps every previously released, previously tested version
available side by side:

```
Registry
  +-- 1.0.0  <- known good
  +-- 1.1.0  <- problematic
```

Rolling back is just running the older, already-verified tag again.

## Why this is easier than `git clone` + `pip install` + `python app.py`

| | Registry rollback | Source-based redeploy |
|---|---|---|
| What runs | The exact bytes that passed CI and were built once | Freshly re-resolved dependencies, freshly interpreted code |
| Speed | Seconds — just a pull of cached/known layers | Minutes — clone, resolve/install deps, hope nothing upstream changed |
| Reproducibility | Guaranteed identical (same image digest) | Not guaranteed — a transitive dependency may have published a new version since `1.0.0` was last built, silently changing behavior |
| Environment drift | None — the image bundles the exact OS packages, Python version, and libraries it was tested with | Depends entirely on whatever is already installed/available on the target machine |
| Failure surface | Docker pull/run only | Git availability, network access to PyPI, build toolchain, OS-level Python version drift |

In short: the Docker image is an immutable, already-tested artifact. A
`git clone && pip install && python app.py` redeploy re-does all of the work
that CI and the release build already did once, and can produce a
*different* result than what was originally tested if anything upstream has
changed since. Promoting a previously built artifact, instead of rebuilding
from source, is the entire point of a container registry in a CI/CD
pipeline.
