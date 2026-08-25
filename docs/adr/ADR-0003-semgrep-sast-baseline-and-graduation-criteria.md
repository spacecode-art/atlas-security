# ADR-0003: Semgrep SAST baseline and graduation criteria

## Status
Accepted

## Context
`reusable-sast-scan.yml` was added with `fail-on-findings` defaulting to
`false`, deferring the hard-fail decision to "an ADR, pending" — this
is that ADR.

atlas-foundation consumed the workflow for the first time on
2026-08-14 (PR #2, run 31817899632), scanning `terraform/` with the
`p/terraform` ruleset: 63 rules against 32 files, 4 findings, all at
`warning` severity (none at `error`).

Reviewing the SARIF output against the actual codebase:
- 3 findings (`aws-provider-static-credentials`) fire on the `test`/
  `test` dummy credentials required by every MiniStack-backed provider
  block (`bootstrap/backend`, `environments/development`,
  `environments/management`). These are not real credentials — the
  rule has no way to distinguish a MiniStack placeholder from a
  genuine leaked key.
- 1 finding (`aws-subnet-has-public-ip-address`) duplicates a decision
  already accepted and documented: `CKV_AWS_130` is already skipped
  in `security-scan`'s Checkov config, citing ADR-0010's deliberate
  public-subnet design.

Net result: **0 findings represent real, un-triaged risk.** The
4-finding baseline is entirely explainable noise from local-emulator
tooling and an already-accepted architecture decision.

## Decision
- Baseline as of 2026-08-14: 4 findings, 0 unexplained. Record this
  run (`31817899632`) as the reference baseline.
- Keep `fail-on-findings: false` for now — not because the tool is
  noisy, but because a single clean run isn't enough evidence that
  the noise pattern (MiniStack creds, duplicate subnet finding) is
  stable across future changes.
- Graduation criteria to flip `fail-on-findings: true`:
  1. **Done** — the 3 credential findings are suppressed inline via
     `# nosemgrep: terraform.aws.security.aws-provider-static-credentials...`
     in all three `atlas-foundation` provider blocks, each citing this
     ADR.
  2. Confirm the subnet finding stays consistent with Checkov's
     already-accepted `CKV_AWS_130` skip — if one drifts from the
     other, that's a signal worth investigating before gating on it.
  3. Three consecutive clean runs (0 findings, post-suppression)
     across real PRs, not just re-runs of the same commit.
- Once met, flip `fail-on-findings: true` in atlas-foundation's
  `ci.yml` call site and record that change here as a follow-up, not
  a new ADR.

## Consequences
- Semgrep currently reports advisory-only in CI — a real vulnerability
  introduced today would show up in the SARIF artifact and the job
  log, but would not block merge. This is an accepted, temporary gap,
  not an oversight.
- The 3 credential-pattern findings are now suppressed inline
  (`nosemgrep`, citing this ADR). Going forward, expect the finding
  count to hold at 1 — the accepted `aws-subnet-has-public-ip-address`
  finding — not 0, until criterion 2 and 3 above are also satisfied.
- This baseline is specific to `terraform/` scanned with `p/terraform`.
  If Semgrep's config or target directory changes (e.g. once app code
  exists per ADR-0001's Tawira containerization work), this baseline
  no longer applies and should be re-established, not assumed.