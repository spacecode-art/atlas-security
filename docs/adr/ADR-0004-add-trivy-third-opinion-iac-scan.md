# ADR-0004: Add Trivy as a third, non-blocking IaC scan opinion

## Status
Accepted

## Context
The original Atlas execution plan lists Trivy alongside Checkov, tfsec,
Semgrep, Grype, Syft, Cosign, and Gitleaks as part of Phase 2's toolset.
It was omitted from the initial build — Checkov (hard gate) + tfsec
(second opinion) already covered IaC misconfiguration, and adding a
third scanner with full overlap would be tooling for its own sake, not
better coverage.

Reviewing Trivy's actual `config` scan mode against Checkov and tfsec:
it uses an independent rule engine (Aqua's own, not Checkov's Bridgecrew
rules or tfsec's rules) and has historically caught misconfigurations
neither of the other two flag, particularly around IAM policy analysis
and newer AWS resource types. That's a real, non-redundant reason to
add it, distinct from "the plan says so."

## Decision
Add `reusable-trivy-scan.yml`, following the exact non-blocking pattern
already established for tfsec in `reusable-iac-scan.yml`:
`continue-on-error: true`, SARIF artifact uploaded regardless of
findings, zero effect on merge gating. Checkov remains the only hard
gate (unchanged from ADR-0010 in `atlas-foundation`).

Trivy ships as its own reusable workflow rather than folded into
`reusable-iac-scan.yml` — that file already has two jobs (Checkov,
tfsec); a third scanner with an independent triage cadence is easier
to reason about, version, and skip per-consumer as a separate
`workflow_call`.

## Consequences
- A finding here has no ADR-citation requirement the way a Checkov
  skip does, since nothing blocks on it yet — same status as tfsec's
  16 findings before ADR-0010/0013 triaged them. If Trivy findings
  accumulate untriaged, that's a signal to either triage them properly
  or drop the scanner — silent, ignored findings help no one.
- Three independent IaC scanners now run per consumer PR. Worth
  revisiting Actions-minutes budget (see Cost Model) as more consumers
  wire this in.
- No consumer is required to adopt this — it's opt-in, same as every
  other reusable workflow here.
## Update — 2026-08-25: pin to commit SHA after CVE-2026-33634

The initial version of `reusable-trivy-scan.yml` referenced a
non-existent tag (`@0.29.0`) and failed on first real CI run. While
fixing it, found that `aquasecurity/trivy-action` suffered a real
supply-chain compromise on 2026-03-19 (CVE-2026-33634,
GHSA-69fq-xp46-6x23): an attacker with compromised maintainer
credentials force-pushed malicious commits to 76 of 77 version tags,
including tags GitHub had marked "immutable." Only `v0.35.0`
(`57a97c7e7821a5776cebc9bb87c984fa69cba8f1`) survived, because it
happened to point at `master` HEAD when the attacker's tag-rewrite
automation ran — not because tags are actually a safe pin mechanism.

This directly confirms the open Spoofing gap already recorded in this
repo's own `docs/threat-model.md` ("no SHA/tag pinning for consumers
— `@main` only"). Fixed here as the first concrete instance: Trivy is
now pinned to the full commit SHA above, not a tag.

**Not yet extended to this repo's other actions** (`actions/checkout`,
`bridgecrewio/checkov-action`, `aquasecurity/tfsec-action`, etc.) or to
consumers pinning `atlas-security`'s own reusable workflows at `@main`
— that remains the threat model's open item, tracked in Future
Roadmap. This update closes the gap for Trivy specifically, as the
one action in this repo's supply chain with a *confirmed* real-world
compromise, not as a general policy change yet.  