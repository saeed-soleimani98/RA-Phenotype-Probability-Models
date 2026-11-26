# Security and privacy reporting

The repository contains only source code and documentation. It must never contain participant-level clinical material, identifiers, credentials, tokens, private Drive links, signed URLs, or cloud authorization details.

Automated safeguards in `.github/workflows/static-audit.yml`, `.pre-commit-config.yaml` and `tests/` reject prohibited file extensions, disclosure patterns, notebook outputs and oversized files. `tools/privacy_audit.py` inventories tracked files and scans Git history.

If you find a possible disclosure: **stop**, do not publish or share the repository, do not rewrite history on your own, and report it privately to the owner using the channel specified in `docs/DATA_AVAILABILITY.md` once the owner supplies it. Include the exact commit, path and line or cell. The owner will decide whether to remove the item from all history and rerun the full audit.

[OWNER_ACTION: add a monitored security contact and any institutional reporting requirements. Do not put private contact details in the repository without approval.]

GitHub code scanning, Dependabot and third-party integrations remain **owner decisions**; enable them only if they do not upload restricted runtime artifacts. CI must never request or receive the clinical dataset.
