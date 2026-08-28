# ADR-0010: IAM Access Analyzer / least-privilege report descoped from this repo

## Status
Accepted

## Context
The Atlas Path plan's Phase 2 checklist includes: "IAM Access
Analyzer / least-privilege generation: burst-deploy briefly against a
real (empty) account to generate one real report, capture it, tear
down." Nothing in `atlas-security` does this, and it was never
explicitly decided whether that's a gap or a non-goal here.

`atlas-security`'s actual scope is reusable CI/CD security tooling —
everything here runs against code or Terraform plan output, not a
live AWS account. IAM Identity Center config and the account
structure Access Analyzer would evaluate both live in
`atlas-foundation`.

## Decision
Descope IAM Access Analyzer / least-privilege reporting from
`atlas-security`. If built, it belongs in `atlas-foundation` as a
burst-deploy exercise per the original plan — not here.

## Consequences
- `atlas-security` stays static/CI-time tooling only, no direct AWS
  account interaction of its own.
- Tracked as an open item on `atlas-foundation`'s roadmap, not a
  silent drop.
- No code change in this repo from this ADR — it exists to make the
  scope call explicit and reviewable.