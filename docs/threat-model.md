# Atlas Security — Threat Model (STRIDE)

## Scope
This threat model covers `atlas-security` as it actually exists today:
the three reusable GitHub Actions workflows
(`reusable-secrets-scan.yml`, `reusable-iac-scan.yml`,
`reusable-opa-scan.yml`), the OPA/Conftest policies under
`policies/opa/`, and their consumption by other Atlas repositories
(`atlas-foundation` today, `Tawira` once its SBOM/Grype/Cosign pipeline
lands). It does not cover the security of infrastructure inside a
*consuming* repo — that's each consumer's own threat model — or the
security of GitHub as a platform.

## Assets
- The reusable workflow YAML files themselves — the actual product
- `policies/opa/*.rego` — determines pass/fail for every consumer's
  Terraform plan
- The `checkov-skip-checks` workflow_call input — consumer-supplied,
  but the *mechanism* for accepting it is this repo's design
- `GITHUB_TOKEN`, used by the tfsec step to annotate results
- Repository write access / branch protection on `main`

## STRIDE Analysis

### Spoofing
- **Threat:** Every consumer currently pins reusable workflows to
  `@main`, not a tag or commit SHA (see `reusable-opa-scan.yml`'s
  checkout and every `uses:` line in `atlas-foundation`'s `ci.yml`). A
  compromised or malicious commit to `main` is live for every consumer
  on their very next CI run, with no review step on the consumer side.
- **Mitigation:** Partial. This threat has two layers: (1) this repo's
  own third-party Action dependencies (`actions/checkout`,
  `checkov-action`, etc.) were themselves pinned by mutable tag — fixed
  in ADR-0007, every one now pinned to a commit SHA. (2) Consumers
  still reference *this repo's* reusable workflows by `@main`, not a
  tag or SHA — still open. Planned mitigation: tag a versioned release
  (`@v1`) once the workflow surface stabilizes (see README Future
  Roadmap), so consumers pin to a reviewed release instead of tracking
  `main` directly.

### Tampering
- **Threat:** `tagging.rego`'s `deny` rule is weakened or removed in a
  PR that also edits `tagging_test.rego` to match — since this repo's
  own CI (`ci.yml`, `opa test policies/opa/`) only proves the tests
  and policy agree with *each other*, a single coordinated PR can
  defeat the actual protection for every consumer while still showing
  green.
- **Mitigation:** PR review is the only gate today. There is no
  adversarial or independently-maintained test suite that a
  compromised PR author couldn't also edit in the same change.

### Repudiation
- **Threat:** Because consumers track `@main` rather than a pinned
  SHA or tag, there's no easy answer to "which exact version of this
  workflow ran for a given historical CI run" once `main` has moved on.
- **Mitigation:** GitHub Actions resolves and records the exact commit
  SHA of a reusable workflow at the time a run executes, so a
  retroactive audit is technically possible via the run's logs — but
  nothing in this repo makes that easy or obvious to do.

### Information Disclosure
- **Threat:** The tfsec step in `reusable-iac-scan.yml` uses
  `github_token: ${{ secrets.GITHUB_TOKEN }}` to post findings —
  meaning specific infrastructure detail (resource types, ARNs,
  misconfiguration detail) becomes visible to anyone with read access
  to the consuming repo's PR/Actions history, not just the person who
  opened the PR.
- **Mitigation:** Acceptable today since both `atlas-security` and
  `atlas-foundation` are private repos with a small, trusted
  contributor set. Would need revisiting if a consumer repo ever has
  broader read access than its infra findings should have.

### Denial of Service
- **Threat:** Every reusable workflow pins a specific tool version
  (`checkov-version: 3.3.10`, `conftest-version: 0.69.0`) as a
  deliberate single-source-of-truth design choice. If that exact image
  tag or GitHub release is ever pulled or becomes unavailable upstream,
  every consumer's CI breaks simultaneously, at the same time, for a
  reason none of them control directly.
- **Mitigation:** None today beyond noticing quickly — this is the
  first candidate incident type named in the README's own (currently
  unwritten) Incident Runbook section. See the runbook below.

### Elevation of Privilege
- **Threat:** `checkov-skip-checks` lets a consuming repo skip
  arbitrary Checkov check IDs with zero enforcement from this side.
  The convention is "every skip must cite an ADR in the consuming
  repo" (as `atlas-foundation` does correctly) — but that's a social
  convention, not something `reusable-iac-scan.yml` can verify. A
  careless or malicious consumer could pass an empty-justification
  skip list and this repo would have no way to know or block it.
- **Mitigation:** Partial. `scripts/lint-skip-citations.py` (ADR-0008)
  now exists and correctly detects an uncited skip when run against a
  workflow file — verified against `atlas-foundation`'s real `ci.yml`
  and against a deliberately-broken copy. It is not yet wired into any
  consumer's CI as an actual gating step, so today it's a tool someone
  has to remember to run, which is a smaller version of the same
  underlying gap (enforcement depends on a human choosing to invoke
  it), not yet a closed one.

## Known Gaps (honest, not hidden)
- Consumers still pin this repo's reusable workflows by `@main`, not a
  tag or SHA (ADR-0007 fixed this repo's *own* third-party Action
  pins; consumer-facing pinning of this repo is the remaining half).
- Branch protection rules on `main` are assumed, not documented or
  verified in this repo.
- `scripts/lint-skip-citations.py` (ADR-0008) exists and works but
  isn't wired into any consumer's CI as a gate yet — enforcement is
  still opt-in until that happens.
- No Dependabot (or equivalent) keeping the ADR-0007 SHA pins current
  — pinning solves the mutable-tag threat but introduces a new one
  (silently stale dependencies) if nothing ever bumps them.
- No signing or provenance verification of this repo's own workflow
  files — notable given this repo's own Future Roadmap includes adding
  Cosign signing *for other repos' artifacts*, but doesn't yet apply
  that same rigor to itself.