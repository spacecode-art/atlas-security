# ADR-0005: Security dashboard uses CSV history + Grafana, not Prometheus

## Status
Accepted

## Context
The original Atlas execution plan calls for "a security dashboard:
run Grafana locally in Docker, feed it your scan results as time-
series data" as part of Phase 2. This was not built in the initial
repo scope.

Scan results (Checkov, tfsec, Trivy, Semgrep, Grype, Gitleaks) are
discrete, periodic events — one data point per CI run, not a
continuous metric stream. A Prometheus + Pushgateway setup solves for
continuously-scraped or continuously-pushed metrics; using it here
would mean standing up a scrape target or a persistently-reachable
Pushgateway for something that happens a few times a day at most, and
add an always-running service with no continuous data behind it.

## Decision
Findings are appended as rows to a single committed CSV
(`dashboard/metrics/scan-history.csv`) by a script
(`scripts/ingest-scan-results.py`) run manually or from CI after each
scan job. A `docker-compose.yml` in `dashboard/` runs Grafana plus a
minimal `nginx:alpine` static file server exposing that CSV; Grafana's
CSV datasource plugin (`marcusolsson-csv-datasource`) reads it over
HTTP. No Prometheus, no Pushgateway, no persistently-running scrape
target — the whole stack is two containers, started on demand.

## Consequences
- The CSV is committed to git, so scan history is itself version-
  controlled and diffable — a side benefit Prometheus's on-disk TSDB
  wouldn't give for free.
- This only captures runs where someone (or CI) explicitly ran the
  ingest script — it is not a live, continuously-updating dashboard.
  That's an accepted tradeoff, consistent with "periodic event," not
  "continuous metric."
- If scan frequency or volume ever grows to the point a real time-
  series database is justified, this ADR should be revisited — the
  CSV approach doesn't scale past a few hundred rows gracefully in
  Grafana's CSV plugin.
- Not yet wired into CI automatically (manual `ingest-scan-results.py`
  invocation for now) — see Future Roadmap.