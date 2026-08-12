# ADR-0001: Use Tawira (private SaaS repo) instead of a throwaway sample-app

## Status
Accepted

## Context
The original Atlas execution plan calls for a minimal `sample-app/`
inside `atlas-security`, whose only purpose is giving the SBOM/Grype/
Cosign pipeline (Phase 2) something real to build a container image
from. A separate, already-in-progress project — Tawira, a TanStack
Start + Supabase SaaS application — exists in a private repository on
the same GitHub account.

Scanning and signing a real, working application is stronger evidence
than scanning a hello-world container built solely to satisfy a
checklist. The tradeoff: Tawira has no Dockerfile yet, so it cannot be
containerized as-is.

`atlas-security`'s reusable workflows are called via
`uses: spacecode-art/atlas-security/.github/workflows/X.yml@main`.
GitHub Actions permits a private repository to call a reusable workflow
from a *public* repository without extra configuration — the
constraint only bites in the other direction (a private repo's
workflows being called from elsewhere). Since `atlas-security` is and
remains public, this direction is unaffected regardless of Tawira's
visibility.

## Decision
- Retire the empty `sample-app/` placeholder directory.
- Containerize Tawira (add a `Dockerfile`, likely multi-stage: Node
  build stage + a slim runtime stage) as a prerequisite step before
  the SBOM/Grype/Cosign pipeline can run against it.
- Point the upcoming `reusable-sbom-scan-sign.yml` workflow at
  Tawira's built image instead of a synthetic sample app.

## Consequences
- One additional real deliverable (Tawira's Dockerfile) sits ahead of
  the SBOM/Grype/Cosign phase that wasn't previously scoped — this is
  legitimate scope, not padding, since a production app needing a
  proper build image is valuable independent of security tooling.
- Scan/SBOM/signing evidence going forward is generated against real,
  evolving software rather than a static toy app, which is more
  representative of how these tools behave against dependency churn
  over time.
- If Tawira's dependency tree changes (new npm packages, base image
  bumps), Grype findings will fluctuate accordingly — this is a
  feature, not noise; a sample-app's dependency tree would have
  stayed frozen and stopped generating interesting findings.