# Atlas Security

> Shared security tooling and policy-as-code for the Atlas platform —
> consumed by every other Atlas repository, not duplicated into each one.

## Problem Statement

Security scanning done independently per-repo drifts: skip-lists
diverge, tool versions diverge, nobody remembers why repo A allows a
finding that repo B blocks. Atlas Security exists to be the single
source of truth for scan policy across every Atlas repository —
reusable GitHub Actions workflows and OPA/Conftest policies that other
repos call by reference, version-pinned, instead of reimplementing.

## Overview

This repo does not scan itself in isolation — its value is proven by
being *consumed*. `atlas-foundation`'s CI is retrofitted in this
phase to call `atlas-security`'s reusable workflows instead of running
Checkov inline, closing the loop from "security tooling exists" to
"security tooling is actually load-bearing infrastructure."

## Objectives

- Reusable GitHub Actions workflows: secrets scanning (Gitleaks), IaC
  scanning (Checkov + tfsec), SBOM generation and vulnerability
  scanning (Syft + Grype), artifact signing (Cosign), SAST (Semgrep)
- OPA/Conftest policies for repo-specific standards not covered by
  off-the-shelf scanners
- A single, versioned skip-list/exception mechanism, ADR-linked, that
  every consuming repo inherits rather than reinvents
- STRIDE threat model and incident runbook for this repo and the
  shared tooling itself
- Prove the platform claim by retrofitting `atlas-foundation` to
  consume it

## Architecture Diagram

_(added once the first reusable workflow exists — no diagram before
there's something real to diagram)_

## Repository Structure

```text
atlas-security/
├── .github/
│   └── workflows/
│       ├── reusable-secrets-scan.yml
│       ├── reusable-iac-scan.yml
│       ├── reusable-sbom-scan-sign.yml
│       └── reusable-sast.yml
├── policies/
│   └── opa/                  # Rego policies (Conftest)
├── docs/
│   ├── adr/
│   ├── threat-model.md
│   └── incident-runbook.md
├── sample-app/                # minimal container image, exists only
│                               # so SBOM/scan/sign has something real
│                               # to operate on
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
└── README.md
```

## Current Status

Repository initialized. No reusable workflows built yet — this
README exists first, per the Atlas execution plan's standing rule.

## Future Roadmap

- Gitleaks reusable workflow (first, cheapest, highest-impact)
- IaC scan reusable workflow, generalized from `atlas-foundation`
- OPA/Conftest custom policies
- SBOM + Grype + Cosign pipeline against `sample-app/`
- Semgrep SAST
- Threat model, incident runbook
- Retrofit `atlas-foundation/.github/workflows/ci.yml` to consume
  this repo's reusable workflows