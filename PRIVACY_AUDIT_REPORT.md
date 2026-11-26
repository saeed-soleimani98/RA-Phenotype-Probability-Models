# Privacy and disclosure audit report

**Status:** construction audit completed; **owner approved public release on 2026-11-26**. Publication is pending push to the owner-created GitHub repository. License, author, DOI/archive and release metadata remain owner-action placeholders.
**Scope:** all tracked files, all 13 notebooks, and the complete local Git history. No clinical data were accessed, downloaded, generated, or committed.

## 1. Source verification

| Item | Value |
|:--|:--|
| Source package | `RA_Phenotype_Models_Code_Repository_Package.zip` (Google Drive) |
| Supplied SHA-256 | `dc8c0c0b14411d88b6d0e9946b61841a8f6695ba42a6ff611c9b69977fb60f40` |
| Computed SHA-256 | identical |
| Verification | `sha256sum -c ...` → `OK` |
| Supporting files read first | `README.md`, `PRIVACY_AND_DATA_GOVERNANCE.md`, `FILE_MANIFEST.tsv` |

The source package itself contained **no** data/model binaries: 13 `.ipynb`, 23 `.md`, 8 `.py`, 7 `.txt`, 5 `.yaml`, 1 `.tsv`. All notebooks had zero outputs and zero execution counts on arrival.

## 2. Files excluded or changed for privacy

No participant-level file existed in the source package, so none was copied. The following supplied *text* items were disclosive and were sanitized **before the first commit**:

| Supplied file | Finding | Action |
|:--|:--|:--|
| `notebooks/02_data_cleaning_and_preprocessing.ipynb` | Six correction records containing VisitID values and individual original/cleaned values | Replaced the hard-coded list with `_load_authorized_corrections()` reading `RA_CORRECTIONS_PATH`; validation logic unchanged |
| `scripts/build_decision_report.py` | Four decision-register lines with identifiers, individual values and rare-record counts | Reworded without identifiers, values or counts |
| `docs/stage2_verification.md` | Numbered list of VisitID-linked corrections with values | Replaced by a statement that the authorized local specification holds them |
| All notebooks/scripts/docs | Machine-specific absolute paths (`G:\Medical-ML\RA`, `/home/user/...`, Colab Drive folders) | Replaced with `RA_*` environment variables and `pathlib.Path` resolution |

Additionally, the byte-identical notebook `03B_modeling_validation_COLAB_v1_1.ipynb` was moved to `archive/notebooks/` and documented, not deleted.

**Explicitly excluded from the repository:** raw/cleaned/imputed/derived participant data, VisitID values, row-level outcomes/predictors, fold assignments, OOF predictions, bootstrap rows, patient-stability tables, patient-level SHAP/local explanations/direction-linkage files, trained models/preprocessors/calibrators/packages, notebook outputs/previews/widget state/result images, credentials/tokens/private emails/private Drive links/signed URLs, and any Git history containing them. No synthetic patient data were created; the only fixture is a hand-written schema template with placeholders (`config/corrections_template.json`).

## 3. Methods

* SHA-256 verification of the source ZIP against the supplied checksum file.
* Full MIME/size/hash inventory of tracked files (`docs/FILE_INVENTORY_SHA256.tsv`, `FILE_MANIFEST.tsv`; owner-approved threshold 1 MiB).
* Text scans over every tracked text file and notebook cell source for: email addresses, token/API-key/password patterns, signed URLs, private Drive links, absolute private paths, VisitID-plus-number patterns, long base64 blobs.
* Notebook validation: JSON parse, zero cell outputs, zero execution counts, no embedded binary payloads.
* Compilation of every Python file; YAML parse of every YAML/CFF file.
* Prohibited-extension check (CSV, TSV*, Excel, Parquet, Feather, HDF5, pickle/joblib, NPY/NPZ, ONNX, model binaries). *Allowed TSV exceptions: the non-sensitive manifests only.
* Forbidden path-term check (`raw_data`, `cleaned_data`, `derived_data`, `patient_level`, `predictions`, `fold_assignments`, `shap_values`) outside documentation describing exclusions.
* Complete Git-history scan of all commits and all trees (not only `HEAD`).
* Git LFS check: no `.gitattributes` with `filter=lfs`; no LFS objects.
* Static scientific-integrity checks of frozen protocols and notebooks.

Tooling: `python tools/privacy_audit.py` and `python -m pytest -q tests`. Both are data-free and reproducible by reviewers.

## 4. Findings

| Check | Result |
|:--|:--|
| Source checksum | PASS |
| Notebooks valid JSON | PASS (13/13) |
| Notebook outputs | PASS (0 in all 13) |
| Notebook execution counts | PASS (0 in all 13) |
| Embedded base64/image payloads | PASS (none; one HTML template uses a runtime `{b64}` placeholder, not embedded data) |
| Email / token / credential patterns | PASS (0) |
| Private Drive / signed URLs | PASS (0) |
| VisitID-plus-value patterns in code/notebooks | PASS (0) |
| Absolute private paths in executable code/notebooks | PASS (0) |
| Prohibited data/model extensions tracked | PASS (0, aside from three approved text manifests) |
| Forbidden filename terms outside exclusion documentation | PASS (0) |
| Python compilation | PASS |
| YAML/CFF parse | PASS |
| Data-free static tests | PASS (81 tests) |
| Git history scan | PASS at construction; see `tools/privacy_audit.py` output for the final commit |
| Git LFS | Not used |
| Releases / issues / Actions artifacts / caches / branch history | No remote, release, issue or artifact existed during construction. Owner must re-check after push; CI uploads only the text audit report. |

The only text locations containing historical private path strings are `config/PATH_CONFIGURATION.md` and the audit tests, where they appear **as prose describing what was removed**; they are not executable paths and are allowlisted for that pattern only.

## 5. Scientific integrity observations

No scientific inconsistency requiring a code rewrite was found. The frozen protocols prohibit SMOTE/oversampling/undersampling, favorable seeds, global feature selection, full-cohort apparent performance, and promotion of exploratory models. VisitID is used only for alignment; `OnlyLargeJoints` is EDA-only; blank binary/comorbidity values remain unknown; reproductive variables are excluded from all-patient primary models; OOF evaluation is separated from final refits; mean-absolute SHAP is not treated as direction; SHAP direction is documented as predictive and non-causal. These are asserted in `tests/test_scientific_invariants.py`.

## 6. Unresolved owner decisions (must not be completed by the agent)

Repository name/account, software license, public/private status, issues/discussions/forks/integrations, author/contact/ethics/funder metadata, DOI/Zenodo/OSF archive, reviewer link, and final release tag. See `RELEASE_CHECKLIST.md`.

**Do not state that anonymization makes the dataset safe to share.** The owner has decided not to share the data for ethical and governance reasons.
