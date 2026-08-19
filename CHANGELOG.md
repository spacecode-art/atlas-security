# Changelog

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
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