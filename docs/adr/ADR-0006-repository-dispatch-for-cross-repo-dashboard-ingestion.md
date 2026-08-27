# ADR-0006: Wire dashboard ingestion into CI via `repository_dispatch`

## Status
Accepted

## Context
ADR-0005 introduced the CSV-backed Grafana dashboard but left ingestion
manual: `scripts/ingest-scan-results.py` had to be invoked by hand
after each scan. Closing that gap means getting a scan result produced
in a *consumer* repo's CI run (atlas-foundation, Tawira) appended to a
CSV that is committed inside *this* repo — a cross-repo write, which
reusable `workflow_call` workflows don't solve on their own: a called
workflow executes with the secrets and `GITHUB_TOKEN` of the *caller*,
not of the repo the workflow file lives in. Three approaches were
considered:

1. **Push-based**: the reusable scan workflow checks out atlas-security
   directly (as `reusable-opa-scan.yml` already does for policies) and
   commits/pushes using a PAT passed in by the *consumer*. Simple, but
   puts the commit logic in every scan workflow and means atlas-security
   accepts pushes authenticated as whatever token each consumer holds.
2. **Pull-based polling**: atlas-security runs its own scheduled
   workflow that calls the GitHub API to fetch each consumer's latest
   run artifacts. Avoids consumers needing a token at all, but requires
   atlas-security to hold read tokens scoped to every consumer and adds
   polling latency and API-quota cost for something that happens a few
   times a day.
3. **`repository_dispatch`**: the consumer's scan workflow sends a
   dispatch event (authenticated with a narrowly-scoped PAT that can
   only *trigger* the event) to atlas-security; a workflow living in
   atlas-security, triggered by that event, does the actual ingest and
   commit using its own repo-scoped `GITHUB_TOKEN`.

## Decision
Use `repository_dispatch` (option 3). Each reusable scan workflow gains
an optional `ingest-token` secret input; if a consumer hasn't set it,
the dispatch step no-ops rather than failing the workflow. `atlas-
security` owns `ingest-scan-results.yml`, triggered on
`repository_dispatch: types: [scan-result]`, which is the only place
that ever commits to `dashboard/metrics/scan-history.csv` — via
`permissions: contents: write` on its own `GITHUB_TOKEN`, not a PAT.

**Payload contents differ by tool.** Checkov, tfsec, Semgrep, and Grype
findings are configuration/dependency data, not secret material, so
their raw JSON/SARIF is embedded directly in the dispatch payload and
parsed by the existing `parse_*` functions in `ingest-scan-results.py`
— no duplicate parsing logic. Gitleaks is the exception: its report
contains the actual matched secret text. The gitleaks reusable workflow
never lets that leave the runner — it re-runs gitleaks locally, keeps
only the finding count, and sends a redacted stub (`[{}, {}, ...]`,
length-preserving but content-free) that satisfies `parse_gitleaks`'s
existing `len(findings)` logic without transmitting anything sensitive
cross-repo.

## Consequences
- Each consumer repo now needs one manually-configured secret (a
  fine-grained PAT scoped only to trigger dispatches on
  `spacecode-art/atlas-security`) — a one-time setup cost per repo,
  not automated by this ADR. `atlas-foundation`'s `ci.yml` documents
  where to wire it; Tawira's CI needs the same secret added separately.
- `repository_dispatch` client payloads are capped (GitHub enforces a
  practical limit in the tens of KB). At current scale every tool's
  JSON output is well under that. If a scanned repo grows enough that
  Checkov or Grype output approaches the limit, the fix is to switch
  that tool's payload to an artifact pointer (run ID + artifact name)
  and have `ingest-scan-results.yml` pull it via the API instead of
  embedding it — not a redesign, an extension of this same workflow.
- A dispatch landing while another commit is mid-flight can lose a
  race and fail its push. Accepted at today's volume (a few scans a
  day, per ADR-0005) rather than adding retry/rebase logic; revisit if
  dispatch frequency grows enough to make collisions routine.
- Every scan job now runs its tool a second time (in a JSON-only,
  `continue-on-error` step) purely for ingestion, because the primary
  gating step's own output format isn't a contract this dashboard
  should depend on. This roughly doubles each tool's runtime in CI —
  acceptable for tools that run in seconds to low minutes; worth
  revisiting if a future tool is slow enough to make that costly.