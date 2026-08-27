# ADR-0008: Enforce skip-list ADR citations with a script, not review alone

## Status
Accepted

## Context
The convention that every Checkov/tfsec skip must cite an ADR (visible
in `atlas-foundation`'s `checkov-skip-checks` comments, e.g. `# CKV_AWS_130
— ADR-0010 (...)`) has existed since early in this project but was
enforced only by whoever reviewed the PR noticing an uncited ID. The
threat model flagged this explicitly under Elevation of Privilege: a
skip added without review, or reviewed by someone who didn't check,
silently widens what a consuming repo's CI will pass.

## Decision
`scripts/lint-skip-citations.py` parses a consumer's workflow file,
extracts every check ID referenced by its `checkov-skip-checks:` value
(the canonical, comma-separated form Checkov itself consumes), and
checks that each ID also appears in a `#`-comment line somewhere in
the file alongside an `ADR-\d+` token. It understands the shorthand
slash-chain form already in use for readability (`CKV_AWS_144/145/119
/18/CKV2_61/62/11` — a family/provider is stated once and carried
forward until it changes), so the existing comment style in
`atlas-foundation`'s `ci.yml` didn't need to be rewritten to pass.

Exit code 1 and a list of uncited IDs on failure; exit 0 with a count
on success. Verified against `atlas-foundation`'s real `ci.yml` (13
skipped checks, all cited — passes) and against a deliberately-broken
copy with an uncited ID injected (correctly fails, naming it).

## Consequences
- This is a script, not a `workflow_call` — a consuming repo runs it
  against its own workflow file(s) as a CI step; it isn't wired into
  every consumer's CI yet (that's a per-consumer follow-up, tracked in
  the Future Roadmap, same class of rollout as `reusable-*-scan.yml`
  itself needing to be adopted one repo at a time).
- It only checks that a citation *exists* near the ID — it does not
  verify the cited ADR number actually exists in `docs/adr/`, or that
  the ADR's content genuinely justifies that specific check. That's a
  meaningfully smaller guarantee than "the skip is justified," but a
  strictly larger one than "someone remembered to look" (the status
  quo it replaces).
- The shorthand-chain parser is heuristic (regex-based state carried
  across `/`-separated segments), not a real YAML/Rego-level parser.
  It was built and tested against the one real shorthand style this
  project uses; a sufficiently different comment style could defeat
  it silently. Acceptable for a first version; worth hardening if the
  convention grows more varied across repos.