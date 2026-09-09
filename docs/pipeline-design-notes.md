# Pipeline Design Notes

## Merge strategy (Part 8)

| PR | Strategy used | Why |
|---|---|---|
| #1 `feature/prediction-api` | Merge commit | The first PR — kept every individual commit (`feat:`, `test:`, `ci:`, `docs:`) visible in `main`'s history as separate, meaningful steps, since this was the foundational PR and its internal history is worth preserving for anyone reading `git log` later. |
| #2 `feature/ci-demo` | Squash and merge | Its two commits (deliberately break a test, then fix it) are only meaningful *as a pair* and only within the PR's own timeline. Squashing collapses them into one clean `main` entry ("demonstrate CI failure/recovery") instead of leaving a broken-then-fixed state visible in `main`'s own history. |
| #3, #5 `docs/update-traceability-*` | Squash and merge | Single-purpose, single-commit documentation updates — squash vs. merge-commit makes no practical difference here, but squash keeps `main`'s history flatter for small doc-only changes. |
| #4 `feature/model-metadata` | Squash and merge | Two commits (`feat:` + `docs:`) that together form one logical unit ("ship v1.1.0's health endpoint change"); squashing keeps `main` to one entry per shippable feature. |
| #6 `fix/dockerfile-label-cache-order` | Squash and merge | Single logical fix, delivered as one commit; consistent with the rest of the small, single-purpose PRs. |

**General rule applied:** merge commit for the PR whose internal commit
history is itself worth preserving (the initial feature build-out); squash
for every PR that is really "one logical change" made of incidental
intermediate commits. Rebase-and-merge was avoided throughout, since it
rewrites the feature branch's commit SHAs — for a repo whose whole point is
traceability (Part 21), keeping the original commits' identities stable
until they're intentionally squashed at merge time is simpler to reason
about than a rebase's silent SHA changes.

## Why CI must not publish images from every Pull Request (Part 22)

`ci.yml` runs `pytest` and a build-only Docker validation on every PR, but
**never** logs into a registry or pushes anything. `release.yml` is the only
workflow that publishes, and it only runs on a semantic-version tag push
(i.e. after merge). Reasons this separation matters:

1. **Unreviewed code shouldn't produce distributable artifacts.** A PR is,
   by definition, not-yet-approved code. Publishing an image from every PR
   push means anyone who opens a PR — including from a fork, in an
   open-source setting — can cause a real artifact to land in the registry
   before a human has reviewed anything.
2. **Tag noise and registry bloat.** Iterating on a PR can mean dozens of
   pushes. Publishing on every one would flood the registry with
   short-lived, meaningless images (most of which represent WIP code that
   never becomes a real release), making it hard to tell which images are
   actually meant to be run anywhere.
3. **`latest` would become meaningless.** If every PR push updated
   `latest`, it could point at unmerged, unreviewed, possibly broken code
   at any given moment — exactly the traceability problem `latest` already
   has (see `docs/viva-answers.md`, Q6), made worse.
4. **Registry credentials shouldn't be exposed to PR runs.** GitHub Actions
   intentionally restricts secrets on `pull_request`-triggered workflows
   from forks for this reason; keeping publishing entirely out of the CI
   workflow avoids ever needing registry credentials in that context at
   all.
5. **Version tags are the actual release contract.** The whole point of
   Part 13–15 is that a human deliberately decides "this commit on `main`
   is now version X.Y.Z" by pushing a tag. Publishing from every PR would
   bypass that decision point entirely — there would be no single moment
   that represents "this is a real, intentional release."
