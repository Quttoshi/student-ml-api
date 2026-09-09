# Traceability Records (Part 21)

For each release, the full chain must be documented:

```
Pull Request Number -> Merge Commit SHA -> Git Tag -> Docker Image Tag -> Docker Image Digest
```

Fill in each row from the actual repository/Actions run once the release
workflow has completed — values below are placeholders until then.

## v1.0.0

| Field | Value |
|---|---|
| PR | #1 (`feature/prediction-api` — app, tests, Dockerfile, CI/release workflows), #2 (`feature/ci-demo` — mandatory Part 6 deliberate-failure demonstration) |
| Merge Commit | `d6d740f333a80097d3ca3d475d0be28314c0bff1` (merge of PR #2, tip of `main` at the time `v1.0.0` was tagged) |
| Git Tag | v1.0.0 |
| Docker Image | `ghcr.io/quttoshi/student-ml-api:1.0.0` |
| Image Digest | `sha256:0c2678c5cb6a532fba9e3cd37bdfa87b06d0a4321c4f811df2de19c74da29409` |

## v1.1.0

| Field | Value |
|---|---|
| PR | #4 (`feature/model-metadata`) |
| Merge Commit | `e56749f6a70b74d88c8895cbdeb3bb5d058eaaca` |
| Git Tag | v1.1.0 |
| Docker Image | `ghcr.io/quttoshi/student-ml-api:1.1.0` (also tagged `latest`) |
| Image Digest | `sha256:bb3fe1af846fa8247c7a6e53be158aac58296291957e182e719e3e107e3982c2` |

## How to fill these in

- **PR number / Merge Commit SHA**: from the PR page on GitHub after
  merging (the "squash and merge"/"merge" button shows the resulting commit
  SHA; it's also `git log --oneline -1 main` right after `git pull`).
- **Docker Image Digest**: printed in the `release.yml` run's job summary
  (the workflow writes a "Release Traceability" table via
  `$GITHUB_STEP_SUMMARY`), or via:
  ```bash
  docker inspect --format='{{index .RepoDigests 0}}' ghcr.io/quttoshi/student-ml-api:1.0.0
  ```
