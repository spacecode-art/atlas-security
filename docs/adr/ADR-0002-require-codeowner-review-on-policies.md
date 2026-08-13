# ADR-0002: Require CODEOWNERS review on `policies/` and workflow changes

## Status
Accepted

## Context
The threat model's Tampering entry identifies a real gap: a single PR
can weaken a `deny` rule in `policies/opa/*.rego` and update the
matching `*_test.rego` in the same change, and this repo's own CI
(`opa test`) would show green — because CI only proves the policy and
its tests agree with *each other*, not that the policy still does its
job. The same class of risk applies to the reusable workflow YAML
files themselves: every consumer inherits a change on `main`
immediately, with no review step on their side (see the Spoofing and
Denial of Service entries in `docs/threat-model.md`).

This repo currently has one maintainer, so "require a second reviewer"
has no one to name yet — but the control should exist in the repo now,
so it activates automatically the moment a second contributor joins,
rather than being something that has to be remembered and added later.

## Decision
Add a `.github/CODEOWNERS` file requiring review on:
- `policies/opa/**` (the actual policy logic every consumer trusts)
- `.github/workflows/**` (the reusable workflows themselves)

GitHub branch protection on `main` must additionally have "Require
review from Code Owners" enabled for this to take effect — that
setting is not itself version-controlled, so it's tracked here as a
manual, documented step rather than something this ADR can fully
self-enforce.

## Consequences
- With a single maintainer, this is currently a no-op in practice (the
  owner can still approve their own PR under default GitHub settings,
  or the setting can be configured to block self-approval once there's
  a second person to approve).
- The moment a second contributor is added to this repo, every change
  to policy logic or workflow YAML requires their sign-off before
  merge — closing the Tampering gap without needing a follow-up ADR
  later.
- Does not address Repudiation (no SHA/tag pinning for consumers) or
  the unenforced skip-list-ADR-citation convention — both remain open,
  tracked in the threat model's Known Gaps.

## Manual step required (not code)
In the repo's GitHub settings → Branches → branch protection rule for
`main`: enable "Require a pull request before merging" and "Require
review from Code Owners."