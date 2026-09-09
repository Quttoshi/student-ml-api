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
| PR | # |
| Merge Commit | |
| Git Tag | v1.0.0 |
| Docker Image | `ghcr.io/<owner>/student-ml-api:1.0.0` |
| Image Digest | `sha256:` |

## v1.1.0

| Field | Value |
|---|---|
| PR | # |
| Merge Commit | |
| Git Tag | v1.1.0 |
| Docker Image | `ghcr.io/<owner>/student-ml-api:1.1.0` |
| Image Digest | `sha256:` |

## How to fill these in

- **PR number / Merge Commit SHA**: from the PR page on GitHub after
  merging (the "squash and merge"/"merge" button shows the resulting commit
  SHA; it's also `git log --oneline -1 main` right after `git pull`).
- **Docker Image Digest**: printed in the `release.yml` run's job summary
  (the workflow writes a "Release Traceability" table via
  `$GITHUB_STEP_SUMMARY`), or via:
  ```bash
  docker inspect --format='{{index .RepoDigests 0}}' ghcr.io/<owner>/student-ml-api:1.0.0
  ```
