# ADR-0009: The ingest workflow self-merges a PR, not a direct push

## Status
Accepted

## Context
ADR-0006 designed `ingest-scan-results.yml` to commit and `git push`
directly to `main` using its own `GITHUB_TOKEN`. That design didn't
account for this repo's own branch protection ("changes must be made
through a pull request"), which applies to every push to `main`
regardless of which token makes it — including the bot's. Every real
dispatch since ADR-0006 shipped reached this workflow successfully,
parsed correctly, and ran the ingest script correctly, but failed at
the final `git push` with `GH013: Repository rule violations`. Grype's
real findings against Tawira (a genuine CVE, CVE-2025-60876) never
reached the dashboard because of this, not because anything about the
scanning or dispatch was wrong.

Two fixes were considered:
1. **Bypass list**: add the Actions bot to `main`'s ruleset bypass
   list. Fast, but permanently weakens "every change to main is a
   reviewable PR" — not just for this workflow, for anything that
   later runs as that same actor.
2. **Self-merged PR**: have the workflow open its own PR from a short-
   lived branch and merge it via the API, the same mechanism a human
   uses. Slightly more moving parts, but the protection rule is
   respected uniformly rather than carved around.

## Decision
Self-merged PR (option 2). The workflow branches as
`dashboard/ingest-<tool>-<run_id>`, commits, pushes the branch (not
main — so the protection rule doesn't apply to that push), opens a PR
with `gh pr create`, and immediately merges it with `gh pr merge
--squash --delete-branch`. This repo's ruleset has no required-
approving-review rule, so the merge succeeds without waiting on a
human — if that ever changes, this workflow would start queueing PRs
instead of failing silently, which is a safer failure mode than a
silent push rejection.

## Consequences
- Every dashboard ingestion now leaves a real, auditable PR in this
  repo's history (auto-merged, but visible) instead of a bare commit
  — arguably better audit trail than the original design, not just a
  workaround.
- If a required-approving-review rule is ever added to `main`, this
  workflow's `gh pr merge` will start failing (queued, not merged) and
  needs a human to notice and either merge manually or adjust the
  ruleset for this specific path. Not automatically detected today.
- One more API call per ingestion (`gh pr create` + `gh pr merge`)
  than a direct push — negligible at current volume (a few scans a
  day, per ADR-0005).
- The 8 real dispatches that failed under the old design are gone —
  their data was never committed. Nothing to backfill from; the CSV's
  first real automated row starts from whenever this fix merges.