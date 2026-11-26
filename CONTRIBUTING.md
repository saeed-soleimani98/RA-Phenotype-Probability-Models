# Contributing

This is a journal-review code repository for a clinical modeling project.

## Before contributing

* Do **not** add clinical data, identifiers, row-level outputs, model binaries, notebook outputs, credentials, private links, or generated figures from restricted data.
* Do **not** change analytical estimands, frozen protocols, outcome definitions, leakage exclusions, CV structure, or seed policies without an explicit owner decision and a documented protocol amendment.
* Keep machine-specific paths out of code; use the environment variables in `.env.example` and `config/PATH_CONFIGURATION.md`.
* Keep notebooks output-free: clear all outputs and execution counts before committing.

## Workflow

1. Create a branch from `main`.
2. Make a minimal, documented change.
3. Run `python -m pytest -q tests` and the privacy scan (`python tools/privacy_audit.py`).
4. Confirm no restricted file type or disclosure pattern is staged.
5. Open a pull request describing the scientific rationale, not merely the code change.

## Review expectations

Changes to scientific logic require owner approval and a note in `CHANGELOG.md` and `docs/SCIENTIFIC_DECISIONS.md`. Cosmetic or navigation changes should not alter notebook cell semantics.

[OWNER_ACTION: add contributor names, contact policy, and any institutional contribution requirements.]
