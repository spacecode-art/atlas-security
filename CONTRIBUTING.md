# Contributing

Thank you for your interest in contributing to Atlas Security.

## Development Workflow

1. Create a feature branch from `main`.
2. Make focused, well-documented changes.
3. Run `opa test policies/opa/ -v` locally before committing if you
   touched anything under `policies/opa/`.
4. Open a Pull Request with a clear description.

## Policy and Workflow Changes

Per [ADR-0002](docs/adr/ADR-0002-require-codeowner-review-on-policies.md),
`policies/opa/**` and `.github/workflows/**` are CODEOWNERS-protected.
Any change to a `.rego` policy must update its matching `*_test.rego`
file in the *same* PR — a policy change without a matching test change
is a review red flag on its own (see the threat model's Tampering
entry).

## Commit Messages

Follow a clear, descriptive style.

Examples:

```text
feat(workflows): add reusable-sbom-scan-sign.yml
docs: record ADR-0003 graduation criteria
fix(opa): correct tagging.rego namespace evaluation
```