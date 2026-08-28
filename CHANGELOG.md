# Changelog

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.3] - <date you tagged it>

### Fixed
- `ingest-scan-results.yml` failed on every real dispatch since
  ADR-0006 shipped: branch protection on `main` rejected the bot's
  direct `git push`, silently dropping real Grype findings (including
  CVE-2025-60876) before they reached the dashboard
- Workflow now opens a short-lived branch and self-merges its own PR
  instead of pushing to `main` directly (ADR-0009)
- `gh pr create` required a dedicated `DASHBOARD_BOT_TOKEN`
  (fine-grained PAT, Contents + Pull requests read/write) since the
  default `GITHUB_TOKEN` is blocked from creating/approving PRs by a
  repo-wide setting — widening that setting repo-wide was rejected as
  too broad a blast radius for one job (ADR-0009 update)

### Added
- `docs/evidence/tawira/` — real SBOM, Grype, and Cosign verify
  output captured from Tawira's live CI, proving the SBOM/scan/sign
  pipeline and the ADR-0009 fix end-to-end

## [1.0.2] - <date you tagged it>

### Added
- `ingest-token` wired into `reusable-sbom-scan-sign.yml`'s Tawira
  call, completing dashboard ingestion for the second real consumer

## [1.0.1] - <date you tagged it>

### Added
- `scripts/lint-skip-citations.py` — enforces the skip-list
  ADR-citation convention in tooling instead of relying on PR review
  alone (ADR-0008)
- `lint-skip-citations.py` wired into `atlas-foundation`'s CI as an
  actual gating step (not just an available script)

### Changed
- Every third-party Action across every workflow pinned to a commit
  SHA instead of a mutable tag (ADR-0007)
- Consumers (`atlas-foundation`, `Tawira`) moved off `@main` onto
  pinned release tags for every reusable workflow reference

## [1.0.0] - 2026-08-27

### Added
- `ingest-scan-results.yml` — `repository_dispatch` receiver that
  commits scan results to `dashboard/metrics/scan-history.csv` on
  atlas-security's own `GITHUB_TOKEN` (ADR-0006), closing the manual-
  invocation gap left by ADR-0005
- Optional `ingest-token` secret + dashboard-dispatch step added to
  `reusable-iac-scan.yml` (Checkov, tfsec), `reusable-sast-scan.yml`
  (Semgrep), `reusable-sbom-scan-sign.yml` (Grype), and
  `reusable-secrets-scan.yml` (Gitleaks, count-only/redacted per
  ADR-0006 — raw secret matches never leave the runner)
- Repository initialized: governance files, README, CHANGELOG
- `reusable-secrets-scan.yml` — Gitleaks wrapper, full-history scan
- `reusable-iac-scan.yml` — Checkov (hard gate) + tfsec (non-blocking)
  wrapper, skip-list accepted as a `workflow_call` input so ADR-cited
  exceptions stay owned by the consuming repo
- `reusable-opa-scan.yml` + `policies/opa/tagging.rego` — first
  repo-specific policy not covered by off-the-shelf scanners, 6/6
  tests passing
- `reusable-sast-scan.yml` — Semgrep, soft-fail during baseline
  (ADR-0003 defines graduation criteria to hard-fail)
- `reusable-sbom-scan-sign.yml` — Syft (SBOM) + Grype (vuln scan) +
  Cosign (keyless/OIDC signing)
- Threat model (STRIDE) and incident runbook for this repo itself
- First real consumer: `atlas-foundation`'s CI now calls the secrets,
  IaC, and OPA workflows instead of running scanners inline
- Second real consumer: `Tawira` — containerized (ADR-0001), now
  calling all four workflows (secrets, SAST, and the full
  build/SBOM/scan/sign pipeline) from its own CI