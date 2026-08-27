# ADR-0007: Pin every third-party Action to a commit SHA, not a tag

## Status
Accepted

## Context
`reusable-trivy-scan.yml` was already pinned to a commit SHA rather
than a version tag, because of CVE-2026-33634 (March 2026): an
attacker force-pushed 76 of 77 `trivy-action` version tags — including
ones GitHub had marked "immutable" — to malicious commits. That
incident applies equally to every other third-party Action this repo
calls (`actions/checkout`, `bridgecrewio/checkov-action`,
`aquasecurity/tfsec-action`, `gitleaks/gitleaks-action`,
`sigstore/cosign-installer`, `docker/login-action`,
`actions/upload-artifact`, `actions/download-artifact`) — a tag is a
mutable pointer by default on every one of these repos, not just
Trivy's. The threat model's Spoofing entry already called this out as
a known gap for *this* repo's consumers pinning `@main`; it applies
just as much one layer down, to the Actions this repo itself calls by
tag.

## Decision
Every `uses:` line across every workflow in this repo is pinned to the
commit SHA behind its current version tag, with the tag kept as a
trailing comment for readability:

```yaml
uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6
```

SHAs were resolved via `git ls-remote --tags <repo> <tag> "<tag>^{}"`
against each Action's actual repository at the time of this ADR — not
guessed or reused from memory — and the peeled (dereferenced) commit
was used for the one annotated tag encountered (`sigstore/cosign-
installer@v3`).

## Consequences
- A tag being repointed upstream (maliciously or by accident) can no
  longer silently change what this repo's CI executes — the workflow
  keeps running the exact commit that was reviewed when the pin was
  added, until someone deliberately updates it.
- Updating a dependency now means updating a SHA, not just a tag
  number — slightly more friction than `@v3` auto-tracking patch
  releases, and a deliberate tradeoff: supply-chain integrity over
  update convenience, consistent with `reusable-trivy-scan.yml`'s
  existing precedent.
- This pins the *tag currently in use*, not necessarily the latest
  available release — e.g. `gitleaks/gitleaks-action@v3` pins v3, not
  whatever v4 exists at read time. Bumping to a newer major/minor is a
  separate, deliberate decision, same as it would be with tags.
- Dependabot (or an equivalent) should eventually be configured to
  open PRs bumping these SHAs on a schedule, so pinning doesn't quietly
  calcify into "never updated" — not yet configured, tracked in the
  Future Roadmap.