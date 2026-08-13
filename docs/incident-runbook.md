# Atlas Security — Incident Runbook

## Purpose
A short, practical guide for what to do when this repo's tooling
breaks — either for itself or, more importantly, for every consumer
relying on it at once. Written for whoever is on call, including
future-me.

## Incident classes covered

### 1. Self-validate CI (`opa test`) is red
1. Open the failed `opa-test` job in GitHub Actions.
2. This only runs `opa test policies/opa/ -v` — a failure here means a
   Rego policy and its own test file disagree. Read which specific
   test case failed before touching policy logic.
3. If a policy change was intentional, update the corresponding
   `*_test.rego` file in the *same* PR, and say why in the PR
   description — a policy change without a matching test change is a
   review red flag (see Tampering, in the threat model).

### 2. A reusable workflow breaks every consumer simultaneously
This is the highest-blast-radius incident class this repo can cause,
and it has already happened once in a related form (see the README's
Postmortem: `soft_fail_commented` silently ignored, and Conftest's
default single-namespace evaluation silently skipping the tagging
policy).
1. Check whether the break is in *this* repo's workflow YAML, or in a
   pinned tool's own release (Checkov `3.3.10`, tfsec `1.0.3`,
   Conftest `0.69.0`, Gitleaks `gitleaks-action@v2`) going bad
   upstream.
2. If it's this repo's YAML: revert the breaking commit on `main`
   immediately — every consumer tracking `@main` inherits the fix the
   moment it's merged, same as they inherited the break.
3. If it's an upstream tool release: pin back to the last known-good
   version in the relevant `*-version` input's default, and open an
   issue to track re-upgrading once the upstream problem is confirmed
   fixed.
4. **Silent failures are worse than loud ones** (see Postmortem in the
   README) — after any fix, don't just confirm the job goes green;
   confirm it's actually evaluating what it's supposed to (e.g., rerun
   with `-v`/verbose output and read it, don't trust the exit code
   alone).

### 3. Suspected compromised commit on `main`
1. Immediately review recent commit history (`git log --oneline -20`)
   and diff each recent change against what its PR description claims.
2. Pay specific attention to any commit touching `policies/opa/*.rego`
   that *also* touches the matching `*_test.rego` in the same commit —
   that combination is the exact shape of the Tampering threat above
   and deserves the highest scrutiny.
3. If confirmed malicious or accidental-but-dangerous: revert on
   `main` immediately, notify anyone with access to consuming repos
   (currently just `atlas-foundation`) that a bad version was live
   between two timestamps, and have them re-run their CI once the
   revert lands.
4. File an ADR documenting what happened and what changed as a result
   (e.g., "this incident is why we now require two-reviewer approval
   on `policies/` changes"), consistent with how `atlas-foundation`
   handles its own incidents.

### 4. A consumer reports a false positive/negative from a Rego policy
1. Reproduce locally: `conftest test <their-plan.json> --policy
   policies/opa/ --all-namespaces` against the plan JSON they provide.
2. If it's a genuine bug in the policy logic, fix it and add a test
   case to `tagging_test.rego` (or the relevant `*_test.rego`) that
   would have caught it — every real bug found this way should leave
   behind a permanent regression test, not just a fix.
3. If it's expected behavior the consumer misunderstood, that's a
   signal the policy's `deny` message isn't clear enough — improve the
   message text, since a confusing CI failure message is itself a
   minor incident in a shared-tooling repo.

## Escalation
Single-maintainer project, no on-call rotation today. In a
multi-engineer context, this section would name who to page for a
class-2 (multi-consumer-breaking) incident specifically, since that's
the one that affects people outside this repo.