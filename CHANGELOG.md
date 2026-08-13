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
- First real consumer: `atlas-foundation`'s CI now calls both
  workflows instead of running scanners inline