#!/usr/bin/env python3
"""
Enforce the skip-list ADR-citation convention (atlas-security ADR-0008):
every Checkov/tfsec check ID a consuming repo skips via
`checkov-skip-checks:` must be justified by a comment, directly above
that key, citing an ADR (a token matching `ADR-\d+`).

Handles the shorthand slash-chain convention already in use (e.g.
`CKV_AWS_144/145/119/18/CKV2_61/62/11` — a provider is only spelled out
once per family and carried forward until the family changes).

Usage:
    python3 lint-skip-citations.py path/to/consumer/ci.yml
Exit code 0 if every skipped ID is cited; 1 otherwise, printing the
uncited IDs.
"""
import re
import sys

SKIP_KEY_RE = re.compile(r'^(\s*)checkov-skip-checks:\s*(.*)$')
CANONICAL_ID_RE = re.compile(r'\bCKV2?_[A-Z]+_\d+\b')
CHAIN_RE = re.compile(r'\bCKV2?[A-Z0-9_/]*\d\b')
ADR_RE = re.compile(r'ADR-\d+')


def expand_chain(run):
    """Expand a shorthand slash-chain into full canonical IDs, e.g.
    'CKV_AWS_144/145/119/18/CKV2_61/62/11' -> [CKV_AWS_144, CKV_AWS_145,
    CKV_AWS_119, CKV_AWS_18, CKV2_AWS_61, CKV2_AWS_62, CKV2_AWS_11].
    A bare family+number segment (CKV2_61) inherits the most recently
    seen provider in the chain, defaulting to AWS if none seen yet."""
    ids = []
    cur_family = "CKV"
    cur_provider = "AWS"
    for seg in run.split('/'):
        m3 = re.match(r'^(CKV2?)_([A-Z]+)_(\d+)$', seg)
        m2 = re.match(r'^(CKV2?)_(\d+)$', seg)
        m1 = re.match(r'^(\d+)$', seg)
        if m3:
            cur_family, cur_provider, num = m3.groups()
            ids.append(f"{cur_family}_{cur_provider}_{num}")
        elif m2:
            cur_family, num = m2.groups()
            ids.append(f"{cur_family}_{cur_provider}_{num}")
        elif m1:
            ids.append(f"{cur_family}_{cur_provider}_{m1.group(1)}")
    return ids


def find_skipped_ids(lines):
    """Full canonical IDs referenced by every `checkov-skip-checks:`
    block's value (folded scalar or inline) — this list always uses
    canonical form, never shorthand."""
    ids = set()
    in_value_block = False
    value_indent = None
    for line in lines:
        m = SKIP_KEY_RE.match(line)
        if m:
            key_indent = len(m.group(1))
            inline = m.group(2).strip()
            if inline and not inline.startswith(('>', '|')):
                ids.update(CANONICAL_ID_RE.findall(inline))
            else:
                in_value_block = True
                value_indent = key_indent
            continue
        if in_value_block:
            if line.strip() == '':
                continue
            indent = len(line) - len(line.lstrip(' '))
            if indent <= value_indent:
                in_value_block = False
                continue
            ids.update(CANONICAL_ID_RE.findall(line))
    return ids


def find_cited_ids(lines):
    """{full_id: has_adr_citation} for every ID mentioned in a
    `#`-comment line, expanding shorthand chains."""
    cited = {}
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('#'):
            continue
        has_adr = bool(ADR_RE.search(stripped))
        for run in CHAIN_RE.findall(stripped):
            for full_id in expand_chain(run):
                cited[full_id] = cited.get(full_id, False) or has_adr
    return cited


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: lint-skip-citations.py <workflow.yml>")

    path = sys.argv[1]
    with open(path) as f:
        lines = f.readlines()

    skipped = find_skipped_ids(lines)
    cited = find_cited_ids(lines)
    uncited = sorted(i for i in skipped if not cited.get(i, False))

    if uncited:
        print(f"FAIL: {len(uncited)} skipped check(s) with no ADR-cited comment in {path}:")
        for i in uncited:
            print(f"  - {i}")
        sys.exit(1)

    print(f"OK: {len(skipped)} skipped check(s) in {path}, all ADR-cited.")
    sys.exit(0)


if __name__ == "__main__":
    main()