# `main` Branch Protection Settings (Part 7)

Configured under **Settings → Branches → Branch protection rules → Add rule**
for branch name pattern `main`.

| Setting | Value | Why |
|---|---|---|
| Require a pull request before merging | ✅ Enabled | Blocks any direct push to `main`; every change must go through review. |
| Require approvals | 0 for solo work* | GitHub does not allow self-approval; with a single contributor, the PR-plus-passing-CI gate is the enforced review, not a second human. In a real team this would be set to **1+**. |
| Require status checks to pass before merging | ✅ Enabled | Prevents merging while `pytest` or the Docker build-check job is red. |
| Status checks required | `Unit Tests`, `Docker Build Validation` (job names from `ci.yml`) | These are the two required CI jobs from Part 5. |
| Require branches to be up to date before merging | ✅ Enabled | Ensures the PR was actually tested against the latest `main`, not a stale base. |
| Require conversation resolution before merging | ✅ Enabled | Forces open review comments to be addressed, not silently merged past. |
| Do not allow bypassing the above settings | ✅ Enabled (includes repo admins) | Without this, the repository owner could push straight to `main` and skip CI entirely, defeating the whole exercise. |
| Block force pushes | ✅ Enabled (default once a rule exists) | Protects `main`'s history from being rewritten. |
| Restrict deletions | ✅ Enabled | Prevents `main` from being deleted. |

\* If GitHub's UI requires a non-zero number to enable the "Require
approvals" checkbox at all, it is left **unchecked** for this solo-student
repository and only "Require status checks to pass" + "Require a pull
request before merging" are enforced. This still fully satisfies the
assignment's minimum bar: *require PR before merging, require successful
status checks, prevent direct pushes to `main`*.

## Net effect

- `git push origin main` from a local clone is rejected — even for the repo
  owner — unless it goes through an approved, green Pull Request.
- A PR cannot be merged from the GitHub UI while `ci.yml`'s jobs are
  red or still running.
- `main` can never be force-pushed or deleted.
