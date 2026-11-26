# Release checklist — owner approvals still required

The repository stays **private** until every item below is checked by the owner.

## Owner decisions (none completed by the agent)

- [ ] Approve final repository name: `[OWNER_ACTION: name]`
- [ ] Approve GitHub account/organization: `[OWNER_ACTION: account]`
- [ ] Choose a software license: `[OWNER_ACTION: SPDX identifier]` — without a license the code is not openly reusable
- [x] Decide whether to publish at all — **owner approved public release, 2026-11-26**
- [ ] Decide whether to enable issues, discussions, forks and third-party integrations
- [ ] Supply author names, affiliations and a public contact route
- [ ] Supply ethics approval identifier **only if** the owner wants it public
- [ ] Supply funders/institutional acknowledgements
- [ ] Supply article DOI, journal, year and title
- [ ] Decide whether to create a Zenodo/OSF archive and reserve a DOI
- [ ] Approve reviewer-facing read-only link (do not create before approval)

## Technical checks (agent-completed; re-run at release time)

- [ ] `python -m pytest -q tests` passes with zero data present
- [ ] `python tools/privacy_audit.py` reports no findings
- [ ] All notebooks have zero outputs and zero execution counts
- [ ] No prohibited data/model extensions tracked
- [ ] Full Git history scanned, not only `HEAD`
- [ ] No Git LFS objects with excluded material
- [ ] File inventory and SHA-256 hashes recorded in `docs/FILE_INVENTORY_SHA256.tsv`
- [ ] Final commit hash recorded here and in the manuscript: `[OWNER_ACTION: commit hash]`
- [ ] `CITATION.cff` placeholders replaced
- [ ] `DATA_AVAILABILITY.md` contact placeholder replaced
- [ ] Versioned release tag chosen, e.g. `v1.0.0-review`
- [ ] Immutable archive created **after** approval, with the exact commit recorded

## Recommended release sequence

1. Owner approves `PRIVACY_AUDIT_REPORT.md` and all decisions above.
2. Update placeholders, commit, re-run the full privacy audit.
3. Tag `v1.0.0-review` at the reviewed commit.
4. Optionally create an immutable archive with DOI.
5. Only then share a read-only reviewer link.

Do not claim that code availability makes the results fully reproducible without the restricted data.
