#!/usr/bin/env python3
"""
Append a row to dashboard/metrics/scan-history.csv from a scan tool's
raw output. Supports checkov (JSON), tfsec (JSON), semgrep (SARIF),
grype (JSON), and gitleaks (JSON). See ADR-0005 for why CSV, not
Prometheus.

Usage:
    python3 scripts/ingest-scan-results.py \
        --tool checkov --repo atlas-foundation \
        --input /tmp/checkov-output.json \
        --output dashboard/metrics/scan-history.csv
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ["date", "tool", "repo", "passed", "failed", "high", "medium", "low"]


def parse_checkov(data):
    summary = data.get("summary", data)
    if isinstance(data, list):
        summary = next((d.get("summary", {}) for d in data if "summary" in d), {})
    return {
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "high": 0, "medium": 0, "low": 0,  # Checkov summary has no severity breakdown
    }


def parse_tfsec(data):
    results = data.get("results") or []
    sev = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "CRITICAL": 0}
    for r in results:
        s = (r.get("severity") or "").upper()
        if s in sev:
            sev[s] += 1
    return {
        "passed": 0,  # tfsec JSON doesn't report a passed count directly
        "failed": len(results),
        "high": sev["HIGH"] + sev["CRITICAL"],
        "medium": sev["MEDIUM"],
        "low": sev["LOW"],
    }


def parse_semgrep_sarif(data):
    runs = data.get("runs", [])
    results = runs[0].get("results", []) if runs else []
    sev = {"error": 0, "warning": 0, "note": 0}
    for r in results:
        lvl = r.get("level", "warning")
        if lvl in sev:
            sev[lvl] += 1
    return {
        "passed": 0,
        "failed": len(results),
        "high": sev["error"],
        "medium": sev["warning"],
        "low": sev["note"],
    }


def parse_grype(data):
    matches = data.get("matches", [])
    sev = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Negligible": 0}
    for m in matches:
        s = m.get("vulnerability", {}).get("severity", "")
        if s in sev:
            sev[s] += 1
    return {
        "passed": 0,
        "failed": len(matches),
        "high": sev["Critical"] + sev["High"],
        "medium": sev["Medium"],
        "low": sev["Low"] + sev["Negligible"],
    }


def parse_gitleaks(data):
    findings = data if isinstance(data, list) else data.get("findings", [])
    return {"passed": 0, "failed": len(findings), "high": len(findings), "medium": 0, "low": 0}


PARSERS = {
    "checkov": parse_checkov,
    "tfsec": parse_tfsec,
    "semgrep": parse_semgrep_sarif,
    "grype": parse_grype,
    "gitleaks": parse_gitleaks,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True, choices=PARSERS.keys())
    ap.add_argument("--repo", required=True)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    if not args.input.exists():
        sys.exit(f"Input file not found: {args.input}")

    with open(args.input) as f:
        data = json.load(f)

    row = PARSERS[args.tool](data)
    row["date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    row["tool"] = args.tool
    row["repo"] = args.repo

    write_header = not args.output.exists() or args.output.stat().st_size == 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    print(f"Appended: {row}")


if __name__ == "__main__":
    main()