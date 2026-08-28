# Tawira evidence

Real output, not fabricated or hand-typed. Captured 2026-08-28 against
the image built and signed by Tawira CI run
[33154386457](https://github.com/spacecode-art/Tawira/actions/runs/33154386457)
(commit `20601f2921ce191ad2e53c5188d2aae7652fbf48`), using
`reusable-sbom-scan-sign.yml@v1.0.1`.

| File | What it is | How it was produced |
|---|---|---|
| `sbom-20601f2921ce191ad2e53c5188d2aae7652fbf48.spdx.json` | The real SBOM, downloaded as-is from that CI run's artifact | `gh run download 33154386457 --repo spacecode-art/Tawira` |
| `grype-table-output.txt` | Human-readable vuln scan of that exact SBOM | `grype sbom:<file> -o table` |
| `grype-results.json` | Same scan, machine-readable | `grype sbom:<file> -o json` |
| `cosign-verify-output.txt` | Cryptographic proof the pushed image was signed by this exact pipeline version | `cosign verify --certificate-identity ".../reusable-sbom-scan-sign.yml@refs/tags/v1.0.1" --certificate-oidc-issuer "https://token.actions.githubusercontent.com" ghcr.io/spacecode-art/tawira@sha256:6aaba734bc5c09aecf1347cd94f7bdb11fc3b609a5442329d59ac0424bb8bdbc` |
| `scan-history-snapshot-2026-08-28.csv` | Dashboard's real state as of this capture, including the automated grype/gitleaks rows from ADR-0009's fix | copy of `dashboard/metrics/scan-history.csv` |

## What this proves

- **3 medium-severity findings** (CVE-2025-60876, BusyBox wget header
  injection, affecting `busybox`, `busybox-binsh`, `ssl_client` in the
  base Alpine image) — genuinely present, genuinely below the
  `fail-on-severity: critical` threshold, so the build correctly did
  not block on them. Not yet triaged/ADR-documented — see Future
  Roadmap.
- The signature's certificate subject is
  `spacecode-art/atlas-security/.github/workflows/reusable-sbom-scan-sign.yml@refs/tags/v1.0.1`,
  **not** a Tawira-specific identity — this is expected and correct:
  GitHub's OIDC token for a reusable workflow call identifies the
  *called* workflow, not the caller. Verifying against this identity
  proves the image came from the official pinned pipeline, regardless
  of which consuming repo triggered it — a stronger guarantee than
  "some workflow in Tawira signed this," not a weaker one.
- The transparency-log entry (`logIndex`, `logID`, integrated
  timestamp) is independently checkable on
  [Rekor](https://search.sigstore.dev/) — not just "trust this file."

## Reproducing this yourself

Requires `gh`, `grype`, and `cosign` installed locally, and
`gh auth refresh -h github.com -s read:packages` once if `cosign
login ghcr.io` returns `DENIED` rather than `UNAUTHORIZED` — the
default `gh` token doesn't carry package-read scope by default.
