# Viva Question Answers

**1. Why should developers avoid directly pushing to `main`?**
Direct pushes bypass code review and CI validation entirely, so untested or
broken code can reach the branch every deployment is built from. Branch
protection + PR-only merges guarantee every change on `main` has already
passed tests and been reviewed.

**2. What is the purpose of a Pull Request beyond simply merging code?**
A PR is a review checkpoint and an audit trail: it documents *why* a change
was made (description, checklist), triggers automated validation (CI),
gives collaborators a place to discuss and request changes, and creates a
permanent, searchable record linking a feature to the exact commits and
discussion that produced it.

**3. Why should CI execute before a PR is merged?**
Because the whole point is to catch regressions *before* they land on
`main`, not after. Running CI post-merge only tells you `main` is broken,
by which point every other branch built from it inherits the bug.

**4. What is the difference between a Docker image and a container?**
An image is an immutable, layered filesystem + metadata template (the
"class"); a container is a running (or stopped) instance of that image with
its own writable layer, process namespace, and network stack (the
"object"). One image can back many simultaneously running containers.

**5. Why should Docker images be versioned?**
Versioning makes deployments reproducible and reversible: you can always
identify, redeploy, or roll back to the exact artifact that was tested,
rather than an ambiguous "whatever `main` currently builds to."

**6. Why is `latest` insufficient for production traceability?**
`latest` is a mutable pointer that gets silently reassigned to whatever was
pushed most recently. Two people (or two deploys) referencing "latest" at
different times can be running completely different code with no way to
tell from the tag alone which commit produced it.

**7. Why should the same Docker artifact be promoted rather than rebuilt?**
Rebuilding re-resolves dependencies and can pull in newer transitive
package versions, base image patches, or a different build environment —
producing a *different* artifact than the one that was actually tested.
Promoting the already-built, already-tested image guarantees what ships is
byte-for-byte what CI validated.

**8. What is the purpose of a container registry?**
It's the durable, versioned distribution point for built images — the
"artifact repository" of the pipeline. It stores every tagged image, lets
any environment (staging, production, another developer's machine) pull the
exact same bytes, and enables rollback by keeping older versions available
after a newer one is pushed.

**9. What is the difference between the CI workflow and release workflow?**
CI (`ci.yml`) runs on every Pull Request and answers "is this change safe to
merge?" — it tests and does a build-only Docker validation, but publishes
nothing. Release (`release.yml`) runs only when a semantic-version tag is
pushed (i.e. after merge) and answers "ship this exact, already-reviewed
commit" — it builds, tags, and pushes the image to the registry.

**10. Why should registry credentials be stored as secrets?**
Hard-coding credentials in a workflow file exposes them to anyone who can
read the repository (including public forks' PR diffs) and leaves them in
Git history forever, even if later "removed". GitHub Actions secrets are
encrypted at rest, injected only at runtime, and automatically redacted from
logs.

**11. How can you identify which source-code commit produced a Docker image?**
Two ways here: (a) the release workflow also tags the image with the short
Git commit SHA (e.g. `student-ml-api:92f4abc`), and (b) OCI labels baked
into the image (`org.opencontainers.image.revision`) record the commit,
inspectable via `docker inspect`.

**12. Why does Docker layer ordering affect CI/CD performance?**
Docker caches each instruction as a layer and reuses a cached layer if
neither it nor anything above it in the Dockerfile changed. Copying
`requirements.txt` and running `pip install` *before* copying application
source means editing `app.py` only invalidates the final, cheap `COPY`
layer — the expensive dependency-installation layer stays cached. Copying
everything (`COPY . .`) up front invalidates the dependency-install layer on
every single source change, forcing a full reinstall every build.

**13. How would you rollback from version `1.1.0` to `1.0.0`?**
`docker pull ghcr.io/quttoshi/student-ml-api:1.0.0` followed by
`docker run` (after removing/stopping the `1.1.0` container). No code
change, no rebuild — just running a previously published, already-tested
image tag. See `docs/rollback.md`.

**14. What is the relationship between a Git tag and a Docker image tag?**
The Git tag (`v1.1.0`) marks the exact source commit a release corresponds
to; the release workflow derives the Docker image tag (`1.1.0`) from it
automatically by stripping the leading `v`. They are intentionally kept in
lockstep so that `git checkout v1.1.0` and `docker pull ...:1.1.0` always
refer to the same logical release.

**15. In an MLOps system, what additional problems arise when the application
version and model version change independently?**
The API/application version and the underlying model version can now drift
out of sync — a bug fix to the API (`1.1.0`) doesn't necessarily mean the
model changed, and a new model can be deployed without any API code
changing at all. This means: (a) both must be surfaced independently in
`/health` (as this repo does with `application_version` and
`model_version`) so consumers and monitoring can tell which changed; (b)
rollback decisions need to consider both axes separately — rolling back a
bad model doesn't necessarily mean rolling back the API image, and vice
versa; (c) reproducibility and traceability records (Part 21) need to track
model provenance (training data/version) in addition to the Docker image
digest, since the same API image could in principle be paired with
different model artifacts over time.
