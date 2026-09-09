# Docker Build Cache (Part 25)

## A caching bug found and fixed along the way

The original `Dockerfile` declared the OCI metadata `ARG`s and `LABEL`
*before* `COPY requirements.txt` / `RUN pip install`. Since `GIT_COMMIT` and
`BUILD_DATE` change on **every** build, that `LABEL` instruction's effective
content changes every time — and Docker's layer cache invalidates
sequentially: once one instruction's cache misses, every instruction after
it is rebuilt too, regardless of whether *their* inputs changed. That meant
the expensive `pip install` layer was being rebuilt on every single build,
release or local, even when `requirements.txt` hadn't changed at all.

**Fix:** moved the `ARG`/`LABEL`/`ENV` block to *after* the dependency and
source-copy layers, so only the cheap, already-last layers pay the
"changes every build" cost.

## Experiment 1 — modify only `app.py`

Baseline build (`GIT_COMMIT=commitA`), then a rebuild after touching only
`app.py`, with a *different* commit/date build-arg too (simulating a real
new commit):

```
#8  [2/7] RUN addgroup --system app && adduser --system --ingroup app app   CACHED
#9  [4/7] COPY requirements.txt .                                          CACHED
#10 [3/7] WORKDIR /app                                                     CACHED
#11 [5/7] RUN pip install --no-cache-dir -r requirements.txt               CACHED
#12 [6/7] COPY app.py .                                                    DONE 0.0s
#13 [7/7] COPY VERSION .                                                   DONE 0.0s
```

Every layer up through and including `pip install` was reused; only the
`COPY app.py` layer (and the trivial `COPY VERSION` after it) actually
re-ran. The expensive dependency install (which took ~37s cold) cost
**nothing** on this rebuild.

## Experiment 2 — modify `requirements.txt`

Same setup, but this time `requirements.txt` itself was touched:

```
#8  [2/7] RUN addgroup --system app && adduser --system --ingroup app app   CACHED
#9  [3/7] WORKDIR /app                                                     CACHED
#10 [4/7] COPY requirements.txt .                                          DONE 0.0s
#11 [5/7] RUN pip install --no-cache-dir -r requirements.txt               DONE 37.4s
#12 [6/7] COPY app.py .                                                    DONE 0.1s
#13 [7/7] COPY VERSION .                                                   DONE 0.0s
```

`COPY requirements.txt` is the first layer to see different content, so
Docker correctly reruns it and everything after it — including the full
`pip install` again — while the two `addgroup`/`WORKDIR` layers *before*
`COPY requirements.txt` still cache-hit.

## Why `COPY requirements.txt` + `RUN pip install` + `COPY app.py` beats `COPY . .`

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
```

vs.

```dockerfile
COPY . .
RUN pip install -r requirements.txt
```

With `COPY . .`, *any* file change anywhere in the build context — a
one-line edit to `app.py`, a docs typo fix, anything — invalidates that
single combined `COPY` layer, which sits immediately before `pip install`,
so `pip install` reruns on every build regardless of whether dependencies
actually changed. Separating the dependency manifest into its own `COPY`
means the dependency-install layer's cache key is tied *only* to
`requirements.txt`'s content — it's reused for every build where
dependencies didn't change, which in practice is almost all of them. This
matters most in CI/CD: a multi-minute `pip install` on every single commit,
versus a few seconds of cached reuse, is the difference between a pipeline
developers tolerate and one they route around.
